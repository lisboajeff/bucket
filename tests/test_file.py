import os
import unittest
import hashlib
from src.file import Device


class FileInfo:
    def __init__(self, file_hash, file_path):
        self.file_hash = file_hash
        self.file_path = file_path


class TestDevice(unittest.TestCase):

    def setUp(self):
        self.actions = {"Uploaded": ["file1.jpg", "file2.jpg"], "Removed": ["file3.jpg"]}
        self.device = Device(self.actions, "path")

    def test_format_summary(self):
        summary = self.device._format_summary()
        expected_summary = ["| Action     | File Name |",
                            "|------------|-----------------|",
                            "| Uploaded    | file1.jpg |",
                            "| Uploaded    | file2.jpg |",
                            "| Removed     | file3.jpg |"]
        self.assertEqual(summary, expected_summary)

    def test_format_summary_no_actions(self):
        self.device.actions = {"Uploaded": [], "Removed": []}
        summary = self.device._format_summary()
        expected_summary = ["No file was added or removed."]
        self.assertEqual(summary, expected_summary)

    def test_determine_sha256_hash(self):
        # create a temporary file to test
        with open("temp_file", "w") as f:
            f.write("This is a temporary file for testing.")
        actual_hash = self.device._determine_sha256_hash(full_path="temp_file")
        with open("temp_file", "rb") as f:
            sha_hash = hashlib.sha256()
            for byte_block in iter(lambda: f.read(4096), b""):
                sha_hash.update(byte_block)
        expected_hash = sha_hash.hexdigest()
        self.assertEqual(actual_hash, expected_hash)
        os.remove("temp_file")

    def test_find_files(self):
        os.makedirs("path/folder", exist_ok=True)
        with open("path/folder/test.txt", "w") as f:
            f.write("Test text file.")
        files_with_hash = self.device.find_files(file_extension=".txt", folder="folder")
        self.assertEqual(len(files_with_hash), 1)
        os.remove("path/folder/test.txt")
        os.rmdir("path/folder")

    def test_find_files_no_files(self):
        files_with_hash = self.device.find_files(file_extension=".txt", folder="folder")
        self.assertEqual(files_with_hash, {})


if __name__ == '__main__':
    unittest.main()
