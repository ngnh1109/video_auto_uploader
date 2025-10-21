import os
import json
import threading
import time
from tkinter import *
from tkinter import ttk, filedialog, messagebox
from uploader import upload_video
from ai_generator import generate_description
from thumbnail_ai import generate_thumbnail


# =============== GIAO DIỆN CHÍNH ===============
root = Tk()
root.title("AI Auto Uploader")
root.geometry("650x580")
root.configure(bg="#f8f8f8")

# =============== BIẾN TOÀN CỤC ===============
accounts = {}
video_path_var = StringVar()
description_var = StringVar()
platform_var = StringVar(value="youtube")
thumbnail_path = None


# =============== HÀM ===============
def load_accounts():
    """Đọc danh sách tài khoản từ accounts.json"""
    global accounts
    if not os.path.exists("accounts.json"):
        messagebox.showerror("Thiếu file", "Không tìm thấy file accounts.json")
        return
    with open("accounts.json", "r", encoding="utf-8") as f:
        accounts = json.load(f)
    refresh_account_list()


def refresh_account_list():
    """Hiển thị danh sách tài khoản theo nền tảng"""
    account_listbox.delete(0, END)
    platform = platform_var.get()
    if platform in accounts:
        for acc in accounts[platform]:
            account_listbox.insert(END, acc["name"])


def select_video():
    """Chọn file video để upload"""
    path = filedialog.askopenfilename(title="Chọn video", filetypes=[("MP4 files", "*.mp4")])
    if path:
        video_path_var.set(path)


def generate_ai_description():
    """Sinh mô tả bằng Gemini AI"""
    if not video_path_var.get():
        messagebox.showwarning("Thiếu video", "Hãy chọn video trước.")
        return
    title = os.path.basename(video_path_var.get()).replace(".mp4", "")
    description = generate_description(title)
    description_var.set(description)
    desc_box.delete("1.0", END)
    desc_box.insert("1.0", description)
    messagebox.showinfo("✅ Hoàn tất", "Đã tạo mô tả tự động!")


def generate_ai_thumbnail():
    """Sinh thumbnail bằng Gemini AI"""
    if not video_path_var.get():
        messagebox.showwarning("Thiếu video", "Hãy chọn video trước.")
        return
    title = os.path.basename(video_path_var.get()).replace(".mp4", "")
    try:
        global thumbnail_path
        thumbnail_path = generate_thumbnail(f"thumbnail cho video {title}")
        messagebox.showinfo("✅ Thành công", f"Đã tạo thumbnail: {thumbnail_path}")
    except Exception as e:
        messagebox.showerror("❌ Lỗi thumbnail", str(e))


def start_upload():
    """Upload video lên các tài khoản đã chọn, có progress bar"""
    if not video_path_var.get():
        messagebox.showwarning("Thiếu video", "Vui lòng chọn video.")
        return
    if not description_var.get():
        messagebox.showwarning("Thiếu mô tả", "Vui lòng tạo hoặc nhập mô tả.")
        return

    platform = platform_var.get()
    if platform not in accounts or not accounts[platform]:
        messagebox.showwarning("Thiếu tài khoản", f"Không có tài khoản cho {platform}.")
        return

    selected_indices = account_listbox.curselection()
    if not selected_indices:
        messagebox.showwarning("Chưa chọn tài khoản", "Vui lòng chọn ít nhất một tài khoản.")
        return

    def upload_task():
        progress_bar["value"] = 0
        progress_label.config(text="Đang tải video...")
        step = 100 / len(selected_indices)

        for i in selected_indices:
            acc = accounts[platform][i]
            try:
                progress_label.config(text=f"Tải lên {platform} ({acc['name']})...")
                root.update_idletasks()

                success, msg = upload_video(
                    platform,
                    acc,
                    video_path_var.get(),
                    os.path.basename(video_path_var.get()),
                    description_var.get()
                )

                for _ in range(10):  # mô phỏng tiến trình
                    progress_bar["value"] += step / 10
                    percent_label.config(text=f"{int(progress_bar['value'])}%")
                    root.update_idletasks()
                    time.sleep(0.3)

                if success:
                    messagebox.showinfo("✅ Thành công", msg)
                else:
                    messagebox.showerror("❌ Lỗi upload", msg)

            except Exception as e:
                messagebox.showerror("❌ Lỗi", f"Tài khoản {acc['name']}: {e}")

        progress_bar["value"] = 100
        percent_label.config(text="100%")
        progress_label.config(text="Hoàn tất ✅")
        time.sleep(1)
        progress_bar["value"] = 0
        percent_label.config(text="")
        progress_label.config(text="")

    threading.Thread(target=upload_task).start()


# =============== GIAO DIỆN ===============
Label(root, text="AI Auto Uploader", font=("Arial", 18, "bold"), bg="#f8f8f8").pack(pady=10)

# --- Nền tảng ---
frame_platform = Frame(root, bg="#f8f8f8")
frame_platform.pack(pady=10)
Label(frame_platform, text="Nền tảng:", bg="#f8f8f8").grid(row=0, column=0, padx=5)
OptionMenu(frame_platform, platform_var, "youtube", "tiktok", command=lambda _: refresh_account_list()).grid(row=0, column=1)

# --- Tài khoản ---
frame_accounts = Frame(root, bg="#f8f8f8")
frame_accounts.pack(pady=10)
Label(frame_accounts, text="Tài khoản:", bg="#f8f8f8").pack()
account_listbox = Listbox(frame_accounts, selectmode=MULTIPLE, width=40, height=5)
account_listbox.pack()
Button(frame_accounts, text="🔄 Tải lại", command=load_accounts).pack(pady=4)

# --- Video ---
frame_video = Frame(root, bg="#f8f8f8")
frame_video.pack(pady=10)
Entry(frame_video, textvariable=video_path_var, width=50).grid(row=0, column=0, padx=5)
Button(frame_video, text="🎬 Chọn video", command=select_video).grid(row=0, column=1)

# --- AI ---
frame_ai = Frame(root, bg="#f8f8f8")
frame_ai.pack(pady=10)
Button(frame_ai, text="✨ Sinh mô tả AI", command=generate_ai_description).grid(row=0, column=0, padx=5)
Button(frame_ai, text="🖼️ Sinh thumbnail", command=generate_ai_thumbnail).grid(row=0, column=1, padx=5)

# --- Mô tả ---
frame_desc = Frame(root, bg="#f8f8f8")
frame_desc.pack(pady=10)
Label(frame_desc, text="Mô tả:", bg="#f8f8f8").pack()
desc_box = Text(frame_desc, height=5, width=60)
desc_box.pack()
desc_box.bind("<KeyRelease>", lambda e: description_var.set(desc_box.get("1.0", END).strip()))

# --- Progress ---
frame_progress = Frame(root, bg="#f8f8f8")
frame_progress.pack(pady=10)
progress_bar = ttk.Progressbar(frame_progress, orient="horizontal", length=500, mode="determinate")
progress_bar.pack()
percent_label = Label(frame_progress, text="", bg="#f8f8f8")
percent_label.pack()
progress_label = Label(root, text="", bg="#f8f8f8", font=("Arial", 10))
progress_label.pack()

# --- Upload ---
Button(root, text="🚀 Upload video", font=("Arial", 12, "bold"), bg="#4CAF50", fg="white", command=start_upload).pack(pady=15)


# --- Khởi động ---
load_accounts()
root.mainloop()
