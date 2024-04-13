#!/bin/bash

# Primeiro argumento: Caminho para o arquivo .env
ENV_FILE=$1

if [ ! -f "$ENV_FILE" ]; then
    echo "Arquivo .env não encontrado: $ENV_FILE"
    exit 1
fi

while IFS= read -r line || [[ -n "$line" ]]; do
    # Ignora linhas vazias e comentários
    if [[ $line = \#* ]] || [ -z "$line" ]; then
        continue
    fi
    echo "$line" >>$GITHUB_ENV
done <"$ENV_FILE"
