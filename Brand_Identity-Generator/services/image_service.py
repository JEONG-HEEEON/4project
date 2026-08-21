import os
import io
import re
from typing import Dict, Any, List
from dotenv import load_dotenv
from PIL import Image, ImageDraw, ImageFont

load_dotenv()

class GeminiImageService:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        self.client = None
        self.use_new_sdk = False

        if self.api_key:
            try:
                from google import genai
                self.client = genai.Client(api_key=self.api_key)
                self.use_new_sdk = True
            except ImportError:
                pass

    def generate_logos(self, brand_info: Dict[str, Any], output_dir: str, num_logos: int = 2) -> List[str]:
        """
        Generates logo concepts using Gemini Imagen API or aesthetic Pillow fallback graphics generator.
        Saves PNG files into output_dir and returns the list of file paths.
        """
        os.makedirs(output_dir, exist_ok=True)
        saved_paths = []

        brand_name = "Brand"
        namings = brand_info.get("namings", [])
        if namings and isinstance(namings, list) and len(namings) > 0:
            first_naming = namings[0]
            brand_name = first_naming.get("english_name") or first_naming.get("name") or "Brand"

        industry = brand_info.get("industry", "Brand")
        color_palette = brand_info.get("color_palette", {})
        main_hex = color_palette.get("main", {}).get("hex", "#2E7D32")
        sub_hex = color_palette.get("sub", [{}])[0].get("hex", "#81C784") if color_palette.get("sub") else "#81C784"

        for i in range(1, num_logos + 1):
            file_name = f"logo_{i:02d}.png"
            file_path = os.path.join(output_dir, file_name)

            prompt = (
                f"Minimalist modern aesthetic logo design for brand '{brand_name}' in {industry} industry. "
                f"Vector style icon logo, clean lines, white background, primary color {main_hex}, secondary color {sub_hex}. "
                f"High quality branding concept {i}."
            )

            generated = False
            if self.api_key and self.client and self.use_new_sdk:
                try:
                    result = self.client.models.generate_images(
                        model='imagen-3.0-generate-002',
                        prompt=prompt,
                        config=dict(
                            number_of_images=1,
                            output_mime_type='image/png',
                            aspect_ratio='1:1'
                        )
                    )
                    if result.generated_images:
                        image_bytes = result.generated_images[0].image.image_bytes
                        image = Image.open(io.BytesIO(image_bytes))
                        image.save(file_path, "PNG")
                        generated = True
                except Exception as e:
                    print(f"⚠️ [Gemini Imagen API 경고] 로고 {i} 생성 실패: {e}")

            if not generated:
                # Generate aesthetic vector placeholder logo using Pillow
                self._generate_pillow_logo(brand_name, main_hex, sub_hex, i, file_path)

            saved_paths.append(file_path)

        return saved_paths

    def _generate_pillow_logo(self, brand_name: str, main_hex: str, sub_hex: str, concept_id: int, file_path: str):
        """Generates a clean, minimalist 800x800 PNG logo concept with proper font rendering."""
        size = (800, 800)
        img = Image.new("RGBA", size, (255, 255, 255, 255))
        draw = ImageDraw.Draw(img)

        # Convert hex to RGB
        def hex_to_rgb(hex_str, default=(46, 125, 50)):
            hex_str = hex_str.lstrip("#")
            if len(hex_str) == 6:
                return tuple(int(hex_str[i:i+2], 16) for i in (0, 2, 4))
            return default

        main_rgb = hex_to_rgb(main_hex, (46, 125, 50))
        sub_rgb = hex_to_rgb(sub_hex, (129, 199, 132))

        # Geometric Shapes according to concept id
        if concept_id == 1:
            # Concept 1: Modern Circle & Arc Badge
            draw.ellipse([250, 200, 550, 500], outline=main_rgb, width=16)
            draw.ellipse([320, 270, 480, 430], fill=sub_rgb)
            draw.arc([220, 170, 580, 530], start=45, end=225, fill=main_rgb, width=8)
        else:
            # Concept 2: Elegant Diamond & Inner Leaf Emblem
            draw.polygon([(400, 180), (550, 330), (400, 480), (250, 330)], fill=main_rgb)
            draw.polygon([(400, 230), (500, 330), (400, 430), (300, 330)], fill=(255, 255, 255, 255))
            draw.ellipse([360, 290, 440, 370], fill=sub_rgb)

        # Font Selection (Try Windows Korean Fonts first, then Arial)
        font_candidates = ["malgun.ttf", "malgunbd.ttf", "gulim.ttc", "arial.ttf"]
        title_font = None
        sub_font = None

        for font_name in font_candidates:
            try:
                title_font = ImageFont.truetype(font_name, 40)
                sub_font = ImageFont.truetype(font_name, 18)
                break
            except Exception:
                continue

        if not title_font:
            title_font = ImageFont.load_default()
            sub_font = ImageFont.load_default()

        # Clean display text
        display_text = str(brand_name).upper()

        # Render Brand Name
        text_bbox = draw.textbbox((0, 0), display_text, font=title_font)
        text_width = text_bbox[2] - text_bbox[0]
        text_x = (800 - text_width) / 2
        draw.text((text_x, 560), display_text, fill=(30, 30, 30), font=title_font)

        # Render Subtitle Concept ID
        sub_text = f"CONCEPT LOGO #{concept_id:02d}"
        sub_bbox = draw.textbbox((0, 0), sub_text, font=sub_font)
        sub_width = sub_bbox[2] - sub_bbox[0]
        sub_x = (800 - sub_width) / 2
        draw.text((sub_x, 620), sub_text, fill=(120, 120, 120), font=sub_font)

        img.save(file_path, "PNG")
