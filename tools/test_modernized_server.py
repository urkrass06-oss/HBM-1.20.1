#!/usr/bin/env python3
# SPDX-License-Identifier: LGPL-3.0-only
"""Install Forge and smoke-test the built JAR in a new, loopback-only test directory."""

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import queue
import shutil
import socket
import subprocess
import sys
import threading
import time

import modernized_build as base

INSTALLERS = {
    "47.4.20": "0ebcf198609f925e0018842a79473ef74fda78534f86d82f2c0fdb26449c1fa4",
    "47.4.23": "75cfcb11f60cc641dc83757c1357c08c9bdba255ec529feb115c5e89a59cf75a",
}


def java_command(java17, trust_store):
    from urllib.parse import urlsplit
    command = [str(java17 / "bin/java")]
    for scheme in ("http", "https"):
        value = os.environ.get(scheme.upper() + "_PROXY") or os.environ.get(scheme + "_proxy")
        if value:
            proxy = urlsplit(value)
            if proxy.username or proxy.password or proxy.scheme != "http" or not proxy.hostname:
                raise ValueError("Use an http://host:port proxy without embedded credentials")
            command += [f"-D{scheme}.proxyHost={proxy.hostname}", f"-D{scheme}.proxyPort={proxy.port or 80}"]
    if trust_store:
        command += [f"-Djavax.net.ssl.trustStore={Path(trust_store).resolve(strict=True)}"]
    return command


