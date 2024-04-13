#!/bin/bash

# Verifica se o comando python3 está disponível
if ! command -v python3 &> /dev/null; then
    echo "Python 3 não está instalado. Instale o Python 3 para continuar."
    exit 1
fi

# Verifica se os argumentos necessários foram fornecidos
if [ "$#" -ne 2 ]; then
    echo "Uso: $0 <PAIS> <AMBIENTE>"
    exit 1
fi

PAIS=$1

AMBIENTE=$2

# Caminho para o arquivo de configuração
CONFIG_PATH="env/$PAIS/$AMBIENTE/config.env"

# Verifica se o arquivo de configuração existe
if [ ! -f "$CONFIG_PATH" ]; then
    echo "Arquivo de configuração não encontrado: $CONFIG_PATH"
    exit 1
fi

VENV="/tmp/python_bucket_ambiente"

# Cria um ambiente virtual chamado 'local' se ele não existir
if [ ! -d "$VENV" ]; then
    python3 -m venv "$VENV"
    echo "Ambiente virtual '$VENV' criado."
else
    echo "O ambiente virtual '$VENV' já existe."
fi

# Ativa o ambiente virtual
source "$VENV/bin/activate"

# Instala as dependências do arquivo requirements.txt
if [ ! -f "src/requirements.txt" ]; then
    echo "Arquivo requirements.txt não encontrado."
    exit 1
else
    pip install -r src/requirements.txt
fi

# Carrega as variáveis de ambiente do arquivo CONFIG
set -a # Automaticamente exporta variáveis
source "$CONFIG_PATH"
set +a # Desativa a exportação automática

# Executa o script Python
python3 src/bucket.py $PAIS $AMBIENTE
