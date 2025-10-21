# uploader.py
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials
import requests

def upload_youtube_video(account_info, video_path, title="Video from Python", description="Uploaded automatically"):
    """Upload video lên YouTube"""
    try:
        creds = Credentials.from_authorized_user_info(account_info["credentials"])
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


def upload_tiktok_video(account_info, video_path, title="Video from Python"):
    """Upload video lên TikTok"""
    try:
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


def upload_video(platform, account_info, video_path, title="Video từ Python"):
    """Hàm tổng hợp gọi upload theo nền tảng"""
    if platform == "youtube":
        return upload_youtube_video(account_info, video_path, title)
    elif platform == "tiktok":
        return upload_tiktok_video(account_info, video_path, title)
    else:
        return False, f"Nền tảng {platform} chưa được hỗ trợ."
