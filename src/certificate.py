from file import Device
from s3 import S3

class Certificate:

    def __init__(self, s3: S3, device: Device) -> None:
        self.s3 = s3
        self.device = device

    def sincronizar(self, s3_tls_folder: str, s3_truststore_folder: str):

        self.__upload_certificates(extension='.crt', s3_prefix=s3_tls_folder)

        self.__upload_certificates(extension='.pem', s3_prefix=s3_truststore_folder)

    def __upload_certificates(self, extension, s3_prefix=''):

        local_files = self.device.find_files(extension, folder=s3_prefix)

        s3_files = self.s3.get_s3_objects(s3_prefix)
    
        files_to_sync = {
                'upload': self.__uploading(local_files, s3_files),
                'remove': self.__removing(local_files, s3_files)
        }

        self.s3.sync_to_s3(files_to_sync)

    def __removing(self, local_files, s3_files):
        # Constrói um conjunto de 'virtual_path' a partir de 'local_files'
        local_virtual_paths = {metadata["virtual_path"] for metadata in local_files.values()}
        
        # Retorna um conjunto de nomes de arquivos em 's3_files' que não possuem correspondência em 'local_virtual_paths'
        return {fname for fname in s3_files if fname not in local_virtual_paths}

    def __uploading(self, local_files, s3_files):
        """
        Retorna um dicionário de arquivos locais marcados para upload, baseado na inexistência
        ou diferença de hash entre os arquivos locais e os do S3.
        """
        return {
            fname: metadata for fname, metadata in local_files.items()
            if metadata["virtual_path"] not in s3_files or metadata["hash"] != s3_files.get(metadata["virtual_path"], "")
        }
