#!/usr/bin/env python3
# SPDX-License-Identifier: LGPL-3.0-only
"""Record generated resource hashes or inspect Java bytecode in a mod JAR."""

import argparse
from collections import Counter
import hashlib
import io
import json
from pathlib import Path
import sys
import zipfile


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
            unexpected_tests = [n for n in archive.namelist()
                                if n.startswith("com/hbm/integration/Modernized") or n == "data/hbm_m/structures/empty.nbt"]
            if unexpected_tests:
                raise ValueError(f"Test-only content in production JAR: {unexpected_tests}")
        print(f"Generated-resource packaging gate passed: {len(expected)} paths present; no integration test classes/template.")
    print("Bytecode gate passed for Java 17, including nested JARs; API/linkage and gameplay require runtime tests.")


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
    args = parser.parse_args()
    resources(args) if args.action == "resources" else jar(args)


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, zipfile.BadZipFile) as error:
        print(f"Audit failed: {error}", file=sys.stderr)
        sys.exit(1)
