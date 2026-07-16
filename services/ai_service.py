import json
import urllib.parse
import requests
from groq import Groq
from PIL import Image
from io import BytesIO

class AIService:
    """Handles communications with External generative models (Groq, Pollinations)."""
    
    def __init__(self, groq_api_key: str):
        self.api_key = groq_api_key
        self.client = Groq(api_key=self.api_key) if groq_api_key else None

    def generate_seo_content(self) -> dict:
        """Calls Groq Llama to draft a trend-based prompt, title, and description."""
        if not self.client:
            raise ValueError("Groq API Key is not configured.")

        system_prompt = (
            "Ты — эксперт по маркетплейсу Wildberries и fashion-дизайнер. "
            "Придумай трендовую идею для принта на футболке и сгенерируй SEO-контент. "
            "Ответь СТРОГО в формате JSON со следующими ключами:\n"
            "1. 'prompt': детальный промпт для генерации картинки на английском языке.\n"
            "2. 'title': продающее название футболки на русском языке (до 60 символов, с ключевыми словами).\n"
            "3. 'description': SEO-оптимизированное описание товара на русском языке (до 1000 символов, "
            "включая ключевые слова: оверсайз, хлопок, стильный принт, подарок).\n"
            "Не пиши никаких вступлений или объяснений, только чистый JSON."
        )

        completion = self.client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": "Дай мне одну случайную трендовую идею для футболки."}
            ],
            temperature=0.8,
            response_format={"type": "json_object"}
        )
        return json.loads(completion.choices[0].message.content)

    @staticmethod
    def generate_print_image(prompt: str) -> Image.Image:
        """Calls Pollinations AI API to yield an image base based on user's prompt."""
        clean_prompt = " ".join(prompt.split())
        encoded_prompt = urllib.parse.quote(clean_prompt)
        image_url = f"https://image.pollinations.ai/p/{encoded_prompt}?width=1024&height=1024&model=flux&nologo=true"
        
        response = requests.get(image_url, timeout=60)
        response.raise_for_status()
        
        return Image.open(BytesIO(response.content)).convert("RGBA")