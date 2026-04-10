# Gazebo Open Container Initiative Images

[Open Container Initiative](https://opencontainers.org/) images for [Gazebo](https://gazebosim.org)!


Are you looking for **Docker images**?
You're in the right spot!
OCI images are Docker images.
[Here's how Docker and OCI relate](https://www.docker.com/blog/demystifying-open-container-initiative-oci-specifications/).

> [!NOTE]
> This repository is mostly a fork of the work done by @slorezt in https://github.com/sloretz/ros_oci_images
> adapted to Gazebo. All credit goes to Shane.

## Quick Start

New to containers? Start with [Rocker](https://github.com/osrf/rocker) - it automatically handles GPU and display setup for you.
We recommend using Rocker inside of a Python [virtual environment.](https://docs.python.org/3/library/venv.html)

```bash
# Install rocker (requires Docker)
python3 -m venv venv && source venv/bin/activate && pip install rocker

# Run Gazebo with GPU and X11 display support
rocker --x11 --nvidia gpus ghcr.io/openrobotics/gazebo:jetty-full -- gz sim --verbose
```

For other container tools or advanced usage, see the sections below.

> [!TIP]
> Having issues with graphics or GPU acceleration?
> See the [Troubleshooting Guide](TROUBLESHOOTING.md) for step-by-step diagnostics.

## About the images

Named Gazebo release images are updated once per week at midnight GMT on Sunday.
Additionally each Gazebo release's images are updated automatically after a sync, and rotary images are rebuilt daily from the nightly repository.

The Gazebo releases provide different variants based on the included libraries.
All images are based on Ubuntu.

| Image           | amd64 | arm64 v8 | Full Image Name                                |
|-----------------|-------|----------|-----------------------------------------------|
| **Stable distributions** | | | |
| **[Gazebo Jetty (LTS)](https://gazebosim.org/docs/jetty)** | | | |
| core            | ✅     | ✅        | `ghcr.io/openrobotics/gazebo:jetty-core`           |
| full            | ✅     | ✅        | `ghcr.io/openrobotics/gazebo:jetty-full`           |
| **[Gazebo Ionic](https://gazebosim.org/docs/ionic)** | | | |
| core            | ✅     | ✅        | `ghcr.io/openrobotics/gazebo:ionic-core`           |
| full            | ✅     | ✅        | `ghcr.io/openrobotics/gazebo:ionic-full`           |
| **[Gazebo Harmonic (LTS)](https://gazebosim.org/docs/harmonic)** | | | |
| core            | ✅     | ✅        | `ghcr.io/openrobotics/gazebo:harmonic-core`        |
| full            | ✅     | ✅        | `ghcr.io/openrobotics/gazebo:harmonic-full`        |
| **[Gazebo Fortress (LTS)](https://gazebosim.org/docs/fortress)** | | | |
| core            | ✅     | ✅        | `ghcr.io/openrobotics/gazebo:fortress-core`        |
| full            | ✅     | ✅        | `ghcr.io/openrobotics/gazebo:fortress-full`        |
| **Rolling / Nightly** | | | |
| **Gazebo Rotary** | | | |
| core            | ✅     | ✅        | `ghcr.io/openrobotics/gazebo:rotary-core`          |
| full            | ✅     | ✅        | `ghcr.io/openrobotics/gazebo:rotary-full`          |


## Using with other OCI compatible tools

Used containers for a while? Other tools might be a better fit for your use case. Below are examples showing how to run Gazebo with X11 display and GPU support using various container tools.

### [Apptainer](https://apptainer.org/)

**GPU Support:** NVIDIA GPUs with `--nv` flag, AMD GPUs with `--rocm` flag
**X11 Support:** Manual configuration required

```bash
# Basic usage
apptainer run docker://ghcr.io/openrobotics/gazebo:jetty-full gz sim --help

# With NVIDIA GPU and X11 display
apptainer run --nv --env DISPLAY=$DISPLAY -B /tmp/.X11-unix:/tmp/.X11-unix \
  docker://ghcr.io/openrobotics/gazebo:jetty-full gz sim
```

[GPU Documentation](https://apptainer.org/docs/user/main/gpu.html)

### [Distrobox](https://github.com/89luca89/distrobox)

**Requirements:** Docker or Podman
**GPU Support:** NVIDIA GPUs with `--nvidia gpus` flag, Intel and AMD GPUs automatically supported
**X11 Support:** Automatic X11 and Wayland socket access

```bash
# Create container with NVIDIA GPU support
distrobox create --nvidia --image ghcr.io/openrobotics/gazebo:jetty-full --name jetty-full

# Enter the container
distrobox enter jetty-full

# Run Gazebo (X11 and GPU work automatically)
gz sim
```

[Documentation](https://github.com/89luca89/distrobox/blob/main/docs/useful_tips.md)

### [nerdctl](https://github.com/containerd/nerdctl)

**GPU Support:** Docker-compatible `--gpus` flag
**X11 Support:** Manual configuration required

```bash
# Basic usage
nerdctl run --rm=true -ti ghcr.io/openrobotics/gazebo:jetty-full gz sim --help

# With GPU and X11 display
nerdctl run -it --rm --gpus all -e DISPLAY=$DISPLAY \
  -v /tmp/.X11-unix:/tmp/.X11-unix \
  ghcr.io/openrobotics/gazebo:jetty-full gz sim
```

[GPU Documentation](https://github.com/containerd/nerdctl/blob/main/docs/gpu.md)
[Rootless Mode](https://github.com/containerd/nerdctl?tab=readme-ov-file#rootless-mode)

### [Podman](https://podman.io/)

**GPU Support:** NVIDIA GPUs using CDI with `--device nvidia.com/gpu=all` flag
**X11 Support:** Manual configuration required with SELinux label disabled

```bash
# Basic usage
podman run --rm=true -ti ghcr.io/openrobotics/gazebo:jetty-full gz sim --help

# With NVIDIA GPU and X11 display
podman run -it --rm --device nvidia.com/gpu=all --security-opt=label=disable \
  -e DISPLAY=$DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix \
  ghcr.io/openrobotics/gazebo:jetty-full gz sim
```

[GPU Documentation](https://podman-desktop.io/docs/podman/gpu)

### [Rocker](https://github.com/osrf/rocker)

**Requirements:** Docker
**GPU Support:** NVIDIA GPUs with `--nvidia gpus` flag
**X11 Support:** Automatic with `--x11` flag

```bash
# Basic usage

# With NVIDIA GPU and X11 display
```

[Documentation](https://github.com/osrf/rocker)

### [Sarus](https://sarus.readthedocs.io/en/stable/)

**GPU Support:** NVIDIA GPUs through NVIDIA Container Toolkit (configured via OCI hooks)
**X11 Support:** Manual bind mounting required

```bash
# Pull and run basic usage
sarus pull ghcr.io/openrobotics/gazebo:jetty-full
sarus run -t ghcr.io/openrobotics/gazebo:jetty-full gz sim --help

# With X11 display (GPU configured at system level)
sarus run --mount=type=bind,source=/tmp/.X11-unix,destination=/tmp/.X11-unix \
  ghcr.io/openrobotics/gazebo:jetty-full gz sim
```

[GPU Documentation](https://sarus.readthedocs.io/en/stable/config/nvidia-container-toolkit.html)

### [SingularityCE](https://sylabs.io/singularity/)

**GPU Support:** NVIDIA GPUs with `--nv` flag, AMD GPUs with `--rocm` flag
**X11 Support:** Manual configuration required

```bash
# Basic usage
singularity run docker://ghcr.io/openrobotics/gazebo:jetty-full gz sim --help

# With NVIDIA GPU and X11 display
singularity run --nv --env DISPLAY=$DISPLAY -B /tmp/.X11-unix:/tmp/.X11-unix \
  docker://ghcr.io/openrobotics/gazebo:jetty-full gz sim
```

[GPU Documentation](https://docs.sylabs.io/guides/latest/user-guide/gpu.html)

## Troubleshooting

See the [Troubleshooting Guide](TROUBLESHOOTING.md) for step-by-step diagnostics.

## Comparison to osrf/docker_images

This repo is a spiritual fork of [the official OSRF docker images](https://github.com/osrf/docker_images).
The image definitions here were copied and modified from them.
