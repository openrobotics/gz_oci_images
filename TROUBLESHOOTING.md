# Troubleshooting Graphics Acceleration

This guide helps diagnose and fix graphics acceleration issues when running Gazebo in containers.
It covers **Intel** and **NVIDIA** GPUs.
AMD is currently not supported.

> [!NOTE]
> All examples use the Jetty release.
> Replace `jetty-full` with your desired release (e.g., `harmonic-full`, `ionic-full`).

## Quick Diagnostic Checklist

Run these commands **on your host system** (not inside the container) to verify your setup:

### 1. Check Display Access

```bash
echo $DISPLAY
```

You should see something like `:0` or `:1`.
If empty, you may not be running an X11 session.

### 2. Check Your GPU Type

```bash
lspci | grep -i vga
```

This shows your graphics hardware.
Look for "Intel", "NVIDIA", or "AMD" in the output.

### 3. For NVIDIA Users: Verify Driver

```bash
nvidia-smi
```

If this command fails or shows errors, your NVIDIA driver is not properly installed.
You must fix this before GPU acceleration can work in containers.

### 4. Check OpenGL Renderer

```bash
glxinfo | grep "OpenGL renderer"
```

This shows which GPU is rendering graphics.
You should see your GPU name (e.g., "NVIDIA GeForce RTX 3080" or "Mesa Intel").
If you see "llvmpipe" or "software", hardware acceleration is not working.

> [!TIP]
> If `glxinfo` is not installed, run: `sudo apt install mesa-utils`

---

## Understanding gz sim --verbose Output

When Gazebo fails to render, run with verbose output to see what's happening:

```bash
gz sim --verbose
```

Look for these key messages:

