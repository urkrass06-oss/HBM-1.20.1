#!/usr/bin/env python3
# SPDX-License-Identifier: LGPL-3.0-only
"""Create a new external Phase-4 integration; never vendor unreviewed assets."""

import argparse
from datetime import datetime, timezone
import gzip
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import struct
import sys

import modernized_build as base

REPO = Path(__file__).resolve().parents[1]
PATCH = REPO / "tools/modernized/phase4-integration.patch"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def empty_template():
    """Our own 5x5x5 empty structure, not a copied Minecraft/upstream asset."""
    def name(text):
        data = text.encode("utf-8")
        return struct.pack(">H", len(data)) + data
    data = b"\x0a\x00\x00"  # unnamed root compound
    data += b"\x03" + name("DataVersion") + struct.pack(">i", 3465)
    data += b"\x09" + name("size") + b"\x03" + struct.pack(">iiii", 3, 5, 5, 5)
    data += b"\x09" + name("palette") + b"\x0a" + struct.pack(">i", 1)
    data += b"\x08" + name("Name") + name("minecraft:air") + b"\x00"
    for key in ("blocks", "entities"):
        data += b"\x09" + name(key) + b"\x0a" + struct.pack(">i", 0)
    return gzip.compress(data + b"\x00", mtime=0)


def install_overlay(checkout):
    """Only write into a newly prepared external checkout's new integration tree."""
    destination = checkout / "integration"
    destination.mkdir()  # Fail on an existing overlay rather than replacing it.
    records = []
    for relative in ("com/hbm/HbmPort.java", "com/hbm/client/ClientSetup.java",
                     "com/hbm/registry/ModRegistries.java"):
        source = REPO / "src/main/java" / relative
        target = destination / "src/main/java" / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        content = source.read_text()
        if relative.endswith("HbmPort.java"):
            content = content.replace("import com.hbm.registry.ModRegistries;",
                "import com.hbm_m.main.ForgeEntrypoint;\nimport com.hbm_m.lib.RefStrings;\nimport com.hbm.integration.PortPaintings;")
            content = content.replace('MOD_ID = "hbm"', "MOD_ID = RefStrings.MODID")
            content = content.replace("ModRegistries.register(modBus);",
                "PortPaintings.register(modBus);\n        ForgeEntrypoint.initialize(modBus);")
            content = content.replace("Entry point for the Forge 1.20.1 port; no original game content is registered yet.",
                "Phase-4 integration entry point; delegates all content registration to Modernized.")
            content = content.replace("HBM Forge 1.20.1 port foundation initialized; no gameplay content is implemented.",
                "HBM Complete Port Modernized integration initialized (hbm_m).")
            content = content.replace("package com.hbm;", "// Adapted for the external integration on 2026-10-19.\npackage com.hbm;")
        target.write_text(content)
        records.append({"source": str(source.relative_to(REPO)), "source_sha256": sha(source),
                        "target": str(target.relative_to(checkout)), "sha256": sha(target)})
    shutil.copytree(REPO / "tools/modernized/overlay", destination / "src/main/java", dirs_exist_ok=True)
    shutil.copytree(REPO / "tools/modernized/gametest", destination / "src/gametest/java")
    template = destination / "src/gametest/resources/data/hbm_m/structures/empty.nbt"
    template.parent.mkdir(parents=True)
    template.write_bytes(empty_template())
    notices = destination / "notices"
    notices.mkdir()
    for name in ("LICENSE", "LICENSE.LESSER"):
        shutil.copyfile(REPO / name, notices / (name + ".foundation"))
    for name in ("MODERNIZED_GPL-3.0.txt", "MIXINCONSTRAINTS_LICENSE.txt", "ARCHITECTURY_LICENSE.md"):
        shutil.copyfile(REPO / "third_party_licenses" / name, notices / name)
    notice = (
        "HBM Complete Port: experimental local integration, 2026-10-19.\n"
        f"Modernized source: {base.SOURCE} @ {base.PIN}\n"
        "Modernized authors: RaptorDev, TRFFuchs, razchexlitiel, HyperiO.\n"
        "Contributors: ThePhoenixKnight, boryu._., hexagon_inc, kami_no_samurai.\n"
        "Original HBM: The Bobcat (hbm) and original contributors.\n"
        "The Modernized derivative is GPLv3; foundation files retain LGPL-3.0-only.\n"
        "Changes: Phase-3 build fixes; single hbm_m entry point; separate test profile;\n"
        "port metadata and notices; Forge 1.20.1 painting registration.\n"
        "Upstream copyright/file headers remain intact.\n"
        "Full source: pinned upstream plus this repository's patches, generators and overlay.\n"
        "Asset provenance and embedded-library distribution obligations remain unresolved.\n"
        "Do not publish this evaluation JAR or the unreviewed upstream asset/source tree.\n"
    )
    (notices / "CHANGES-AND-CREDITS.txt").write_text(notice)
    return records


