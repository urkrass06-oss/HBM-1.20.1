#!/usr/bin/env python3
# SPDX-License-Identifier: LGPL-3.0-only
"""Linux x86_64 production-JAR client for isolated, offline development tests.

Uses official Mojang/Forge manifests, verifies downloads, and refuses existing
installation/game directories. No game files are distributed by this script.
Offline identities are for the loopback test server only, not online services.
"""

import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import time
import uuid
import zipfile

import modernized_build as base
from test_modernized_server import INSTALLERS, java_command

MANIFEST_SHA1 = "a5cf661d31d9dfcd3d1645be80f43954f63f63b0"
MANIFEST_URL = f"https://piston-meta.mojang.com/v1/packages/{MANIFEST_SHA1}/1.20.1.json"


def fetch(url, path, expected, algorithm="sha1"):
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(["curl", "--fail", "--silent", "--show-error", "--location",
                        "--retry", "2", "--max-time", "180", "--output", str(path), url], check=True)
    actual = hashlib.new(algorithm, path.read_bytes()).hexdigest()
    if actual != expected:
        raise ValueError(f"Checksum mismatch: {path}: {actual}")


def allowed(entry):
    result = not entry.get("rules")
    for rule in entry.get("rules", []):
        platform = rule.get("os", {})
        matches = (not rule.get("features") and platform.get("name", "linux") == "linux"
                   and platform.get("arch", "x86_64") in ("x86_64", "amd64"))
        if "version" in platform:
            matches = matches and bool(re.search(platform["version"], os.uname().release))
        if matches:
            result = rule["action"] == "allow"
    return result


def prepare(args):
    root = base.external(args.directory)
    root.mkdir(parents=True)  # Refuse any existing installation.
    manifest = root / "versions/1.20.1/1.20.1.json"
    fetch(MANIFEST_URL, manifest, MANIFEST_SHA1)
    vanilla = json.loads(manifest.read_text())
    client = vanilla["downloads"]["client"]
    fetch(client["url"], manifest.with_suffix(".jar"), client["sha1"])
    (root / "launcher_profiles.json").write_text('{"profiles":{}}\n')
    installer = root / "forge-installer.jar"
    forge = "1.20.1-" + args.forge
    fetch(f"https://maven.minecraftforge.net/net/minecraftforge/forge/{forge}/forge-{forge}-installer.jar",
          installer, INSTALLERS[args.forge], "sha256")
    java = java_command(base.jdk(args.java17_home, 17), args.trust_store)
    with (root / "install.log").open("w") as log:
        subprocess.run([*java, "-Xmx1G", "-jar", str(installer), "--installClient", str(root)],
                       cwd=root, stdout=log, stderr=subprocess.STDOUT, check=True, timeout=900)
    forge_manifest = root / f"versions/1.20.1-forge-{args.forge}/1.20.1-forge-{args.forge}.json"
    combined = [*vanilla["libraries"], *json.loads(forge_manifest.read_text())["libraries"]]
    artifacts = {lib["downloads"]["artifact"]["path"]: lib["downloads"]["artifact"]
                 for lib in combined if allowed(lib) and "artifact" in lib.get("downloads", {})}
    def library(artifact):
        path = root / "libraries" / artifact["path"]
        fetch(artifact["url"], path, artifact["sha1"])
    with ThreadPoolExecutor(max_workers=8) as pool:
        list(pool.map(library, artifacts.values()))
    assets = base.external(args.assets)
    assets.mkdir(parents=True, exist_ok=True)
    index = vanilla["assetIndex"]
    fetch(index["url"], assets / "indexes" / (index["id"] + ".json"), index["sha1"])
    objects = json.loads((assets / "indexes" / (index["id"] + ".json")).read_text())["objects"]
    def asset(item):
        digest = item["hash"]
        fetch(f"https://resources.download.minecraft.net/{digest[:2]}/{digest}",
              assets / "objects" / digest[:2] / digest, digest)
    with ThreadPoolExecutor(max_workers=8) as pool:
        list(pool.map(asset, objects.values()))
    (root / "test-installation.json").write_text(json.dumps({
        "minecraft": "1.20.1", "forge": args.forge, "assets": str(assets),
        "manifest_sha1": MANIFEST_SHA1, "installer_sha256": INSTALLERS[args.forge],
        "verified_asset_entries": len(objects), "verified_libraries": len(artifacts),
    }, indent=2) + "\n")
    print(f"Prepared {root}; {len(objects)} asset entries verified")


