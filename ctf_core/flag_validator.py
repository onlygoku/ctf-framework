"""
Flag Validator - Secure flag submission with anti-bruteforce protection
"""

import hashlib
import time
from dataclasses import dataclass
from typing import Optional
from collections import defaultdict

from .database import Database
from .challenge_manager import ChallengeManager
from .config import Config


@dataclass
class ValidationResult:
    correct: bool
    points: int = 0
    message: str = ""
    hint: Optional[str] = None
    already_solved: bool = False


class RateLimiter:
    def __init__(self, max_attempts: int = 10, window_seconds: int = 60):
        self.max_attempts = max_attempts
        self.window = window_seconds
        self._buckets: dict = defaultdict(list)

    def is_allowed(self, key: str) -> bool:
        now = time.time()
        self._buckets[key] = [t for t in self._buckets[key] if now - t < self.window]
        if len(self._buckets[key]) >= self.max_attempts:
            return False
        self._buckets[key].append(now)
        return True

    def retry_after(self, key: str) -> float:
        if not self._buckets[key]:
            return 0
        return max(0, self.window - (time.time() - min(self._buckets[key])))


class FlagValidator:
    def __init__(self, config: Optional[Config] = None):
        self.config = config or Config()
        self.db = Database(self.config.db_path)
        self.manager = ChallengeManager(config)
        self.rate_limiter = RateLimiter(
            max_attempts=self.config.max_flag_attempts,
            window_seconds=self.config.rate_limit_window
        )
        self._ensure_schema()

    def _ensure_schema(self):
        self.db.execute("""
            CREATE TABLE IF NOT EXISTS teams (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                score INTEGER DEFAULT 0,
                solves INTEGER DEFAULT 0,
                country TEXT DEFAULT '',
                last_solve REAL DEFAULT 0
            )
        """)
        self.db.execute("""
            CREATE TABLE IF NOT EXISTS submissions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                team TEXT NOT NULL,
                challenge_id TEXT NOT NULL,
                flag_submitted TEXT NOT NULL,
                correct INTEGER NOT NULL,
                points_awarded INTEGER DEFAULT 0,
                ip_address TEXT DEFAULT '',
                submitted_at REAL DEFAULT (strftime('%s', 'now'))
            )
        """)
        self.db.execute("""
            CREATE TABLE IF NOT EXISTS solves (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                team TEXT NOT NULL,
                challenge_id TEXT NOT NULL,
                points INTEGER NOT NULL,
                first_blood INTEGER DEFAULT 0,
                solved_at REAL DEFAULT (strftime('%s', 'now')),
                UNIQUE(team, challenge_id)
            )
        """)

    def validate(self, challenge_id, submitted_flag, team, ip_address="0.0.0.0") -> ValidationResult:
        rate_key = f"{team}:{challenge_id}"
        if not self.rate_limiter.is_allowed(rate_key):
            return ValidationResult(
                correct=False,
                message=f"Too many attempts. Retry after {self.rate_limiter.retry_after(rate_key):.0f}s"
            )

        challenge = self.manager.get_challenge(challenge_id)
        if not challenge:
            return ValidationResult(correct=False, message="Challenge not found")

        if self._already_solved(team, challenge_id):
            return ValidationResult(correct=True, already_solved=True, message="Already solved!")

        correct = self._compare_flags(submitted_flag, challenge.flag)

        if correct:
            points = self._compute_points(challenge)
            is_first_blood = self._record_solve(team, challenge_id, points)
            self.manager.update_solve_count(challenge_id)
            self._update_team_score(team, points)
            msg = ("🩸 FIRST BLOOD! " if is_first_blood else "") + f"Correct! +{points} points"
            self._log_submission(team, challenge_id, submitted_flag, True, points, ip_address)
            return ValidationResult(correct=True, points=points, message=msg)
        else:
            hint = self._get_hint(challenge, team)
            self._log_submission(team, challenge_id, submitted_flag, False, 0, ip_address)
            return ValidationResult(correct=False, message="Incorrect flag", hint=hint)

    def _compare_flags(self, submitted: str, actual: str) -> bool:
        h1 = hashlib.sha256(submitted.strip().encode()).digest()
        h2 = hashlib.sha256(actual.strip().encode()).digest()
        return h1 == h2

    def _compute_points(self, challenge) -> int:
        if not self.config.dynamic_scoring:
            return challenge.points
        min_pts = max(50, challenge.points // 4)
        decay = max(1, challenge.points - (challenge.solves * self.config.decay_rate))
        return max(min_pts, int(decay))

    def _already_solved(self, team, challenge_id) -> bool:
        return self.db.fetchone(
            "SELECT id FROM solves WHERE team=? AND challenge_id=?", (team, challenge_id)
        ) is not None

    def _record_solve(self, team, challenge_id, points) -> bool:
        first_blood = not self.db.fetchone(
            "SELECT id FROM solves WHERE challenge_id=?", (challenge_id,)
        )
        self.db.execute(
            "INSERT OR IGNORE INTO solves (team, challenge_id, points, first_blood) VALUES (?,?,?,?)",
            (team, challenge_id, points, int(first_blood))
        )
        return first_blood

    def _update_team_score(self, team, points):
        self.db.execute("""
            INSERT INTO teams (name, score, solves) VALUES (?, ?, 1)
            ON CONFLICT(name) DO UPDATE SET
                score = score + excluded.score,
                solves = solves + 1,
                last_solve = strftime('%s', 'now')
        """, (team, points))

    def _get_hint(self, challenge, team) -> Optional[str]:
        wrong_count = self.db.fetchone(
            "SELECT COUNT(*) FROM submissions WHERE team=? AND challenge_id=? AND correct=0",
            (team, challenge.id)
        )[0]
        if challenge.hints and wrong_count >= 3:
            idx = min(wrong_count // 3 - 1, len(challenge.hints) - 1)
            return challenge.hints[idx]
        return None

    def _log_submission(self, team, challenge_id, flag, correct, points, ip):
        self.db.execute("""
            INSERT INTO submissions (team, challenge_id, flag_submitted, correct, points_awarded, ip_address)
            VALUES (?,?,?,?,?,?)
        """, (team, challenge_id, flag, int(correct), points, ip))

    def get_team_solves(self, team: str) -> list:
        return self.db.fetchall(
            "SELECT challenge_id, points, first_blood, solved_at FROM solves WHERE team=? ORDER BY solved_at",
            (team,)
        )