import google.generativeai as genai
from PIL import Image
import io
import base64

# API_KEY của bạn (Gemini)
genai.configure(api_key="API_GEMINI_KEY")

def generate_thumbnail(prompt, save_path="ai_thumbnail.jpg"):
    """
    Sinh thumbnail bằng Gemini AI Image (hoặc mô hình text-to-image nếu bạn có).
    """
    model = genai.GenerativeModel("gemini-1.5-pro")
    response = model.generate_content([
        f"Hãy tạo một ảnh thumbnail YouTube sinh động cho: {prompt}.",
        "Ảnh cần màu tươi sáng, bố cục rõ, không chữ, không logo."
    ])

    # Nếu model trả ra ảnh base64
    if response.candidates and response.candidates[0].content.parts:
        part = response.candidates[0].content.parts[0]
        if hasattr(part, "inline_data"):
            img_bytes = base64.b64decode(part.inline_data.data)
            img = Image.open(io.BytesIO(img_bytes))
            img.save(save_path)
            return save_path

    raise Exception("Không tạo được thumbnail từ AI.")
