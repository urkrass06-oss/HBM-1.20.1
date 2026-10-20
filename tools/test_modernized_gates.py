# SPDX-License-Identifier: LGPL-3.0-only
"""Exercise package corruption and explicit Forge profile boundaries."""
import argparse
import contextlib
import io
import json
from pathlib import Path
import re
import shutil
import tempfile
import unittest
import zipfile

import audit_modernized as audit
import modernized_build as build


class ProfileTests(unittest.TestCase):
    def test_both_profiles_pin_every_task(self):
        for profile, forge in build.PROFILES.items():
            for task in ("runData", "build", "sourcesJar", "runGameTestServer"):
                with self.subTest(profile=profile, task=task):
                    result = build.profile_arguments(profile, [], [task])
                    self.assertIn("-Pdeps.forge=" + forge, result)
                    self.assertEqual("-Pmodernized.gameTests=true" in result, task == "runGameTestServer")

    def test_conflicting_forge_override_rejected(self):
        for profile in build.PROFILES:
            with self.assertRaises(ValueError):
                build.profile_arguments(profile, ["-Pdeps.forge=99"], ["runData"])

    def test_test_packaging_and_combined_tasks_rejected(self):
        for tasks, arguments in ((["build"], ["-Pmodernized.gameTests=true"]),
                                 (["sourcesJar"], ["-Pmodernized.gameTests=true"]),
                                 (["build", "runGameTestServer"], []),
                                 (["runGameTestServer"], ["-Pmodernized.gameTests=false"])):
            with self.assertRaises(ValueError):
                build.profile_arguments("production", arguments, tasks)


class PackageTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.path = self.root / "own-fixture.jar"
        self.generated = self.root / "resources"
        (self.generated / "data/fixture").mkdir(parents=True)
        (self.generated / "data/fixture/resource.json").write_bytes(b"{}\n")
        self.entries = {"com/hbm/HbmPort.class": self.bytecode(61) + b"Lnet/minecraftforge/fml/common/Mod;",
                        "data/fixture/resource.json": b"{}\n"}

    @staticmethod
    def bytecode(major):
        # Minimal own header fixture for the bytecode scanner, not a JVM program.
        return b"\xca\xfe\xba\xbe\x00\x00" + major.to_bytes(2, "big")

    def check(self):
        with zipfile.ZipFile(self.path, "w") as archive:
            for name, data in self.entries.items():
                archive.writestr(name, data)
        with contextlib.redirect_stdout(io.StringIO()):
            audit.jar(argparse.Namespace(source=self.path, generated_source=self.generated, provenance=None))

    def test_valid_java17_and_exact_resources(self):
        self.check()

    def test_missing_or_changed_generated_resource(self):
        for content in (None, b'{"different":true}'):
            if content is None:
                self.entries.pop("data/fixture/resource.json")
            else:
                self.entries["data/fixture/resource.json"] = content
            with self.assertRaises(ValueError):
                self.check()

    def test_java21_rejected_also_in_nested_jar(self):
        nested = io.BytesIO()
        with zipfile.ZipFile(nested, "w") as archive:
            archive.writestr("Own.class", self.bytecode(65))
        self.entries["META-INF/jarjar/own.jar"] = nested.getvalue()
        with self.assertRaises(ValueError):
            self.check()

    def test_declared_and_undeclared_test_content_rejected(self):
        for name in ("com/hbm/integration/rendering/AnyTests.class", "com/hbm/integration/ModernizedIntegrationTests.class",
                     "data/hbm_m/structures/empty.nbt", "hbm-parallel-contract.json"):
            with self.subTest(name=name):
                self.entries[name] = self.bytecode(61) if name.endswith(".class") else b"fixture"
                with self.assertRaises(ValueError):
                    self.check()
                del self.entries[name]

    def test_second_mod_entrypoint_rejected(self):
        self.entries["com/example/Other.class"] = self.entries["com/hbm/HbmPort.class"]
        with self.assertRaises(ValueError):
            self.check()

    def test_missing_mod_entrypoint_rejected(self):
        self.entries["com/hbm/HbmPort.class"] = self.bytecode(61)
        with self.assertRaises(ValueError):
            self.check()

    def test_only_exact_reviewed_resource_override_is_accepted(self):
        import hashlib
        generated, packed = b"own generated", b"own authored"
        overrides = {"own.json": {"generated_sha256": hashlib.sha256(generated).hexdigest(),
                                  "packaged_sha256": hashlib.sha256(packed).hexdigest()}}
        self.assertTrue(audit.resource_override("own.json", generated, packed, overrides))
        self.assertFalse(audit.resource_override("other.json", generated, packed, overrides))
        self.assertFalse(audit.resource_override("own.json", b"changed", packed, overrides))
        self.assertFalse(audit.resource_override("own.json", generated, b"changed", overrides))


class ReportTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root / "integration/src/gametest/java").mkdir(parents=True)
        (self.root / "integration/provenance.json").write_text('{"deliveries":[]}')
        repo = Path(__file__).resolve().parents[1]
        self.ids = []
        for folder in ("gametest", "phase5-gametest"):
            for source in (repo / "tools/modernized" / folder).rglob("*.java"):
                shutil.copyfile(source, self.root / "integration/src/gametest/java" / source.name)
                text = source.read_text()
                cls = re.search(r"public final class (\w+)", text)[1]
                self.ids += [method.lower() for method in
                             re.findall(r"@GameTest\([^)]*\)\s+public static void (\w+)\(", text)]
        self.report = self.root / "report.xml"
        self.log = self.root / "run.log"
        self.log.write_text("Forge 47.4.23\nAll 14 required tests passed :)\n")
        self.write_report(self.ids)

    def write_report(self, names, child=""):
        self.report.write_text("<testsuite>" + "".join(f'<testcase name="{name}">{child}</testcase>' for name in names) + "</testsuite>")

    def check(self):
        with contextlib.redirect_stdout(io.StringIO()):
            audit.gametests(argparse.Namespace(checkout=self.root, report=self.report, log=self.log, forge="47.4.23"))

    def test_exact_fourteen_required_ids_pass(self):
        self.assertEqual(len(self.ids), 14)
        self.check()

    def test_zero_tests_rejected(self):
        self.write_report([])
        with self.assertRaises(ValueError):
            self.check()

    def test_correct_count_with_wrong_id_rejected(self):
        self.write_report([*self.ids[:-1], "unrelated.test"])
        with self.assertRaises(ValueError):
            self.check()

    def test_runtime_names_follow_prefix_false_annotation(self):
        self.write_report(["unwantedclassprefix." + name for name in self.ids])
        with self.assertRaises(ValueError):
            self.check()

    def test_failures_errors_and_skips_rejected(self):
        for child in ("<failure/>", "<error/>", "<skipped/>"):
            self.write_report(self.ids, child)
            with self.assertRaises(ValueError):
                self.check()

    def test_wrong_runtime_version_rejected(self):
        self.log.write_text("Forge 47.4.20\nAll 14 required tests passed :)\n")
        with self.assertRaises(ValueError):
            self.check()

    def test_missing_success_summary_rejected(self):
        self.log.write_text("Forge 47.4.23\nBUILD SUCCESSFUL\n")
        with self.assertRaises(ValueError):
            self.check()

    def test_declared_but_missing_area_test_rejected(self):
        (self.root / "integration/provenance.json").write_text(json.dumps({"deliveries": [{"manifest": {"tests": [{"id": "area.missing"}]}}]}))
        with self.assertRaises(ValueError):
            self.check()


if __name__ == "__main__":
    unittest.main()
