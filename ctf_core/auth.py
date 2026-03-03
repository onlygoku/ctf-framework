import os
import secrets
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dataclasses import dataclass
from typing import Optional
from collections import defaultdict

import bcrypt
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature

from .database import Database
from .config import Config


@dataclass
class AuthResult:
    success: bool
    message: str
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
                id SERIAL PRIMARY KEY,
                name TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                score INTEGER DEFAULT 0,
                solves INTEGER DEFAULT 0,
                country TEXT DEFAULT '',
                verified INTEGER DEFAULT 0,
                banned INTEGER DEFAULT 0,
                last_solve REAL DEFAULT 0,
                created_at REAL DEFAULT (EXTRACT(EPOCH FROM NOW()))
            )
        """)
        self.db.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                id SERIAL PRIMARY KEY,
                team TEXT NOT NULL,
                token TEXT UNIQUE NOT NULL,
                created_at REAL DEFAULT (EXTRACT(EPOCH FROM NOW())),
                expires_at REAL NOT NULL
            )
        """)
        self.db.execute("""
            CREATE TABLE IF NOT EXISTS login_attempts (
                id SERIAL PRIMARY KEY,
                ip_address TEXT NOT NULL,
                attempted_at REAL DEFAULT (EXTRACT(EPOCH FROM NOW()))
            )
        """)
        # Fix old schema if ip column exists instead of ip_address
        try:
            self.db.execute(
                "ALTER TABLE login_attempts ADD COLUMN IF NOT EXISTS ip_address TEXT"
            )
        except:
            pass

    def register(self, team_name: str, email: str, password: str, country: str = "") -> AuthResult:
        if not team_name or len(team_name) < 2:
            return AuthResult(False, "Team name must be at least 2 characters")
        if not email or "@" not in email:
            return AuthResult(False, "Invalid email address")
        if not password or len(password) < 8:
            return AuthResult(False, "Password must be at least 8 characters")

        if self.db.fetchone("SELECT id FROM teams WHERE name=?", (team_name,)):
            return AuthResult(False, "Team name already taken")
        if self.db.fetchone("SELECT id FROM teams WHERE email=?", (email,)):
            return AuthResult(False, "Email already registered")

        password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

        if self.config.skip_email:
            self.db.execute(
                "INSERT INTO teams (name, email, password_hash, country, verified) VALUES (?,?,?,?,1)",
                (team_name, email, password_hash, country)
            )
            return AuthResult(True, "Registration successful! You can now login.")
        else:
            self.db.execute(
                "INSERT INTO teams (name, email, password_hash, country, verified) VALUES (?,?,?,?,0)",
                (team_name, email, password_hash, country)
            )
            try:
                self._send_verification_email(team_name, email)
                return AuthResult(True, "Registration successful! Please check your email to verify your account.")
            except Exception as e:
                print(f"[AUTH] Email error: {e}")
                return AuthResult(True, "Registration successful! (Email verification unavailable - contact admin)")

    def _send_verification_email(self, team_name: str, email: str):
        token = self.serializer.dumps(email, salt="email-verify")
        verify_url = f"{self.config.base_url}/verify/{token}"

        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"[{self.config.ctf_name}] Verify your email"
        msg["From"] = self.config.mail_sender or self.config.mail_username
        msg["To"] = email

        html = f"""
        <html><body style="background:#050a0f;color:#cde;font-family:monospace;padding:2rem;">
        <h2 style="color:#00ff88;">Welcome to {self.config.ctf_name}, {team_name}!</h2>
        <p>Click the link below to verify your email:</p>
        <a href="{verify_url}" style="color:#00d4ff;">{verify_url}</a>
        <p style="color:#4a8a6a;margin-top:2rem;">This link expires in 24 hours.</p>
        </body></html>
        """
        msg.attach(MIMEText(html, "html"))

        with smtplib.SMTP(self.config.mail_server, self.config.mail_port) as server:
            server.starttls()
            server.login(self.config.mail_username, self.config.mail_password)
            server.sendmail(self.config.mail_username, email, msg.as_string())

    def verify_email(self, token: str) -> AuthResult:
        try:
            email = self.serializer.loads(token, salt="email-verify", max_age=86400)
            row = self.db.fetchone("SELECT name FROM teams WHERE email=?", (email,))
            if not row:
                return AuthResult(False, "Team not found")
            self.db.execute("UPDATE teams SET verified=1 WHERE email=?", (email,))
            return AuthResult(True, "Email verified! You can now login.")
        except SignatureExpired:
            return AuthResult(False, "Verification link has expired.")
        except BadSignature:
            return AuthResult(False, "Invalid verification link.")

    def resend_verification(self, email: str) -> AuthResult:
        row = self.db.fetchone("SELECT name, verified FROM teams WHERE email=?", (email,))
        if not row:
            return AuthResult(False, "Email not found")
        if row[1]:
            return AuthResult(False, "Email already verified")
        try:
            self._send_verification_email(row[0], email)
            return AuthResult(True, "Verification email resent!")
        except Exception as e:
            return AuthResult(False, f"Failed to send email: {e}")

    def login(self, team_name: str, password: str, ip: str = "0.0.0.0") -> AuthResult:
        now = time.time()
        # Bruteforce protection
        try:
            attempts = self.db.fetchall(
                "SELECT id FROM login_attempts WHERE ip_address=? AND attempted_at > ?",
                (ip, now - 300)
            )
            if len(attempts) >= 5:
                return AuthResult(False, "Too many login attempts. Try again in 5 minutes.")
            self.db.execute("INSERT INTO login_attempts (ip_address) VALUES (?)", (ip,))
        except Exception as e:
            print(f"[AUTH] Rate limit check failed: {e}")

        row = self.db.fetchone(
            "SELECT name, password_hash, verified, banned FROM teams WHERE name=?",
            (team_name,)
        )
        if not row:
            return AuthResult(False, "Invalid team name or password")

        name, pw_hash, verified, banned = row

        if not bcrypt.checkpw(password.encode(), pw_hash.encode()):
            return AuthResult(False, "Invalid team name or password")
        if banned:
            return AuthResult(False, "Your team has been banned.")
        if not verified:
            return AuthResult(False, "Please verify your email before logging in.")

        token = secrets.token_hex(32)
        expires = now + 86400
        self.db.execute(
            "INSERT INTO sessions (team, token, expires_at) VALUES (?,?,?)",
            (name, token, expires)
        )
        return AuthResult(True, "Login successful!", token=token, team=name)

    def validate_session(self, token: str) -> Optional[str]:
        if not token:
            return None
        row = self.db.fetchone(
            "SELECT team FROM sessions WHERE token=? AND expires_at > ?",
            (token, time.time())
        )
        return row[0] if row else None

    def logout(self, token: str):
        self.db.execute("DELETE FROM sessions WHERE token=?", (token,))

    def is_admin(self, team_name: str) -> bool:
        return team_name == self.config.admin_username

    def get_team_info(self, team_name: str) -> Optional[dict]:
        row = self.db.fetchone(
            "SELECT name, score, solves, country, verified, banned FROM teams WHERE name=?",
            (team_name,)
        )
        if not row:
            return None
        return {
            "name": row[0], "score": row[1], "solves": row[2],
            "country": row[3], "verified": bool(row[4]), "banned": bool(row[5])
        }

    def get_all_teams(self) -> list:
        rows = self.db.fetchall(
            "SELECT name, email, score, solves, country, verified, banned FROM teams ORDER BY score DESC"
        )
        return [
            {"name": r[0], "email": r[1], "score": r[2], "solves": r[3],
             "country": r[4], "verified": bool(r[5]), "banned": bool(r[6])}
            for r in rows
        ]

    def ban_team(self, name: str):
        self.db.execute("UPDATE teams SET banned=1 WHERE name=?", (name,))
        self.db.execute("DELETE FROM sessions WHERE team=?", (name,))

    def unban_team(self, name: str):
        self.db.execute("UPDATE teams SET banned=0 WHERE name=?", (name,))

    def delete_team(self, name: str):
        self.db.execute("DELETE FROM solves WHERE team=?", (name,))
        self.db.execute("DELETE FROM sessions WHERE team=?", (name,))
        self.db.execute("DELETE FROM hint_unlocks WHERE team=?", (name,))
        self.db.execute("DELETE FROM submissions WHERE team=?", (name,))
        self.db.execute("DELETE FROM teams WHERE name=?", (name,))

    def reset_team_score(self, name: str):
        self.db.execute("UPDATE teams SET score=0, solves=0, last_solve=0 WHERE name=?", (name,))
        self.db.execute("DELETE FROM solves WHERE team=?", (name,))
        self.db.execute("DELETE FROM hint_unlocks WHERE team=?", (name,))