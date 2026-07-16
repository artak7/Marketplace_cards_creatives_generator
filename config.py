import os
from dotenv import load_dotenv

# Load variables from .env
load_dotenv()

class Config:
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    S3_ACCESS_KEY_ID = os.getenv("S3_ACCESS_KEY_ID")
    S3_SECRET_ACCESS_KEY = os.getenv("S3_SECRET_ACCESS_KEY")
    S3_ENDPOINT_URL = os.getenv("S3_ENDPOINT_URL")
    S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")

    # Static Color Mapping for Infographics
    COLOR_MAP = {
        "Фиолетовый (#7914e6)": "#7914e6",
        "Бирюзовый (#14bde6)": "#14bde6",
        "Черный (#111111)": "#111111",
        "Графитовый (#2c3e50)": "#2c3e50",
        "Красный (#e74c3c)": "#e74c3c",
        "Зеленый (#2ecc71)": "#2ecc71",
        "Оранжевый (#e67e22)": "#e67e22"
    }