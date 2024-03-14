#!/bin/bash

source_directory="$1"  

if [ -z "$source_directory" ]; then
    echo "Usage: $0 <source_directory>"
    exit 1
fi

echo "Total size of $source_directory: $(du -sh $source_directory | awk '{print $1}')" # Print total size of source directory
subdirectories=$(find "$source_directory" -mindepth 1 -maxdepth 1 -type d -exec du -sh {} + | awk '$1 ~ /^[0-9]+(\.[0-9]+)?[GT]/' | sort -rh)

# Print the number of subdirectories with numbered choices in order of their size
echo "Number of subdirectories in $source_directory with 50 GB or more in order of their size:"
numbered=1
while read -r size path; do
    echo "[$numbered] $size - $path"
    ((numbered++))
done <<< "$subdirectories"

read -p "Choose a subdirectory: " choice

if [[ $choice =~ ^[0-9]+$ && $choice -ge 1 && $choice -le $numbered ]]; then
    selected_subdirectory=$(echo "$subdirectories" | sed -n "${choice}p" | awk '{print $2}')
    echo "You selected subdirectory: $selected_subdirectory"
else
    echo "Invalid choice. Please enter a valid number."
fi

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

    # Check if data/filterbank folder exists, if not create it
    destination_directory="$selected_drive/data/filterbanks"
    if [ ! -d "$destination_directory" ]; then
        echo "Creating data/filterbanks folder in $selected_drive"
        sudo mkdir -p "$destination_directory"
        echo "Folder created successfully."
    else
        echo "data/filterbanks folder already exists in $selected_drive."
    fi

    log_file="$source_directory/filterbank-transfer-$(date +%Y%m%d_%H%M%S).log"

    # Use rsync to move .zst files while preserving directory structure
    rsync -a --progress --remove-source-files --include='*/' --include='*.fil' --exclude='*.sh' "$selected_subdirectory" "$destination_directory" | tee "$log_file"

    # Remove any folders that are empty
    find "$destination_directory" -type d -empty -delete
else
    echo "Invalid choice. Please enter a valid number."
fi
