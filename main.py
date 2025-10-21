import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import json
import os
from uploader import upload_video
from ai_generator import generate_description

ACCOUNTS_FILE = "accounts.json"

# --- Đọc danh sách tài khoản ---
def load_accounts():
    if not os.path.exists(ACCOUNTS_FILE):
        return {"youtube": [], "tiktok": []}
    with open(ACCOUNTS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_accounts(data):
    with open(ACCOUNTS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

accounts = load_accounts()

# --- Khởi tạo giao diện ---
root = tk.Tk()
root.title("Auto Video Uploader")
root.geometry("680x600")
root.resizable(False, False)

# --- Video chọn ---
tk.Label(root, text="🎬 Chọn video:").pack(pady=(10, 2))
video_path_var = tk.StringVar()
tk.Entry(root, textvariable=video_path_var, width=60).pack()
tk.Button(
    root,
    text="Duyệt...",
    command=lambda: video_path_var.set(filedialog.askopenfilename(filetypes=[("Video", "*.mp4 *.mov *.avi")]))
).pack(pady=5)

# --- Chọn nền tảng ---
tk.Label(root, text="🌐 Nền tảng:").pack(pady=(10, 2))
platform_var = tk.StringVar(value="youtube")
frame_platform = tk.Frame(root)
frame_platform.pack()
tk.Radiobutton(frame_platform, text="YouTube", variable=platform_var, value="youtube").pack(side="left", padx=10)
tk.Radiobutton(frame_platform, text="TikTok", variable=platform_var, value="tiktok").pack(side="left", padx=10)

# --- Danh sách tài khoản ---
tk.Label(root, text="👤 Chọn tài khoản:").pack(pady=(10, 2))
account_var = tk.StringVar()
account_menu = tk.OptionMenu(root, account_var, [])
account_menu.pack()

def update_account_list(*_):
    platform = platform_var.get()
    acc_list = [acc["name"] for acc in accounts.get(platform, [])]
    account_var.set(acc_list[0] if acc_list else "")
    menu = account_menu["menu"]
    menu.delete(0, "end")
    for name in acc_list:
        menu.add_command(label=name, command=lambda n=name: account_var.set(n))

platform_var.trace("w", update_account_list)
update_account_list()

# --- Thêm tài khoản ---
def add_account():
    platform = platform_var.get()
    name = simpledialog.askstring("Tên tài khoản", f"Nhập tên hiển thị cho tài khoản {platform}:")
    if not name:
        return

    client_id = simpledialog.askstring("Client ID", "Nhập Client ID:")
    client_secret = simpledialog.askstring("Client Secret", "Nhập Client Secret:")

    if platform == "youtube":
        refresh_token = simpledialog.askstring("Refresh Token", "Nhập Refresh Token:")
        new_acc = {"name": name, "client_id": client_id, "client_secret": client_secret, "refresh_token": refresh_token}
    else:
        access_token = simpledialog.askstring("Access Token", "Nhập Access Token:")
        new_acc = {"name": name, "client_id": client_id, "client_secret": client_secret, "access_token": access_token}

    accounts[platform].append(new_acc)
    save_accounts(accounts)
    update_account_list()
    messagebox.showinfo("Thành công", f"Đã thêm tài khoản {name} cho {platform.capitalize()}")

tk.Button(root, text="➕ Thêm tài khoản", command=add_account).pack(pady=5)

# --- Mô tả video ---
tk.Label(root, text="📝 Mô tả video:").pack(pady=(10, 2))
description_text = tk.Text(root, height=8, width=70)
description_text.pack()

# --- Sinh mô tả bằng Gemini ---
def generate_ai_desc():
    video_name = os.path.basename(video_path_var.get())
    if not video_name:
        messagebox.showwarning("Thiếu video", "Hãy chọn video trước.")
        return
    messagebox.showinfo("Đang tạo", "AI đang sinh mô tả, vui lòng chờ...")
    desc = generate_description(f"Hãy viết mô tả hấp dẫn cho video có tên: {video_name}")
    description_text.delete("1.0", tk.END)
    description_text.insert(tk.END, desc)

tk.Button(root, text="✨ Tạo mô tả bằng Gemini AI", command=generate_ai_desc).pack(pady=5)

# --- Upload video ---
def start_upload():
    path = video_path_var.get()
    if not path:
        messagebox.showwarning("Lỗi", "Hãy chọn video.")
        return

    platform = platform_var.get()
    account_name = account_var.get()
    desc = description_text.get("1.0", tk.END).strip()

    acc_list = accounts.get(platform, [])
    account = next((a for a in acc_list if a["name"] == account_name), None)
    if not account:
        messagebox.showerror("Lỗi", "Không tìm thấy tài khoản.")
        return

    messagebox.showinfo("Đang tải", f"Đang tải lên {platform.capitalize()}...")
    try:
        upload_video(platform, account, path, desc)
        messagebox.showinfo("✅ Thành công", f"Tải video lên {platform.capitalize()} thành công!")
    except Exception as e:
        messagebox.showerror("Lỗi", f"Tải lên thất bại:\n{e}")

tk.Button(root, text="⬆️ Upload Video", bg="#4CAF50", fg="white", width=20, height=2, command=start_upload).pack(pady=15)

root.mainloop()
