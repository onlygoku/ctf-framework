"""
Auth - Email registration, verification, login, sessions, bruteforce protection
"""

import os
import secrets
import smtplib
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dataclasses import dataclass
from typing import Optional
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature

from .database import Database
from .config import Config


@dataclass
class AuthResult:
    success: bool
    message: str = ""
    token: str = ""
    team: str = ""


class AuthManager:
    def __init__(self, config: Optional[Config] = None):
        self.config = config or Config()
        self.db = Database(self.config.db_path)
        self.serializer = URLSafeTimedSerializer(self.config.secret_key)
        self._ensure_schema()

    def _ensure_schema(self):
        self.db.execute("""
            CREATE TABLE IF NOT EXISTS teams (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                country TEXT DEFAULT '',
                score INTEGER DEFAULT 0,
                solves INTEGER DEFAULT 0,
                last_solve REAL DEFAULT 0,
                verified INTEGER DEFAULT 0,
                banned INTEGER DEFAULT 0,
                created_at REAL DEFAULT (strftime('%s', 'now'))
            )
        """)
        self.db.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                team_name TEXT NOT NULL,
                token TEXT UNIQUE NOT NULL,
                ip_address TEXT DEFAULT '',
                created_at REAL DEFAULT (strftime('%s', 'now')),
                expires_at REAL NOT NULL
            )
        """)
        self.db.execute("""
            CREATE TABLE IF NOT EXISTS login_attempts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ip_address TEXT NOT NULL,
                team_name TEXT DEFAULT '',
                success INTEGER DEFAULT 0,
                attempted_at REAL DEFAULT (strftime('%s', 'now'))
            )
        """)

    def _hash_password(self, password: str) -> str:
        import bcrypt
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    def _verify_password(self, password: str, hashed: str) -> bool:
        import bcrypt
        return bcrypt.checkpw(password.encode(), hashed.encode())

    def _is_bruteforce(self, ip: str) -> bool:
        cutoff = time.time() - 300
        row = self.db.fetchone("""
            SELECT COUNT(*) FROM login_attempts
            WHERE ip_address=? AND success=0 AND attempted_at > ?
        """, (ip, cutoff))
        return (row[0] if row else 0) >= 5

    def _log_attempt(self, ip: str, team: str, success: bool):
        self.db.execute(
            "INSERT INTO login_attempts (ip_address, team_name, success) VALUES (?,?,?)",
            (ip, team, int(success))
        )

    def register(self, team_name: str, email: str, password: str, country: str = "") -> AuthResult:
        if not self.config.registration_open:
            return AuthResult(False, "Registration is closed.")
        if len(team_name) < 3 or len(team_name) > 32:
            return AuthResult(False, "Team name must be 3-32 characters.")
        if len(password) < 8:
            return AuthResult(False, "Password must be at least 8 characters.")
        if "@" not in email or "." not in email.split("@")[-1]:
            return AuthResult(False, "Invalid email address.")

        existing_name = self.db.fetchone(
            "SELECT id FROM teams WHERE name=?", (team_name,)
        )
        if existing_name:
            return AuthResult(False, "Team name already taken.")

        existing_email = self.db.fetchone(
            "SELECT id FROM teams WHERE email=?", (email,)
        )
        if existing_email:
            return AuthResult(False, "Email already registered.")

        password_hash = self._hash_password(password)
        self.db.execute(
            "INSERT INTO teams (name, email, password_hash, country) VALUES (?,?,?,?)",
            (team_name, email, password_hash, country)
        )
        self._send_verification_email(email, team_name)
        return AuthResult(True, "Registration successful! Check your email to verify.")

    def _send_verification_email(self, email: str, team_name: str):
        if os.getenv("SKIP_EMAIL", "false").lower() == "true":
            print(f"[DEV MODE] Auto-verifying {team_name} ({email})")
            self.db.execute(
                "UPDATE teams SET verified=1 WHERE email=?", (email,)
            )
            return

        token = self.serializer.dumps(email, salt="email-verify")
        base_url = os.getenv("CTF_BASE_URL", "http://localhost:5000")
        verify_url = f"{base_url}/verify/{token}"
        ctf_name = self.config.ctf_name

        html = f"""
        <div style="font-family:monospace;background:#050a0f;color:#00ff88;padding:40px;border-radius:8px;">
            <h1 style="color:#00ff88;">🏴 {ctf_name}</h1>
            <p style="color:#cde;">Welcome, <strong>{team_name}</strong>!</p>
            <p style="color:#cde;">Click below to verify your email.</p>
            <a href="{verify_url}"
               style="display:inline-block;margin:20px 0;padding:12px 24px;
                      background:#00ff88;color:#050a0f;text-decoration:none;
                      font-weight:bold;border-radius:4px;">
               VERIFY EMAIL
            </a>
            <p style="color:#6a8;font-size:12px;">Expires in 24 hours.</p>
        </div>
        """

        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"[{ctf_name}] Verify your email"
        msg["From"] = os.getenv("MAIL_DEFAULT_SENDER", "noreply@ctf.local")
        msg["To"] = email
        msg.attach(MIMEText(html, "html"))

        try:
            server = smtplib.SMTP(
                os.getenv("MAIL_SERVER", "smtp.gmail.com"),
                int(os.getenv("MAIL_PORT", "587"))
            )
            server.starttls()
            server.login(os.getenv("MAIL_USERNAME"), os.getenv("MAIL_PASSWORD"))
            server.sendmail(msg["From"], email, msg.as_string())
            server.quit()
            print(f"[EMAIL] Sent to {email}")
        except Exception as e:
            print(f"[EMAIL ERROR] {e}")

    def verify_email(self, token: str) -> AuthResult:
        try:
            email = self.serializer.loads(
                token, salt="email-verify", max_age=86400
            )
        except SignatureExpired:
            return AuthResult(False, "Link expired. Please register again.")
        except BadSignature:
            return AuthResult(False, "Invalid verification link.")

        row = self.db.fetchone(
            "SELECT name, verified FROM teams WHERE email=?", (email,)
        )
        if not row:
            return AuthResult(False, "Account not found.")
        if row[1]:
            return AuthResult(True, "Already verified! You can log in.")

        self.db.execute(
            "UPDATE teams SET verified=1 WHERE email=?", (email,)
        )
        return AuthResult(True, f"Email verified! Welcome, {row[0]}!")

    def login(self, team_name: str, password: str, ip: str = "0.0.0.0") -> AuthResult:
        if self._is_bruteforce(ip):
            return AuthResult(False, "Too many failed attempts. Try again in 5 minutes.")

        row = self.db.fetchone(
            "SELECT name, password_hash, verified, banned FROM teams WHERE name=?",
            (team_name,)
        )

        if not row:
            self._log_attempt(ip, team_name, False)
            return AuthResult(False, "Invalid team name or password.")

        name, password_hash, verified, banned = row

        if not self._verify_password(password, password_hash):
            self._log_attempt(ip, team_name, False)
            return AuthResult(False, "Invalid team name or password.")

        if banned:
            return AuthResult(False, "This team has been banned.")

        if not verified:
            return AuthResult(False, "Please verify your email first.")

        self._log_attempt(ip, team_name, True)

        token = secrets.token_urlsafe(32)
        expires = time.time() + (24 * 3600)
        self.db.execute(
            "INSERT INTO sessions (team_name, token, ip_address, expires_at) VALUES (?,?,?,?)",
            (name, token, ip, expires)
        )
        return AuthResult(True, f"Welcome back, {name}!", token=token, team=name)

    def validate_session(self, token: str) -> Optional[str]:
        if not token:
            return None
        row = self.db.fetchone(
            "SELECT team_name, expires_at FROM sessions WHERE token=?", (token,)
        )
        if not row:
            return None
        team_name, expires_at = row
        if time.time() > expires_at:
            self.db.execute("DELETE FROM sessions WHERE token=?", (token,))
            return None
        return team_name

    def logout(self, token: str):
        self.db.execute("DELETE FROM sessions WHERE token=?", (token,))

    def get_team_info(self, team_name: str) -> Optional[dict]:
        row = self.db.fetchone(
            "SELECT name, email, country, score, solves, verified, created_at FROM teams WHERE name=?",
            (team_name,)
        )
        if not row:
            return None
        return {
            "name": row[0], "email": row[1], "country": row[2],
            "score": row[3], "solves": row[4],
            "verified": bool(row[5]), "created_at": row[6]
        }

    def resend_verification(self, email: str) -> AuthResult:
        row = self.db.fetchone(
            "SELECT name, verified FROM teams WHERE email=?", (email,)
        )
        if not row:
            return AuthResult(False, "Email not found.")
        if row[1]:
            return AuthResult(False, "Already verified!")
        self._send_verification_email(email, row[0])
        return AuthResult(True, "Verification email resent!")