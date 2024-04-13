# Project

[![Deploy Certificates to S3](https://github.com/lisboajeff/bucket/actions/workflows/update_bucket.yml/badge.svg)](https://github.com/lisboajeff/bucket/actions/workflows/update_bucket.yml)

# Synchronization of Certificates with S3

## Description

The script `bucket.py` is a command-line tool developed to automate the process of synchronizing `.pem` and `.crt`
certificates with an AWS S3 bucket. Essential for maintaining the security and integrity of communications in
distributed infrastructures, this script ensures that necessary certificates are always up-to-date and accessible in the
AWS environment.

## Features

- **Automated Synchronization:** Compares local certificates with those stored in S3, performing uploads or removals as
  necessary to maintain synchronization.
- **Report Generation:** Creates a report in Markdown format (`s3_sync_report.md`) detailing the actions performed
  during synchronization, including which files were added or removed.
- **Verification Hash:** Uses SHA-256 hash to verify the integrity of the files and determine the need for
  synchronization.
- **Usage Flexibility:** Allows the specification of different environments and countries for certificate
  synchronization, enhancing applicability in multi-regional scenarios.

## Prerequisites

To use this script, you must have installed:

- Python 3
- Boto3 (AWS SDK for Python)

Additionally, AWS credentials (AWS Access Key ID and AWS Secret Access Key) must be configured, preferably through the
AWS CLI or an AWS configuration file.

## How to Use

1. **Environment Configuration:**
   Ensure that the environment variables `AWS_REGION`, `BUCKET_NAME`, `TRUSTSTORE`, and `TLS` are properly configured to
   reflect your AWS infrastructure.

2. **To execute the script, use the following command:**

```bash
COUNTRY="Brazil"
ENVIRONMENT="DEV"
CERTIFICATE="env/$COUNTRY/$ENVIRONMENT/certificates"
bash src/generate_certificate.sh "projeto.corp" $CERTIFICATE/ssl "crt"
bash src/generate_certificate.sh "client" $CERTIFICATE/truststore "pem"
bash src/local.sh "$COUNTRY" "$ENVIRONMENT"
rm s3_sync_report.md
```