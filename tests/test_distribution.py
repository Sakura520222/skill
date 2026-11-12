"""Behavioral checks for source integrity, archive portability and validation."""

from __future__ import annotations

import io
import json
import shutil
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from build import archive_bytes, build  # noqa: E402
from fetch_sources import blob_sha, fetch_sources, safe_source_path  # noqa: E402
from validate_skill import SKILL, validate  # noqa: E402


class DistributionTests(unittest.TestCase):
    def test_napcat_distribution_covers_both_upstreams(self):
        skill = ROOT / "skills/napcat-api-dev"
        result = validate(skill)
        manifests = [
            json.loads(path.read_text(encoding="utf-8"))
            for path in (skill / "references").glob("sources*.json")
        ]
        self.assertEqual(
            {manifest["repository"] for manifest in manifests},
            {"NapNeko/NapCatDocs", "NapNeko/NapCatQQ"},
        )
        self.assertEqual(
            result["sources"], sum(len(item["sources"]) for item in manifests)
        )
        content = archive_bytes(skill)
        self.assertEqual(content, archive_bytes(skill))
        with zipfile.ZipFile(io.BytesIO(content)) as archive:
            self.assertIsNone(archive.testzip())
            expected = {
                "napcat-api-dev/" + path.relative_to(skill).as_posix()
                for path in skill.rglob("*")
                if path.is_file()
            }
            self.assertEqual(set(archive.namelist()), expected)

    def test_secondary_source_manifest_is_validated(self):
        skill = ROOT / "skills/napcat-api-dev"
        with tempfile.TemporaryDirectory(prefix="napcat-provenance-test-") as directory:
            copy = Path(directory) / skill.name
            shutil.copytree(skill, copy)
            source = copy / "references/sources-implementation.json"
            manifest = json.loads(source.read_text(encoding="utf-8"))
            manifest["sources"][0]["blob_sha"] = "invalid"
            source.write_text(json.dumps(manifest), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "Invalid source blob SHA"):
                validate(copy)

    def test_napcat_sources_fetch_from_each_pinned_repository(self):
        data = b"# Official source\n"
        for repository in ("NapNeko/NapCatDocs", "NapNeko/NapCatQQ"):
            with self.subTest(repository=repository):
                manifest = {
                    "repository": repository,
                    "commit": "d" * 40,
                    "sources": [{"path": "README.md", "blob_sha": blob_sha(data)}],
                }
                with tempfile.TemporaryDirectory(
                    prefix="napcat-source-test-"
                ) as directory:
                    with patch("fetch_sources.download", return_value=data) as fetch:
                        fetch_sources(manifest, Path(directory) / "sources")
                    self.assertEqual(
                        fetch.call_args.args[0],
                        f"https://raw.githubusercontent.com/{repository}/"
                        + "d" * 40
                        + "/README.md",
                    )

    def test_miuix_distribution_is_complete_and_reproducible(self):
        skill = ROOT / "skills/miuix-guidance"
        self.assertEqual(validate(skill)["name"], "miuix-guidance")
        content = archive_bytes(skill)
        self.assertEqual(content, archive_bytes(skill))
        with zipfile.ZipFile(io.BytesIO(content)) as archive:
            self.assertIsNone(archive.testzip())
            expected = {
                "miuix-guidance/" + path.relative_to(skill).as_posix()
                for path in skill.rglob("*")
                if path.is_file()
            }
            self.assertEqual(set(archive.namelist()), expected)

    def test_miuix_sources_use_the_recorded_repository(self):
        data = b"# Miuix source\n"
        manifest = {
            "repository": "compose-miuix-ui/miuix",
            "commit": "a" * 40,
            "sources": [{"path": "docs/guide/theme.md", "blob_sha": blob_sha(data)}],
        }
        with tempfile.TemporaryDirectory(prefix="miuix-source-test-") as directory:
            with patch("fetch_sources.download", return_value=data) as fetch:
                fetch_sources(manifest, Path(directory) / "sources")
            self.assertEqual(
                fetch.call_args.args[0],
                "https://raw.githubusercontent.com/compose-miuix-ui/miuix/"
                + "a" * 40
                + "/docs/guide/theme.md",
            )

    def test_skill_and_examples_validate(self):
        result = validate()
        self.assertGreater(result["examples"], 0)
        self.assertGreater(result["local_links"], 0)

    def test_archives_are_reproducible_complete_and_portable(self):
        content = archive_bytes(SKILL)
        self.assertEqual(content, archive_bytes(SKILL))
        with tempfile.TemporaryDirectory(prefix="astrbot-skill-archive-") as directory:
            output = Path(directory).resolve()
            self.assertTrue(
                output.is_relative_to(Path(tempfile.gettempdir()).resolve())
            )
            paths = build(SKILL, output / "dist")
            self.assertEqual(paths[0].read_bytes(), paths[1].read_bytes())
            with zipfile.ZipFile(io.BytesIO(content)) as archive:
                self.assertIsNone(archive.testzip())
                names = archive.namelist()
                self.assertEqual(names, sorted(names))
                self.assertTrue(
                    all(name.startswith("astrbot-plugin-dev/") for name in names)
                )
                self.assertTrue(all(".." not in Path(name).parts for name in names))
                expected = {
                    "astrbot-plugin-dev/" + path.relative_to(SKILL).as_posix()
                    for path in SKILL.rglob("*")
                    if path.is_file()
                    and "__pycache__" not in path.parts
                    and path.suffix != ".pyc"
                }
                self.assertEqual(set(names), expected)
                archive.extractall(output / "extracted")
            validate(output / "extracted/astrbot-plugin-dev")

    def test_rejects_unsafe_source_paths(self):
        for path in ("../escape", "/absolute", "C:/escape", "a\\b", "a//b", "a/./b"):
            with self.subTest(path=path), self.assertRaises(ValueError):
                safe_source_path(path)

    def test_source_fetch_checks_blob_and_preserves_bytes(self):
        data = b"# Source\n\nExample.\n"
        manifest = {
            "repository": "AstrBotDevs/AstrBot",
            "commit": "a" * 40,
            "sources": [{"path": "docs/zh/example.md", "blob_sha": blob_sha(data)}],
        }
        with tempfile.TemporaryDirectory(prefix="astrbot-source-test-") as directory:
            output = Path(directory) / "sources"
            with patch("fetch_sources.download", return_value=data):
                result = fetch_sources(manifest, output)
            self.assertEqual(result["commit"], manifest["commit"])
            self.assertEqual((output / "files/docs/zh/example.md").read_bytes(), data)
            saved = json.loads((output / "sources.json").read_text(encoding="utf-8"))
            self.assertEqual(saved["sources"][0]["blob_sha"], blob_sha(data))
            with (
                patch("fetch_sources.download", return_value=data),
                self.assertRaises(ValueError),
            ):
                fetch_sources(manifest, output)

    def test_source_integrity_failure_does_not_write_partial_cache(self):
        manifest = {
            "repository": "AstrBotDevs/AstrBot",
            "commit": "b" * 40,
            "sources": [{"path": "docs/zh/example.md", "blob_sha": "0" * 40}],
        }
        with tempfile.TemporaryDirectory(prefix="astrbot-source-test-") as directory:
            output = Path(directory) / "sources"
            with (
                patch("fetch_sources.download", return_value=b"changed"),
                self.assertRaises(ValueError),
            ):
                fetch_sources(manifest, output)
            self.assertFalse(output.exists())

    def test_upstream_ref_resolves_once_before_download(self):
        data = b"new source\n"
        manifest = {
            "repository": "AstrBotDevs/AstrBot",
            "commit": "a" * 40,
            "sources": [{"path": "docs/zh/example.md", "blob_sha": "0" * 40}],
        }
        with tempfile.TemporaryDirectory(prefix="astrbot-source-test-") as directory:
            with patch(
                "fetch_sources.download",
                side_effect=[json.dumps({"sha": "c" * 40}).encode(), data],
            ) as fetch:
                result = fetch_sources(manifest, Path(directory) / "sources", "master")
            self.assertEqual(result["commit"], "c" * 40)
            self.assertIn("/" + "c" * 40 + "/", fetch.call_args_list[1].args[0])
            self.assertEqual(fetch.call_count, 2)


if __name__ == "__main__":
    unittest.main()
