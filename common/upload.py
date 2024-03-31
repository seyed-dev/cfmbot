from pathlib import Path
from common.providers.s3 import S3Provider
from common.utils import load_config

def upload_to_s3(file_path):
    config = load_config("config.yaml")

    s3_provider = S3Provider(config["s3"])

    # Specify the upload destination in S3
    upload_to = Path(file_path).name

    # Upload the file to S3
    s3_provider.upload_stream("image.jpeg", file_path, part_size=10 * 1024 * 1024, content_type="image/png")
    print("Upload End")