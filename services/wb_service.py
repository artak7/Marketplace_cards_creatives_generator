from curl_cffi import requests
import time

class WildberriesService:
    """Выполняет официальные запросы к каталогу контента WB API с обходом антибота."""

    BASE_URL = "https://wildberries.ru"

    @classmethod
    def _get_headers(cls, token: str) -> dict:
        """Формирует заголовки. Автоматически добавляет Bearer, если его забыли."""
        clean_token = str(token).strip()
        auth_token = (
            clean_token
            if clean_token.startswith("Bearer ")
            else f"Bearer {clean_token}"
        )
        return {"Authorization": auth_token, "Content-Type": "application/json"}

    @classmethod
    def create_card(
        cls, token: str, vendor_code: str, title: str, description: str
    ) -> tuple[bool, str]:
        """Создает черновик карточки товара. Возвращает (Успех, Текст_Ответа)."""
        url = f"{cls.BASE_URL}/content/v2/cards/upload"
        headers = cls._get_headers(token)

        payload = [
            {
                "subjectID": 105,  # Футболки
                "variants": [
                    {
                        "vendorCode": str(vendor_code),
                        "title": str(title)[:60],
                        "description": str(description)[:5000],
                        "brand": "ИИ Тренды",
                        "dimensions": {
                            "length": 40,
                            "width": 30,
                            "height": 2,
                        },
                        "characteristics": [
                            {"name": "Плотность", "value": ["180 г/кв.м"]},
                            {"name": "Состав", "value": ["Хлопок 100%"]},
                        ],
                        "sizes": [{"techSize": "42", "wbSize": "42"}],
                    }
                ],
            }
        ]

        try:
            # Используем impersonate="chrome" для полной маскировки сетевого отпечатка
            res = requests.post(
                url,
                json=payload,
                headers=headers,
                impersonate="chrome",
                timeout=30,
            )
            is_success = res.status_code in (200, 201)
            return is_success, res.text
        except Exception as e:
            return False, f"Исключение curl_cffi: {str(e)}"

    @classmethod
    def link_media(cls, token: str, vendor_code: str, image_url: str) -> bool:
        """Опрашивает WB через скрытый браузерный запрос, ищет nmId и привязывает фото."""
        headers = cls._get_headers(token)
        nm_id = None

        for _ in range(6):
            time.sleep(15)
            try:
                list_url = f"{cls.BASE_URL}/content/v2/get/cards/list"
                list_payload = {
                    "settings": {
                        "cursor": {"limit": 50},
                        "filter": {"withError": False},
                    }
                }
                # Маскируем запрос под Chrome
                list_res = requests.post(
                    list_url,
                    json=list_payload,
                    headers=headers,
                    impersonate="chrome",
                    timeout=30,
                )

                if list_res.status_code == 200:
                    cards_data = (
                        list_res.json().get("data", {}).get("cards", [])
                    )
                    for card in cards_data:
                        if card.get("vendorCode") == vendor_code:
                            nm_id = card.get("nmID")
                            break
                if nm_id:
                    break
            except Exception:
                continue

        if not nm_id:
            return False

        media_url = f"{cls.BASE_URL}/content/v3/media/save"
        media_payload = {"nmId": int(nm_id), "data": [str(image_url)]}

        try:
            # Маскируем финальный запрос отправки фото под Chrome
            media_res = requests.post(
                media_url,
                json=media_payload,
                headers=headers,
                impersonate="chrome",
                timeout=30,
            )
            return media_res.status_code == 200
        except Exception:
            return False