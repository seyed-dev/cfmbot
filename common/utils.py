import sys
from pathlib import Path

from dynaconf import Dynaconf

BASE_DIR = Path(__file__).resolve().parent.parent

def load_config(file_path: str) -> dict:
    config = Dynaconf(settings_files=[file_path])
    return config