import os
import boto3

actions = {"Uploaded": [], "Removed": []}

def write_summary_to_file(report_file):
    """Escreve o resumo das ações realizadas em formato de tabela em um arquivo."""

    with open(report_file, "w") as file:

        if not actions["Uploaded"] and not actions["Removed"]:
            file.write("Nenhum arquivo foi adicionado ou removido.\n")
        else:
            # Cabeçalho da Tabela
            file.write(f"{'Ação':<15}{'Nome do Arquivo'}\n")
            file.write(f"{'-'*15}{'-'*50}\n")

            # Linhas para Arquivos Carregados
            for filename in actions["Uploaded"]:
                file.write(f"{'Uploaded':<15}{filename}\n")

            # Linhas para Arquivos Removidos
            for filename in actions["Removed"]:
                file.write(f"{'Removed':<15}{filename}\n")

def find_files(directory, extension):
    """Retorna uma lista de arquivos com a extensão especificada dentro do diretório."""
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
        remove_file_from_s3(s3_client, file, bucket, s3_path)

def upload_file(s3_client, filename, bucket, s3_path, local_dir):
    """Faz o upload de um arquivo para o S3."""
    try:
        full_path = os.path.join(local_dir, filename)
        s3_client.upload_file(full_path, bucket, os.path.join(s3_path, filename))
        print(f"Uploaded {filename} to s3://{bucket}/{s3_path}/{filename}")
        actions["Uploaded"].append(filename)
    except Exception as e:
        print(f"Failed to upload {filename}: {e}")

def remove_file_from_s3(s3_client, filename, bucket, s3_path):
    """Remove um arquivo do S3."""
    try:
        s3_client.delete_object(Bucket=bucket, Key=os.path.join(s3_path, filename))
        print(f"Removed {filename} from s3://{bucket}/{os.path.join(s3_path, filename)}")
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

    report_file = "s3_sync_report.txt"
    write_summary_to_file(report_file)

if __name__ == "__main__":
    main()
