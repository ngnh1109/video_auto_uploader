from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials
import requests
import json
import time
import os

# Đường dẫn mặc định của accounts.json
ACCOUNTS_FILE = "accounts.json" 


def save_accounts(data):
    """Lưu dữ liệu accounts vào file"""
    if os.path.exists(ACCOUNTS_FILE):
        with open(ACCOUNTS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)


def load_accounts_data():
    """Tải dữ liệu accounts từ file"""
    if os.path.exists(ACCOUNTS_FILE):
        with open(ACCOUNTS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def upload_youtube_video(account_info, video_path, title="Video from Python", description="Uploaded automatically"):
    """Upload video lên YouTube"""
    try:
        # Code YouTube OK
        creds = Credentials.from_authorized_user_info(account_info)
        youtube = build("youtube", "v3", credentials=creds)

        body = {
            "snippet": {"title": title, "description": description},
            "status": {"privacyStatus": "private"}  # có thể đổi thành public
        }

        media = MediaFileUpload(video_path, chunksize=-1, resumable=True)
        request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)
        response = request.execute()

        print("✅ Upload thành công lên YouTube:", response["id"])
        return True, f"Đã upload video ID: {response['id']}"
    except Exception as e:
        print("❌ Lỗi upload YouTube:", e)
        return False, str(e)


def refresh_tiktok_token(account_info):
    """Tự refresh access token TikTok nếu có refresh_token"""
    if "refresh_token" not in account_info or not account_info["refresh_token"]:
        return account_info

    # **THAY ĐỔI QUAN TRỌNG:** TikTok refresh token yêu cầu POST, không phải GET và cần client_secret
    try:
        url = "https://open-api.tiktok.com/oauth/refresh_token/"
        
        # Kiểm tra Client Secret
        if "client_secret" not in account_info:
             print("⚠️ Thiếu client_secret trong accounts.json cho TikTok.")
             return account_info

        data = {
            "client_key": account_info["client_id"],
            "client_secret": account_info["client_secret"], # Bổ sung client_secret
            "grant_type": "refresh_token",
            "refresh_token": account_info["refresh_token"]
        }
        
        # Dùng POST request
        r = requests.post(url, data=data)
        response_data = r.json()

        if r.status_code == 200 and "data" in response_data and "access_token" in response_data["data"]:
            new_token = response_data["data"]["access_token"]
            account_info["access_token"] = new_token
            
            # Lưu lại token mới vào accounts.json
            accs = load_accounts_data()
            for acc in accs.get("tiktok", []):
                if acc["name"] == account_info["name"]:
                    acc["access_token"] = new_token
            save_accounts(accs)

            print("🔄 Refresh token TikTok thành công!")
        else:
            print("⚠️ Lỗi refresh token TikTok:", response_data)
        return account_info
    except Exception as e:
        print("⚠️ Lỗi refresh TikTok:", e)
        return account_info


def upload_tiktok_video(account_info, video_path, title="Video từ Python"):
    """Upload video lên TikTok"""
    try:
        # B1: Tự refresh token nếu cần
        account_info = refresh_tiktok_token(account_info)

        token = account_info.get("access_token")
        client_key = account_info.get("client_id")

        if not token or not client_key:
             return False, "Thiếu access_token hoặc client_id cho TikTok. Vui lòng kiểm tra lại accounts.json."

        upload_url = "https://open-api.tiktok.com/share/video/upload/"

        with open(video_path, "rb") as f:
            files = {"video": f}
            headers = {
                "Authorization": f"Bearer {token}",
                "Client-Key": client_key # Đảm bảo Client-Key được gửi trong header
            }
            # **THAY ĐỔI QUAN TRỌNG:** TikTok upload API cần POST request 
            # Dùng POST request
            response = requests.post(upload_url, headers=headers, files=files) 

        if response.status_code == 200 and response.json().get("data", {}).get("error_code") == 0:
            print("✅ Upload thành công lên TikTok!")
            return True, "Upload thành công lên TikTok!"
        else:
            # Bắt lỗi chi tiết từ API TikTok (như lỗi client_id)
            error_msg = response.json().get("message", response.text) 
            print("❌ Lỗi upload TikTok:", error_msg)
            return False, error_msg
    except Exception as e:
        print("❌ Lỗi upload TikTok:", e)
        return False, str(e)


def upload_video(platform, account_info, video_path, title="Video từ Python", description=""):
    """Hàm tổng hợp gọi upload theo nền tảng"""
    if platform == "youtube":
        return upload_youtube_video(account_info, video_path, title, description)
    elif platform == "tiktok":
        # Truyền cả client_secret (nếu có)
        return upload_tiktok_video(account_info, video_path, title)
    else:
        return False, f"Nền tảng {platform} chưa được hỗ trợ."