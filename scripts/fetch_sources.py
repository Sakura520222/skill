#!/usr/bin/env python3
"""Fetch the recorded official sources to a fresh cache, pinned to one commit."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import UTC, datetime
from pathlib import Path, PurePosixPath
from urllib.parse import quote
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "skills/astrbot-plugin-dev/references/sources.json"
MAX_SOURCE_BYTES = 2 * 1024 * 1024


def download(url: str) -> bytes:
    request = Request(url, headers={"User-Agent": "Skill-source-fetcher/1.0"})
    with urlopen(request, timeout=30) as response:
        data = response.read(MAX_SOURCE_BYTES + 1)
    if len(data) > MAX_SOURCE_BYTES:
        raise ValueError(f"Source exceeds 2 MiB: {url}")
    data.decode("utf-8")
    return data


def blob_sha(data: bytes) -> str:
    return hashlib.sha1(f"blob {len(data)}\0".encode() + data).hexdigest()


def safe_source_path(value: str) -> PurePosixPath:
    path = PurePosixPath(value)
    if (
        path.is_absolute()
        or "\\" in value
        or ":" in value
        or any(part in {"", ".", ".."} for part in value.split("/"))
    ):
        raise ValueError(f"Unsafe source path: {value}")
    return path


def fetch_sources(manifest: dict, output: Path, ref: str | None = None) -> dict:
    if output.exists() and (not output.is_dir() or any(output.iterdir())):
        raise ValueError(f"Output must be a new or empty directory: {output}")
    repository = manifest["repository"]
    if repository not in {
        "AstrBotDevs/AstrBot",
        "compose-miuix-ui/miuix",
        "NapNeko/NapCatDocs",
        "NapNeko/NapCatQQ",
    }:
        raise ValueError("This fetcher only retrieves recorded official repositories")
    commit = ref or manifest["commit"]
    if not re.fullmatch(r"[0-9a-f]{40}", commit):
        info = json.loads(
            download(
                f"https://api.github.com/repos/{repository}/commits/{quote(commit, safe='')}"
            )
        )
        commit = info["sha"]
    if not re.fullmatch(r"[0-9a-f]{40}", commit):
        raise ValueError("Could not resolve an immutable commit")

    fetched = []
    entries = []
    seen = set()
    for entry in manifest["sources"]:
        path = safe_source_path(entry["path"])
        if path.as_posix().casefold() in seen:
            raise ValueError(f"Duplicate source path: {path}")
        seen.add(path.as_posix().casefold())
        url = f"https://raw.githubusercontent.com/{repository}/{commit}/{path}"
        data = download(url)
        actual = blob_sha(data)
        if commit == manifest["commit"] and actual != entry["blob_sha"]:
            raise ValueError(f"Source blob mismatch: {path}")
        fetched.append((path, data))
        entries.append(
            {
                **entry,
                "blob_sha": actual,
                "sha256": hashlib.sha256(data).hexdigest(),
                "url": entry.get("url", "").replace(manifest["commit"], commit),
                "source_url": f"https://github.com/{repository}/blob/{commit}/{path}",
            }
        )

    # Network or integrity failures above leave the destination untouched.
    timestamp = datetime.now(UTC)
    updated = {
        **manifest,
        "commit": commit,
        "snapshot_date": timestamp.date().isoformat(),
        "retrieved_at_utc": timestamp.isoformat(),
        "sources": entries,
    }
    for path, data in fetched:
        if str(path) == "pyproject.toml":
            import tomllib

            updated["astrbot_version"] = tomllib.loads(data.decode())["project"][
                "version"
            ]
    output.mkdir(parents=True, exist_ok=True)
    for path, data in fetched:
        target = output / "files" / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
    (output / "sources.json").write_text(
        json.dumps(updated, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return updated


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=MANIFEST)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--ref", help="Optional upstream ref; resolved to an immutable SHA"
    )
    args = parser.parse_args()
    try:
        manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
        result = fetch_sources(manifest, args.output, args.ref)
    except (OSError, ValueError, KeyError) as error:
        print(f"Fetch failed: {error}", file=sys.stderr)
        return 1
    print(
        f"Fetched {len(result['sources'])} sources at {result['commit']} to {args.output}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
