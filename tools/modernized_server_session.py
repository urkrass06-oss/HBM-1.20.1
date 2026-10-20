#!/usr/bin/env python3
# SPDX-License-Identifier: LGPL-3.0-only
"""Record an interactive session in an already installed isolated Forge test server.

Use its console for the fixture commands. Stop with `save-all flush`, then `stop`.
Existing worlds are deliberately reused for persistence checks; logs are never overwritten.
"""

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import subprocess
import time

import modernized_build as base
from test_modernized_server import INSTALLERS, java_command


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", help="Existing external installation from test_modernized_server.py")
    parser.add_argument("jar", help="Expected single HBM JAR already copied to mods")
    parser.add_argument("--forge", choices=INSTALLERS, required=True)
    parser.add_argument("--session", required=True, help="New log/JSON name, e.g. multiplayer-fixed")
    parser.add_argument("--java17-home", required=True)
    parser.add_argument("--trust-store")
    parser.add_argument("--heap-mb", type=int, default=1600)
    parser.add_argument("--accept-eula", action="store_true")
    parser.add_argument("--allow-offline-auth-failure", action="store_true")
    args = parser.parse_args()
    if not args.accept_eula or not re.fullmatch(r"[a-zA-Z0-9_-]+", args.session):
        parser.error("Explicit EULA acceptance and a plain new session name are required")
    directory = base.external(args.directory).resolve(strict=True)
    jar = base.external(args.jar).resolve(strict=True)
    properties = {}
    for line in (directory / "server.properties").read_text().splitlines():
        if "=" in line and not line.startswith("#"):
            key, value = line.split("=", 1)
            properties[key] = value
    if any(properties.get(key) != value for key, value in {
        "server-ip": "127.0.0.1", "online-mode": "false", "enable-rcon": "false", "enable-query": "false"
    }.items()):
        raise ValueError("Require a loopback-only offline test server with RCON/query disabled")
    if "eula=true" not in (directory / "eula.txt").read_text().splitlines():
        raise ValueError("Use the isolated installer/EULA setup first")
    installed = list((directory / "mods").glob("*.jar"))
    digest = hashlib.sha256(jar.read_bytes()).hexdigest()
    if len(installed) != 1 or hashlib.sha256(installed[0].read_bytes()).hexdigest() != digest:
        raise ValueError("mods must contain exactly the selected, unchanged HBM JAR")
    java = java_command(base.jdk(args.java17_home, 17), args.trust_store)
    command = [*java, "-Dterminal.jline=false", "-Dterminal.ansi=false", "-XX:ActiveProcessorCount=2",
               "-Xms256M", f"-Xmx{args.heap_mb}M",
               f"@libraries/net/minecraftforge/forge/1.20.1-{args.forge}/unix_args.txt", "nogui"]
    record_file = directory / (args.session + ".json")
    transcript = directory / (args.session + ".log")
    record = {"utc": datetime.now(timezone.utc).isoformat(), "command": command, "cwd": str(directory),
              "jar": str(jar), "jar_sha256": digest, "forge": args.forge,
              "bind": "127.0.0.1:" + properties["server-port"], "transcript": str(transcript),
              "world": properties.get("level-name", "world"), "eula": "accepted-for-isolated-test",
              "done": False, "error_lines": [], "command_failure_lines": [], "save_confirmed": False}
    with record_file.open("x") as output:
        output.write(json.dumps(record, indent=2) + "\n")
    with transcript.open("x") as log:
        started = time.monotonic()
        # Inherit terminal stdin for interactive commands; capture all child output.
        process = subprocess.Popen(command, cwd=directory, stdout=subprocess.PIPE,
                                   stderr=subprocess.STDOUT, text=True, bufsize=1)
        for line in process.stdout:
            log.write(line)
            log.flush()
            print(line, end="", flush=True)
            if "Done (" in line and not record["done"]:
                record["done"] = True
                record["startup_seconds"] = round(time.monotonic() - started, 3)
            if "Saved the game" in line:
                record["save_confirmed"] = True
            if "/ERROR]" in line or "/FATAL]" in line:
                record["error_lines"].append(line.rstrip())
            if "An unexpected error occurred trying to execute that command" in line:
                record["command_failure_lines"].append(line.rstrip())
        record["exit_code"] = process.wait()
    record["duration_seconds"] = round(time.monotonic() - started, 3)
    record["environment_error_lines"] = [line for line in record["error_lines"]
        if args.allow_offline_auth_failure
        and "Yggdrasil Key Fetcher/ERROR] [mojang/YggdrasilServicesKeyInfo]" in line
        and "Failed to request yggdrasil public key" in line]
    record["unexpected_error_lines"] = [line for line in record["error_lines"]
                                       if line not in record["environment_error_lines"]]
    record["passed_start_save_stop"] = (record["done"] and record["save_confirmed"]
        and record["exit_code"] == 0 and not record["unexpected_error_lines"])
    record_file.write_text(json.dumps(record, indent=2) + "\n")
    return 0 if record["passed_start_save_stop"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
