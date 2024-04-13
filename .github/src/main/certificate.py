from file import Device
from info import FileInfo
from s3 import S3


class Certificate:
    """
    A class for managing certificate files.

    Parameters:
        s3 (S3): The S3 object for interacting with Amazon S3.
        device (Device): The device object for interacting with the device.

    Attributes:
        s3 (S3): The S3 object for interacting with Amazon S3.
        device (Device): The device object for interacting with the device.

    Methods:
        upload_certificates: Uploads the certificates to S3.
        _sync_files: Synchronizes the local files with S3.
        _manage_files: Manages the modified and missing files.
        _find_missing_files: Finds the missing files.
        _detect_modified_files: Detects the modified files.
    """

    def __init__(self, s3: S3, device: Device):
        self.s3 = s3
        self.device = device

    def upload_certificates(self, keystore_folder: str, truststore_folder: str):
        """
        Uploads certificates from the provided keystore and truststore folders.

        :param keystore_folder: The path to the folder containing keystore files.
        :param truststore_folder: The path to the folder containing truststore files.
        """
        self._sync_files(file_extension='.crt', folder=keystore_folder)
        self._sync_files(file_extension='.pem', folder=truststore_folder)

    def _sync_files(self, file_extension: str, folder: str = ''):
        """

        Syncs files between local device and AWS S3.

        :param file_extension: The file extension to filter for synchronization.
        :param folder: Optional. The folder path to synchronize. Defaults to root directory.

        :return: None

        """
        local_files: dict[str, FileInfo] = self.device.find_files(file_extension, folder=folder)

        s3_files: dict[str, str] = self.s3.get_hashed_s3_objects(folder)

        modified_files: dict[str, FileInfo] = self._detect_modified_files(local_files, s3_files)

        missing_files: set[str] = self._find_missing_files(local_files, s3_files)

        self._manage_files(modified_files=modified_files, missing_files=missing_files)

    def _manage_files(self, modified_files: dict[str, FileInfo], missing_files: set[str]):
        for filename, info in modified_files.items():
            self.s3.upload_to_bucket(filename, info)
        for filename in missing_files:
            self.s3.delete_object(filename)

    @staticmethod
    def _find_missing_files(local_files: dict[str, FileInfo], s3_files: dict[str, str]) -> set[str]:
        local_virtual_paths: set[str] = {info.virtual_path for info in local_files.values()}
        return {object_name for object_name in s3_files if object_name not in local_virtual_paths}

    @staticmethod
    def _detect_modified_files(local_files: dict[str, FileInfo], s3_files: dict[str, str]) -> dict[str, FileInfo]:
        modified_files: dict[str, FileInfo] = {}
        for object_name, metadata in local_files.items():
            if metadata.virtual_path not in s3_files or not metadata.is_file_hash_match(
                    s3_files[metadata.virtual_path]):
                modified_files[object_name] = metadata
        return modified_files
