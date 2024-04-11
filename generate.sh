#!/bin/bash

# Verifica se os argumentos corretos foram fornecidos
if [ "$#" -ne 2 ]; then
    echo "Uso: $0 <Common Name> <Diretório de Destino>"
    exit 1
fi

CN=$1
DEST_DIR=$2

# Cria o diretório de destino se ele não existir
mkdir -p "$DEST_DIR"

# Define os nomes de arquivo de saída
KEY_FILE="${DEST_DIR}/${CN}.key"
CERT_FILE="${DEST_DIR}/${CN}.pem"

# Gera uma chave privada
openssl genrsa -out "${KEY_FILE}" 2048

# Gera um pedido de assinatura de certificado (CSR) e um certificado autoassinado
openssl req -new -x509 -key "${KEY_FILE}" -out "${CERT_FILE}" -days 365 -subj "/CN=${CN}"

echo "Chave privada salva em: ${KEY_FILE}"
echo "Certificado salva em: ${CERT_FILE}"
