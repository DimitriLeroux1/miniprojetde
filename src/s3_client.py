
import os
import logging

import boto3
from botocore.config import Config
from botocore.exceptions import (
    ClientError,
    BotoCoreError,
    ConnectionClosedError,
    EndpointConnectionError,
    ReadTimeoutError,
    ConnectTimeoutError,
)

from dotenv import load_dotenv
from tenacity import (
    retry,
    retry_if_exception,
    stop_after_attempt,
    wait_exponential,
    before_sleep_log,
)

load_dotenv()

logger = logging.getLogger(__name__)

BUCKET = os.environ.get(
    "S3_BUCKET", "financial-transactions"
)


def get_s3_client():
    return boto3.client(
        "s3",
        endpoint_url=os.environ["S3_ENDPOINT"],
        aws_access_key_id=os.environ["S3_ACCESS_KEY"],
        aws_secret_access_key=os.environ["S3_SECRET_KEY"],
        region_name="us-east-1",
        config=Config(
            retries={"total_max_attempts": 1},
            s3={"addressing_style": "path"},
        ),
    )


def is_temporary_error(exc):
    if isinstance(exc, (
        EndpointConnectionError,
        ConnectionClosedError,
        ReadTimeoutError,
        ConnectTimeoutError,
    )):
        return True

    if isinstance(exc, ClientError):
        error = exc.response.get("Error", {})
        code = str(error.get("Code", ""))

        return code in {
            "RequestTimeout",
            "SlowDown",
            "InternalError",
            "ServiceUnavailable",
            "500", "502", "503", "504",
        }

    return False


s3_retry = retry(
    retry=retry_if_exception(is_temporary_error),
    stop=stop_after_attempt(4),
    wait=wait_exponential(
        multiplier=1, min=1, max=8
    ),
    before_sleep=before_sleep_log(
        logger, logging.WARNING
    ),
    reraise=True,
)


@s3_retry
def create_bucket():
    client = get_s3_client()

    try:
        client.create_bucket(Bucket=BUCKET)
        logger.info("Bucket créé : %s", BUCKET)

    except ClientError as exc:
        code = exc.response["Error"]["Code"]

        if code in {
            "BucketAlreadyOwnedByYou",
            "BucketAlreadyExists",
        }:
            client.head_bucket(Bucket=BUCKET)
        else:
            raise


@s3_retry
def upload_file(filepath):
    from pathlib import Path

    filepath = Path(filepath)
    key = f"transactions/{filepath.name}"

    get_s3_client().put_object(
        Bucket=BUCKET,
        Key=key,
        Body=filepath.read_bytes(),
        ContentType="text/csv",
    )

    logger.info("Fichier envoyé : %s", key)
    return key


@s3_retry
def download_file(key):
    response = get_s3_client().get_object(
        Bucket=BUCKET,
        Key=key,
    )

    try:
        return response["Body"].read()
    finally:
        response["Body"].close()


@s3_retry
def list_csv_files():
    client = get_s3_client()
    paginator = client.get_paginator("list_objects_v2")

    keys = []

    for page in paginator.paginate(
        Bucket=BUCKET,
        Prefix="transactions/",
    ):
        for obj in page.get("Contents", []):
            if obj["Key"].lower().endswith(".csv"):
                keys.append(obj["Key"])

    return sorted(keys)
