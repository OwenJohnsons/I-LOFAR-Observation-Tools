#!/bin/bash

# Directory containing the files
directory="./"

# Loop through each file in the directory
for file in "$directory"/*; do
    date=$(echo "$file" | grep -oE '[0-9]{4}-[0-9]{2}-[0-9]{2}')

    if [ -n "$date" ]; then
        # Create the directory if it doesn't exist
        mkdir -p "$directory/$date"

        # Move the file to the respective directory
        mv "$file" "$directory/$date/"
    fi
done
