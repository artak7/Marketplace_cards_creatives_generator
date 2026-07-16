import time
import requests

class WildberriesService:
    """Executes official requests onto Wildberries seller endpoint catalogs."""
    
    @staticmethod
    def create_card(token: str, vendor_code: str, title: str, description: str) -> bool:
        """Attempts to register a single fashion variant with WB API."""
        headers = {
            "Authorization": token,
            "Content-Type": "application/json"
        }
        
        payload = [{
            "subjectID": 105, # T-Shirt category code
            "variants": [{
                "vendorCode": vendor_code,
                "title": title,
                "description": description,
                "brand": "ИИ Тренды",
                "dimensions": {"length": 40, "width": 30, "height": 2},
                "characteristics": [
                    {"Плотность": "180 г/кв.м"},
                    {"Состав": "Хлопок 100%"}
                ],
                "sizes": [{"techSize": "42", "wbSize": "42"}]
            }]
        }]
        
        res = requests.post("https://wildberries.ru", json=payload, headers=headers, timeout=30)
        return res.status_code in [200, 201]

    @staticmethod
    def link_media(token: str, vendor_code: str, image_url: str) -> bool:
        """Links your public S3 image with an existing product listing."""
        headers = {
            "Authorization": token,
            "Content-Type": "application/json"
        }
        
        payload = {
            "vendorCode": vendor_code,
            "data": [image_url]
        }
        
        # Artificial delay allowing WB servers to process the registration payload first
        time.sleep(1)
        res = requests.post("https://wildberries.ru", json=payload, headers=headers, timeout=30)
        return res.status_code == 200