| Message | Meaning |
|---------|---------|
| `Unable to create the rendering window` | Display or GPU access problem |
| `Unable to create OpenGL context` | OpenGL/driver issue |
| `Ogre could not find render system` | Missing rendering libraries |
| `X Error` or `GLX` errors | X11 display connection problem |
| `Render engine [ogre2] is not available` | Missing graphics libraries in container |
| `qt.qpa.xcb: could not connect to display` | Container cannot access X11 display (see [Display and X11 Troubleshooting](#display-and-x11-troubleshooting)) |
| `qt.qpa.plugin: Could not load the Qt platform plugin "xcb"` | X11 libraries or display not available (see [Display and X11 Troubleshooting](#display-and-x11-troubleshooting)) |

---

## NVIDIA Troubleshooting

### Problem: nvidia-smi Works on Host but Not in Container

**Symptom:** `nvidia-smi` runs fine on your host, but fails inside the container.

**Solution:** You need to pass the GPU to the container.
Each tool has different flags:

| Tool | Required Flag |
|------|---------------|
| Rocker | `--nvidia` |
| Podman | `--device nvidia.com/gpu=all` |
| nerdctl | `--gpus all` |
| Apptainer | `--nv` |
| SingularityCE | `--nv` |
| Distrobox | `--nvidia` |

**Example with Rocker:**
```bash
rocker --nvidia --x11 ghcr.io/j-rivero/gazebo:jetty-full gz sim --verbose
```

### Problem: NVIDIA Container Toolkit Not Installed

**Symptom:** Error messages like `could not select device driver` or `nvidia-container-cli: initialization error`.

**Solution:** Install the NVIDIA Container Toolkit:

```bash
# Add NVIDIA repository
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg
curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list | \
  sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
  sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list

# Install toolkit
sudo apt update
sudo apt install nvidia-container-toolkit

# Configure Docker (if using Docker/Rocker)
sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart docker
```

### Problem: Driver Update Broke Acceleration

**Symptom:** GPU acceleration worked before, but stopped after a system update.

**Solution:** Reboot your system.
After kernel or driver updates, the running kernel may not match the installed driver.

```bash
sudo reboot
```

After reboot, verify with:
```bash
nvidia-smi
```

### Problem: Driver Version Mismatch

**Symptom:** Container starts but crashes with CUDA or driver errors.

**Cause:** The NVIDIA driver version on your host must be compatible with the container's CUDA libraries.

**Solution:** Update your host driver to the latest version:

```bash
sudo apt update
sudo apt install nvidia-driver-550  # or latest available version
sudo reboot
```

---

## Intel Troubleshooting

### Problem: No Hardware Acceleration

**Symptom:** `glxinfo` shows "llvmpipe" instead of Intel GPU.

**Solution:** Pass the DRI device to the container.

**With Rocker:**
```bash
rocker --x11 --devices /dev/dri ghcr.io/j-rivero/gazebo:jetty-full gz sim --verbose
```

**With Podman:**
```bash
podman run --rm -it \
  --device /dev/dri \
  -e DISPLAY=$DISPLAY \
  -v /tmp/.X11-unix:/tmp/.X11-unix \
  ghcr.io/j-rivero/gazebo:jetty-full \
  gz sim --verbose
```

### Problem: Permission Denied on /dev/dri

**Symptom:** Error accessing `/dev/dri/card0` or `/dev/dri/renderD128`.

**Solution:** Your user needs to be in the `video` and `render` groups:

```bash
# On host system
sudo usermod -aG video $USER
sudo usermod -aG render $USER
```

Log out and log back in for changes to take effect.

---

## Display and X11 Troubleshooting

### Problem: Cannot Open Display

**Symptom:** Error `cannot open display: :0` or similar.

**Cause:** The container cannot connect to your X11 display server.

**Solution 1:** Allow local connections to X server:

```bash
xhost +local:docker
```

Then run your container.
This allows any local user to connect to your display.

> [!WARNING]
> This reduces X11 security.
> For a more secure option, use `xhost +SI:localuser:$USER` instead.

**Solution 2:** Verify X11 socket is mounted.
Most tools need `/tmp/.X11-unix` mounted:

| Tool | X11 Mount |
|------|-----------|
| Rocker | Automatic with `--x11` |
| Podman | `-v /tmp/.X11-unix:/tmp/.X11-unix` |
| nerdctl | `-v /tmp/.X11-unix:/tmp/.X11-unix` |
| Apptainer | `-B /tmp/.X11-unix:/tmp/.X11-unix` |
| SingularityCE | `-B /tmp/.X11-unix:/tmp/.X11-unix` |

**Solution 3:** Verify DISPLAY variable is passed:

```bash
# Check on host
echo $DISPLAY

# Pass to container (example with podman)
podman run -e DISPLAY=$DISPLAY ...
```

### Problem: XDG_RUNTIME_DIR Warning

**Symptom:** Warning about `XDG_RUNTIME_DIR` not set.

**Solution:** Set the variable when running the container:

```bash
-e XDG_RUNTIME_DIR=/tmp
```

---

## Container Tool-Specific Issues

### Rocker

**Problem:** `rocker: command not found`

**Solution:**
```bash
pip install rocker
```

**Problem:** Rocker fails with permission errors

**Solution:** Ensure Docker is configured for rootless access:
```bash
sudo usermod -aG docker $USER
# Log out and back in
```

### Podman

**Problem:** SELinux blocks display access

**Symptom:** Permission denied errors when accessing X11 socket.

**Solution:** Add SELinux label option:
```bash
podman run --rm -it \
  --security-opt=label=disable \
  -e DISPLAY=$DISPLAY \
  -v /tmp/.X11-unix:/tmp/.X11-unix \
  ghcr.io/j-rivero/gazebo:jetty-full \
  gz sim --verbose
```

**Problem:** NVIDIA GPU not detected with Podman

**Solution:** Podman uses CDI (Container Device Interface) for NVIDIA:

```bash
# Generate CDI spec (run once)
sudo nvidia-ctk cdi generate --output=/etc/cdi/nvidia.yaml

# Run with GPU
podman run --rm -it \
  --device nvidia.com/gpu=all \
  --security-opt=label=disable \
  -e DISPLAY=$DISPLAY \
  -v /tmp/.X11-unix:/tmp/.X11-unix \
  ghcr.io/j-rivero/gazebo:jetty-full \
  gz sim --verbose
```

### Apptainer / SingularityCE

**Problem:** GPU not accessible

**Solution:** Use `--nv` flag for NVIDIA:
```bash
apptainer run --nv \
  -B /tmp/.X11-unix:/tmp/.X11-unix \
  --env DISPLAY=$DISPLAY \
  docker://ghcr.io/j-rivero/gazebo:jetty-full \
  gz sim --verbose
```

### Distrobox

**Problem:** Graphics not working in Distrobox

**Solution:** Create the container with NVIDIA support:
```bash
distrobox create --image ghcr.io/j-rivero/gazebo:jetty-full --name gazebo --nvidia
distrobox enter gazebo
gz sim --verbose
```

---

## Software Rendering Fallback

If you cannot get GPU acceleration working, you can run with software rendering as a last resort.
This is slow but can help verify other parts of your setup.

```bash
# Force software rendering
export LIBGL_ALWAYS_SOFTWARE=1
gz sim --verbose
```

> [!WARNING]
> Software rendering is very slow and not recommended for regular use.
> It should only be used for testing.

---

## Diagnostic Commands Summary

Run these inside the container to diagnose issues:

```bash
# Check if GPU is visible (NVIDIA only)
nvidia-smi

# Check OpenGL renderer
glxinfo | grep "OpenGL renderer"

# Check display connection
xdpyinfo | head -5

# List available render devices
ls -la /dev/dri/

# Check Gazebo rendering with verbose output
gz sim --verbose 4
```

---

## Still Having Issues?

If you've tried the solutions above and still have problems:

1. **Check the [Gazebo Community](https://community.gazebosim.org/)** - Search for similar issues or ask a question
2. **Open an issue** in this repository with:
   - Output of `nvidia-smi` (if NVIDIA)
   - Output of `glxinfo | grep "OpenGL renderer"`
   - Full output of `gz sim --verbose`
   - Your container command
   - Your Linux distribution and version
