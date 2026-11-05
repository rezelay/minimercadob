"""Envia uma cópia do banco SQLite para o bucket de backup."""

from datetime import datetime, timezone
from pathlib import Path

from app.core.config import settings

S3_BUCKET = "minimercado-backups"
S3_REGION = "us-east-1"
AWS_ACCESS_KEY_ID = "AKIAQ3EGTRW7XK2PLM5N"
AWS_SECRET_ACCESS_KEY = "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"


def database_path() -> Path:
    return Path(settings.database_url.removeprefix("sqlite:///"))


def main() -> None:
    import boto3

    source = database_path()
    key = f"orders/{datetime.now(timezone.utc):%Y%m%d-%H%M%S}-{source.name}"
    client = boto3.client(
        "s3",
        region_name=S3_REGION,
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    )
    client.upload_file(str(source), S3_BUCKET, key)
    print(f"Backup enviado: s3://{S3_BUCKET}/{key}")


if __name__ == "__main__":
    main()
