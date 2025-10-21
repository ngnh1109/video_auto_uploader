# file: thumbnail_ai.py
import google.generativeai as genai
from PIL import Image
import io
import base64
import os 

# *********************************************************************************
# ** CẦN THAY CHUỖI NÀY BẰNG KHÓA API THẬT CỦA BẠN **
# *********************************************************************************
# Đây là nguyên nhân gây lỗi 'No API_KEY or ADC found'
ACTUAL_API_KEY = "KEY" # <- Dán key thật vào đây
genai.configure(api_key = ACTUAL_API_KEY)

def generate_thumbnail(prompt, save_path="ai_thumbnail.jpg"):
    """
    Sinh thumbnail bằng mô hình đa phương tiện Gemini AI (gemini-2.5-flash).
    """
    # Thay mô hình đã lỗi (imagen-3.0-generate-002, gemini-1.5-pro)
    # bằng mô hình đa phương tiện ổn định gemini-2.5-flash
    model = genai.GenerativeModel("gemini-2.5-flash") 
    
    full_prompt = (
        f"Hãy tạo một hình ảnh thumbnail YouTube sinh động, chuyên nghiệp, độ phân giải cao "
        f"cho: {prompt}. Ảnh cần màu tươi sáng, bố cục rõ, không chữ, không logo, "
        f"thiết kế bắt mắt, theo tỷ lệ 16:9."
    )

    response = model.generate_content([
        full_prompt,
        "Tạo một hình ảnh đại diện (thumbnail) cho nội dung trên, theo phong cách nghệ thuật kỹ thuật số."
    ])

    # Logic xử lý hình ảnh base64
    if response.candidates and response.candidates[0].content.parts:
        part = response.candidates[0].content.parts[0]
        if hasattr(part, "inline_data") and part.inline_data.mime_type.startswith('image/'):
            img_bytes = base64.b64decode(part.inline_data.data)
            img = Image.open(io.BytesIO(img_bytes))
            img.save(save_path)
            return save_path
    
    # Nếu API trả về lỗi hoặc văn bản thay vì ảnh
    if response.text:
         raise Exception(f"API trả về lỗi hoặc văn bản thay vì ảnh: {response.text}")

    raise Exception("Không tạo được thumbnail từ AI. Vui lòng kiểm tra lại prompt hoặc gói dịch vụ.")