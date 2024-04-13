# Python standard library
from types import SimpleNamespace
from unittest import TestCase, mock

# Relative application import
from src.s3 import S3


class TestS3(TestCase):

    def setUp(self):
        self.s3_client_mock = mock.Mock()
        self.s3 = S3(self.s3_client_mock, 'bucket_name', {'Uploaded': [], 'Removed': []})
        self.file_info_mock = SimpleNamespace(
            file_path='file_path',
            file_hash='file_hash',
        )

    def test_get_hashed_s3_objects(self):
        self.s3_client_mock.list_objects_v2.return_value = {
            'Contents': [{'Key': 'file_key_1'}, {'Key': 'file_key_2'}]
        }
        self.s3_client_mock.head_object.return_value = {
            'Metadata': {'hash': 'hash_val'}
        }
        expected = {'file_key_1': 'hash_val', 'file_key_2': 'hash_val'}

        result = self.s3.get_hashed_s3_objects()

        self.assertEqual(result, expected)

    def test_upload_to_bucket(self):
        with mock.patch('builtins.open', mock.mock_open(read_data='data')) as m:
            self.s3.upload_to_bucket('filename', self.file_info_mock)

        m.assert_called_once_with('filename', 'rb')
        self.s3_client_mock.upload_fileobj.assert_called_once()
        self.s3_client_mock.upload_fileobj.assert_called_once_with(
            Fileobj=m.return_value.__enter__.return_value,
            Bucket='bucket_name',
            Key=self.file_info_mock.file_path,
            ExtraArgs={'Metadata': {'hash': self.file_info_mock.file_hash}},
        )
        self.assertIn(self.file_info_mock.file_path, self.s3.actions['Uploaded'])

    def test_delete_object(self):
        self.s3.delete_object('filename')

        self.s3_client_mock.delete_object.assert_called_once_with(
            Bucket='bucket_name',
            Key='filename',
        )
        self.assertIn('filename', self.s3.actions['Removed'])

    def test_log_action_error(self):
        with mock.patch('builtins.print') as print_mock:
            self.s3._log_action_error('action', 'filename', Exception('exception'))

        print_mock.assert_called_once_with('Failed to action filename: exception')
