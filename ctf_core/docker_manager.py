"""
Docker Manager - Challenge container lifecycle
"""

import subprocess
import json
from dataclasses import dataclass
from typing import Optional

from .challenge_manager import ChallengeManager
from .config import Config


@dataclass
class DockerResult:
    success: bool
    image_name: str = ""
    port: int = 0
    container_id: str = ""
    error: str = ""


class DockerManager:
    def __init__(self, config: Optional[Config] = None):
        self.config = config or Config()
        self.manager = ChallengeManager(config)
        self._verify_docker()

    def _verify_docker(self):
        try:
            subprocess.run(["docker", "info"], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            raise RuntimeError("Docker is not available. Please install Docker.")

    def _run(self, cmd, **kwargs):
        return subprocess.run(cmd, capture_output=True, text=True, **kwargs)

    def build(self, challenge_id: str) -> DockerResult:
        challenge = self.manager.get_challenge(challenge_id)
        if not challenge:
            return DockerResult(success=False, error="Challenge not found")
        image_name = f"ctf/{challenge.name.lower().replace(' ', '_')}:{challenge.id}"
        result = self._run(["docker", "build", "-t", image_name, challenge.path])
        if result.returncode != 0:
            return DockerResult(success=False, error=result.stderr)
        return DockerResult(success=True, image_name=image_name)

    def deploy(self, challenge_id: str, port: Optional[int] = None) -> DockerResult:
        challenge = self.manager.get_challenge(challenge_id)
        if not challenge:
            return DockerResult(success=False, error="Challenge not found")
        image_name = f"ctf/{challenge.name.lower().replace(' ', '_')}:{challenge.id}"
        container_name = f"ctf_{challenge.id}"
        host_port = port or (10000 + hash(challenge_id) % 5000)
        self._run(["docker", "rm", "-f", container_name])
        result = self._run([
            "docker", "run", "-d", "--name", container_name,
            "-p", f"{host_port}:5000", "--restart", "unless-stopped",
            "--security-opt", "no-new-privileges", "--read-only",
            "--tmpfs", "/tmp", "-e", f"FLAG={challenge.flag}", image_name,
        ])
        if result.returncode != 0:
            return DockerResult(success=False, error=result.stderr)
        return DockerResult(success=True, image_name=image_name, port=host_port,
                            container_id=result.stdout.strip()[:12])

    def stop(self, challenge_id: str) -> DockerResult:
        result = self._run(["docker", "rm", "-f", f"ctf_{challenge_id}"])
        return DockerResult(success=result.returncode == 0, error=result.stderr)

    def list_running(self) -> list:
        result = self._run(["docker", "ps", "--filter", "name=ctf_", "--format", "{{json .}}"])
        containers = []
        for line in result.stdout.strip().split("\n"):
            if line:
                try:
                    containers.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
        return containers