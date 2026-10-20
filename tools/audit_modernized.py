#!/usr/bin/env python3
# SPDX-License-Identifier: LGPL-3.0-only
"""Record generated resource hashes or inspect Java bytecode in a mod JAR."""

import argparse
from collections import Counter
import hashlib
import io
import json
from pathlib import Path
import re
import sys
import zipfile
import xml.etree.ElementTree as ET

RESOURCE_OVERRIDES = Path(__file__).resolve().parent / "modernized/resource-overrides.json"


def resource_override(name, generated, packaged, overrides):
    record = overrides.get(name)
    return bool(record and hashlib.sha256(generated).hexdigest() == record["generated_sha256"]
                and hashlib.sha256(packaged).hexdigest() == record["packaged_sha256"])


def resources(args):
    source = Path(args.source).resolve(strict=True)
    rows = []
    for path in sorted(source.rglob("*")):
        relative = path.relative_to(source)
        if not path.is_file() or ".cache" in relative.parts:
            continue
        data = path.read_bytes()
        if path.suffix == ".json":
            json.loads(data)
        rows.append(f"{hashlib.sha256(data).hexdigest()}  {relative.as_posix()}")
    if not rows:
        raise ValueError("No generated resources found")
    manifest = ("\n".join(rows) + "\n").encode()
    if args.output:
        Path(args.output).write_bytes(manifest)
    print(json.dumps({"files": len(rows), "manifest_sha256": hashlib.sha256(manifest).hexdigest()}))
    if args.compare and Path(args.compare).read_bytes() != manifest:
        raise ValueError("Generated resource content differs from the comparison manifest")
    if args.compare:
        print("Resource manifests match byte-for-byte (excluding .cache).")


def jar_record(data, name):
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        names = archive.namelist()
        versions = Counter()
        newer = []
        nested = []
        for entry in names:
            if entry.endswith(".class"):
                header = archive.read(entry)[:8]
                if len(header) != 8 or header[:4] != b"\xca\xfe\xba\xbe":
                    raise ValueError(f"Invalid class header: {entry}")
                major = int.from_bytes(header[6:8], "big")
                minor = int.from_bytes(header[4:6], "big")
                versions[major] += 1
                if major > 61 or minor == 65535:
                    newer.append(entry)
            elif entry.endswith(".jar"):
                nested.append(jar_record(archive.read(entry), entry))
        record = {"name": name, "sha256": hashlib.sha256(data).hexdigest(),
            "entries": len(names), "class_major_counts": dict(sorted(versions.items())),
            "unsupported_or_preview_classes": newer,
            "license_notice_paths": [n for n in names if any(k in n.lower() for k in ("license", "notice", "copying"))],
            "refmap_paths": [n for n in names if "refmap" in n],
            "platform_classes_in_outer_jar": [n for n in names if n.endswith(".class") and n.startswith(("net/minecraft/", "net/minecraftforge/"))],
            "nested": nested}
        for entry in ("META-INF/MANIFEST.MF", "META-INF/jarjar/metadata.json"):
            if entry in names:
                record[entry] = archive.read(entry).decode("utf-8")
        if "mixins.hbm_m.json" in names:
            config = json.loads(archive.read("mixins.hbm_m.json"))
            record["mixin_sides"] = {key: config.get(key, []) for key in ("mixins", "client", "server")}
            record["mixin_side_overlap"] = sorted(set(config.get("mixins", [])) &
                (set(config.get("client", [])) | set(config.get("server", []))))
        return record


def compatible(record):
    return not record["unsupported_or_preview_classes"] and all(compatible(child) for child in record["nested"])


