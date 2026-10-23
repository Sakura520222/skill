#!/usr/bin/env python3
"""Install through the real Skills CLI in a temporary project and compare files."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills/astrbot-plugin-dev"


def hashes(root: Path) -> dict[str, str]:
    return {
        path.relative_to(root).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in root.rglob("*")
        if path.is_file() and "__pycache__" not in path.parts and path.suffix != ".pyc"
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--source", default=str(ROOT), help="Local repository or GitHub owner/repo"
    )
    args = parser.parse_args()
    npx = shutil.which("npx.cmd" if os.name == "nt" else "npx")
    if not npx:
        raise SystemExit("npx is required (Node.js >=22.20)")
    env = {**os.environ, "DISABLE_TELEMETRY": "1", "CI": "1"}
    with tempfile.TemporaryDirectory(prefix="astrbot-skill-install-") as directory:
        project = Path(directory).resolve()
        if not project.is_relative_to(Path(tempfile.gettempdir()).resolve()):
            raise RuntimeError(
                "Temporary project is outside the expected temp directory"
            )
        command = [
            npx,
            "--yes",
            "skills@1.7.4",
            "add",
            args.source,
            "--skill",
            "astrbot-plugin-dev",
            "--agent",
            "claude-code",
            "codex",
            "--copy",
            "--yes",
            "--json",
        ]
        result = subprocess.run(
            command,
            check=False,
            cwd=project,
            env=env,
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
            timeout=180,
        )
        if result.returncode:
            print(result.stdout)
            print(result.stderr)
            return result.returncode
        expected = hashes(SKILL)
        destinations = {
            "claude-code": project / ".claude/skills/astrbot-plugin-dev",
            "codex": project / ".agents/skills/astrbot-plugin-dev",
        }
        for agent, path in destinations.items():
            actual = hashes(path)
            if actual != expected:
                raise RuntimeError(f"Installed files differ for {agent}: {path}")
        print(
            json.dumps(
                {
                    "source": args.source,
                    "installer": "skills@1.7.4",
                    "agents": list(destinations),
                    "verified_files_per_agent": len(expected),
                }
            )
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
