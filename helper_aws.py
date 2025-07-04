import boto3
from botocore.client import Config
from botocore.exceptions import BotoCoreError, ClientError
import os

# ─── Config S3 ───────────────────────────────────────────
S3_BUCKET  = "backup-qdrant"
AWS_REGION = "us-east-2"
 
# ─────────────────────────────────────────────────────────



s3_client = boto3.client(
    's3',
    aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY"),
    aws_session_token=os.environ.get("AWS_SESSION_TOKEN"),
    config=Config(region_name=AWS_REGION, signature_version='s3v4'),
    endpoint_url=None,
)


def upload_file_to_s3(path: str, bucket_name: str = S3_BUCKET) -> dict:
    """
    Faz upload de um arquivo local para o S3, usando o nome do arquivo como key.

    :param path: Caminho local do arquivo a ser enviado.
    :param bucket_name: Nome do bucket S3.
    :return: dict com 'success' (bool) e 'file_url' ou 'error'.
    """
    try:
        if not os.path.isfile(path):
            raise ValueError(f"Arquivo não encontrado em: {path}")

        filename = os.path.basename(path)
        with open(path, "rb") as f:
            s3_client.upload_fileobj(f, bucket_name, filename)

        file_url = f"https://{bucket_name}.s3.{AWS_REGION}.amazonaws.com/{filename}"
        return {"success": True, "file_url": file_url}

    except Exception as e:
        return {"success": False, "error": str(e)}
    


def download_file_from_s3(
    key: str,
    destination_path: str,
    bucket_name: str = S3_BUCKET
) -> dict:
    """
    Faz o download de um objeto S3 para um arquivo local.

    :param key:       Nome da object key no bucket (por exemplo, "meu_snapshot.snapshot").
    :param destination_path: Caminho completo onde o arquivo será salvo localmente.
    :param bucket_name:       Nome do bucket S3.
    :return: dict com 'success' (bool) e 'path' ou 'error'.
    """
    try:
        # Certifica que o diretório existe
        os.makedirs(os.path.dirname(destination_path), exist_ok=True)

        # Baixa o objeto
        s3_client.download_file(bucket_name, key, destination_path)

        return {"success": True, "path": destination_path}

    except (BotoCoreError, ClientError) as e:
        return {"success": False, "error": str(e)}


