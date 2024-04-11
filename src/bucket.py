import os
import boto3

actions = {"Uploaded": [], "Removed": []}

def write_summary_to_file(report_file):
    """Escreve o resumo das ações em formato Markdown."""
    lines = []
    if not actions["Uploaded"] and not actions["Removed"]:
        lines.append("Nenhum arquivo foi adicionado ou removido.")
    else:
        lines.append("| Ação       | Nome do Arquivo |")
        lines.append("|------------|-----------------|")
        for filename in actions["Uploaded"]:
            lines.append(f"| Uploaded    | {filename} |")
        for filename in actions["Removed"]:
            lines.append(f"| Removed     | {filename} |")

    with open(report_file, "w") as file:
        file.write("\n".join(lines))

def find_files(directory, extension):
    """Retorna uma lista de arquivos com a extensão especificada dentro do diretório."""
    if not os.path.exists(directory) or not os.listdir(directory):
        return []
    # Lista todos os arquivos no diretório que correspondem à extensão especificada
    return [f for f in os.listdir(directory) if f.endswith(extension) and os.path.isfile(os.path.join(directory, f))]

def get_s3_objects(s3_client, bucket, prefix=''):
    """Retorna uma lista de objetos dentro do bucket e prefixo especificado."""
    objects = []
    response = s3_client.list_objects_v2(Bucket=bucket, Prefix=prefix)
    if 'Contents' in response:
        objects = [obj['Key'] for obj in response['Contents']]
    return objects

def sync_to_s3(s3_client, files, bucket, s3_path, local_dir):
    """Sincroniza arquivos locais com o bucket S3, fazendo upload de novos arquivos e removendo os obsoletos."""
    for file in files['upload']:
        upload_file(s3_client, file, bucket, s3_path, local_dir)
    for file in files['remove']:
        remove_file_from_s3(s3_client, file, bucket)

def upload_file(s3_client, filename, bucket, s3_path, local_dir):
    """Faz o upload de um arquivo para o S3."""
    try:
        full_path = os.path.join(local_dir, filename)
        s3_client.upload_file(full_path, bucket, os.path.join(s3_path, filename))
        print(f"Uploaded {filename} to s3://{bucket}/{s3_path}/{filename}")
        actions["Uploaded"].append(filename)
    except Exception as e:
        print(f"Failed to upload {filename}: {e}")

def remove_file_from_s3(s3_client, filename, bucket):
    """Remove um arquivo do S3."""
    try:
        s3_client.delete_object(Bucket=bucket, Key=filename)
        print(f"Removed {filename} from s3://{bucket}/{filename}")
        actions["Removed"].append(filename)
    except Exception as e:
        print(f"Failed to remove {filename}: {e}")

def main():
    aws_region = os.getenv('AWS_REGION')
    bucket_name = os.getenv('BUCKET_NAME')
    local_path = 'certificates'
    s3_path = os.getenv('TRUSTSTORE')

    s3_client = boto3.client('s3', region_name=aws_region)
    local_files = set(find_files(local_path, '.pem'))
    s3_files = set(get_s3_objects(s3_client, bucket_name, s3_path))

    files_to_sync = {
        'upload': local_files - s3_files,
        'remove': s3_files - local_files
    }

    sync_to_s3(s3_client, files_to_sync, bucket_name, s3_path, local_path)

    report_file = "s3_sync_report.md"
    write_summary_to_file(report_file)

if __name__ == "__main__":
    main()