def launch(args):
    if not re.fullmatch(r"[A-Za-z0-9_]{3,16}", args.username):
        raise ValueError("Use a Minecraft test username of 3-16 ASCII letters, digits or underscores")
    root = base.external(args.directory).resolve(strict=True)
    game = base.external(args.game_directory)
    game.mkdir(parents=True)  # Each client gets its own new game directory.
    jar = base.external(args.jar).resolve(strict=True)
    (game / "mods").mkdir()
    shutil.copyfile(jar, game / "mods" / jar.name)
    (game / "options.txt").write_text(
        "renderDistance:2\nsimulationDistance:2\nmaxFps:20\ngraphicsMode:0\n"
        "particles:2\nentityDistanceScaling:0.5\nsoundCategory_master:0.0\n"
        "mipmapLevels:0\nresourcePacks:[]\nmodelPart_cape:false\n"
        "onboardAccessibility:false\nskipMultiplayerWarning:true\n"
    )
    install = json.loads((root / "test-installation.json").read_text())
    version = "1.20.1-forge-" + install["forge"]
    vanilla = json.loads((root / "versions/1.20.1/1.20.1.json").read_text())
    forge = json.loads((root / f"versions/{version}/{version}.json").read_text())
    libraries = {}
    for library in [*vanilla["libraries"], *forge["libraries"]]:
        if allowed(library) and "artifact" in library.get("downloads", {}):
            key = ":".join(library["name"].split(":")[:2])
            if len(library["name"].split(":")) > 3:
                key += ":" + library["name"].split(":")[3]
            libraries[key] = root / "libraries" / library["downloads"]["artifact"]["path"]
    natives = game / "natives"
    natives.mkdir()
    for name, path in libraries.items():
        if "natives-linux" in name:
            with zipfile.ZipFile(path) as archive:
                for entry in archive.infolist():
                    if entry.filename.endswith(".so"):
                        (natives / Path(entry.filename).name).write_bytes(archive.read(entry))
    identity = uuid.UUID(bytes=hashlib.md5(("OfflinePlayer:" + args.username).encode()).digest(), version=3)
    replacements = {
        "auth_player_name": args.username, "auth_uuid": identity.hex,
        "auth_access_token": "0", "clientid": "0", "auth_xuid": "0", "user_type": "legacy",
        "version_name": version, "version_type": "isolated-development-test",
        "game_directory": str(game), "assets_root": install["assets"],
        "assets_index_name": vanilla["assetIndex"]["id"], "natives_directory": str(natives),
        "launcher_name": "HBM-isolated-test", "launcher_version": "1",
        "library_directory": str(root / "libraries"), "classpath_separator": os.pathsep,
        # Forge loads its patched client and client-extra via its own locator.
        # Adding the raw vanilla client creates a duplicate automatic module.
        "classpath": os.pathsep.join(str(p) for p in libraries.values()),
    }
    def arguments(kind):
        result = []
        for argument in [*vanilla["arguments"][kind], *forge["arguments"][kind]]:
            if isinstance(argument, dict):
                if not allowed(argument):
                    continue
                argument = argument["value"]
            for value in ([argument] if isinstance(argument, str) else argument):
                result.append(re.sub(r"\$\{([^}]+)\}", lambda m: replacements[m[1]], value))
        return result
    java = java_command(base.jdk(args.java17_home, 17), args.trust_store)
    command = [*java, "-Xms256M", f"-Xmx{args.heap_mb}M", "-XX:ActiveProcessorCount=2",
               *arguments("jvm"), forge["mainClass"], *arguments("game"), "--width", "854", "--height", "480"]
    if args.server:
        if not re.fullmatch(r"127\.0\.0\.1:\d+", args.server):
            raise ValueError("Offline direct-connect is restricted to 127.0.0.1:PORT")
        command += ["--quickPlayMultiplayer", args.server]
    record = {"command": command, "cwd": str(game), "jar_sha256": hashlib.sha256(jar.read_bytes()).hexdigest(),
              "forge": install["forge"], "username": args.username, "server": args.server,
              "display": os.environ.get("DISPLAY"), "offline_test_only": True,
              "utc": datetime.now(timezone.utc).isoformat()}
    (game / "launch.json").write_text(json.dumps(record, indent=2) + "\n")
    with (game / "console.log").open("w") as log:
        started = time.monotonic()
        process = subprocess.run(command, cwd=game, stdout=log, stderr=subprocess.STDOUT)
    record["exit_code"] = process.returncode
    record["duration_seconds"] = round(time.monotonic() - started, 3)
    (game / "launch.json").write_text(json.dumps(record, indent=2) + "\n")
    raise SystemExit(process.returncode)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="action", required=True)
    setup = commands.add_parser("prepare")
    setup.add_argument("directory")
    setup.add_argument("--forge", choices=INSTALLERS, default="47.4.23")
    setup.add_argument("--assets", required=True, help="External assets cache; missing objects downloaded and verified")
    run = commands.add_parser("launch")
    run.add_argument("directory")
    run.add_argument("game_directory")
    run.add_argument("jar")
    run.add_argument("--username", required=True)
    run.add_argument("--server", help="Optional loopback-only direct connect")
    run.add_argument("--heap-mb", type=int, default=1800)
    for subparser in (setup, run):
        subparser.add_argument("--java17-home", required=True)
        subparser.add_argument("--trust-store")
    args = parser.parse_args()
    (prepare if args.action == "prepare" else launch)(args)


if __name__ == "__main__":
    main()
