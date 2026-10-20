# SPDX-License-Identifier: LGPL-3.0-only
"""Independent miniature deliveries; no upstream code, assets, network or JDK."""
import copy
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

import integrate_modernized as integration
import modernized_areas as areas


def encode(value):
    return (json.dumps(value, sort_keys=True) + "\n").encode()


def delivery(area, target, content=b"new\n", patch=False):
    source = None if patch else "overlay/New.java"
    payloads = {"evidence/tests.txt": b"Independent synthetic fixture; unittest exercises actual application.\n"}
    if patch:
        payloads["changes.patch"] = (f"--- a/{target}\n+++ b/{target}\n@@ -1 +1 @@\n-old\n+new\n").encode()
    else:
        payloads[source] = content
    manifest = {"schema": 1, "area": area, "baseline": {"target_base": "a" * 40},
                "kind": "area", "tasks": ["fixture"], "features": ["fixture"], "api_version": "1",
                "requires": [], "patch": "changes.patch" if patch else None,
                "files": [{"target": target, "source": source, "before_sha256": areas.digest(b"old\n") if patch else None,
                           "sha256": areas.digest(content)}], "registrations": [], "tests": [],
                "evidence": ["evidence/tests.txt"]}
    result = {"area": area, "commit": ("1" if area == "machines" else "2") * 40,
              "files": payloads, "manifest": manifest}
    return seal(result)


def seal(item):
    """Re-sign fixtures after intentional metadata edits, so each test hits its own gate."""
    item["files"].pop("area.json", None)
    item["files"].pop("rights.json", None)
    rights = {name: {"sha256": areas.digest(data), "origin": "independent fixture",
                     "source_commit": "fixture", "authors": ["HBM port contributors"],
                     "license": "LGPL-3.0-only", "notices": ["SPDX"], "review": "own fixture",
                     "publication_status": "cleared"} for name, data in item["files"].items()}
    item["files"]["rights.json"] = encode(rights)
    item["manifest"]["payloads"] = {name: areas.digest(data) for name, data in item["files"].items()}
    item["files"]["area.json"] = encode(item["manifest"])
    return item


class DeliveryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.target = self.root / "result"
        self.a = delivery("machines", "src/A.java", patch=True)
        self.b = delivery("nuclear", "src/B.java")
        self.policy = {"baseline": {"target_base": "a" * 40}, "owners": {"src/A.java": "machines", "src/B.java": "nuclear"}}

    def populate(self, checkout, selected):
        checkout.mkdir()
        subprocess.run(["git", "init", "-q", str(checkout)], check=True)
        (checkout / "src").mkdir()
        (checkout / "src/A.java").write_bytes(b"old\n")
        return areas.apply(checkout, selected)

    def run_delivery(self, items):
        selected = areas.validate(items, self.policy)
        integration.publish(self.target, lambda path: self.populate(path, selected))

    def reject(self, items):
        with self.assertRaises((ValueError, KeyError, subprocess.CalledProcessError)):
            self.run_delivery(items)
        self.assertFalse(self.target.exists(), "Rejected delivery exposed a partial target")
        self.assertEqual(list(self.root.glob(".hbm-staging-*")), [])

    def test_two_independent_deltas_reproduce_in_either_selection_order(self):
        self.run_delivery([self.b, self.a])
        before = {str(p.relative_to(self.target)): p.read_bytes() for p in self.target.rglob("*") if p.is_file() and ".git" not in p.parts}
        self.target = self.root / "replay"
        self.run_delivery([self.a, self.b])
        after = {str(p.relative_to(self.target)): p.read_bytes() for p in self.target.rglob("*") if p.is_file() and ".git" not in p.parts}
        self.assertEqual(before, after)
        self.assertEqual(after["src/A.java"], b"new\n")
        self.assertEqual(after["src/B.java"], b"new\n")

    def test_wrong_pin(self):
        self.a["manifest"]["baseline"]["target_base"] = "b" * 40
        self.reject([seal(self.a)])

    def test_wrong_basis_patch_or_overlay_hash(self):
        self.a["manifest"]["baseline"]["files"] = {"basis.patch": "0" * 64}
        self.reject([seal(self.a)])

    def test_wrong_payload_hash(self):
        self.a["files"]["changes.patch"] += b"tampered"
        self.reject([self.a])

    def test_file_outside_allowlist(self):
        self.policy["owners"].clear()
        self.reject([self.a])

    def test_other_owner(self):
        self.policy["owners"]["src/A.java"] = "rendering"
        self.reject([self.a])

    def test_traversal_absolute_backslash_and_git_paths(self):
        for name in ("../escape.java", "/tmp/escape.java", "src/../escape.java", "src\\escape.java", ".git/config", "src//A.java"):
            with self.subTest(name=name):
                item = delivery("machines", name)
                self.policy["owners"][name] = "machines"
                self.reject([item])

    def test_overlapping_overlay(self):
        self.b["manifest"]["files"][0]["target"] = "src/A.java"
        self.reject([self.a, seal(self.b)])

    def test_existing_overlay_target(self):
        self.reject([delivery("machines", "src/A.java")])

    def test_duplicate_area(self):
        self.reject([self.a, self.a])

    def test_undeclared_patch_target(self):
        self.a["files"]["changes.patch"] = self.a["files"]["changes.patch"].replace(b"src/A.java", b"src/B.java")
        self.reject([seal(self.a)])

    def test_disagreeing_diff_header(self):
        self.a["files"]["changes.patch"] = b"diff --git a/secret.java b/secret.java\n" + self.a["files"]["changes.patch"]
        self.reject([seal(self.a)])

    def test_mode_rename_delete_binary_rejected(self):
        for data in (b"old mode 100644\nnew mode 120000\n", b"rename from src/A.java\n", b"GIT binary patch\n", b"--- a/src/A.java\n+++ /dev/null\n"):
            with self.subTest(data=data):
                self.a["files"]["changes.patch"] = data
                self.reject([seal(self.a)])

    def test_patch_hunk_failure_is_atomic(self):
        self.a["files"]["changes.patch"] = self.a["files"]["changes.patch"].replace(b"-old", b"-absent")
        self.reject([seal(self.a), self.b])

    def test_wrong_preimage_hash_is_atomic(self):
        self.a["manifest"]["files"][0]["before_sha256"] = "0" * 64
        self.reject([seal(self.a), self.b])

    def test_wrong_result_hash_is_atomic(self):
        self.a["manifest"]["files"][0]["sha256"] = "0" * 64
        self.reject([seal(self.a), self.b])

    def test_missing_dependency(self):
        self.a["manifest"]["requires"] = [{"area": "nuclear", "commit": self.b["commit"], "api_version": "1"}]
        self.reject([seal(self.a)])

    def test_wrong_dependency_commit_and_api(self):
        for commit, api in (("f" * 40, "1"), (self.b["commit"], "2")):
            self.a["manifest"]["requires"] = [{"area": "nuclear", "commit": commit, "api_version": api}]
            self.reject([seal(self.a), self.b])

    def test_dependency_order(self):
        self.a["manifest"]["requires"] = [{"area": "nuclear", "commit": self.b["commit"], "api_version": "1"}]
        order = areas.validate([seal(self.a), self.b], self.policy)
        self.assertEqual([d["area"] for d in order], ["nuclear", "machines"])

    def test_cycle(self):
        self.a["manifest"]["requires"] = [{"area": "nuclear", "commit": self.b["commit"], "api_version": "1"}]
        self.b["manifest"]["requires"] = [{"area": "machines", "commit": self.a["commit"], "api_version": "1"}]
        self.reject([seal(self.a), seal(self.b)])

    def test_duplicate_registry_identity(self):
        item = delivery("rendering", "src/R.java")
        self.policy["owners"]["src/R.java"] = "rendering"
        item["manifest"]["kind"] = "central"
        item["manifest"]["requests"] = ["requests/registry.json"]
        item["files"]["requests/registry.json"] = encode({"request": "independent registry fixture"})
        registry = {"registry": "block", "id": "hbm_m:fixture", "class": "com.example.Fixture", "bindings": "fixture",
                    "initialization": "fixture", "resources": ["fixture.json"], "tests": ["fixture"], "request": "requests/registry.json"}
        item["manifest"]["registrations"] = [registry, registry]
        self.reject([seal(item)])

    def test_central_requests_before_independent_area_delta(self):
        central = delivery("rendering", "src/R.java")
        self.policy["owners"]["src/R.java"] = "rendering"
        central["manifest"]["kind"] = "central"
        order = areas.validate([self.a, seal(central)], self.policy)
        self.assertEqual([d["area"] for d in order], ["rendering", "machines"])

    def test_game_test_requires_separate_declared_package(self):
        self.a["manifest"]["files"][0]["source"] = "gametest/com/hbm/integration/nuclear/Wrong.java"
        self.reject([seal(self.a)])

    def test_noncentral_registry_rejected(self):
        self.a["manifest"]["registrations"] = [{"registry": "block", "id": "hbm_m:fixture"}]
        self.reject([seal(self.a)])

    def registry_delivery(self, after, registrations):
        target = "src/main/java/com/hbm_m/block/ModBlocks.java"
        before = b'register("existing");\n'
        item = delivery("rendering", target, after, patch=True)
        self.policy["owners"][target] = "rendering"
        item["manifest"]["kind"] = "central"
        item["manifest"]["files"][0]["before_sha256"] = areas.digest(before)
        item["manifest"]["requests"] = ["requests/registry.json"]
        item["files"]["requests/registry.json"] = encode({"request": "independent fixture"})
        item["manifest"]["registrations"] = registrations
        added = b"".join(b"+" + row + b"\n" for row in after.splitlines())
        item["files"]["changes.patch"] = (f"--- a/{target}\n+++ b/{target}\n@@ -1 +1,{len(after.splitlines())} @@\n".encode()
                                           + b'-register("existing");\n' + added)
        selected = areas.validate([seal(item)], self.policy)
        def builder(path):
            path.mkdir()
            subprocess.run(["git", "init", "-q", str(path)], check=True)
            source = path / target
            source.parent.mkdir(parents=True)
            source.write_bytes(before)
            areas.apply(path, selected)
        integration.publish(self.target, builder)

    def test_undeclared_registry_addition_rejected_atomically(self):
        with self.assertRaisesRegex(ValueError, "delta"):
            self.registry_delivery(b'register("existing");\nregister("new");\n', [])
        self.assertFalse(self.target.exists())

    def test_removed_existing_registry_rejected_atomically(self):
        with self.assertRaisesRegex(ValueError, "removed"):
            self.registry_delivery(b'register("replacement");\n', [])
        self.assertFalse(self.target.exists())

    def test_valid_central_registry_request(self):
        registration = {"registry": "block", "id": "hbm_m:new", "class": "com.example.New",
                        "bindings": "own fixture", "initialization": "own fixture", "resources": ["fixture.json"],
                        "tests": ["fixture"], "request": "requests/registry.json"}
        self.registry_delivery(b'register("existing");\nregister("new");\n', [registration])
        self.assertTrue(self.target.exists())

    def test_existing_registry_id_rejected_before_patch(self):
        registration = {"registry": "block", "id": "hbm_m:existing", "class": "com.example.New",
                        "bindings": "fixture", "initialization": "fixture", "resources": ["fixture.json"],
                        "tests": ["fixture"], "request": "requests/registry.json"}
        with self.assertRaisesRegex(ValueError, "already present"):
            self.registry_delivery(b'register("existing");\n', [registration])
        self.assertFalse(self.target.exists())

    def test_unlisted_payload(self):
        self.a["files"]["extra.java"] = b"untracked"
        self.reject([self.a])

    def test_uncleared_or_missing_rights(self):
        records = areas.unique_json(self.a["files"]["rights.json"])
        records["changes.patch"]["publication_status"] = "open-external-only"
        self.a["files"]["rights.json"] = encode(records)
        self.a["manifest"]["payloads"]["rights.json"] = areas.digest(self.a["files"]["rights.json"])
        self.a["files"]["area.json"] = encode(self.a["manifest"])
        self.reject([self.a])

    def test_symlink_target(self):
        selected = areas.validate([self.a], self.policy)
        def build(path):
            path.mkdir()
            (path / "src").symlink_to(self.root, target_is_directory=True)
            areas.apply(path, selected)
        with self.assertRaises(ValueError):
            integration.publish(self.target, build)
        self.assertFalse(self.target.exists())

    def test_existing_destination_is_never_touched(self):
        self.target.mkdir()
        marker = self.target / "keep"
        marker.write_bytes(b"existing world")
        with self.assertRaises(ValueError):
            self.run_delivery([self.a])
        self.assertEqual(marker.read_bytes(), b"existing world")

    def test_duplicate_json_keys(self):
        with self.assertRaises(ValueError):
            areas.unique_json(b'{"area":1,"area":2}')

    def test_commit_snapshot_rejects_symlink_and_ignores_worktree_changes(self):
        repo = self.root / "repo"
        subprocess.run(["git", "init", "-q", str(repo)], check=True)
        folder = repo / "tools/modernized/parallel/machines"
        folder.mkdir(parents=True)
        for name, data in self.a["files"].items():
            dest = folder / name
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(data)
        subprocess.run(["git", "-C", str(repo), "add", "."], check=True)
        command = ["git", "-C", str(repo), "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid", "commit", "-qm"]
        subprocess.run([*command, "fixture"], check=True)
        commit = subprocess.check_output(["git", "-C", str(repo), "rev-parse", "HEAD"], text=True).strip()
        (folder / "changes.patch").write_bytes(b"tampered worktree")
        self.assertEqual(areas.snapshot(repo, "machines@" + commit)["files"], self.a["files"])
        (folder / "link").symlink_to("/tmp")
        subprocess.run(["git", "-C", str(repo), "add", "."], check=True)
        subprocess.run([*command, "symlink"], check=True)
        commit = subprocess.check_output(["git", "-C", str(repo), "rev-parse", "HEAD"], text=True).strip()
        with self.assertRaises(ValueError):
            areas.snapshot(repo, "machines@" + commit)


if __name__ == "__main__":
    unittest.main()
