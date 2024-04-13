import os

import boto3

from certificate import Certificate
from file import Device
from info import FileInfo
from s3 import S3


def main():
    aws_region: str = os.getenv('AWS_REGION')

    bucket_name: str = os.getenv('BUCKET_NAME')

    country: str = os.getenv('COUNTRY')

    environment: str = os.getenv('ENVIRONMENT')

    path_to_certificate: str = os.getenv('PATH_TO_CERTIFICATE')

    actions: dict[str, list[FileInfo]] = {"Uploaded": [], "Removed": []}

    s3: S3 = S3(s3_client=boto3.client('s3', region_name=aws_region), bucket_name=bucket_name,
                actions=actions)

    device: Device = Device(actions=actions, path=path_to_certificate, country=country, environment=environment)

    certificate: Certificate = Certificate(s3=s3, device=device)

    certificate.upload_certificates(keystore_folder=os.getenv('TLS'), truststore_folder=os.getenv('TRUSTSTORE'))

    device.write_summary_to_file("s3_sync_report.md")


if __name__ == "__main__":
    main()
