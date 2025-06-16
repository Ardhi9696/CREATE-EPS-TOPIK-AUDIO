#Cek Dependencies
import sys
import subprocess
import platform
import importlib.util
import shutil
import webbrowser

# Minimum Python version
REQUIRED_PYTHON_VERSION = (3, 11, 3)

# Fungsi cek dan buka link jika gagal
def ensure_dependency(name, install_instruksi, url=None):
    if importlib.util.find_spec(name) is None:
        print(f"❌ Modul '{name}' belum terinstal.")
        print(f"📌 Instruksi: {install_instruksi}")
        if url:
            print(f"🌐 Mengarahkan ke: {url}")
            webbrowser.open(url)
        sys.exit(1)

# Cek versi Python
if sys.version_info < REQUIRED_PYTHON_VERSION:
    print(f"❌ Python {REQUIRED_PYTHON_VERSION[0]}.{REQUIRED_PYTHON_VERSION[1]}.{REQUIRED_PYTHON_VERSION[2]} diperlukan.")
    print("🌐 Silakan download dari https://www.python.org/downloads/")
    sys.exit(1)

# Cek pydub
ensure_dependency("pydub", "pip install pydub", "https://pypi.org/project/pydub/")

# Cek customtkinter
ensure_dependency("customtkinter", "pip install customtkinter", "https://pypi.org/project/customtkinter/")

# Cek ffmpeg (pakai shutil untuk cek executable)
if not shutil.which("ffmpeg"):
    print("❌ 'ffmpeg' belum ditemukan di PATH.")
    os_type = platform.system()
    if os_type == "Windows":
        print("🌐 Download ffmpeg Windows: https://www.gyan.dev/ffmpeg/builds/")
    elif os_type == "Darwin":
        print("💡 MacOS: install via Homebrew: brew install ffmpeg")
        print("🌐 https://formulae.brew.sh/formula/ffmpeg")
    elif os_type == "Linux":
        print("💡 Linux (Debian/Ubuntu): sudo apt install ffmpeg")
    else:
        print("⚠️ OS tidak dikenali. Silakan install ffmpeg sesuai platform Anda.")
    sys.exit(1)

# Info sistem
print(f"🖥️ Sistem Operasi: {platform.system()} {platform.release()}")
print(f"🐍 Python versi: {sys.version}")
print("✅ Semua dependensi tersedia.\n")


# Import pustaka yang diperlukan
import customtkinter as ctk          # Untuk membuat GUI modern berbasis Tkinter
from tkinter import messagebox, filedialog
import threading                     # Untuk menjalankan proses berat (audio) tanpa membekukan GUI
from pydub import AudioSegment       # Untuk memproses dan menggabungkan file audio
from pydub.playback import play
import os                            # Untuk membuat folder dan mengelola file
import platform
import subprocess
import json

# File konfigurasi untuk simpan tema dan folder terakhir
CONFIG_FILE = "config.json"

# Set tampilan dan tema customtkinter
ctk.set_appearance_mode("System")    # Bisa "Dark", "Light", atau "System"
ctk.set_default_color_theme("blue")  # Tema warna GUI

# Inisialisasi jendela utama
app = ctk.CTk()
app.title("EPS-TOPIK Audio Generator")
app.geometry("480x520")

# Fungsi untuk memuat konfigurasi tema dan folder
config = {
    "appearance": "System",
    "color_theme": "blue",
    "last_folder": ""
}

if os.path.exists(CONFIG_FILE):
    with open(CONFIG_FILE, "r") as f:
        config.update(json.load(f))

# Fungsi menyimpan konfigurasi
def save_config():
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f)

# Variabel global
is_canceled = False
selected_set_folder = config.get("last_folder", "")

# Fungsi memuat file audio dari path
def load(file_path):
    print(f"🔍 Loading: {file_path}")
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Tidak ditemukan: {file_path}")
    return AudioSegment.from_file(file_path)

# Fungsi suara notifikasi
def play_done_sound():
    try:
        if platform.system() == "Darwin":
            subprocess.run(["afplay", "/System/Library/Sounds/Glass.aiff"])
        elif platform.system() == "Windows":
            import winsound
            winsound.MessageBeep()
    except Exception as e:
        print("Gagal memainkan suara notifikasi:", e)

