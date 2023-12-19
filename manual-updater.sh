#!/bin/bash

# List of packages to install
packages=(
    "libpulse-mainloop-glib0"
    "libpulse0"
    "libpulsedsp"
    "linux-headers-generic"
    "linux-signed-generic"
    "linux-signed-image-generic"
    "nvidia-container-toolkit"
    "pulseaudio"
    "pulseaudio-module-x11"
    "pulseaudio-utils"
    "update-notifier-common"
)

# Install each package
for package in "${packages[@]}"; do
    sudo apt-get install -y "$package"
done

echo "All packages installed successfully!"
