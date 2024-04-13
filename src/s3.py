class S3:
    
    def __init__(self, s3_client, bucket: str, actions: dict[str]) -> None:
        self.s3_cliente = s3_client
        self.bucket = bucket
        self.actions = actions

    def verificar_hash_s3(self, objeto, hash_local):
        try:
            resposta = self.s3_client.head_object(Bucket=self.bucket, Key=objeto)
            hash_s3 = resposta['Metadata'].get('hash')
            return hash_local == hash_s3
        except self.s3_client.exceptions.NoSuchKey:
            # O objeto não existe no S3
            return False

    def get_s3_objects(self, prefix=''):
        objects_with_hash = {}
        response = self.s3_client.list_objects_v2(Bucket=self.bucket, Prefix=prefix)
        if 'Contents' in response:
            for obj in response['Contents']:
                obj_key = obj['Key']
                if not obj_key.endswith('/'):  # Ignora "pastas"
                    # Supõe que o hash está armazenado nos metadados do objeto
                    meta = self.s3_client.head_object(Bucket=self.bucket, Key=obj_key)
                    obj_hash = meta['Metadata'].get('hash', '')  # Substitua 'filehash' pelo nome real da chave de metadados
                    objects_with_hash[obj_key] = obj_hash
        return objects_with_hash


    def sync_to_s3(self, files):
        """Sincroniza arquivos locais com o bucket S3, fazendo upload de novos arquivos e removendo os obsoletos."""
        for file, metadata in files['upload'].items():
            self.upload_file(self.s3_client, file, metadata)
        for file in files['remove']:
            self.remove_file_from_s3(self.s3_client, file, self.bucket)

    def upload_file(self, filename, metadata):
        """Faz o upload de um arquivo para o S3."""
        key = metadata["virtual_path"]
        try:
            with open(filename, 'rb') as f:
                self.s3_client.upload_fileobj(
                    Fileobj=f,
                    Bucket=self.bucket,
                    Key=key,
                    ExtraArgs={'Metadata': {'hash': metadata["hash"]}}
                )
            print(f"Uploaded {filename} to s3://{self.bucket}/{key}")
            self.actions["Uploaded"].append(key)
        except Exception as e:
            print(f"Failed to upload {filename}: {e}")

    def remove_file_from_s3(self,filename):
        """Remove um arquivo do S3."""
        try:
            self.s3_client.delete_object(Bucket=self.bucket, Key=filename)
            print(f"Removed {filename} from s3://{self.bucket}/{filename}")
            self.actions["Removed"].append(filename)
        except Exception as e:
            print(f"Failed to remove {filename}: {e}")