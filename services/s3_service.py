import boto3
from io import BytesIO
from PIL import Image

class S3Service:
    """Manages cloud asset uploads and yields secure, shareable, direct URLs."""
    
    def __init__(self, key_id: str, secret_key: str, endpoint: str, bucket_name: str):
        self.bucket = bucket_name
        self.endpoint = endpoint
        self.client = boto3.client(
            's3',
            aws_access_key_id=key_id,
            aws_secret_access_key=secret_key,
            endpoint_url=endpoint
        ) if all([key_id, secret_key, endpoint]) else None

    def upload_image(self, img: Image.Image, filename: str) -> str:
        """Uploads Pillow object and returns a public URL."""
        if not self.client:
            raise ValueError("S3 service is unconfigured. Set variables in .env file.")

        img_buffer = BytesIO()
        img.convert("RGB").save(img_buffer, format="JPEG", quality=95)
        img_buffer.seek(0)

        self.client.upload_fileobj(
            img_buffer,
            self.bucket,
            filename,
            ExtraArgs={'ACL': 'public-read', 'ContentType': 'image/jpeg'}
        )
        return f"{self.endpoint}/{self.bucket}/{filename}"