class FileInfo:

    def __init__(self, file_hash: str, file_path: str):
        self.file_hash: str = file_hash
        self.file_path: str = file_path

    def is_file_hash_match(self, file_hash: str) -> bool:
        return self.file_hash == file_hash
