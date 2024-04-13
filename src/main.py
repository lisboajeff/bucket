import argparse
import os
from certificate import Certificate
from file import Device
from s3 import S3
import boto3

def main(certificate: Certificate, device: Device):
    
    certificate.sincronizar(s3_tls_folder=os.getenv('TLS'), s3_truststore_folder=os.getenv('TRUSTSTORE'))

    device.write_summary_to_file("s3_sync_report.md")

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Sincroniza certificados .pem com um bucket S3.')
    parser.add_argument('pais', type=str, help='Pais')
    parser.add_argument('ambiente', type=str, help='Ambiente')
    argumentos = parser.parse_args()
    
    actions = {"Uploaded": [], "Removed": []}    

    s3 = S3(s3_client=boto3.client('s3', region_name=os.getenv('AWS_REGION')), bucket=os.getenv('BUCKET_NAME'),actions=actions)

    device = Device(actions=actions, path= f'env/{argumentos.pais}/{argumentos.ambiente}/certificates')

    certificate = Certificate(s3=s3, device=device)

    main(certificate, device)
