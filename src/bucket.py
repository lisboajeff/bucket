import os
import boto3
import argparse

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

def find_files(directory, extension, s3_folder=''):
    """
    Retorna uma lista de arquivos com a extensão especificada dentro do diretório, 
    concatenados com uma pasta do bucket especificada.
    
    :param directory: Diretório local onde os arquivos serão procurados.
    :param extension: Extensão dos arquivos a serem listados.
    :param s3_folder: Pasta dentro do bucket S3 onde os arquivos deverão ser colocados. 
                      Este parâmetro é opcional.
    :return: Lista de caminhos completos dos arquivos para upload no S3.
    """

    path=f'{directory}/{s3_folder}'

    # print(path)

    if not os.path.exists(path) or not os.listdir(path):
        return []
    
    # Lista todos os arquivos no diretório que correspondem à extensão especificada
    files = [f for f in os.listdir(path) if f.endswith(extension) and os.path.isfile(os.path.join(path, f))]
        
    # Se uma pasta do S3 foi especificada, concatena essa pasta com o nome do arquivo
    if s3_folder:
        return [os.path.join(s3_folder, f) for f in files]
    else:
        return files

def get_s3_objects(s3_client, bucket, prefix=''):
    """Retorna uma lista de objetos dentro do bucket e prefixo especificado,
       excluindo chaves que representam 'pastas'."""
    objects = []
    response = s3_client.list_objects_v2(Bucket=bucket, Prefix=prefix)
    if 'Contents' in response:
        # Filtra os objetos para excluir chaves que terminam com '/'
        objects = [obj['Key'] for obj in response['Contents'] if not obj['Key'].endswith('/')]
    return objects

def sync_to_s3(s3_client, files, bucket, local_path):
    """Sincroniza arquivos locais com o bucket S3, fazendo upload de novos arquivos e removendo os obsoletos."""
    for file in files['upload']:
        upload_file(s3_client, file, bucket, local_path)
    for file in files['remove']:
        remove_file_from_s3(s3_client, file, bucket)

def upload_file(s3_client, filename, bucket, local_path):
    """Faz o upload de um arquivo para o S3."""
    try:
        full_path = os.path.join(local_path, filename)
        s3_client.upload_file(full_path, bucket, filename)
        print(f"Uploaded {filename} to s3://{bucket}/{filename}")
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

def args():
    parser = argparse.ArgumentParser(description='Sincroniza certificados .pem com um bucket S3.')
    parser.add_argument('pais', type=str, help='Pais')
    parser.add_argument('ambiente', type=str, help='Ambiente')
    return parser.parse_args()

def upload_certificates(s3_client, bucket_name, local_path, extension, s3_prefix=''):
    local_files = set(find_files(local_path, extension, s3_folder=s3_prefix))
    s3_files = set(get_s3_objects(s3_client, bucket_name, s3_prefix))
    # print(local_files)
    # print(s3_files)
    files_to_sync = {
            'upload': local_files - s3_files,
            'remove': s3_files - local_files
        }

    sync_to_s3(s3_client, files_to_sync, bucket_name, local_path)

def main():
    
    argumentos = args()
    
    local_path = f'env/{argumentos.pais}/{argumentos.ambiente}/certificates'

    aws_region = os.getenv('AWS_REGION')
    bucket_name = os.getenv('BUCKET_NAME')
    s3_truststore = os.getenv('TRUSTSTORE')
    s3_tls= os.getenv('TLS')

    s3_client = boto3.client('s3', region_name=aws_region)

    upload_certificates(s3_client=s3_client, bucket_name=bucket_name, local_path=local_path, extension='.crt', s3_prefix=s3_tls)

    upload_certificates(s3_client=s3_client, bucket_name=bucket_name, local_path=local_path, extension='.pem', s3_prefix=s3_truststore)

    report_file = "s3_sync_report.md"

    write_summary_to_file(report_file)

if __name__ == "__main__":
    main()
