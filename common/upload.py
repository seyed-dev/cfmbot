from pathlib import Path
from common.providers.s3 import S3Provider
from common.utils import load_config

def upload_to_s3(file_path, class_id):
    config = load_config("config.yaml")

    s3_provider = S3Provider(config["s3"])

    # Upload the file to S3
    s3_provider.upload_stream(f"{class_id}.mp4", file_path, part_size=10 * 1024 * 1024, content_type="video/mp4")
    print("Upload End")