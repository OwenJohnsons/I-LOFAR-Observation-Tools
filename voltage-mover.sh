#!/bin/bash

source_directory="/mnt/ucc1_recording2/data/observations"

# Get list of mounted drives with more than 1 TB 
drives=$(df -h | awk '$4 ~ /^[1-9][0-9]*\.[0-9]+T/ || $4 ~ /^[0-9]+T/' | grep -vE '^Filesystem|tmpfs|cdrom' | awk '{print $6}')
space=$(df -h | awk '$4 ~ /^[1-9][0-9]*\.[0-9]+T/ || $4 ~ /^[0-9]+T/' | grep -vE '^Filesystem|tmpfs|cdrom' | awk '{print $4}')  

numbered=1
echo "Available drives with more than 1 TB of space:"
for drive in $drives; do
    space_value=$(echo "$space" | sed -n "${numbered}p")
    echo "[$numbered] - $drive - $space_value"
    ((numbered++))
done

read -p "Choose a drive: " choice

if [[ $choice =~ ^[0-9]+$ && $choice -ge 1 && $choice -le $numbered ]]; then
    selected_drive=$(echo "$drives" | sed -n "${choice}p")
    selected_space=$(echo "$space" | sed -n "${choice}p")
    echo "You selected drive: $selected_drive with available space: $selected_space"
    
    # Check if data/observations folder exists, if not create it
    if [ ! -d "$selected_drive/data/observations" ]; then
        echo "Creating data/observations folder in $selected_drive"
        sudo mkdir -p "$selected_drive/data/observations"
        echo "Folder created successfully."
    else
        echo "data/observations folder already exists in $selected_drive."
    fi
else
    echo "Invalid choice. Please enter a valid number."
fi

destination_directory="$selected_drive/data/observations"

# Use rsync to move .zst files while preserving directory structure
rsync -a --progress --remove-source-files --include='*/' --include='*.zst' --exclude='*' "$source_directory" "$destination_directory"
