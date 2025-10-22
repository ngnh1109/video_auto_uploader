# file: ai_generator.py
import google.generativeai as genai
import os

# *********************************************************************************
# ** CẦN THAY CHUỖI NÀY BẰNG KHÓA API THẬT CỦA BẠN **
# *********************************************************************************
# Đây là nguyên nhân gây lỗi 'No API_KEY or ADC found'
ACTUAL_API_KEY = "KEY" # <- Dán key thật vào đây
genai.configure(api_key = ACTUAL_API_KEY)

def generate_title(video_summary: str) -> str:
    """
    Tạo tiêu đề video hấp dẫn bằng Gemini AI.
    """
    prompt = f"""
    Dựa trên nội dung tóm tắt sau, hãy tạo một tiêu đề video YouTube hấp dẫn,
    ngắn gọn (dưới 20 ký tự) và thu hút người xem.
    Tóm tắt: "{video_summary}"
    Tiêu đề:
    """

    try:
        model = genai.GenerativeModel("gemini-2.5-flash") # Sử dụng mô hình flash ổn định
        response = model.generate_content(prompt)
        return response.text.strip().split('\n')[0][:90] 
    except Exception as e:
        print("Lỗi khi tạo tiêu đề:", e)
        raise Exception(f"Lỗi gọi AI: {e}. Vui lòng kiểm tra lại API Key và kết nối mạng.")


def generate_description(video_title: str) -> str:
    """
    Tạo mô tả video tự động bằng Gemini AI.
    """
    prompt = f"""
    Viết mô tả video YouTube hấp dẫn, tự nhiên và có tính thu hút cao (50-60 từ)
    cho video có tiêu đề: "{video_title}".
    Yêu cầu:
    - Giọng văn tự nhiên, thân thiện.
    - Có lời kêu gọi like, share, subscribe.
    - Thêm 3-5 hashtag liên quan.
    """

    try:
        model = genai.GenerativeModel("gemini-2.5-flash") # Sử dụng mô hình flash ổn định
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print("Lỗi khi gọi Gemini API:", e)
        raise Exception(f"Lỗi gọi AI: {e}. Vui lòng kiểm tra lại API Key và kết nối mạng.")