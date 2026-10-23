#!/usr/bin/env python3
"""Validate the portable skill, local references, provenance and code examples."""

from __future__ import annotations

import argparse
import ast
import json
import re
import sys
import textwrap
from pathlib import Path
from urllib.parse import unquote, urlsplit

import yaml

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills/astrbot-plugin-dev"


def frontmatter(text: str) -> dict:
    match = re.match(r"\A---\n(.*?)\n---(?:\n|$)", text, re.S)
    if not match:
        raise ValueError("SKILL.md needs YAML frontmatter")
    result = yaml.safe_load(match[1])
    if not isinstance(result, dict):
        raise ValueError("Frontmatter must be a mapping")
    return result


def validate(skill: Path = SKILL) -> dict:
    skill = skill.resolve()
    text = (skill / "SKILL.md").read_text(encoding="utf-8")
    meta = frontmatter(text)
    name = meta.get("name", "")
    if not isinstance(name, str) or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name):
        raise ValueError("Invalid skill name")
    if len(name) > 64 or name != skill.name:
        raise ValueError(
            "Skill name must match its folder and be at most 64 characters"
        )
    description = meta.get("description")
    if (
        not isinstance(description, str)
        or not description.strip()
        or len(description) > 1024
    ):
        raise ValueError("A concise, non-empty description is required")
    if "[TODO:" in text or "\ufffd" in text:
        raise ValueError("Unfinished scaffold or invalid Unicode in skill entrypoint")
    if meta.get("license") != "AGPL-3.0-or-later":
        raise ValueError("Preserve the upstream-compatible license declaration")
    for name in ("LICENSE.txt", "NOTICE.txt"):
        if not (skill / name).is_file():
            raise ValueError(f"Missing distribution notice: {name}")

    ui = yaml.safe_load((skill / "agents/openai.yaml").read_text(encoding="utf-8"))
    interface = ui["interface"]
    if not 25 <= len(interface["short_description"]) <= 64:
        raise ValueError("UI short_description must contain 25-64 characters")
    if "$" + meta["name"] not in interface["default_prompt"]:
        raise ValueError("UI prompt must invoke the skill by name")
    if ui.get("policy", {}).get("allow_implicit_invocation", True) is not True:
        raise ValueError("Automatic skill discovery should remain enabled")

    links = examples = 0
    for path in sorted(skill.rglob("*")):
        if "__pycache__" in path.parts or path.suffix == ".pyc":
            continue
        if path.is_symlink():
            raise ValueError(f"Distributable skill contains a symlink: {path}")
        if not path.is_file():
            continue
        content = path.read_text(encoding="utf-8")
        if path.suffix in {".yaml", ".yml"}:
            yaml.safe_load(content)
        elif path.suffix == ".json":
            json.loads(content)
        elif path.suffix == ".py":
            compile(content, str(path), "exec")
        elif path.suffix == ".md":
            for target in re.findall(r"\[[^\]\n]+\]\(([^)\s]+)\)", content):
                url = urlsplit(target)
                if url.scheme or not url.path:
                    continue
                resolved = (path.parent / unquote(url.path)).resolve()
                if not resolved.is_relative_to(skill) or not resolved.exists():
                    raise ValueError(
                        f"Broken or non-portable local link in {path.name}: {target}"
                    )
                links += 1
            for language, block in re.findall(
                r"^```([\w-]*)\n(.*?)^```[ \t]*$", content, re.M | re.S
            ):
                if language in {"python", "py"}:
                    # Handler fragments may contain top-level await/yield.
                    wrapped = "async def _example():\n" + textwrap.indent(block, "    ")
                    compile(
                        wrapped, str(path), "exec", flags=ast.PyCF_ALLOW_TOP_LEVEL_AWAIT
                    )
                    examples += 1
                elif language == "json":
                    json.loads(block)
                    examples += 1
                elif language in {"yaml", "yml"}:
                    yaml.safe_load(block)
                    examples += 1

    manifest = json.loads(
        (skill / "references/sources.json").read_text(encoding="utf-8")
    )
    if not re.fullmatch(r"[0-9a-f]{40}", manifest["commit"]):
        raise ValueError("Sources must be pinned to an immutable upstream commit")
    if meta["metadata"]["documentation_snapshot"] != manifest["snapshot_date"]:
        raise ValueError("Snapshot dates disagree")
    covered = set()
    for entry in manifest["sources"]:
        if not re.fullmatch(r"[0-9a-f]{40}", entry["blob_sha"]):
            raise ValueError(f"Invalid source blob SHA: {entry['path']}")
        if f"/blob/{manifest['commit']}/" not in entry["source_url"]:
            raise ValueError(f"Unpinned source URL: {entry['path']}")
        for ref in entry["references"]:
            if not (skill / "references" / ref).is_file():
                raise ValueError(f"Missing source destination: {ref}")
            covered.add(ref)
    for path in (skill / "references").glob("*.md"):
        if path.name != "sources.md" and path.name not in covered:
            raise ValueError(f"Reference has no recorded source: {path.name}")
    return {
        "name": meta["name"],
        "local_links": links,
        "examples": examples,
        "sources": len(manifest["sources"]),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", type=Path, nargs="?", default=SKILL)
    args = parser.parse_args()
    try:
        result = validate(args.path)
    except (OSError, ValueError, KeyError, SyntaxError, yaml.YAMLError) as error:
        print(f"Validation failed: {error}", file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