def jar(args):
    path = Path(args.source).resolve(strict=True)
    record = jar_record(path.read_bytes(), path.name)
    print(json.dumps(record, ensure_ascii=False, indent=2))
    if not record["class_major_counts"]:
        raise ValueError("No mod bytecode found; a source archive is not a runtime JAR")
    if not compatible(record):
        raise ValueError("Classes requiring newer Java or preview features were found")
    if record.get("mixin_side_overlap"):
        raise ValueError("Client/server mixins are also listed as common mixins")
    if record["platform_classes_in_outer_jar"]:
        raise ValueError("Minecraft/Forge classes bundled in the outer mod JAR")
    provenance = json.loads(Path(args.provenance).read_text()) if getattr(args, "provenance", None) else {"deliveries": []}
    with zipfile.ZipFile(path) as archive:
        names = set(archive.namelist())
        forbidden = {"data/hbm_m/structures/empty.nbt", "hbm-parallel-contract.json"}
        test_prefixes = ["com/hbm/integration/Modernized"]
        registrations = []
        for delivery in provenance["deliveries"]:
            manifest = delivery["manifest"]
            registrations += manifest["registrations"]
            for change in manifest["files"]:
                if change["target"].startswith("integration/src/gametest/java/"):
                    test_prefixes.append(change["target"].removeprefix("integration/src/gametest/java/").removesuffix(".java"))
                elif change["target"].endswith(".java") and change["source"] is not None:
                    relative = change["target"].split("src/main/java/", 1)[-1].removesuffix(".java") + ".class"
                    if relative not in names:
                        raise ValueError(f"Declared production overlay absent from JAR: {relative}")
        leaked = sorted(n for n in names if n in forbidden or any(n.startswith(prefix) for prefix in test_prefixes)
                        or re.match(r"com/hbm/integration/(machines|weapons|nuclear|rendering)/", n))
        if leaked:
            raise ValueError(f"Test-only content in production JAR: {leaked}")
        entrypoints = [n for n in names if n.endswith(".class") and b"Lnet/minecraftforge/fml/common/Mod;" in archive.read(n)]
        if entrypoints != ["com/hbm/HbmPort.class"]:
            raise ValueError(f"Expected sole Foundation @Mod entrypoint: {entrypoints}")
        for registry in registrations:
            required = [registry["class"].replace(".", "/") + ".class", *registry["resources"]]
            if any(name not in names for name in required):
                raise ValueError(f"Declared registry delta not packaged: {registry['registry']}/{registry['id']}")
        print(f"Entrypoint/test isolation/declared registry package gates passed ({len(registrations)} new registrations).")
    if args.generated_source:
        generated = Path(args.generated_source).resolve(strict=True)
        expected = {str(p.relative_to(generated)).replace("\\", "/")
                    for p in generated.rglob("*") if p.is_file() and ".cache" not in p.relative_to(generated).parts}
        if not expected:
            raise ValueError("No generated resources to verify")
        with zipfile.ZipFile(path) as archive:
            missing = sorted(expected - set(archive.namelist()))
            if missing:
                raise ValueError(f"{len(missing)} generated resources missing from JAR; first: {missing[:5]}")
            overrides = json.loads(RESOURCE_OVERRIDES.read_text())["files"]
            changed, retained = [], []
            for name in sorted(expected):
                data, packed = (generated / name).read_bytes(), archive.read(name)
                if data == packed:
                    continue
                if resource_override(name, data, packed, overrides):
                    retained.append(name)
                else:
                    changed.append(name)
            if changed:
                raise ValueError(f"Generated resource bytes differ in JAR: {changed[:5]}")
            print(f"Resource content gate: {len(retained)} explicitly hashed existing main-resource overrides retained.")
            unexpected_tests = [n for n in archive.namelist()
                                if n.startswith("com/hbm/integration/Modernized") or n == "data/hbm_m/structures/empty.nbt"]
            if unexpected_tests:
                raise ValueError(f"Test-only content in production JAR: {unexpected_tests}")
        print(f"Generated-resource packaging gate passed: {len(expected)} paths present; no integration test classes/template.")
    print("Bytecode gate passed for Java 17, including nested JARs; API/linkage and gameplay require runtime tests.")


def gametests(args):
    """Require the exact named required test set, not merely Gradle exit zero."""
    checkout = Path(args.checkout)
    provenance = json.loads((checkout / "integration/provenance.json").read_text())
    expected = set()
    for source in sorted((checkout / "integration/src/gametest/java").rglob("*.java")):
        text = source.read_text()
        cls = re.search(r"public (?:final )?class (\w+)", text)
        for annotation, method in re.findall(r"@GameTest\((.*?)\)\s+public static void (\w+)\(", text, re.S):
            if re.search(r"required\s*=\s*false", annotation):
                raise ValueError("Optional integration GameTest is forbidden")
            expected.add((cls[1] + "." + method).lower())
    declared = {t["id"] for d in provenance["deliveries"] for t in d["manifest"]["tests"]}
    baseline = set()
    repo = Path(__file__).resolve().parents[1]
    for folder in ("gametest", "phase5-gametest"):
        for source in (repo / "tools/modernized" / folder).rglob("*.java"):
            text = source.read_text()
            cls = re.search(r"public (?:final )?class (\w+)", text)[1]
            baseline.update((cls + "." + m).lower() for m in re.findall(r"@GameTest\([^)]*\)\s+public static void (\w+)\(", text))
    if len(baseline) != 14 or expected != baseline | declared:
        raise ValueError("Expected the unchanged 14 baseline IDs plus exactly the declared area tests")
    report = ET.parse(args.report).getroot()
    cases = report.findall(".//testcase")
    actual = [case.attrib["name"].removeprefix("hbm_m:").lower() for case in cases]
    if len(actual) != len(expected) or set(actual) != expected or report.findall(".//failure") or report.findall(".//error") or report.findall(".//skipped"):
        raise ValueError(f"GameTest report differs from required IDs: expected {sorted(expected)}, actual {actual}")
    log = Path(args.log).read_text()
    if f"All {len(expected)} required tests passed" not in log or args.forge not in log:
        raise ValueError("Missing required success summary or actual Forge version")
    print(json.dumps({"forge": args.forge, "required_passed": len(actual), "ids": sorted(actual)}, indent=2))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="action", required=True)
    resource_parser = commands.add_parser("resources")
    resource_parser.add_argument("source")
    resource_parser.add_argument("--output")
    resource_parser.add_argument("--compare")
    jar_parser = commands.add_parser("jar")
    jar_parser.add_argument("source")
    jar_parser.add_argument("--generated-source", help="Require every generated resource and reject integration-test content in the production JAR")
    jar_parser.add_argument("--provenance", help="Verify declared production overlays, registry delta and test isolation")
    tests_parser = commands.add_parser("gametests")
    tests_parser.add_argument("checkout")
    tests_parser.add_argument("--report", required=True)
    tests_parser.add_argument("--log", required=True)
    tests_parser.add_argument("--forge", choices=("47.4.20", "47.4.23"), required=True)
    args = parser.parse_args()
    {"resources": resources, "jar": jar, "gametests": gametests}[args.action](args)


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, zipfile.BadZipFile) as error:
        print(f"Audit failed: {error}", file=sys.stderr)
        sys.exit(1)
