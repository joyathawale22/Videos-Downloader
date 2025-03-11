import yt_dlp
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

# Function to update progress bar
def progress_hook(d):
    if d['status'] == 'downloading':
        percent = d['_percent_str'].strip().replace('%', '')
        progress_bar["value"] = float(percent)
        root.update_idletasks()

# Function to download video
def download_video():
    urls = url_entry.get().split("\n")  # Allow multiple URLs
    if not urls:
        messagebox.showerror("Error", "Please enter at least one video URL!")
        return

    save_path = filedialog.askdirectory()  # Ask user where to save files
    if not save_path:
        return

    quality = quality_var.get()
    format_option = "bestaudio" if audio_only_var.get() else f"best[height<={quality}]"

    options = {
        'outtmpl': f'{save_path}/%(title)s.%(ext)s',
        'format': format_option,
        'progress_hooks': [progress_hook],
        'noplaylist': True,
    }

    # Enable subtitles if selected
    if subtitles_var.get():
        options["writesubtitles"] = True
        options["subtitleslangs"] = ['en']

    try:
        with yt_dlp.YoutubeDL(options) as ydl:
            ydl.download(urls)
        messagebox.showinfo("Success", "Download completed!")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to download: {e}")

# GUI Setup
root = tk.Tk()
root.title("Advanced Video Downloader")
root.geometry("500x400")

tk.Label(root, text="Enter Video URLs (One per Line):").pack(pady=5)
url_entry = tk.Text(root, height=5, width=60)
url_entry.pack(pady=5)

# Quality selection
tk.Label(root, text="Select Video Quality:").pack(pady=5)
quality_var = tk.StringVar(value="1080")
quality_dropdown = ttk.Combobox(root, textvariable=quality_var, values=["1080", "720", "480", "360"])
quality_dropdown.pack()

# Download audio-only option
audio_only_var = tk.BooleanVar()
audio_checkbox = tk.Checkbutton(root, text="Download Audio Only (MP3)", variable=audio_only_var)
audio_checkbox.pack()

# Download subtitles option
subtitles_var = tk.BooleanVar()
subtitles_checkbox = tk.Checkbutton(root, text="Download Subtitles (if available)", variable=subtitles_var)
subtitles_checkbox.pack()

# Progress Bar
progress_bar = ttk.Progressbar(root, length=300, mode="determinate")
progress_bar.pack(pady=10)

# Download Button
download_button = tk.Button(root, text="Download", command=download_video)
download_button.pack(pady=10)

root.mainloop()
