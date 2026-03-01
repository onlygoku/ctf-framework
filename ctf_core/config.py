"""
Config - Environment-based configuration
"""

import os
from dataclasses import dataclass, field


@dataclass
class Config:
    db_path: str = field(default_factory=lambda: os.getenv("CTF_DB_PATH", "ctf.db"))
    challenges_dir: str = field(default_factory=lambda: os.getenv("CTF_CHALLENGES_DIR", "challenges"))
    secret_key: str = field(default_factory=lambda: os.getenv("CTF_SECRET_KEY", os.urandom(32).hex()))
    host: str = field(default_factory=lambda: os.getenv("CTF_HOST", "0.0.0.0"))
    port: int = field(default_factory=lambda: int(os.getenv("CTF_PORT", "5000")))
    ctf_name: str = field(default_factory=lambda: os.getenv("CTF_NAME", "MyCTF2026"))
    ctf_description: str = field(default_factory=lambda: os.getenv("CTF_DESCRIPTION", "Welcome to the CTF!"))
    flag_prefix: str = field(default_factory=lambda: os.getenv("CTF_FLAG_PREFIX", "CTF"))
    dynamic_scoring: bool = field(default_factory=lambda: os.getenv("CTF_DYNAMIC_SCORING", "true").lower() == "true")
    decay_rate: int = field(default_factory=lambda: int(os.getenv("CTF_DECAY_RATE", "5")))
    max_flag_attempts: int = field(default_factory=lambda: int(os.getenv("CTF_MAX_ATTEMPTS", "10")))
    rate_limit_window: int = field(default_factory=lambda: int(os.getenv("CTF_RATE_WINDOW", "60")))
    registration_open: bool = field(default_factory=lambda: os.getenv("CTF_REGISTRATION", "true").lower() == "true")
    base_url: str = field(default_factory=lambda: os.getenv("CTF_BASE_URL", "http://localhost:5000"))

    # Email
    mail_server: str = field(default_factory=lambda: os.getenv("MAIL_SERVER", "smtp.gmail.com"))
    mail_port: int = field(default_factory=lambda: int(os.getenv("MAIL_PORT", "587")))
    mail_username: str = field(default_factory=lambda: os.getenv("MAIL_USERNAME", ""))
    mail_password: str = field(default_factory=lambda: os.getenv("MAIL_PASSWORD", ""))
    mail_sender: str = field(default_factory=lambda: os.getenv("MAIL_DEFAULT_SENDER", ""))
    admin_username: str = field(default_factory=lambda: os.getenv("CTF_ADMIN", "admin"))
    admin_password: str = field(default_factory=lambda: os.getenv("CTF_ADMIN_PASSWORD", "admin123"))
    start_time: str = field(default_factory=lambda: os.getenv("CTF_START_TIME", ""))
    end_time: str = field(default_factory=lambda: os.getenv("CTF_END_TIME", ""))
    