def exercise(directory, command, number, startup_timeout, observe_seconds, allow_offline_auth_failure=False):
    """Require Done, observe ticks, save and stop gracefully; retain all output."""
    transcript = directory / f"server-{number}.log"
    lines = queue.Queue()
    record = {"utc": datetime.now(timezone.utc).isoformat(), "command": command,
              "cwd": str(directory), "transcript": str(transcript), "done": False}
    process = subprocess.Popen(command, cwd=directory, stdin=subprocess.PIPE,
                               stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                               text=True, bufsize=1)
    with transcript.open("w") as output:
        def reader():
            for line in process.stdout:
                output.write(line)
                output.flush()
                lines.put(line)
        thread = threading.Thread(target=reader, daemon=True)
        thread.start()
        start = time.monotonic()
        deadline = start + startup_timeout
        observed_until = None
        stopped = False
        errors = []
        try:
            while process.poll() is None:
                try:
                    line = lines.get(timeout=0.25)
                    if "/ERROR]" in line or "/FATAL]" in line:
                        errors.append(line.strip())
                    if 'Done (' in line and 'For help, type' in line and not record["done"]:
                        record["done"] = True
                        record["startup_seconds"] = round(time.monotonic() - start, 3)
                        observed_until = time.monotonic() + observe_seconds
                        process.stdin.write("list\n")
                        process.stdin.flush()
                    if "Saved the game" in line:
                        record["save_confirmed"] = True
                except queue.Empty:
                    pass
                if not record["done"] and time.monotonic() > deadline:
                    raise TimeoutError("Server never reached Done before startup deadline")
                if observed_until and time.monotonic() >= observed_until and not stopped:
                    process.stdin.write("save-all flush\nstop\n")
                    process.stdin.flush()
                    record["observed_seconds"] = observe_seconds
                    stopped = True
                    deadline = time.monotonic() + 90
                if stopped and time.monotonic() > deadline:
                    raise TimeoutError("Server did not stop gracefully")
            thread.join(timeout=10)
            output.flush()
            # Include final output queued during JVM shutdown as well.
            complete = transcript.read_text()
            errors = [line for line in complete.splitlines() if "/ERROR]" in line or "/FATAL]" in line]
            record["save_confirmed"] = "Saved the game" in complete
            environment_errors = [line for line in errors if allow_offline_auth_failure
                                  and "Yggdrasil Key Fetcher/ERROR] [mojang/YggdrasilServicesKeyInfo]" in line
                                  and "Failed to request yggdrasil public key" in line]
            unexpected = [line for line in errors if line not in environment_errors]
            record.update(exit_code=process.returncode, error_lines=errors,
                          environment_error_lines=environment_errors, unexpected_error_lines=unexpected)
            record["passed"] = record["done"] and record.get("save_confirmed", False) and process.returncode == 0 and not unexpected
        finally:
            if process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=15)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait()
            thread.join(timeout=10)
            (directory / f"server-{number}.json").write_text(json.dumps(record, indent=2) + "\n")
    return record


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("jar")
    parser.add_argument("directory", help="New external test directory; existing paths are refused")
    parser.add_argument("--java17-home", required=True)
    parser.add_argument("--trust-store")
    parser.add_argument("--forge", choices=INSTALLERS, default="47.4.20")
    parser.add_argument("--accept-eula", action="store_true", help="Accept https://aka.ms/MinecraftEULA for this isolated test")
    parser.add_argument("--allow-offline-auth-failure", action="store_true",
                        help="Record the specific Yggdrasil public-key error separately in this offline loopback test")
    parser.add_argument("--observe-seconds", type=int, default=30)
    parser.add_argument("--startup-timeout", type=int, default=240)
    parser.add_argument("--heap-mb", type=int, default=3072, help="Maximum server heap; 1600 was used for the constrained two-client environment")
    args = parser.parse_args()
    forge = "1.20.1-" + args.forge
    installer_url = f"https://maven.minecraftforge.net/net/minecraftforge/forge/{forge}/forge-{forge}-installer.jar"
    installer_sha256 = INSTALLERS[args.forge]
    if args.heap_mb < 512:
        raise ValueError("Use a server heap of at least 512 MB")
    if not args.accept_eula:
        raise ValueError("Explicit --accept-eula is required; user must authorize EULA acceptance")
    directory = base.external(args.directory)
    jar = base.external(args.jar).resolve(strict=True)
    java17 = base.jdk(args.java17_home, 17)
    java = java_command(java17, args.trust_store)
    directory.mkdir(parents=True)  # Never overwrite an existing server or world.
    installer = directory / "forge-installer.jar"
    # Forge's CDN rejected Python urllib here (HTTP 403); the Phase-3 curl path works.
    # Keep the inherited proxy, normal TLS verification, and mandatory content checksum.
    download_command = ["curl", "--fail", "--silent", "--show-error", "--location", "--retry", "2",
                        "--max-time", "180", "--output", str(installer), installer_url]
    subprocess.run(download_command, check=True, timeout=600)
    data = installer.read_bytes()
    if hashlib.sha256(data).hexdigest() != installer_sha256:
        raise ValueError("Forge installer checksum mismatch")
    install_command = [*java, "-jar", str(installer), "--installServer"]
    with (directory / "install.log").open("w") as output:
        subprocess.run(install_command, cwd=directory, stdout=output, stderr=subprocess.STDOUT, check=True, timeout=600)
    (directory / "mods").mkdir(exist_ok=True)
    shutil.copyfile(jar, directory / "mods" / jar.name)
    (directory / "eula.txt").write_text("# Accepted by explicit user authorization for this isolated test only.\neula=true\n")
    with socket.socket() as listener:
        listener.bind(("127.0.0.1", 0))
        port = listener.getsockname()[1]
    (directory / "server.properties").write_text(
        f"server-ip=127.0.0.1\nserver-port={port}\nonline-mode=false\n"
        "enable-rcon=false\nenable-query=false\nmotd=Isolated HBM integration test\n"
        "level-name=integration-test-world\nlevel-seed=42012001\n"
        "view-distance=4\nsimulation-distance=4\nmax-players=2\nspawn-protection=0\n"
    )
    command = [*java, "-Xms512M", f"-Xmx{args.heap_mb}M", f"@libraries/net/minecraftforge/forge/{forge}/unix_args.txt", "nogui"]
    result = {"utc": datetime.now(timezone.utc).isoformat(), "jar": str(jar),
              "jar_sha256": hashlib.sha256(jar.read_bytes()).hexdigest(), "forge": forge,
              "installer_url": installer_url, "installer_sha256": installer_sha256,
              "download_command": download_command,
              "install_command": install_command, "bind": f"127.0.0.1:{port}",
              "eula": "accepted-for-isolated-test", "runs": []}
    for number in (1, 2):
        run = exercise(directory, command, number, args.startup_timeout, args.observe_seconds,
                       args.allow_offline_auth_failure)
        result["runs"].append(run)
        (directory / "result.json").write_text(json.dumps(result, indent=2) + "\n")
        print(json.dumps(run), flush=True)
        if not run["passed"]:
            return 1
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (ValueError, OSError, subprocess.SubprocessError, TimeoutError) as error:
        print(f"Server test failed: {error}", file=sys.stderr)
        sys.exit(1)
