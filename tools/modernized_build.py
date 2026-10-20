#!/usr/bin/env python3
# SPDX-License-Identifier: LGPL-3.0-only
"""Prepare and exercise a pinned, external Modernized checkout; import no files."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import shlex
import subprocess
import sys
from datetime import datetime, timezone
from urllib.parse import urlsplit
from urllib.request import urlopen


PIN = "0365cef5956016913095eeeb9366f26c601ca9a0"
SOURCE = "https://github.com/Raptor324/HBM-Modernized.git"
WRAPPER_URL = "https://raw.githubusercontent.com/gradle/gradle/v9.3.1/gradle/wrapper/gradle-wrapper.jar"
WRAPPER_SHA256 = "b3a875ddc1f044746e1b1a55f645584505f4a10438c1afea9f15e92a7c42ec13"
REPO = Path(__file__).resolve().parents[1]
PATCH = REPO / "tools/modernized/forge-1.20.1.patch"
TASKS = ("tasks", "javaToolchains", "runData", "build", "sourcesJar", "runServer",
         "runClient", "runGameTestServer", "clean", "dependencies")
PROFILES = {"production": "47.4.23", "compatibility": "47.4.20"}


def profile_arguments(profile, arguments, tasks):
    forge = PROFILES[profile]
    overrides = [arg for arg in arguments if arg.startswith("-Pdeps.forge=")]
    if any(arg != f"-Pdeps.forge={forge}" for arg in overrides):
        raise ValueError(f"Forge override conflicts with {profile} profile ({forge})")
    if any(arg.startswith(("-Pdeps.minecraft=", "-Pmod.id=")) for arg in arguments):
        raise ValueError("Minecraft target and namespace are fixed")
    if {"build", "sourcesJar"} & set(tasks) and "-Pmodernized.gameTests=true" in arguments:
        raise ValueError("Production packaging and GameTests require separate invocations")
    result = [arg for arg in arguments if not arg.startswith("-Pdeps.forge=")]
    if "runGameTestServer" in tasks:
        if tasks != ["runGameTestServer"]:
            raise ValueError("Run GameTests separately from other tasks")
        if "-Pmodernized.gameTests=false" in result:
            raise ValueError("GameTest task requires the test profile")
        if "-Pmodernized.gameTests=true" not in result:
            result.append("-Pmodernized.gameTests=true")
    return [*result, f"-Pdeps.forge={forge}"]


def external(path):
    result = Path(path).expanduser().resolve()
    worktrees = subprocess.check_output(["git", "-C", str(REPO), "worktree", "list", "--porcelain"], text=True)
    roots = [Path(row.removeprefix("worktree ")).resolve() for row in worktrees.splitlines() if row.startswith("worktree ")]
    if any(result == root or root in result.parents for root in roots):
        raise ValueError("The checkout, cache and logs must be outside every public worktree")
    return result


def git(checkout, *args):
    return subprocess.check_output(["git", "-C", str(checkout), *args], text=True).strip()


def pinned(checkout):
    if git(checkout, "rev-parse", "HEAD") != PIN:
        raise ValueError(f"Expected Modernized commit {PIN}")


def prepare(args):
    checkout = external(args.checkout)
    if checkout.exists():
        raise ValueError("Destination already exists; choose a new external directory")
    # Fetch the object by SHA, even if the upstream default branch changes later.
    subprocess.run(["git", "init", str(checkout)], check=True)
    subprocess.run(["git", "-C", str(checkout), "remote", "add", "origin", SOURCE], check=True)
    subprocess.run(["git", "-C", str(checkout), "fetch", "--depth=1", "origin", PIN], check=True)
    subprocess.run(["git", "-C", str(checkout), "checkout", "--detach", "FETCH_HEAD"], check=True)
    pinned(checkout)
    subprocess.run(["git", "-C", str(checkout), "apply", "--check", str(PATCH)], check=True)
    subprocess.run(["git", "-C", str(checkout), "apply", str(PATCH)], check=True)
    with urlopen(WRAPPER_URL, timeout=60) as response:
        data = response.read()
    if hashlib.sha256(data).hexdigest() != WRAPPER_SHA256:
        raise ValueError("Official Gradle wrapper checksum mismatch")
    (checkout / "gradle/wrapper/gradle-wrapper.jar").write_bytes(data)
    print(f"Prepared {checkout} at {PIN}; inspect git diff before running Gradle.")


def jdk(path, major):
    if not path:
        raise ValueError(f"Set the JDK {major} path explicitly or via its environment variable")
    result = Path(path).expanduser().resolve()
    executable = result / "bin" / ("javac.exe" if os.name == "nt" else "javac")
    version = subprocess.check_output([str(executable), "-version"], text=True, stderr=subprocess.STDOUT)
    if not version.startswith(f"javac {major}."):
        raise ValueError(f"Expected a complete JDK {major}, including javac")
    return result


def run(args):
    if "runData" in args.tasks and len(args.tasks) != 1:
        raise ValueError("Run runData by itself, then build in a separate invocation: runData depends on classes/processResources")
    arguments = profile_arguments(args.profile, args.gradle_arg, args.tasks)
    checkout = external(args.checkout)
    pinned(checkout)
    java21 = jdk(args.java21_home, 21)
    java17 = jdk(args.java17_home, 17)
    cache = external(args.gradle_home)
    logs = external(args.log_dir)
    cache.mkdir(parents=True, exist_ok=True)
    logs.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    env.update(JAVA_HOME=str(java21), JAVA17_HOME=str(java17), GRADLE_USER_HOME=str(cache))
    # Applies to wrapper, daemon and forked tooling JVMs, without disabling TLS verification.
    options = []
    for scheme in ("http", "https"):
        value = env.get(f"{scheme.upper()}_PROXY") or env.get(f"{scheme}_proxy")
        if value:
            proxy = urlsplit(value)
            if proxy.username or proxy.password:
                raise ValueError("Use supported JVM authentication for a credentialed proxy")
            if not proxy.hostname or proxy.scheme != "http":
                raise ValueError("Java proxy adaptation expects an http://host:port proxy")
            options += [f"-D{scheme}.proxyHost={proxy.hostname}", f"-D{scheme}.proxyPort={proxy.port or 80}"]
    if args.trust_store:
        trust = Path(args.trust_store).expanduser().resolve(strict=True)
        options.append(f"-Djavax.net.ssl.trustStore={trust}")
    # JAVA_TOOL_OPTIONS is parsed by the JVM, not by a shell. Quote paths with spaces.
    env["JAVA_TOOL_OPTIONS"] = " ".join(filter(None, [env.get("JAVA_TOOL_OPTIONS", ""),
        " ".join('"' + option + '"' for option in options)]))
    wrapper = "gradlew.bat" if os.name == "nt" else "./gradlew"
    command = [wrapper, "--no-daemon", "--console=plain", "--max-workers=2",
        "-Porg.gradle.java.installations.fromEnv=JAVA_HOME,JAVA17_HOME",
        "-Porg.gradle.java.installations.auto-download=false",
        *[f":1.20.1-forge:{task}" for task in args.tasks], "--stacktrace", *arguments]
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    log = logs / f"{stamp}-{'-'.join(args.tasks)}.log"
    record = {"utc": stamp, "upstream": PIN, "cwd": str(checkout), "command": command,
        "jdk21": str(java21), "jdk17": str(java17), "log": str(log),
        "profile": args.profile, "forge": PROFILES[args.profile]}
    provenance = checkout / "integration/provenance.json"
    if provenance.exists():
        record["integration_provenance_sha256"] = hashlib.sha256(provenance.read_bytes()).hexdigest()
    print(f"Running {shlex.join(command)}\nLog: {log}", flush=True)
    with log.open("w", encoding="utf-8") as output:
        output.write(json.dumps(record, ensure_ascii=False) + "\n")
        output.flush()
        completed = subprocess.run(command, cwd=checkout, env=env, stdout=output, stderr=subprocess.STDOUT)
    record["exit_code"] = completed.returncode
    with (logs / "commands.jsonl").open("a", encoding="utf-8") as output:
        output.write(json.dumps(record, ensure_ascii=False) + "\n")
    print(f"Exit {completed.returncode}; full output: {log}", flush=True)
    return completed.returncode


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="action", required=True)
    prep = commands.add_parser("prepare", help="Create a new external checkout and apply the recorded patch")
    prep.add_argument("checkout")
    build = commands.add_parser("run", help="Run only explicit Forge 1.20.1 tasks and retain a transcript")
    build.add_argument("checkout")
    build.add_argument("tasks", nargs="+", choices=TASKS)
    build.add_argument("--java21-home", default=os.environ.get("JAVA21_HOME") or os.environ.get("JAVA_HOME"))
    build.add_argument("--java17-home", default=os.environ.get("JAVA17_HOME"))
    build.add_argument("--gradle-home", required=True)
    build.add_argument("--log-dir", required=True)
    build.add_argument("--trust-store")
    build.add_argument("--profile", choices=PROFILES, default="compatibility",
                       help="production pins Forge 47.4.23; compatibility preserves 47.4.20")
    build.add_argument("--gradle-arg", action="append", default=[], help="Use --gradle-arg=--info, for example")
    args = parser.parse_args()
    return prepare(args) if args.action == "prepare" else run(args)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (ValueError, OSError, subprocess.CalledProcessError) as error:
        print(f"Modernized preparation failed: {error}", file=sys.stderr)
        sys.exit(1)