def provenance(checkout, records):
    tree = subprocess.check_output(["git", "-C", str(checkout), "ls-tree", "-r", "-z", "HEAD"])
    files = []
    # Git object bytes, not generated/modified working files, establish source identity.
    objects = subprocess.Popen(["git", "-C", str(checkout), "cat-file", "--batch"],
                               stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    try:
        for entry in tree.split(b"\0"):
            if not entry:
                continue
            metadata, path = entry.split(b"\t", 1)
            mode, kind, blob = metadata.decode().split()
            if kind != "blob":
                raise ValueError("Unexpected non-file upstream entry")
            objects.stdin.write(blob.encode() + b"\n")
            objects.stdin.flush()
            header = objects.stdout.readline().split()
            data = objects.stdout.read(int(header[2]))
            if objects.stdout.read(1) != b"\n":
                raise ValueError("Invalid git object response")
            files.append({"path": path.decode(), "git_blob": blob, "mode": mode,
                          "sha256": hashlib.sha256(data).hexdigest(),
                          "publication_status": "not-cleared-external-only"})
    finally:
        objects.stdin.close()
        objects.wait()
    manifest = {"schema": 1, "utc": datetime.now(timezone.utc).isoformat(),
                "source_repository": base.SOURCE, "source_commit": base.PIN,
                "target_base": base.git(REPO, "rev-parse", "HEAD"),
                "phase3_patch_sha256": sha(base.PATCH), "phase4_patch_sha256": sha(PATCH),
                "wrapper_sha256": base.WRAPPER_SHA256, "foundation_overlay": records,
                "upstream_files": files,
                "overlay_files": [{"path": str(p.relative_to(checkout)), "sha256": sha(p)}
                                  for p in sorted((checkout / "integration").rglob("*")) if p.is_file()]}
    (checkout / "integration/provenance.json").write_text(json.dumps(manifest, indent=2) + "\n")


def prepare_game_test_directory(checkout):
    # Forge's GameTest main otherwise logs an ERROR for the absent properties on first use.
    # This is a new external runtime directory, never an existing server/world.
    runtime = checkout / "versions/1.20.1-forge/run-gametest"
    runtime.mkdir(parents=True)
    (runtime / "server.properties").write_text(
        "server-ip=127.0.0.1\nonline-mode=false\nenable-rcon=false\nenable-query=false\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("checkout", help="New directory outside the target repository")
    args = parser.parse_args()
    checkout = base.external(args.checkout)
    base.prepare(args)
    subprocess.run(["git", "-C", str(checkout), "apply", "--check", str(PATCH)], check=True)
    subprocess.run(["git", "-C", str(checkout), "apply", str(PATCH)], check=True)
    provenance(checkout, install_overlay(checkout))
    prepare_game_test_directory(checkout)
    print(f"Integrated at {checkout}; source identities in integration/provenance.json")
    print("Evaluation only: no source/assets/JAR uploaded. Use modernized_build.py run next.")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, subprocess.CalledProcessError) as error:
        print(f"Integration failed: {error}", file=sys.stderr)
        sys.exit(1)
