# Gazebo OCI Images - AI Coding Agent Instructions

## Project Overview

This repository builds multi-architecture OCI/Docker images for [Gazebo](https://gazebosim.org) robotics simulator using [Earthly](https://docs.earthly.dev/). It's a fork of the ROS OCI images work by @sloretz, adapted for Gazebo's unique versioning and release cadence.

**Core Purpose:** Automated weekly builds and release-triggered updates of Gazebo container images pushed to GitHub Packages (ghcr.io).

## Architecture & Build System

### Earthly-Based Build Pipeline

This project uses **Earthly** (v0.8+) as the primary build tool, NOT traditional Dockerfiles. All image definitions live in `Earthfile` files using Earthly's declarative syntax.

**Build Hierarchy:**
```
./Earthfile (root)                    # Defines platforms & orchestrates multi-arch builds
├── gazebo/Earthfile                  # Gazebo release targets (jetty, ionic, harmonic, fortress)
│   ├── Uses +GAZEBO_BINARY_IMAGES    # Function to generate core/full variants
│   └── Imports from apt/ and lib/
├── apt/Earthfile                     # Reusable INSTALL function for apt packages
└── lib/Earthfile                     # SAVE_IMAGE_AND_DATE function for tagging & pushing
```

**Key Pattern:** Each Gazebo release has TWO image variants:
- `core` - Minimal install (gz-tools, libsdformat, python bindings)
- `full` - Complete Gazebo suite (all gz-* packages)

### Multi-Architecture Support

- **Platforms:** `linux/amd64` and `linux/arm64/v8` for all releases
- **Multi-arch targets:** Use `-multiarch` suffix (e.g., `+jetty-multiarch`)
- **QEMU dependency:** `qemu-user-static` v6.2+ required for cross-compilation

## Critical Gazebo-Specific Conventions

### Release-Specific Package Handling

Each Gazebo release has different package names and Ubuntu base images. The logic in [gazebo/Earthfile](gazebo/Earthfile) lines 93-106 shows conditional package installation:

- **Fortress** (LTS): Ubuntu 22.04, uses `libignition-tools-dev` (legacy naming)
- **Harmonic** (LTS): Ubuntu 22.04, `gz-tools2`, `libsdformat14-dev`
- **Ionic**: Ubuntu 24.04, `gz-tools2`, `libsdformat15-dev`, `sdformat15-cli`
- **Jetty** (LTS): Ubuntu 24.04, `gz-tools2`, `libsdformat16-dev`, `sdformat16-cli`

**Why this matters:** When adding new Gazebo releases, you MUST update conditional logic with correct package versions and Ubuntu base images.

### Command Naming: ign vs gz

Fortress uses the legacy `ign` command; all newer releases use `gz`. This affects testing in [scripts/test_images.py](scripts/test_images.py#L57-L61).

## Developer Workflows

### Local Image Building

```bash
# Build single-arch image for local testing
earthly +jetty --registry=localhost/ --image_name=gazebo

# Build multi-arch images (requires QEMU)
earthly +jetty-multiarch --registry=localhost/ --image_name=gazebo
```

### Testing Images

```bash
# Test all variants of a release (pulls from registry)
./scripts/test_images.py --release jetty --registry ghcr.io/openrobotics --image-name gazebo

# Dry run to see commands
./scripts/test_images.py --release jetty --dry-run
```

**Test Coverage:** The script validates:
1. Image pulls successfully for both architectures
2. Package versions are correct (`apt-cache show`)
3. Commands run (`gz sim --help` or `ign gazebo --help` for Fortress)

### Checking for New Package Versions

```bash
# Check if a Gazebo release has updates (used by CI)
apt-get update && ./scripts/is_new_version_available.py --apt-package gz-harmonic
```

Returns "YES" or "NO" - used by `build-one-gazebo-release-if-necessary.yaml` workflows.

## GitHub Actions Workflows

### Three-Tier Workflow Architecture

1. **Weekly builds** (`ci-amd64-{release}.yaml`): Scheduled full rebuilds every Sunday at midnight GMT
2. **On-demand builds** (`{release}-build.yaml`): Manually triggered via workflow_dispatch
3. **Conditional builds** (`{release}-build-if-necessary.yaml`): Triggered by package sync detection

**Pattern to add new release:**
1. Add target to [gazebo/Earthfile](gazebo/Earthfile) with correct Ubuntu version
2. Update root [Earthfile](Earthfile) with new target + multiarch variant
3. Copy & rename workflow files (3 files per release)
4. Update [scripts/test_images.py](scripts/test_images.py) architecture support list

### CI-Specific Concerns

- **Disk space:** Uses `jlumbroso/free-disk-space` action to clean runner before builds
- **QEMU setup:** `docker/setup-qemu-action` required for multi-arch
- **Retry logic:** Docker login wrapped in `Wandalen/wretry.action` with 3 attempts and 4min delays
- **Push flag:** Earthly runs with `--ci --push` flags for production builds

## Code Style & Linting

- **Python:** Black formatter (any 2024 version) - enforced by `.github/workflows/ci-python-lint.yaml`
- **Markdown:** One sentence per line (see [CONTRIBUTING.md](CONTRIBUTING.md#L7-L15))
- **GitHub Actions:** yamllint runs via `ci-github-actions-lint.yaml`

## Image Tagging Strategy

Images get TWO tags via [lib/Earthfile](lib/Earthfile) `SAVE_IMAGE_AND_DATE` function:
- `:jetty-core` (stable tag, always points to latest)
- `:jetty-core-2025-12-15` (dated snapshot)

This allows users to pin to exact build dates or track latest automatically.

## External Dependencies

- **packages.osrfoundation.org**: Gazebo packages are NOT in Ubuntu repos; requires custom apt sources
- **ghcr.io**: GitHub Container Registry, requires `packages: write` permission
- **Earthly Cloud** (optional): Can use for caching, not currently configured

## Common Pitfalls

1. **Don't use `docker build`**: All image builds go through Earthly targets
2. **Platform mismatch**: When testing locally, ensure QEMU is installed for cross-arch
3. **Apt cache staleness**: `is_new_version_available.py` assumes `apt-get update` was already run
4. **Hardcoded architectures**: Platform list appears in multiple places ([Earthfile](Earthfile) lines 29-46, [test_images.py](scripts/test_images.py#L92-L98))
5. **GPU testing**: Images are built for GPU support but CI only validates basic command execution

## Quick Reference Commands

```bash
# Install dependencies (Ubuntu 22.04)
./scripts/install_dependencies.bash

# Build all releases locally
earthly +jetty-multiarch +ionic-multiarch +harmonic-multiarch +fortress-multiarch

# Format Python code
black scripts/

# Run image with GPU (example for testing)
docker run --rm -ti --runtime=nvidia -e NVIDIA_VISIBLE_DEVICES=all \
  ghcr.io/openrobotics/gazebo:jetty-full gz sim --verbose
```
