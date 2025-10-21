# file: ai_generator.py
import google.generativeai as genai
import os

# Lấy key từ biến môi trường (khuyến nghị)
genai.configure(api_key=os.getenv("API_GEMINI_KEY"))  #NHẬP KEY VÀO ĐÂY

def generate_description(video_title: str) -> str:
    """
    Tạo mô tả video tự động bằng Gemini AI.
    """
    prompt = f"""
    Viết mô tả video YouTube hấp dẫn, tự nhiên và có tính thu hút cao (150-300 từ)
    cho video có tiêu đề: "{video_title}".
    Yêu cầu:
    - Giọng văn tự nhiên, thân thiện.
    - Có lời kêu gọi like, share, subscribe.
    - Thêm 3-5 hashtag liên quan.
    """

    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print("Lỗi khi gọi Gemini API:", e)
        return "Xem ngay video cực thú vị này nhé! #Shorts #Video"