# Fungsi utama untuk proses penggabungan audio
def proses_gabungan(set_folder_path, progressbar, status_label, btn_start, btn_cancel, label_persen, label_nomor):
    global is_canceled

    satu_detik = AudioSegment.silent(duration=1000)
    jeda_5_detik = AudioSegment.silent(duration=5000)
    jeda_10_detik = AudioSegment.silent(duration=10000)

    base_path = os.path.dirname(os.path.dirname(set_folder_path))
    set_name = os.path.basename(set_folder_path)
    hasil_folder = os.path.join(base_path, "Hasil")
    os.makedirs(hasil_folder, exist_ok=True)
    output_file = os.path.join(hasil_folder, f"{set_name}.mp3")

    if os.path.exists(output_file):
        if not messagebox.askyesno("파일 덮어쓰기", f"파일 '{set_name}.mp3'이(가) 이미 존재합니다. 덮어쓰시겠습니까?"):
            status_label.configure(text="⚠️ 작업이 취소되었습니다.")
            btn_start.configure(state="normal")
            btn_cancel.configure(state="disabled")
            return

        # === Validasi file awal ===
    status_label.configure(text="📂 파일 유효성 검사 중...")
    progressbar.set(0)
    app.update_idletasks()

    try:
        required_files = [
            "intro.mp3", "outro.mp3", "bell.mp3"
            ] + [f"nomor/{i}번.mp3" for i in range(21, 41)] + \
            [f"audio_no_pilgan/{j}번.mp3" for j in range(1, 5)] + \
            [os.path.join(set_folder_path, "soal", f"{i}.mp3") for i in range(21, 41)] + \
            [os.path.join(set_folder_path, "jawaban", "isi", f"{i}_{j}.mp3") for i in range(25, 30) for j in range(1, 5)]

        for idx, f in enumerate(required_files):
            if is_canceled:
                status_label.configure(text="⛔ 검증이 취소되었습니다.")
                progressbar.set(0)
                label_persen.configure(text="")
                label_nomor.configure(text="")
                btn_start.configure(state="normal")
                btn_cancel.configure(state="disabled")
                return

            load(f)
            progress = (idx + 1) / len(required_files)
            progressbar.set(progress)
            label_persen.configure(text=f"🔍 {int(progress * 100)}% 검증 중")
            app.update_idletasks()

    except Exception as e:
        messagebox.showerror("오류", f"필요한 파일이 없습니다: {e}")
        btn_start.configure(state="normal")
        btn_cancel.configure(state="disabled")
        return


    # Reset progress dan label untuk proses utama
    progressbar.set(0)
    label_persen.configure(text="🔢 0% 완료")

    output = load("intro.mp3")
    total = 20

    for i, nomor in enumerate(range(21, 41), 1):
        if is_canceled:
            status_label.configure(text="⛔ 작업이 취소되었습니다.")
            progressbar.set(0)
            label_persen.configure(text="")
            label_nomor.configure(text="")
            btn_start.configure(state="normal")
            btn_cancel.configure(state="disabled")
            return

        percent = i / total
        progressbar.set(percent)
        label_persen.configure(text=f"🔢 {int(percent * 100)}% 완료")
        label_nomor.configure(text=f"📍 현재 번호: {nomor}번")
        status_label.configure(text=f"🔄 {nomor}번 처리 중...")
        print(f"▶️ Menggabungkan soal {nomor}")
        app.update_idletasks()

        bell = load("bell.mp3")
        nomor_audio = load(f"nomor/{nomor}번.mp3")
        soal_audio = load(os.path.join(set_folder_path, "soal", f"{nomor}.mp3"))

        output += bell + satu_detik + nomor_audio + satu_detik

        if 25 <= nomor <= 29:
            output += soal_audio + satu_detik
            for j in range(1, 5):
                nomor_jawab = load(f"audio_no_pilgan/{j}번.mp3")
                isi_jawab = load(os.path.join(set_folder_path, "jawaban", "isi", f"{nomor}_{j}.mp3"))
                output += nomor_jawab + satu_detik + isi_jawab + satu_detik
            output += soal_audio + satu_detik
            for j in range(1, 5):
                nomor_jawab = load(f"audio_no_pilgan/{j}번.mp3")
                isi_jawab = load(os.path.join(set_folder_path, "jawaban", "isi", f"{nomor}_{j}.mp3"))
                output += nomor_jawab + satu_detik + isi_jawab + satu_detik
            output += jeda_5_detik if nomor < 30 else jeda_10_detik
        else:
            output += soal_audio + satu_detik + soal_audio
            output += jeda_5_detik if nomor <= 29 else jeda_10_detik

    output += load("outro.mp3")
    output.export(output_file, format="mp3")

    status_label.configure(text=f"✅ 완료: {output_file} 저장됨")
    label_persen.configure(text="✅ 100% 완료")
    label_nomor.configure(text="")
    btn_start.configure(state="normal")
    btn_cancel.configure(state="disabled")
    play_done_sound()
    print(f"🎉 Selesai: {output_file}")

