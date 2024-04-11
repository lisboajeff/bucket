import os
import boto3
import argparse
import hashlib

actions = {"Uploaded": [], "Removed": []}

def args():
    parser = argparse.ArgumentParser(description='Sincroniza certificados .pem com um bucket S3.')
    parser.add_argument('pais', type=str, help='Pais')
    parser.add_argument('ambiente', type=str, help='Ambiente')
    return parser.parse_args()

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

def calcular_hash_arquivo(full_path):
    sha256_hash = hashlib.sha256()
    with open(full_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def find_files(directory, extension, folder=''):
   
    path=f'{directory}/{folder}'

    files_with_hash = {}

    if not os.path.exists(path) or not os.listdir(path):
        return files_with_hash
    
    for f in os.listdir(path):
        if f.endswith(extension) and os.path.isfile(os.path.join(path, f)):
            full_path = os.path.join(path, f)
            file_hash = calcular_hash_arquivo(full_path)
            # Use o caminho relativo do arquivo como chave para evitar conflitos de nome
            files_with_hash[full_path] = {'hash': file_hash, 'virtual_path': f'{folder}/{os.path.basename(full_path)}'}

    return files_with_hash
    
def verificar_hash_s3(s3_client, bucket, objeto, hash_local):
    try:
        resposta = s3_client.head_object(Bucket=bucket, Key=objeto)
        hash_s3 = resposta['Metadata'].get('hash')
        return hash_local == hash_s3
    except s3_client.exceptions.NoSuchKey:
        # O objeto não existe no S3
        return False

def get_s3_objects(s3_client, bucket, prefix=''):
    objects_with_hash = {}
    response = s3_client.list_objects_v2(Bucket=bucket, Prefix=prefix)
    if 'Contents' in response:
        for obj in response['Contents']:
            obj_key = obj['Key']
            if not obj_key.endswith('/'):  # Ignora "pastas"
                # Supõe que o hash está armazenado nos metadados do objeto
                meta = s3_client.head_object(Bucket=bucket, Key=obj_key)
                obj_hash = meta['Metadata'].get('hash', '')  # Substitua 'filehash' pelo nome real da chave de metadados
                objects_with_hash[obj_key] = obj_hash
    return objects_with_hash


def sync_to_s3(s3_client, files, bucket):
    """Sincroniza arquivos locais com o bucket S3, fazendo upload de novos arquivos e removendo os obsoletos."""
    for file, metadata in files['upload'].items():
        upload_file(s3_client, file, bucket, metadata)
    for file in files['remove']:
        remove_file_from_s3(s3_client, file, bucket)

def upload_file(s3_client, filename, bucket, metadata):
    """Faz o upload de um arquivo para o S3."""
    key = metadata["virtual_path"]
    try:
        with open(filename, 'rb') as f:
            s3_client.upload_fileobj(
                Fileobj=f,
                Bucket=bucket,
                Key=key,
                ExtraArgs={'Metadata': {'hash': metadata["hash"]}}
            )
        print(f"Uploaded {filename} to s3://{bucket}/{key}")
        actions["Uploaded"].append(key)
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

def upload_certificates(s3_client, bucket_name, local_path, extension, s3_prefix=''):

    local_files = find_files(local_path, extension, folder=s3_prefix)

    s3_files = get_s3_objects(s3_client, bucket_name, s3_prefix)
 
    files_to_sync = {
            'upload': uploading(local_files, s3_files),
            'remove': removing(local_files, s3_files)
    }

    sync_to_s3(s3_client, files_to_sync, bucket_name)

def removing(local_files, s3_files):
    # Constrói um conjunto de 'virtual_path' a partir de 'local_files'
    local_virtual_paths = {metadata["virtual_path"] for metadata in local_files.values()}
    
    # Retorna um conjunto de nomes de arquivos em 's3_files' que não possuem correspondência em 'local_virtual_paths'
    return {fname for fname in s3_files if fname not in local_virtual_paths}

def uploading(local_files, s3_files):
    """
    Retorna um dicionário de arquivos locais marcados para upload, baseado na inexistência
    ou diferença de hash entre os arquivos locais e os do S3.
    """
    return {
        fname: metadata for fname, metadata in local_files.items()
        if metadata["virtual_path"] not in s3_files or metadata["hash"] != s3_files.get(metadata["virtual_path"], "")
    }

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
