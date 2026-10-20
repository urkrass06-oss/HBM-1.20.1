# SPDX-License-Identifier: LGPL-3.0-only
"""Fail-closed, commit-addressed deliveries for the four external work areas.

Policy is maintained by the integration writer, never by a delivery. All payloads
are snapshotted from Git objects, validated together, then exercised in staging.
"""

import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import subprocess

AREAS = ("machines", "weapons", "nuclear", "rendering")
REGISTRIES = ("block", "item", "block_entity_type", "entity_type", "menu", "recipe_serializer", "sound_event")
POLICY = Path(__file__).resolve().parent / "modernized/parallel/policy.json"


def digest(data):
    return hashlib.sha256(data).hexdigest()


def path_name(value):
    if not isinstance(value, str) or not re.fullmatch(r"[A-Za-z0-9_./+-]+", value):
        raise ValueError(f"Unsafe path: {value!r}")
    path = PurePosixPath(value)
    if path.is_absolute() or any(p in ("", ".", "..", ".git") for p in value.split("/")):
        raise ValueError(f"Unsafe path: {value}")
    return value


def unique_json(data):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError(f"Duplicate JSON key: {key}")
            result[key] = value
        return result
    return json.loads(data, object_pairs_hook=pairs)


def snapshot(repo, selection):
    """Only ordinary committed blobs; no checkout, shell, archive or symlink escape."""
    area, separator, commit = selection.partition("@")
    if area not in AREAS or not separator or not re.fullmatch(r"[0-9a-f]{40}", commit):
        raise ValueError("Use --delivery <machines|weapons|nuclear|rendering>@<full commit SHA>")
    prefix = f"tools/modernized/parallel/{area}/"
    command = ["git", "-C", str(repo)]
    if subprocess.check_output([*command, "cat-file", "-t", commit]).strip() != b"commit":
        raise ValueError("Delivery reference must be a commit")
    tree = subprocess.check_output([*command, "ls-tree", "-rz", commit, "--", prefix])
    files = {}
    for row in tree.split(b"\0"):
        if not row:
            continue
        metadata, name = row.split(b"\t", 1)
        mode, kind, blob = metadata.decode().split()
        if mode != "100644" or kind != "blob":
            raise ValueError("Delivery permits ordinary nonexecutable files only")
        relative = path_name(name.decode().removeprefix(prefix))
        files[relative] = subprocess.check_output([*command, "cat-file", "blob", blob])
    if "area.json" not in files:
        raise ValueError(f"Missing {area}/area.json at {commit}")
    return {"area": area, "commit": commit, "files": files}


def patch_targets(data):
    """Restricted unified text patches: same-path modifications, no metadata tricks.

    Git remains the authoritative hunk parser via apply --check. This parser
    disallows renames, deletions, binary data, modes, quoted paths and new files;
    new files must use the separately hashed, collision-checked overlay channel.
    """
    lines = data.decode("utf-8").splitlines()
    targets = []
    index = 0
    header_target = None
    while index < len(lines):
        line = lines[index]
        if line.startswith("diff --git "):
            parts = line.split()
            if len(parts) != 4 or parts[2] != "a/" + parts[3].removeprefix("b/"):
                raise ValueError("Unsupported diff paths")
            header_target = path_name(parts[2][2:])
            index += 1
            if index < len(lines) and re.fullmatch(r"index [0-9a-f]+\.\.[0-9a-f]+(?: 100644)?", lines[index]):
                index += 1
            continue
        if not line.startswith("--- a/") or index + 1 >= len(lines):
            raise ValueError("Only ordinary unified text patches are accepted")
        target = path_name(line[6:])
        if header_target is not None and header_target != target:
            raise ValueError("Diff header disagrees with unified target")
        header_target = None
        if lines[index + 1] != "+++ b/" + target or target in targets:
            raise ValueError("Rename, delete or duplicate patch target")
        targets.append(target)
        index += 2
        hunks = 0
        while index < len(lines) and lines[index].startswith("@@ "):
            match = re.fullmatch(r"@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@.*", lines[index])
            if not match:
                raise ValueError("Malformed hunk")
            old, new = int(match[2] or 1), int(match[4] or 1)
            index += 1
            while old or new:
                if index >= len(lines) or not lines[index] or lines[index][0] not in " +-":
                    raise ValueError("Malformed hunk body")
                prefix = lines[index][0]
                old -= prefix in " -"
                new -= prefix in " +"
                if old < 0 or new < 0:
                    raise ValueError("Invalid hunk counts")
                index += 1
                if index < len(lines) and lines[index] == "\\ No newline at end of file":
                    index += 1
            hunks += 1
        if not hunks:
            raise ValueError("Patch has no hunks")
    if not targets:
        raise ValueError("Empty patch")
    return targets


