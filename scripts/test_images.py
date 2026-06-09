#!/usr/bin/env python3

# Copyright 2024 Shane Loretz.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import argparse
import logging
import subprocess


SERVER_ONLY_PACKAGE_BY_RELEASE = {
    "jetty": "gz-sim10-server",
    "rotary": "gz-sim-server",
}

SERVER_ONLY_BINARY_BY_RELEASE = {
    "jetty": "/usr/libexec/gz/sim10/gz-sim-server",
    "rotary": "/usr/libexec/gz/sim/gz-sim-server",
}


# TODO(j-rivero) share implementation with build_images.py
def _full_name(registry, name, tag):
    return f"{registry}/{name}:{tag}"


def _pull(full_name, dry_run):
    cmd = ["docker", "pull", full_name]
    if dry_run:
        logging.info(cmd)
    else:
        subprocess.check_call(cmd)


def _run(full_name, extra_cmd, platform=None, dry_run=False):
    cmd = ["docker", "run", "--rm=true"]
    if platform:
        cmd.append("--platform")
        cmd.append(platform)
    cmd.append(full_name)
    cmd.extend(extra_cmd)
    if dry_run:
        logging.info(cmd)
    else:
        subprocess.check_call(cmd)


def _print_gz_help(
    full_name, platform=None, dry_run=False, gazebo_release="", image_type=""
):
    cmd = []
    gz_subcmd = ["sim"]

    if gazebo_release == "fortress":
        cmd += ["ign"]
        gz_subcmd = ["gazebo"]
    else:
        cmd += ["gz"]

    if image_type == "core":
        cmd += ["sdf"]
    elif image_type == "server-only":
        cmd = [_server_only_binary(gazebo_release)]
    elif image_type == "full":
        cmd += gz_subcmd
    else:
        raise ValueError(
            f"Unknown image_type '{image_type}' for release '{gazebo_release}'. "
            f"Add handling for this variant in _print_gz_help()."
        )

    cmd += ["--help"]

    _run(full_name, cmd, platform, dry_run)


def _print_pkg_version(full_name, pkg, platform=None, dry_run=False):
    cmd = ["apt-cache", "show", pkg]
    _run(full_name, cmd, platform, dry_run)


def _server_only_binary(gazebo_release):
    try:
        return SERVER_ONLY_BINARY_BY_RELEASE[gazebo_release]
    except KeyError as exc:
        raise ValueError(
            f"Unknown server-only binary for release '{gazebo_release}'. "
            "Add it to SERVER_ONLY_BINARY_BY_RELEASE."
        ) from exc


def _server_only_package(gazebo_release):
    try:
        return SERVER_ONLY_PACKAGE_BY_RELEASE[gazebo_release]
    except KeyError as exc:
        raise ValueError(
            f"Unknown server-only package for release '{gazebo_release}'. "
            "Add it to SERVER_ONLY_PACKAGE_BY_RELEASE."
        ) from exc


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("--registry", default="localhost", type=str)
    parser.add_argument("--image-name", default="gazebo", type=str)
    parser.add_argument("--release", required=True, type=str)
    parser.add_argument("--dry-run", action="store_true")

    args = parser.parse_args()

    return args


logging.basicConfig(level=logging.INFO)


def _image_platform_combos(gazebo_release):
    amd64 = "linux/amd64"
    arm64 = "linux/arm64/v8"

    # Rotary packages are not available on arm64, so its images are amd64-only.
    platforms = [amd64] if gazebo_release == "rotary" else [amd64, arm64]

    combos = []
    for platform in platforms:
        combos.extend([("core", platform), ("full", platform)])

    if gazebo_release in SERVER_ONLY_PACKAGE_BY_RELEASE:
        for platform in platforms:
            combos.append(("server-only", platform))

    return combos


def main():
    args = parse_arguments()

    gazebo_release = args.release.lower()
    dry_run = args.dry_run

    combos = _image_platform_combos(gazebo_release)
    for image, platform in combos:
        tag = f"{gazebo_release}-{image}"
        if image == "server-only":
            package = _server_only_package(gazebo_release)
        else:
            package = f"gz-{gazebo_release}"
        full_name = _full_name(args.registry, args.image_name, tag)
        _pull(full_name, dry_run)
        _print_pkg_version(full_name, package, platform, args.dry_run)
        _print_gz_help(full_name, platform, dry_run, gazebo_release, image)


if __name__ == "__main__":
    main()
