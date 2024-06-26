#!/bin/bash

# Validate input parameters
if [ "$#" -ne 4 ]; then
    echo "Usage: $0 <Common Name> <Destination Directory> <Extension> <Backup>"
    exit 1
fi

COMMON_NAME=$1
DESTINATION_DIR=$2
EXTENSION=$3
BACKUP=$4

# Make the destination directory if it doesn't exist
mkdir -p "${DESTINATION_DIR}"
mkdir -p "${BACKUP}"

# Define the path to the key and certificate files
KEY_FILE_PATH="${DESTINATION_DIR}/${COMMON_NAME}.key"
CERT_FILE_PATH="${DESTINATION_DIR}/${COMMON_NAME}.${EXTENSION}"

# Generate a new private key
openssl genrsa -out "${KEY_FILE_PATH}" 2048

# Create a self-signed x509 certificate
openssl req -new -x509 -key "${KEY_FILE_PATH}" -out "${CERT_FILE_PATH}" -days 365 -subj "/CN=${COMMON_NAME}"

# Backup
cp "${CERT_FILE_PATH}" "${BACKUP}/"
cp "${KEY_FILE_PATH}" "${BACKUP}/"

# Delete the private key
rm "${KEY_FILE_PATH}"

# Inform the user that the certificate has been saved
echo "Certificate saved at: ${CERT_FILE_PATH}"