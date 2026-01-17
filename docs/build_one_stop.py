#!/usr/bin/env python3
import argparse
import os
import subprocess
import sys
from pathlib import Path


BUILD_TYPE_CHOICES = ["Build", "Clean", "Rebuild"]
PLATFORM_CHOICES = ["Win32", "x64", "Both"]
CONFIG_CHOICES = [
    "All",
    "Main",
    "Filters",
    "API",
    "MPCHC",
    "Resources",
    "IconLib",
    "Translations",
]
BUILD_CFG_CHOICES = ["Release", "Debug"]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "One-stop build helper for MPC-HC using build.bat. "
            "This script assumes you prepared build.user.bat as described in docs/Compilation.md."
        )
    )
    parser.add_argument(
        "--build-type",
        choices=BUILD_TYPE_CHOICES,
        default="Build",
        help="Build action to run (default: Build).",
    )
    parser.add_argument(
        "--platform",
        choices=PLATFORM_CHOICES,
        default="x64",
        help="Target platform (default: x64).",
    )
    parser.add_argument(
        "--config",
        choices=CONFIG_CHOICES,
        default="All",
        help="Project group to build (default: All).",
    )
    parser.add_argument(
        "--build-cfg",
        choices=BUILD_CFG_CHOICES,
        default="Release",
        help="Build configuration (default: Release).",
    )
    parser.add_argument("--packages", action="store_true", help="Build packages.")
    parser.add_argument("--installer", action="store_true", help="Build installer.")
    parser.add_argument("--zip", action="store_true", help="Build 7z archives.")
    parser.add_argument("--lite", action="store_true", help="Build Lite configuration.")
    parser.add_argument(
        "--lavfilters-clean",
        action="store_true",
        help="Clean LAVFilters (build.bat LAVFilters switch).",
    )
    parser.add_argument("--silent", action="store_true", help="Enable silent mode.")
    parser.add_argument("--nocolors", action="store_true", help="Disable ANSI colors.")
    parser.add_argument("--analyze", action="store_true", help="Enable analysis.")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the command without executing.",
    )
    parser.add_argument(
        "extra_args",
        nargs=argparse.REMAINDER,
        help="Additional arguments passed to build.bat (prefix with --).",
    )
    return parser.parse_args()


def build_command(repo_root: Path, args: argparse.Namespace) -> list[str]:
    build_bat = repo_root / "build.bat"
    cmd = [str(build_bat)]

    cmd.append(args.build_type)
    cmd.append(args.platform)
    cmd.append(args.config)
    cmd.append(args.build_cfg)

    if args.packages:
        cmd.append("Packages")
    if args.installer:
        cmd.append("Installer")
    if args.zip:
        cmd.append("7z")
    if args.lite:
        cmd.append("Lite")
    if args.lavfilters_clean:
        cmd.append("LAVFilters")
    if args.silent:
        cmd.append("Silent")
    if args.nocolors:
        cmd.append("Nocolors")
    if args.analyze:
        cmd.append("Analyze")

    if args.extra_args:
        cmd.extend(args.extra_args)

    return cmd


def main() -> int:
    args = parse_args()

    if os.name != "nt":
        print("This script is intended to run on Windows (cmd.exe required).", file=sys.stderr)
        return 2

    repo_root = Path(__file__).resolve().parents[1]
    build_user = repo_root / "build.user.bat"
    if not build_user.exists():
        print(
            "Missing build.user.bat. Please create it as described in docs/Compilation.md before building.",
            file=sys.stderr,
        )
        return 2

    build_bat = repo_root / "build.bat"
    if not build_bat.exists():
        print("build.bat not found in repository root.", file=sys.stderr)
        return 2

    cmd = build_command(repo_root, args)
    if args.dry_run:
        print("Dry run: cmd /c " + " ".join(cmd))
        return 0

    return subprocess.call(["cmd", "/c", *cmd], cwd=repo_root)


if __name__ == "__main__":
    raise SystemExit(main())
