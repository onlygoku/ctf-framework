"""
Test Suite - Full coverage for CTF Framework
"""

import pytest
import tempfile
from pathlib import Path


@pytest.fixture
def config(tmp_path):
    from ctf_core.config import Config
    return Config(db_path=str(tmp_path/"test.db"), challenges_dir=str(tmp_path/"challenges"),
                  secret_key="a"*32, dynamic_scoring=False)

@pytest.fixture
def manager(config):
    from ctf_core.challenge_manager import ChallengeManager
    return ChallengeManager(config)

@pytest.fixture
def validator(config):
    from ctf_core.flag_validator import FlagValidator
    return FlagValidator(config)

@pytest.fixture
def scoreboard(config):
    from ctf_core.scoreboard import Scoreboard
    return Scoreboard(config)

@pytest.fixture
def client(config):
    from web.app import create_app
    app = create_app(config)
    app.config["TESTING"] = True
    return app.test_client()


class TestChallengeManager:
    def test_create_challenge(self, manager):
        ch = manager.create_challenge("web", "Test Web", points=100, difficulty="easy")
        assert ch.id and ch.flag.startswith("CTF{")
        assert Path(ch.path).exists()

    def test_flag_not_in_public_metadata(self, manager):
        import json
        ch = manager.create_challenge("crypto", "Crypto Test")
        with open(Path(ch.path)/"challenge.json") as f:
            assert "flag" not in json.load(f)

    def test_list_and_filter(self, manager):
        manager.create_challenge("web", "Web 1")
        manager.create_challenge("web", "Web 2")
        manager.create_challenge("crypto", "Crypto 1")
        assert len(manager.list_challenges()) == 3
        assert len(manager.list_challenges(category="web")) == 2

    def test_get_challenge(self, manager):
        ch = manager.create_challenge("pwn", "Pwn Test")
        fetched = manager.get_challenge(ch.id)
        assert fetched and fetched.flag == ch.flag

    def test_invalid_category(self, manager):
        with pytest.raises(ValueError):
            manager.create_challenge("invalid", "Bad")

    def test_delete_challenge(self, manager):
        ch = manager.create_challenge("misc", "Delete Me")
        path = ch.path
        assert manager.delete_challenge(ch.id)
        assert not Path(path).exists()
        assert manager.get_challenge(ch.id) is None

    def test_pwn_scaffold(self, manager):
        ch = manager.create_challenge("pwn", "Overflow")
        assert (Path(ch.path)/"src"/"chall.c").exists()
        assert (Path(ch.path)/"solve.py").exists()

    def test_crypto_scaffold(self, manager):
        ch = manager.create_challenge("crypto", "RSA")
        assert (Path(ch.path)/"chall.py").exists()
        assert (Path(ch.path)/"solve.py").exists()


class TestFlagValidator:
    def test_correct_flag(self, manager, validator):
        ch = manager.create_challenge("web", "Flag Test")
        result = validator.validate(ch.id, ch.flag, "team1")
        assert result.correct and result.points == ch.points

    def test_wrong_flag(self, manager, validator):
        ch = manager.create_challenge("web", "Wrong Test")
        assert not validator.validate(ch.id, "CTF{wrong}", "team1").correct

    def test_whitespace_trimming(self, manager, validator):
        ch = manager.create_challenge("web", "Whitespace")
        assert validator.validate(ch.id, f"  {ch.flag}  ", "team2").correct

    def test_already_solved(self, manager, validator):
        ch = manager.create_challenge("web", "Solved Test")
        validator.validate(ch.id, ch.flag, "team1")
        assert validator.validate(ch.id, ch.flag, "team1").already_solved

    def test_first_blood(self, manager, validator):
        ch = manager.create_challenge("web", "Blood Test")
        result = validator.validate(ch.id, ch.flag, "team_a")
        assert "FIRST BLOOD" in result.message

    def test_rate_limiting(self, manager, validator):
        validator.rate_limiter.max_attempts = 3
        ch = manager.create_challenge("web", "Rate Limit")
        for _ in range(3):
            validator.validate(ch.id, "CTF{wrong}", "limited")
        assert "Too many" in validator.validate(ch.id, "CTF{wrong}", "limited").message

    def test_nonexistent_challenge(self, validator):
        assert not validator.validate("fake_id", "CTF{x}", "t").correct


class TestScoreboard:
    def test_register_team(self, scoreboard):
        assert scoreboard.register_team("alpha")
        assert not scoreboard.register_team("alpha")  # duplicate

    def test_get_top(self, scoreboard):
        scoreboard.register_team("t1")
        scoreboard.register_team("t2")
        assert isinstance(scoreboard.get_top(10), list)

    def test_team_stats(self, scoreboard):
        scoreboard.register_team("stats_team", "US")
        stats = scoreboard.get_team_stats("stats_team")
        assert stats and stats["country"] == "US"


class TestAPI:
    def test_get_challenges(self, client, manager):
        manager.create_challenge("web", "API Test")
        r = client.get("/api/v1/challenges")
        assert r.status_code == 200 and "challenges" in r.get_json()

    def test_submit_correct(self, client, manager):
        ch = manager.create_challenge("web", "Submit Test")
        r = client.post("/api/v1/submit", json={"challenge_id": ch.id, "flag": ch.flag, "team": "t"})
        assert r.get_json()["correct"]

    def test_submit_wrong(self, client, manager):
        ch = manager.create_challenge("web", "Wrong Submit")
        r = client.post("/api/v1/submit", json={"challenge_id": ch.id, "flag": "CTF{no}", "team": "t"})
        assert not r.get_json()["correct"]

    def test_scoreboard(self, client):
        assert client.get("/api/v1/scoreboard").status_code == 200

    def test_register_team(self, client):
        r = client.post("/api/v1/teams/register", json={"name": "new_team"})
        assert r.get_json()["success"]

    def test_duplicate_team(self, client):
        client.post("/api/v1/teams/register", json={"name": "dup"})
        assert client.post("/api/v1/teams/register", json={"name": "dup"}).status_code == 409

    def test_index_loads(self, client):
        assert client.get("/").status_code == 200

    def test_missing_fields(self, client):
        assert client.post("/api/v1/submit", json={"flag": "x"}).status_code == 400


