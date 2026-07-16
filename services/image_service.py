import platform
from PIL import Image, ImageDraw, ImageFont

class ImageService:
    """Combines backgrounds, templates, prints, and custom dynamic infobox badges."""
    
    @staticmethod
    def create_mockup(base_tshirt_path: str, print_img: Image.Image) -> Image.Image:
        """Pastes the print naturally over a local t-shirt mockup."""
        try:
            tshirt = Image.open(base_tshirt_path).convert("RGBA")
        except FileNotFoundError:
            raise FileNotFoundError("Пожалуйста, добавьте базовый файл 'tshirt_base.png' в корень проекта.")

        target_size = tshirt.size
        
        # Create a stylish dark-gray background flat image
        bg = Image.new("RGBA", target_size, "#2c3e50")
        
        # Calculate compact print constraints (35% of t-shirt size)
        print_width = int(target_size[0] * 0.35)
        print_resized = print_img.resize((print_width, print_width), Image.Resampling.LANCZOS)
        
        # Add minor opacity to show underlying fabric texture
        print_resized.putalpha(print_resized.getchannel('A').point(lambda x: int(x * 0.90)))
        
        # Place centered upper-chest
        print_layer = Image.new("RGBA", target_size, (0, 0, 0, 0))
        x_pos = (target_size[0] - print_width) // 2
        y_pos = int(target_size[1] * 0.25)
        print_layer.paste(print_resized, (x_pos, y_pos))
        
        # Merge layers
        composed = Image.alpha_composite(bg, tshirt)
        return Image.alpha_composite(composed, print_layer)

    @staticmethod
    def apply_infographics(image: Image.Image, badges: list) -> Image.Image:
        """Renders dynamic colored labels cleanly onto the image."""
        composed_image = image.copy()
        draw = ImageDraw.Draw(composed_image)
        width, height = composed_image.size

        font_size = int(width * 0.04)
        font = ImageService._load_system_font(font_size)

        padding_x = int(width * 0.05)
        badge_h = int(height * 0.07)
        current_y = padding_x

        for badge in badges:
            if not badge.get("enabled") or not badge.get("text", "").strip():
                continue
            
            text = badge["text"].upper()
            color = badge["color"]
            
            # Dynamic horizontal scale based on length of the label text
            calculated_width = int(len(text) * (font_size * 0.6) + 50)
            
            draw.rounded_rectangle(
                [padding_x, current_y, padding_x + calculated_width, current_y + badge_h],
                radius=15,
                fill=color
            )
            draw.text(
                (padding_x + 25, current_y + int(badge_h * 0.18)),
                text,
                fill="white",
                font=font
            )
            current_y += badge_h + int(height * 0.02)

        return composed_image

    @staticmethod
    def _load_system_font(font_size: int) -> ImageFont.FreeTypeFont:
        """Helper to get a reliable standard OS sans font."""
        try:
            if platform.system() == "Windows":
                return ImageFont.truetype("arial.ttf", font_size)
            return ImageFont.truetype("/Library/Fonts/Arial.ttf", font_size)
        except IOError:
            return ImageFont.load_default()