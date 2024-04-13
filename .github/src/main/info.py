class FileInfo:

    def __init__(self, file_hash: str, virtual_path: str):
        self.file_hash: str = file_hash
        self.virtual_path: str = virtual_path

    def is_file_hash_match(self, file_hash: str) -> bool:
        return self.file_hash == file_hash
