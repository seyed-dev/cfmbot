from datetime import timedelta

import boto3
from minio import Minio
from minio.commonconfig import CopySource


class BaseS3Provider:
    content_type_list = {
        "photo": "image/png",
        "video": "video/mp4",
        "voice": "audio/ogg",
        "audio": "audio/mpeg",
    }

    def __init__(self, config):
        self.provider = config.get("provider", "aws")  # Default to 'minio'
        self.host = config.get("host")
        self.port = config.get("port")
        self.secure = config.get("secure")
        self.access_key = config.get("access_key")
        self.secret_key = config.get("secret_key")
        self.bucket_name = config.get("bucket_name")
        self.upload_url_expire = config.get("upload_url_expire")
        self.object_url_expire = config.get("object_url_expire")

    def get_upload_url(self, object_name, content_type, bucket_name: str = None) -> str:
        ...

    def get_object_url(
        self, object_name, bucket_name: str = None, chat: bool = False, **extra
    ) -> str:
        ...

    def get_avatar_object(self, account_id):
        ...

    def upload_stream(
        self,
        upload_to,
        file_path,
        part_size: int,
        public: bool = True,
        content_type: str = None,
        chat: bool = False,
    ) -> None:
        ...

    def copy_object(
        self, old_dir: str, new_dir: str, old_bucket: str = None, new_bucket: str = None
    ) -> None:
        ...

    def delete_object(self, object_name: str, bucket_name: str = None) -> None:
        ...


class MinioProvider(BaseS3Provider):
    def __init__(self, config):
        super().__init__(config)
        self.client = Minio(
            f"{self.host}:{self.port}",
            access_key=self.access_key,
            secret_key=self.secret_key,
            secure=self.secure,
        )

    def get_upload_url(self, object_name, content_type, bucket_name: str = None):
        url = self.client.get_presigned_url(
            "PUT",
            bucket_name or self.bucket_name,
            object_name,
            expires=timedelta(hours=self.upload_url_expire),
            response_headers={"content-type": self.content_type_list[content_type]},
        )
        return url  # noqa

    def get_object_url(
        self, object_name, bucket_name: str = None, chat: bool = False, **extra
    ):
        bucket_name = bucket_name or self.bucket_name

        url = self.client.presigned_get_object(
            bucket_name,
            object_name,
            expires=timedelta(hours=self.object_url_expire),
            extra_query_params=extra,
        )
        return url  # noqa

    def upload_stream(
        self,
        upload_to,
        file_path,
        part_size: int,
        content_type: str = None,
    ) -> None:
        bucket_name = self.bucket_name

        upload = self.client.fput_object(
            bucket_name,
            upload_to,
            file_path,
            part_size=part_size,
            content_type=content_type,
        )
        print(upload)

    def copy_object(
        self, old_dir: str, new_dir: str, old_bucket: str = None, new_bucket: str = None
    ) -> None:
        self.client.copy_object(
            new_bucket or self.bucket_name,
            new_dir,
            CopySource(old_bucket or self.bucket_name, old_dir),
        )

    def delete_object(self, object_name: str, bucket_name: str = None) -> None:
        try:
            self.client.remove_object(bucket_name or self.bucket_name, object_name)
        except ValueError:
            pass


class AWSProvider(BaseS3Provider):
    def __init__(self, config):
        super().__init__(config)
        self.client = boto3.client(
            "s3",
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
            endpoint_url=f"https://{self.host}",
        )

    def get_upload_url(self, object_name, content_type, bucket_name: str = None):
        url = self.client.generate_presigned_url(
            "put_object",
            Params={
                "Bucket": bucket_name or self.bucket_name,
                "Key": object_name,
                "ContentType": self.content_type_list[content_type],
            },
            ExpiresIn=self.upload_url_expire,
        )
        return url  # noqa

    def get_object_url(
        self, object_name, **extra
    ):

        url = self.client.generate_presigned_url(
            "get_object",
            Params={"Bucket": self.bucket_name, "Key": object_name},
            ExpiresIn=self.object_url_expire,
        )
        return url  # noqa

    def upload_stream(
        self,
        upload_to,
        file_path,
        part_size: int,
        public: bool = True,
        content_type: str = None,
        chat: bool = False,
    ) -> None:
        bucket_name = self.bucket_name
        extra_args = {
            "ContentType": content_type,
        }
        if public:
            extra_args["ACL"] = "public-read"

        with open(file_path, "rb") as file:
            self.client.upload_fileobj(
                Fileobj=file, Bucket=bucket_name, Key=upload_to, ExtraArgs=extra_args
            )

    def copy_object(
        self, old_dir: str, new_dir: str, old_bucket: str = None, new_bucket: str = None
    ) -> None:
        self.client.copy_object(
            CopySource={"Bucket": old_bucket or self.bucket_name, "Key": old_dir},
            Bucket=new_bucket or self.bucket_name,
            Key=new_dir,
        )

    def delete_object(self, object_name: str, bucket_name: str = None) -> None:
        try:
            self.client.delete_object(
                Bucket=bucket_name or self.bucket_name, Key=object_name
            )
        except ValueError:
            pass


def S3Provider(config):  # noqa
    provider = config.get("provider", "minio")
    if provider == "minio":
        return MinioProvider(config)
    elif provider == "aws":
        return AWSProvider(config)
    else:
        raise ValueError(f"Unknown provider: {provider}")
