import argparse
import os
from argparse import Namespace, ArgumentParser
from typing import Any

import boto3

from certificate import Certificate
from file import Device
from s3 import S3


def parse_args():
    parser: ArgumentParser = argparse.ArgumentParser(description="Synchronizes .pem certificates with an S3 bucket.")
    parser.add_argument('country', type=str, help='Country')
    parser.add_argument('environment', type=str, help='Environment')
    return parser.parse_args()


def main():
    """
    Main Method Documentation

    This method is the main entry point for the application. It performs the following tasks:

      1. Parses the input arguments.
      2. Initializes a dictionary to track "Uploaded" and "Removed" actions.
      3. Creates an S3 object with a specified S3 client, bucket name, and actions dictionary.
      4. Creates a Device object with the actions dictionary and a specified path.
      5. Creates a Certificate object with the S3 object and the Device object.
      6. Calls the `upload_certificates` method of the Certificate object, passing the TLS and truststore folder paths.
      7. Calls the `write_summary_to_file` method of the Device object, specifying the file name for the summary.

    Returns:
        None
    """
    input_args: Namespace = parse_args()

    actions: dict[str, list[Any]] = {"Uploaded": [], "Removed": []}

    s3: S3 = S3(s3_client=boto3.client('s3', region_name=os.getenv('AWS_REGION')), bucket_name=os.getenv('BUCKET_NAME'),
                actions=actions)

    device: Device = Device(actions=actions,
                            path=os.path.join("env", input_args.country, input_args.environment, "certificates"))

    certificate: Certificate = Certificate(s3=s3, device=device)

    certificate.upload_certificates(keystore_folder=os.getenv('TLS'), truststore_folder=os.getenv('TRUSTSTORE'))

    device.write_summary_to_file("s3_sync_report.md")


if __name__ == "__main__":
    main()
