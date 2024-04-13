import unittest
from unittest.mock import Mock

from src.certificate import Certificate


class TestCertificate(unittest.TestCase):
    def setUp(self):
        self.s3 = Mock()
        self.device = Mock()
        self.certificate = Certificate(self.s3, self.device)
        self.s3.upload_to_bucket = Mock()
        self.s3.delete_object = Mock()

    def test__manage_files(self):
        files_info_mock = Mock()
        files_info_mock.is_file_hash_match = Mock(return_value=False)
        self.certificate._manage_files({'filename': files_info_mock},
                                       {'old_filename'})
        self.s3.upload_to_bucket.assert_called_once_with('filename', files_info_mock)
        self.s3.delete_object.assert_called_once_with('old_filename')

    def test__find_missing_files(self):
        modified_files = {'mod_file': Mock()}
        missing_files = {'missing_file'}
        result = self.certificate._find_missing_files(modified_files, missing_files)
        self.assertEqual(result, missing_files)

    def test__detect_modified_files(self):
        files_info_mock = Mock()
        files_info_mock.is_file_hash_match = Mock(return_value=False)
        files_info_mock.file_path = 'path'
        local_files = {'filename': files_info_mock}
        s3_files = {'filename': 'file_path'}
        result = self.certificate._detect_modified_files(local_files, s3_files)
        self.assertEqual(result, local_files)


if __name__ == "__main__":
    unittest.main()
