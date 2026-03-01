"""
Scoreboard - Real-time scoring and leaderboard
"""

from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime

from .database import Database
from .config import Config


@dataclass
class ScoreEntry:
    rank: int
    team: str
    score: int
    solves: int
    last_solve: str
    first_bloods: int = 0


@dataclass
class SolveEvent:
    team: str
    challenge: str
    category: str
    points: int
    timestamp: str
    first_blood: bool = False


class Scoreboard:
    def __init__(self, config: Optional[Config] = None):
        self.config = config or Config()
        self.db = Database(self.config.db_path)
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

    def get_top(self, n: int = 10) -> List[ScoreEntry]:
        rows = self.db.fetchall("""
            SELECT t.name, t.score, t.solves, t.last_solve,
                   COUNT(s.first_blood) as first_bloods
            FROM teams t
            LEFT JOIN solves s ON t.name = s.team AND s.first_blood = 1
            GROUP BY t.name
            ORDER BY t.score DESC, t.last_solve ASC
            LIMIT ?
        """, (n,))
        return [
            ScoreEntry(
                rank=i+1, team=r[0], score=r[1], solves=r[2],
                last_solve=(datetime.fromtimestamp(r[3]).strftime("%Y-%m-%d %H:%M") if r[3] else "Never"),
                first_bloods=r[4]
            )
            for i, r in enumerate(rows)
        ]

    def get_team_rank(self, team: str) -> Optional[int]:
        row = self.db.fetchone("""
            SELECT rank FROM (
                SELECT name, RANK() OVER (ORDER BY score DESC, last_solve ASC) as rank
                FROM teams
            ) WHERE name = ?
        """, (team,))
        return row[0] if row else None

    def get_score_timeline(self, team: str) -> List[dict]:
        rows = self.db.fetchall("""
            SELECT s.solved_at, s.points,
                   SUM(s.points) OVER (ORDER BY s.solved_at) as cumulative
            FROM solves s WHERE s.team = ? ORDER BY s.solved_at
        """, (team,))
        return [{"time": r[0], "points": r[1], "total": r[2]} for r in rows]

    def get_solve_feed(self, limit: int = 20) -> List[SolveEvent]:
        rows = self.db.fetchall("""
            SELECT s.team, c.name, c.category, s.points, s.solved_at, s.first_blood
            FROM solves s JOIN challenges c ON s.challenge_id = c.id
            ORDER BY s.solved_at DESC LIMIT ?
        """, (limit,))
        return [
            SolveEvent(
                team=r[0], challenge=r[1], category=r[2], points=r[3],
                timestamp=datetime.fromtimestamp(r[4]).strftime("%H:%M:%S"),
                first_blood=bool(r[5])
            ) for r in rows
        ]

    def get_category_stats(self) -> List[dict]:
        rows = self.db.fetchall("""
            SELECT c.category, COUNT(DISTINCT c.id), COUNT(DISTINCT s.challenge_id), SUM(c.points)
            FROM challenges c LEFT JOIN solves s ON c.id = s.challenge_id
            GROUP BY c.category ORDER BY c.category
        """)
        return [{"category": r[0], "total": r[1], "solved": r[2], "total_pts": r[3]} for r in rows]

    def register_team(self, name: str, country: str = "") -> bool:
        try:
            self.db.execute("INSERT INTO teams (name, country) VALUES (?, ?)", (name, country))
            return True
        except Exception:
            return False

    def get_team_stats(self, team: str) -> Optional[dict]:
        row = self.db.fetchone(
            "SELECT name, score, solves, country, last_solve FROM teams WHERE name=?", (team,)
        )
        if not row:
            return None
        return {"name": row[0], "score": row[1], "solves": row[2],
                "country": row[3], "last_solve": row[4], "rank": self.get_team_rank(team)}