def validate(deliveries, policy):
    """Pure preflight: no writes and no subprocesses; returns deterministic DAG order."""
    selected, targets, registries, test_ids = {}, set(), set(), set()
    for delivery in deliveries:
        area, files = delivery["area"], delivery["files"]
        if area in selected:
            raise ValueError("Duplicate area selection")
        manifest = unique_json(files["area.json"])
        delivery = dict(delivery, manifest=manifest)
        selected[area] = delivery
        if manifest["schema"] != 1 or manifest["area"] != area or manifest["baseline"] != policy["baseline"]:
            raise ValueError("Wrong area, schema, pin or baseline hashes")
        if manifest["kind"] not in ("area", "central") or (manifest["kind"] == "central" and area != "rendering"):
            raise ValueError("Only rendering may supply central requests")
        if not manifest["tasks"] or not manifest["features"] or not manifest["api_version"]:
            raise ValueError("Tasks, features and API version are required")
        expected = manifest["payloads"]
        if set(files) != set(expected) | {"area.json"}:
            raise ValueError("Unlisted or missing delivery file")
        for name, checksum in expected.items():
            path_name(name)
            if digest(files[name]) != checksum:
                raise ValueError(f"Payload hash mismatch: {name}")
        rights = unique_json(files["rights.json"])
        # Every published byte, including patch context, evidence and generator inputs.
        if set(rights) != set(files) - {"rights.json", "area.json"}:
            raise ValueError("Per-file rights records do not cover the delivery")
        for name, record in rights.items():
            if record["sha256"] != digest(files[name]) or not all(record.get(k) for k in
                    ("origin", "source_commit", "authors", "license", "notices", "review")):
                raise ValueError(f"Incomplete rights record: {name}")
            if record["publication_status"] != "cleared":
                raise ValueError(f"Uncleared payload: {name}")
        if not manifest["evidence"] or any(name not in files or not name.startswith("evidence/") for name in manifest["evidence"]):
            raise ValueError("Hashed test evidence is required")
        patch = manifest["patch"]
        patched = set(patch_targets(files[patch])) if patch else set()
        copied = set()
        for change in manifest["files"]:
            target = path_name(change["target"])
            if target in targets:
                raise ValueError(f"Overlapping delivery target: {target}")
            targets.add(target)
            if policy["owners"].get(target) != area:
                raise ValueError(f"Target outside owner's exact reservation: {target}")
            if change["source"] is None:
                if target not in patched or not re.fullmatch(r"[0-9a-f]{64}", change["before_sha256"] or ""):
                    raise ValueError("Patch target or preimage mismatch")
            else:
                source = path_name(change["source"])
                if source not in files or source in copied or change["before_sha256"] is not None:
                    raise ValueError("Invalid new overlay file")
                copied.add(source)
                test = source.startswith("gametest/")
                if test:
                    wanted = "integration/src/gametest/java/" + source.removeprefix("gametest/")
                    if not source.startswith(f"gametest/com/hbm/integration/{area}/") or target != wanted:
                        raise ValueError("Area GameTests must use their separate package")
                elif not source.startswith("overlay/") or not target.endswith(".java"):
                    raise ValueError("Overlay channel accepts new reserved Java files only")
                if digest(files[source]) != change["sha256"]:
                    raise ValueError("Overlay result hash mismatch")
            if not re.fullmatch(r"[0-9a-f]{64}", change["sha256"]):
                raise ValueError("Missing result hash")
        if patched != {c["target"] for c in manifest["files"] if c["source"] is None}:
            raise ValueError("Patch paths differ from exact declaration")
        used = copied | set(manifest["evidence"]) | {"rights.json"} | ({patch} if patch else set())
        if set(expected) != used:
            raise ValueError("Unused delivery payload")
        for registry in manifest["registrations"]:
            key = (registry["registry"], registry["id"])
            if key[0] not in REGISTRIES or key in registries or not re.fullmatch(r"hbm_m:[a-z0-9_./-]+", key[1]):
                raise ValueError("Duplicate or invalid registry identity")
            if area != "rendering" or manifest["kind"] != "central":
                raise ValueError("Registrations require a central rendering request delivery")
            registries.add(key)
            if not all(registry.get(k) for k in ("class", "bindings", "initialization", "resources", "tests", "request")):
                raise ValueError("Incomplete central registration request")
        for test in manifest["tests"]:
            if test["id"] in test_ids or test["source"] not in copied or test["required"] is not True:
                raise ValueError("Duplicate, optional or undeclared GameTest")
            test_ids.add(test["id"])
        sources = {c["source"] for c in manifest["files"] if (c["source"] or "").startswith("gametest/")}
        if sources != {t["source"] for t in manifest["tests"]}:
            raise ValueError("Every GameTest source needs declared required tests")
    visiting, done, ordered = set(), set(), []

    def visit(area):
        if area in visiting:
            raise ValueError("Cyclic delivery dependency")
        if area in done:
            return
        visiting.add(area)
        current = selected[area]
        for dependency in sorted(current["manifest"]["requires"], key=lambda d: d["area"]):
            other = selected.get(dependency["area"])
            if not other or other["commit"] != dependency["commit"] or other["manifest"]["api_version"] != dependency["api_version"]:
                raise ValueError("Missing dependency commit or API version")
            if current["manifest"]["kind"] == "central" and other["manifest"]["kind"] != "central":
                raise ValueError("Central requests must precede area deliveries")
            visit(dependency["area"])
        visiting.remove(area)
        done.add(area)
        ordered.append(current)

    for area in sorted(selected, key=lambda a: (selected[a]["manifest"]["kind"] != "central", a)):
        visit(area)
    return ordered


