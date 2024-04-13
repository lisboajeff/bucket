import hashlib
import os

from src.info import FileInfo


class Device:
    """
    Class representing a device.

    Attributes:
        actions (dict): A dictionary representing the actions performed on files.
        path (str): A string representing the path of the device.

    Methods:
        _format_summary: Formats the summary of actions performed on files.
        write_summary_to_file: Writes the summary of actions to a file.
        _determine_sha256_hash: Determines the SHA256 hash of a given file.
        find_files: Finds files with a specific file extension in a specified folder.

    """

    def __init__(self, actions: dict[str, list], path: str) -> None:
        self.actions = actions
        self.path = path

    def _format_summary(self):
        lines: list[str] = []
        if not self.actions["Uploaded"] and not self.actions["Removed"]:
            lines.append("No file was added or removed.")
        else:
            lines.append("| Action     | File Name |")
            lines.append("|------------|-----------------|")
            for filename in self.actions["Uploaded"]:
                lines.append(f"| Uploaded    | {filename} |")
            for filename in self.actions["Removed"]:
                lines.append(f"| Removed     | {filename} |")
        return lines

    def write_summary_to_file(self, summary_file: str):
        lines = self._format_summary()
        with open(summary_file, "w") as file:
            file.write("\n".join(lines))

    @staticmethod
    def _determine_sha256_hash(full_path: str):
        sha256_hash = hashlib.sha256()
        with open(full_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

    def find_files(self, file_extension: str, folder: str = ''):
        path: str = f'{self.path}/{folder}'
        files_with_hash: dict[str, FileInfo] = {}
        if not os.path.exists(path) or not os.listdir(path):
            return files_with_hash
        for f in os.listdir(path):
            full_path: str = os.path.join(path, f)
            if f.endswith(file_extension) and os.path.isfile(full_path):
                file_hash = self._determine_sha256_hash(full_path)
                files_with_hash[full_path] = FileInfo(file_hash=file_hash,
                                                      file_path=f'{folder}/{os.path.basename(full_path)}')
        return files_with_hash
