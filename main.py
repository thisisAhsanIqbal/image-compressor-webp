import os
import sys
import threading
import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image
import webbrowser

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS  # for PyInstaller
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class RefinedCompressorApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Image Compressor & WebP Converter")
        self.geometry("900x900")
        self.minsize(900, 900)
        self.maxsize(900, 900)
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.folder_path = ""
        self.keyword = ctk.StringVar()
        self.status_text = ctk.StringVar(value="STATUS: Waiting...")
        self.quality = ctk.IntVar(value=80)
        self.processing = False
        self.initial_size = 0
        self.final_size = 0
        self.total_files_converted = 0

        self.configure(bg="#101216")
        self.setup_ui()

    def setup_ui(self):
        outer = ctk.CTkFrame(self, corner_radius=25, fg_color="#1b1e23")
        outer.pack(pady=20, padx=30, fill="both", expand=True)

        # Header
        header = ctk.CTkFrame(outer, fg_color="transparent")
        header.pack(fill="x", pady=(10, 10), padx=10)
        header.grid_columnconfigure(0, weight=1)
        header.grid_columnconfigure(1, weight=4)
        header.grid_columnconfigure(2, weight=1)

        try:
            logo_path = resource_path("ahsan.png")
            avatar_img = ctk.CTkImage(Image.open(logo_path), size=(48, 48))
            avatar_label = ctk.CTkLabel(header, image=avatar_img, text="")
            avatar_label.grid(row=0, column=0, sticky="w", padx=5)
        except Exception as e:
            print(f"Logo load error: {e}")

        ctk.CTkLabel(header, text="IMAGE COMPRESSOR & WEBP CONVERTER",
                     font=("Barlow Semi Condensed", 22, "bold"),
                     text_color="white").grid(row=0, column=1, sticky="n")

        ctk.CTkButton(header, text="Contact",
                      command=lambda: webbrowser.open("https://www.linkedin.com/in/ahsan-iqbal-digitalmarketingexpert/"),
                      width=100, height=32, font=("Barlow Semi Condensed", 13),
                      fg_color="#5090f9", hover_color="#80b3ff",
                      corner_radius=10, text_color="white").grid(row=0, column=2, sticky="e", padx=5)

        # Quality
        quality_section = ctk.CTkFrame(outer, fg_color="#24272c", corner_radius=15)
        quality_section.pack(padx=10, pady=12, fill="x")
        ctk.CTkLabel(quality_section, text="SELECT IMAGE QUALITY (1–100)",
                     font=("Barlow Semi Condensed", 15), text_color="white").pack(pady=(10, 0))

        slider = ctk.CTkSlider(quality_section, from_=1, to=100, variable=self.quality,
                               progress_color="#5090f9", button_color="#80b3ff")
        slider.pack(pady=(10, 5), padx=20)
        self.quality_label = ctk.CTkLabel(quality_section,
                                          text=f"{self.quality.get()}%",
                                          font=("Barlow Semi Condensed", 14),
                                          text_color="white")
        self.quality_label.pack(pady=(0, 10))
        slider.configure(command=lambda v: self.quality_label.configure(text=f"{int(float(v))}%"))

        # Folder selection
        folder_section = ctk.CTkFrame(outer, fg_color="#24272c", corner_radius=15)
        folder_section.pack(padx=10, pady=12, fill="x")
        ctk.CTkLabel(folder_section, text="📁", font=("Arial", 42)).pack(pady=(10, 5))
        ctk.CTkLabel(folder_section, text="Select the Image Folder Path",
                     font=("Barlow Semi Condensed", 15), text_color="white").pack()
        ctk.CTkButton(folder_section, text="Choose Folder", command=self.select_folder,
                      fg_color="#5090f9", hover_color="#80b3ff", text_color="white").pack(pady=8)
        self.folder_label = ctk.CTkLabel(folder_section, text="No folder selected",
                                         text_color="gray", font=("Barlow Semi Condensed", 12))
        self.folder_label.pack(pady=(0, 10))

        # Keyword input
        keyword_section = ctk.CTkFrame(outer, fg_color="#24272c", corner_radius=15)
        keyword_section.pack(padx=10, pady=12, fill="x")
        ctk.CTkLabel(keyword_section, text="ENTER YOUR SEED KEYWORD",
                     font=("Barlow Semi Condensed", 15), text_color="white").pack(pady=(15, 5))
        ctk.CTkEntry(keyword_section, textvariable=self.keyword,
                     placeholder_text="e.g., travel, beach, food", width=400).pack(pady=(0, 15))

        # Start button
        self.start_button = ctk.CTkButton(outer, text="Convert and Resize Images",
                                          command=self.start_thread,
                                          fg_color="#C36527", hover_color="#a14b1a",
                                          text_color="white", corner_radius=20,
                                          height=40, width=280, font=("Barlow Semi Condensed", 14))
        self.start_button.pack(pady=20)

        # Footer/Stats
        stats = ctk.CTkFrame(outer, fg_color="#24272c", corner_radius=15)
        stats.pack(padx=10, pady=10, fill="x")
        self.initial_size_label = ctk.CTkLabel(stats, text="Initial Size: 0 MB",
                                               font=("Courier", 12), text_color="white")
        self.initial_size_label.pack(pady=(10, 2))
        self.final_size_label = ctk.CTkLabel(stats, text="Final Size: 0 MB",
                                             font=("Courier", 12), text_color="white")
        self.final_size_label.pack(pady=2)
        self.saved_label = ctk.CTkLabel(stats, text="Space Saved: 0 MB (0%)",
                                        font=("Courier", 12), text_color="#C36527")
        self.saved_label.pack(pady=2)
        self.progress_bar = ctk.CTkProgressBar(stats, width=500, progress_color="#5090f9")
        self.progress_bar.set(0)
        self.progress_bar.pack(pady=(10, 5))
        self.status_label = ctk.CTkLabel(stats, textvariable=self.status_text,
                                         font=("Barlow Semi Condensed", 12), text_color="gray")
        self.status_label.pack(pady=(0, 15))

        ctk.CTkLabel(outer, text="MADE WITH ❤ BY AHSAN IQBAL",
                     font=("Barlow Semi Condensed", 10), text_color="gray").pack(pady=5)

    def get_folder_size(self, folder_path):
        return sum(os.path.getsize(os.path.join(path, f))
                   for path, _, files in os.walk(folder_path) for f in files)

    def format_size(self, size_bytes):
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} TB"

    def update_size_info(self):
        if self.initial_size > 0 and self.final_size > 0:
            savings = self.initial_size - self.final_size
            percent = (savings / self.initial_size) * 100
            self.saved_label.configure(
                text=f"Space Saved: {self.format_size(savings)} ({percent:.1f}%)")

    def select_folder(self):
        path = filedialog.askdirectory()
        if path:
            self.folder_path = path
            self.folder_label.configure(text=path)
            self.initial_size = self.get_folder_size(path)
            self.initial_size_label.configure(text=f"Initial Size: {self.format_size(self.initial_size)}")
            self.final_size = 0
            self.final_size_label.configure(text="Final Size: 0 MB")
            self.saved_label.configure(text="Space Saved: 0 MB (0%)")

    def update_ui(self, progress=None, status=None, error_text=None, complete_text=None):
        if progress is not None:
            self.progress_bar.set(progress)
        if status is not None:
            self.status_text.set(f"STATUS: {status}")
        if error_text:
            messagebox.showerror("Error", error_text)
            self.processing = False
            self.start_button.configure(state="normal")
        if complete_text:
            self.status_text.set(f"STATUS: {complete_text}")
            self.final_size = self.get_folder_size(self.folder_path)
            self.final_size_label.configure(text=f"Final Size: {self.format_size(self.final_size)}")
            self.update_size_info()
            self.processing = False
            self.start_button.configure(state="normal")

    def start_thread(self):
        if self.processing:
            return
        if not self.folder_path:
            return messagebox.showerror("Error", "Please choose a folder.")
        if not self.keyword.get().strip():
            return messagebox.showerror("Error", "Please enter a seed keyword.")
        self.processing = True
        self.total_files_converted = 0
        self.start_button.configure(state="disabled")
        threading.Thread(target=self.process_images, args=(self.keyword.get().strip(),), daemon=True).start()

    def process_images(self, keyword):
        try:
            files = [f for f in os.listdir(self.folder_path)
                     if f.lower().endswith((".jpg", ".jpeg", ".png", ".bmp", ".tiff"))]
            if not files:
                self.after(0, lambda: self.update_ui(error_text="No image files found."))
                return

            self.after(0, lambda: self.update_ui(progress=0, status="Starting conversion..."))

            for i, file in enumerate(files, 1):
                try:
                    input_path = os.path.join(self.folder_path, file)
                    img = Image.open(input_path).convert("RGB")
                    img.thumbnail((1920, 1080), Image.Resampling.LANCZOS)
                    output_path = os.path.join(self.folder_path, f"{keyword}-{i:03d}.webp")
                    img.save(output_path, "WEBP", quality=self.quality.get(), method=6)
                    os.remove(input_path)

                    self.total_files_converted += 1
                    short_name = (file[:30] + '...') if len(file) > 33 else file
                    self.after(0, lambda i=i, file=short_name, output=output_path: self.update_ui(
                        progress=i / len(files),
                        status=f"{file} ➜ {os.path.basename(output)}"
                    ))
                except Exception as e:
                    self.after(0, lambda: self.update_ui(error_text=f"Error with {file}: {e}"))
                    return

            self.after(0, lambda: self.update_ui(complete_text=f"✅ Done! {len(files)} images converted."))
        except Exception as e:
            self.after(0, lambda: self.update_ui(error_text=f"Unexpected error: {e}"))

if __name__ == "__main__":
    app = RefinedCompressorApp()
    app.mainloop()
