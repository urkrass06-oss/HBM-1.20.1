#!/usr/bin/env python3
# SPDX-License-Identifier: LGPL-3.0-only
"""Verify the narrow M-01 production delta against the reproduced Phase-5 JAR."""

import argparse
import hashlib
import json
from pathlib import Path
import zipfile


BASELINE_SHA256 = "056beb76f3410d34aaf5553cfc5439e767c6b258e73edaa1366c66f05b6b77c3"
EXPECTED_CLASSES = {
    "com/hbm_m/api/energy/EnergyNetwork.class",
    "com/hbm_m/api/energy/WireBlockEntity.class",
    "com/hbm_m/blockentity/machines/FluidValveBlockEntity.class",
    "com/hbm_m/inventory/fluid/tank/FluidTank.class",
    "com/hbm_m/blockentity/machines/FluidPumpBlockEntity.class",
}


def entries(path):
    with zipfile.ZipFile(path) as archive:
        names = archive.namelist()
        if len(names) != len(set(names)):
            raise ValueError("Duplicate JAR entries")
        return {name: hashlib.sha256(archive.read(name)).hexdigest() for name in names}


def audit(baseline, candidate):
    if hashlib.sha256(baseline.read_bytes()).hexdigest() != BASELINE_SHA256:
        raise ValueError("Expected the separately reproduced Phase-5 production baseline")
    before, after = entries(baseline), entries(candidate)
    forbidden = sorted(name for name in after if (
        name.startswith("com/hbm/integration/machines/")
        or name.startswith("com/hbm/integration/Modernized")
        or name == "data/hbm_m/structures/empty.nbt"
    ))
    added = sorted(after.keys() - before.keys())
    removed = sorted(before.keys() - after.keys())
    changed = sorted(name for name in before.keys() & after.keys() if before[name] != after[name])
    if forbidden:
        raise ValueError(f"Test content in production JAR: {forbidden}")
    allowed = lambda name: name in EXPECTED_CLASSES or (
        "$" in name and name.split("$", 1)[0] + ".class" in EXPECTED_CLASSES
    )
    if (removed or not all(map(allowed, added))
            or not EXPECTED_CLASSES.issubset(changed) or not all(map(allowed, changed))):
        raise ValueError(f"Unexpected M-01 delta: added={added}, removed={removed}, changed={changed}")
    return {
        "baseline_sha256": BASELINE_SHA256,
        "candidate_sha256": hashlib.sha256(candidate.read_bytes()).hexdigest(),
        "entries": len(after),
        "added": added,
        "removed": removed,
        "changed": changed,
        "test_content": forbidden,
        "resources_unchanged": True,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("baseline", type=Path)
    parser.add_argument("candidate", type=Path)
    args = parser.parse_args()
    print(json.dumps(audit(args.baseline, args.candidate), indent=2))


if __name__ == "__main__":
    main()
