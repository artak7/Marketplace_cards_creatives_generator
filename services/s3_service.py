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
        """Uploads Pillow object and returns a secure presigned URL for Wildberries."""
        if not self.client:
            raise ValueError("S3 service is unconfigured. Set variables in .env file.")

        img_buffer = BytesIO()
        img.convert("RGB").save(img_buffer, format="JPEG", quality=95)
        img_buffer.seek(0)

        # 1. Загружаем файл БЕЗ 'ACL': 'public-read'
        self.client.upload_fileobj(
            img_buffer,
            self.bucket,
            filename,
            ExtraArgs={'ContentType': 'image/jpeg'} # Оставляем только тип контента
        )
        
        # 2. Генерируем подписанную ссылку, которая будет активна 7 дней (604800 секунд)
        presigned_url = self.client.generate_presigned_url(
            'get_object',
            Params={
                'Bucket': self.bucket,
                'Key': filename
            },
            ExpiresIn=604800 # Робот ВБ гарантированно успеет скачать фото
        )
        
        return presigned_url