# ==============================
# Fungsi Pilih Folder SET_xx
# ==============================
def pilih_set_folder():
    global selected_set_folder
    init_dir = config.get("last_folder") or os.getcwd()
    selected = filedialog.askdirectory(title="📁 SET 폴더 선택 (RAW_QUESTION/SET_xx)", initialdir=init_dir)
    if selected:
        selected_set_folder = selected
        btn_start.configure(state="normal")

        label_set.configure(text=os.path.basename(selected))
        config["last_folder"] = selected
        save_config()

# ==============================
# Fungsi Mulai Proses
# ==============================



def mulai_proses(event=None):
    global is_canceled
    is_canceled = False

    if not selected_set_folder or not os.path.exists(selected_set_folder):
        messagebox.showwarning("경고", "📁 먼저 SET 폴더를 선택하세요!")
        btn_start.configure(state="normal")
        return

    progressbar.set(0)
    label_persen.configure(text="0%")
    label_nomor.configure(text="")
    status_label.configure(text="🔃 시작 중...")
    btn_start.configure(state="disabled")
    btn_cancel.configure(state="normal")

    threading.Thread(
        target=proses_gabungan,
        args=(selected_set_folder, progressbar, status_label, btn_start, btn_cancel, label_persen, label_nomor),
        daemon=True
    ).start()

# ==============================
# Fungsi Cancel Proses
# ==============================
def cancel_proses():
    global is_canceled
    if messagebox.askyesno("❌ 취소 확인", "작업을 정말로 취소하시겠습니까?"):
        is_canceled = True
        status_label.configure(text="⏳ 취소 중...")

# ==============================
# Fungsi Saat Menutup Aplikasi
# ==============================
def on_closing():
    if messagebox.askyesno("종료 확인", "작업을 종료하시겠습니까?"):
        save_config()
        app.destroy()

# ==============================
# === UI Layout ===
# ==============================

btn_pilih = ctk.CTkButton(app, text="📁 SET 폴더 선택", command=pilih_set_folder)
btn_pilih.pack(pady=5)

label_set = ctk.CTkLabel(app, text="❗ 아직 선택되지 않았습니다")
label_set.pack()

btn_start = ctk.CTkButton(app, text="▶️ 생성 시작", command=mulai_proses)
btn_start.pack(pady=10)
# Nonaktifkan tombol saat awal
btn_start.configure(state="disabled")

btn_cancel = ctk.CTkButton(app, text="❌ 취소", command=cancel_proses, state="disabled")
btn_cancel.pack(pady=5)

progressbar = ctk.CTkProgressBar(app, width=300)
progressbar.set(0)
progressbar.pack(pady=10)

label_persen = ctk.CTkLabel(app, text="🔢 0% 완료")
label_persen.pack()

label_nomor = ctk.CTkLabel(app, text="")
label_nomor.pack()

status_label = ctk.CTkLabel(app, text="대기 중...")
status_label.pack(pady=10)

# Set aksi saat ditutup
app.protocol("WM_DELETE_WINDOW", on_closing)

# === Jalankan GUI ===
app.mainloop()
