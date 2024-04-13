#!/bin/bash

ENV_FILE=$1

if [ ! -f "$ENV_FILE" ]; then
    echo "File .env not found: $ENV_FILE"
    exit 1
fi

while IFS= read -r line || [[ -n "$line" ]]; do
    if [[ $line = \#* ]] || [ -z "$line" ]; then
        continue
    fi
    echo "$line" >> "$GITHUB_ENV"
done <"$ENV_FILE"
