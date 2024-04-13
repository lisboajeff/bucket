from botocore.client import BaseClient

from info import FileInfo


class S3:
    """

    This class represents a wrapper around the AWS S3 client for performing various actions on a specified bucket.

    Attributes:
        s3_client (boto3.client): The AWS S3 client.
        bucket_name (str): The name of the S3 bucket.
        actions (dict[str, list]): A dictionary to store the performed actions.

    Methods:
        __init__(self, s3_client, bucket_name: str, actions: dict[str, list]):
            Initializes a new instance of the S3 class.

        get_hashed_s3_objects(self, folder: str = '') -> dict[str, str]:
            Retrieves the objects in the specified folder from the S3 bucket along with their hashes.

        upload_to_bucket(self, filename: str, info: FileInfo):
            Uploads a file to the S3 bucket with the specified metadata.

        delete_object(self, filename: str):
            Deletes an object from the S3 bucket.

        _log_action_error(action: str, filename: str, error: Exception):
            Logs the error message in case of any action failure.

    """

    def __init__(self, s3_client: BaseClient, bucket_name: str, actions: dict[str, list[FileInfo]]):
        self.s3_client: BaseClient = s3_client
        self.bucket_name: str = bucket_name
        self.actions: dict[str, list] = actions

    def get_hashed_s3_objects(self, folder: str = '') -> dict[str, str]:
        objects_with_hash: dict[str, str] = {}
        response = self.s3_client.list_objects_v2(Bucket=self.bucket_name, Prefix=folder)
        if 'Contents' in response:
            for obj in response['Contents']:
                obj_key = obj['Key']
                if not obj_key.endswith('/'):
                    meta = self.s3_client.head_object(Bucket=self.bucket_name, Key=obj_key)
                    obj_hash = meta['Metadata'].get('hash', '')
                    objects_with_hash[obj_key] = obj_hash
        return objects_with_hash

    def upload_to_bucket(self, filename: str, info: FileInfo):
        try:
            key: str = info.get_path()
            with open(filename, 'rb') as f:
                self.s3_client.upload_fileobj(
                    Fileobj=f,
                    Bucket=self.bucket_name,
                    Key=key,
                    ExtraArgs={'Metadata': {'hash': info.get_hash()}}
                )
            print(f"Uploaded {filename} to s3://{self.bucket_name}/{key}")
            self.actions["Uploaded"].append(info)
        except Exception as e:
            self._log_action_error("upload", filename, e)

    def delete_object(self, info: FileInfo):
        key: str = info.get_path()
        try:
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=key)
            print(f"Removed {key} from s3://{self.bucket_name}/{key}")
            self.actions["Removed"].append(info)
        except Exception as e:
            self._log_action_error("remove", key, e)

    @staticmethod
    def _log_action_error(action: str, filename: str, error: Exception):
        print(f"Failed to {action} {filename}: {error}")
