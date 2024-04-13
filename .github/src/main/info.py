class FileInfo:

    def __init__(self, file_hash: str, virtual_path: str, file_hash_old: str | None = None):
        self._file_hash_old: str | None = file_hash_old
        self._file_hash: str = file_hash
        self._virtual_path: str = virtual_path

    def is_file_hash_match(self, file_hash: str) -> bool:
        return self._file_hash == file_hash

    def get_path(self) -> str:
        return self._virtual_path

    def get_old_hash(self) -> str:
        return self._file_hash_old

    def get_hash(self) -> str:
        return self._file_hash

    def print_hash(self) -> str:
        return f'{self._file_hash_old} --> {self._file_hash}'

    def has_old_file_hash(self) -> bool:
        return self._file_hash_old is not None
