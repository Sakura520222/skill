#!/usr/bin/env python3
"""Build reproducible ZIP and .skill archives containing only the portable skill."""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import zipfile
from pathlib import Path

from validate_skill import SKILL, frontmatter, validate


def archive_bytes(skill: Path) -> bytes:
    validate(skill)
    buffer = io.BytesIO()
    with zipfile.ZipFile(
        buffer, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9
    ) as archive:
        for path in sorted(
            skill.rglob("*"), key=lambda p: p.relative_to(skill).as_posix()
        ):
            if path.is_symlink():
                raise ValueError(f"Refusing symlink: {path}")
            if not path.is_file():
                continue
            relative = path.relative_to(skill)
            if "__pycache__" in relative.parts or path.suffix == ".pyc":
                continue
            name = (Path(skill.name) / relative).as_posix()
            info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, path.read_bytes(), compresslevel=9)
    return buffer.getvalue()


def build(skill: Path, output: Path) -> list[Path]:
    content = archive_bytes(skill)
    meta = frontmatter((skill / "SKILL.md").read_text(encoding="utf-8"))
    stem = f"{meta['name']}-{meta['metadata']['version']}"
    output.mkdir(parents=True, exist_ok=True)
    files = [output / f"{stem}.zip", output / f"{stem}.skill"]
    for path in files:
        path.write_bytes(content)
    checksum = output / "SHA256SUMS.txt"
    checksum.write_text(
        "".join(
            f"{hashlib.sha256(path.read_bytes()).hexdigest()}  {path.name}\n"
            for path in files
        ),
        encoding="utf-8",
    )
    return [*files, checksum]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skill", type=Path, default=SKILL)
    parser.add_argument("--output", type=Path, default=Path("dist"))
    args = parser.parse_args()
    print(json.dumps([str(p) for p in build(args.skill, args.output)]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
