import os
import boto3
from botocore.exceptions import NoCredentialsError

def list_local_files(local_path):
    """Lista todos os arquivos .pem no diretório local."""
    return [f for f in os.listdir(local_path) if os.path.isfile(os.path.join(local_path, f)) and f.endswith('.pem')]

def list_s3_files(s3_client, bucket_name, prefix=''):
    """Lista todos os arquivos no diretório especificado do bucket S3."""
    s3_files = []
    response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=prefix)
    # Verifica se 'Contents' está na resposta
    if 'Contents' in response:
        for obj in response['Contents']:
            s3_files.append(obj['Key'])
    return s3_files

def upload_files_to_s3(s3_client, files, bucket_name, s3_path, local_path):
    """Faz o upload dos arquivos para o bucket S3."""
    for file in files:
        try:
            s3_client.upload_file(os.path.join(local_path, file), bucket_name, os.path.join(s3_path, file))
            print(f"Uploaded {file} to s3://{bucket_name}/{s3_path}/{file}")
        except NoCredentialsError:
            print("Credentials not available")

def main():
    aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
    aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
    aws_region = os.getenv('AWS_REGION')
    bucket_name = os.getenv('BUCKET_NAME')
    local_path = 'certificates'
    s3_path = os.getenv('TRUSTSTORE')

    # Configura o cliente S3
    s3_client = boto3.client('s3', aws_access_key_id=aws_access_key_id,
                             aws_secret_access_key=aws_secret_access_key, region_name=aws_region)

    local_files = set(list_local_files(local_path))
    s3_files = set([os.path.basename(key) for key in list_s3_files(s3_client, bucket_name, s3_path)])
    new_files = local_files - s3_files

    if new_files:
        upload_files_to_s3(s3_client, new_files, bucket_name, s3_path, local_path)
    else:
        print("No new files to upload.")

if __name__ == "__main__":
    main()
