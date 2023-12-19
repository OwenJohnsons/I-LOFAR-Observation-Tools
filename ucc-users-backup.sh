#!/bin/bash

backup_dir="backup-files"

# Check if the backup directory exists, create it if necessary
if [ ! -d "$backup_dir" ]; then
  sudo mkdir -p "$backup_dir"
fi

# Backup /etc/passwd
sudo cp /etc/passwd "$backup_dir/passwd.backup"

# Backup /etc/shadow
sudo cp /etc/shadow "$backup_dir/shadow.backup"

# Backup /etc/group
sudo cp /etc/group "$backup_dir/group.backup"

# Backup home directories 
sudo tar czvf "$backup_dir/obs_home_backup.tar.gz" /home

# User to be excluded
exclude_user="obs"

# Iterate over all user home directories and backup individual user data
for user_home in /home/*; do
  if [ -d "$user_home" ]; then
    user=$(basename "$user_home")
    
    # Check if the current user is not the one to be excluded
    if [ "$user" != "$exclude_user" ]; then
      # Exclude .txt and other specified files from the backup
      sudo tar czvf "$backup_dir/${user}_backup.tar.gz" --exclude='*.fil' --exclude='*.zst' -C /home "$user"
    fi
  fi
done

echo "Backup completed successfully."
