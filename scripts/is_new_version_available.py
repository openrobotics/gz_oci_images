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


def is_new_version_available(pkg):
    """Assumes apt-get update has already been called."""
    try:
        subprocess.check_output(
            f"apt-cache depends {pkg}", shell=True, stderr=subprocess.DEVNULL
        )
    except subprocess.CalledProcessError:
        raise ValueError(f"Package '{pkg}' not found")

    # Not using --recursive since the metapackage depends on at least one fo the gz libs that are updated
    # all together.
    cmd = f"apt-cache depends {pkg} | grep 'Depends:' | awk '{{print $2}}' | xargs apt list --upgradable 2>/dev/null"
    try:
        output = subprocess.check_output(cmd, shell=True)
        output_lines = output.decode().strip().split("\n")
        # Filter out the "Listing... Done" line and empty lines
        upgradable_lines = [
            line for line in output_lines if line and not line.startswith("Listing")
        ]
        return len(upgradable_lines) > 0
    except subprocess.CalledProcessError as e:
        logging.error("Command failed with exit code %s: %s", e.returncode, cmd)
        raise


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("--apt-package", required=True, type=str)
    args = parser.parse_args()

    return args


def main():
    args = parse_arguments()
    if is_new_version_available(args.apt_package):
        print("YES")
    else:
        print("NO")


if __name__ == "__main__":
    main()