def load(repo, selections):
    policy = unique_json(POLICY.read_bytes())
    for name, checksum in policy["baseline"]["files"].items():
        if digest((repo / path_name(name)).read_bytes()) != checksum:
            raise ValueError(f"Frozen basis file changed: {name}")
    base = policy["baseline"]["target_base"]
    subprocess.run(["git", "-C", str(repo), "merge-base", "--is-ancestor", base, "HEAD"], check=True)
    deliveries = [snapshot(repo, s) for s in selections]
    for delivery in deliveries:
        subprocess.run(["git", "-C", str(repo), "merge-base", "--is-ancestor", base, delivery["commit"]], check=True)
    return validate(deliveries, policy)


def safe_target(checkout, name):
    target = checkout / path_name(name)
    if any(p.is_symlink() for p in (target, *target.parents)):
        raise ValueError(f"Symlink in target path: {name}")
    return target


def apply(checkout, deliveries):
    """Called only in disposable staging, after the complete pure preflight."""
    records = []
    for delivery in deliveries:
        manifest = delivery["manifest"]
        for change in manifest["files"]:
            target = safe_target(checkout, change["target"])
            before = change["before_sha256"]
            if before is None:
                if target.exists():
                    raise ValueError(f"Overlay collision with existing target: {change['target']}")
            elif not target.is_file() or digest(target.read_bytes()) != before:
                raise ValueError(f"Patch preimage hash mismatch: {change['target']}")
        if manifest["patch"]:
            data = delivery["files"][manifest["patch"]]
            command = ["git", "-C", str(checkout), "apply", "--whitespace=error"]
            subprocess.run([*command, "--check", "-"], input=data, check=True)
            subprocess.run([*command, "-"], input=data, check=True)
        for change in manifest["files"]:
            target = safe_target(checkout, change["target"])
            if change["source"] is not None:
                target.parent.mkdir(parents=True, exist_ok=True)
                with target.open("xb") as output:
                    output.write(delivery["files"][change["source"]])
            if digest(target.read_bytes()) != change["sha256"]:
                raise ValueError(f"Applied result hash mismatch: {change['target']}")
        records.append({"area": delivery["area"], "commit": delivery["commit"],
                        "manifest_sha256": digest(delivery["files"]["area.json"]),
                        "manifest": manifest, "rights": unique_json(delivery["files"]["rights.json"])})
    contract = checkout / "integration/src/gametest/resources/hbm-parallel-contract.json"
    contract.parent.mkdir(parents=True, exist_ok=True)
    with contract.open("x") as output:
        json.dump({"registrations": [r for d in deliveries for r in d["manifest"]["registrations"]]}, output, sort_keys=True)
        output.write("\n")
    return records
