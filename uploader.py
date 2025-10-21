from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials
import requests
import json
import time
import os


def upload_youtube_video(account_info, video_path, title="Video from Python", description="Uploaded automatically"):
    """Upload video lên YouTube"""
    try:
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

    try:
        url = "https://open-api.tiktok.com/oauth/refresh_token/"
        params = {
            "client_key": account_info["client_id"],
            "grant_type": "refresh_token",
            "refresh_token": account_info["refresh_token"]
        }
        r = requests.get(url, params=params)
        data = r.json()

        if "data" in data and "access_token" in data["data"]:
            new_token = data["data"]["access_token"]
            account_info["access_token"] = new_token

            # Lưu lại vào accounts.json
            if os.path.exists("accounts.json"):
                with open("accounts.json", "r", encoding="utf-8") as f:
                    accs = json.load(f)
                for acc in accs.get("tiktok", []):
                    if acc["name"] == account_info["name"]:
                        acc["access_token"] = new_token
                with open("accounts.json", "w", encoding="utf-8") as f:
                    json.dump(accs, f, indent=4, ensure_ascii=False)

            print("🔄 Refresh token TikTok thành công!")
        return account_info
    except Exception as e:
        print("⚠️ Lỗi refresh TikTok:", e)
        return account_info


def upload_tiktok_video(account_info, video_path, title="Video từ Python"):
    """Upload video lên TikTok"""
    try:
        # Tự refresh token nếu có
        account_info = refresh_tiktok_token(account_info)

        token = account_info["access_token"]
        upload_url = "https://open-api.tiktok.com/share/video/upload/"

        with open(video_path, "rb") as f:
            files = {"video": f}
            headers = {"Authorization": f"Bearer {token}"}
            response = requests.post(upload_url, headers=headers, files=files)

        if response.status_code == 200:
            print("✅ Upload thành công lên TikTok!")
            return True, "Upload thành công lên TikTok!"
        else:
            print("❌ Lỗi upload TikTok:", response.text)
            return False, response.text
    except Exception as e:
        print("❌ Lỗi upload TikTok:", e)
        return False, str(e)


def upload_video(platform, account_info, video_path, title="Video từ Python", description=""):
    """Hàm tổng hợp gọi upload theo nền tảng"""
    if platform == "youtube":
        return upload_youtube_video(account_info, video_path, title, description)
    elif platform == "tiktok":
        return upload_tiktok_video(account_info, video_path, title)
    else:
        return False, f"Nền tảng {platform} chưa được hỗ trợ."
