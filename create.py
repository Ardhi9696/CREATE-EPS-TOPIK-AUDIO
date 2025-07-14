import os
import sys
import json
import platform
import subprocess
import shutil
import importlib.util
import time
from datetime import datetime
from pydub import AudioSegment
from tkinter import Tk, filedialog, messagebox
import select


# ========== Logging ==========
LOG_FILE = "log.txt"
is_canceled = False


def log(msg):
    timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    full_msg = f"{timestamp} {msg}"
    print(full_msg)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(full_msg + "\n")


# ========== Dependency Check ==========
REQUIRED_PYTHON_VERSION = (3, 11, 3)

# ========== Info Sistem ==========
log("🖥️ Mendeteksi sistem operasi dan environment Python...")
os_info = f"{platform.system()} {platform.release()} ({platform.machine()})"
python_ver = f"{platform.python_version()} ({platform.python_implementation()})"
log(f"📌 OS Terdeteksi: {os_info}")
log(f"🐍 Python Versi: {python_ver}")

# ========== Cek Versi Python ==========
min_version_str = ".".join(map(str, REQUIRED_PYTHON_VERSION))
if sys.version_info < REQUIRED_PYTHON_VERSION:
    log(f"❌ Python minimal versi {min_version_str} diperlukan.")
    print(f"📥 Silakan download dari: https://www.python.org/downloads/")
    sys.exit(1)
else:
    log(f"✅ Python memenuhi syarat (≥ {min_version_str})")

# ========== Cek Modul ==========
log("📦 Mengecek dependencies Python...")


def verbose_check(name, instruksi, url=None):
    if importlib.util.find_spec(name) is None:
        log(f"❌ Modul '{name}' tidak ditemukan.")
        print(f"📌 Install dengan: {instruksi}")
        if url:
            import webbrowser

            webbrowser.open(url)
        sys.exit(1)
    else:
        log(f"✅ Modul '{name}' tersedia.")


verbose_check("pydub", "pip install pydub", "https://pypi.org/project/pydub/")

# ========== Cek ffmpeg ==========
log("🎵 Mengecek keberadaan 'ffmpeg'...")

if shutil.which("ffmpeg"):
    log("✅ 'ffmpeg' ditemukan di PATH.")
else:
    log("❌ 'ffmpeg' tidak ditemukan.")
    if platform.system() == "Windows":
        print("💡 Download dari: https://www.gyan.dev/ffmpeg/builds/")
    elif platform.system() == "Darwin":
        print("💡 Install via Homebrew: brew install ffmpeg")
    elif platform.system() == "Linux":
        print("💡 Debian/Ubuntu: sudo apt install ffmpeg")
    sys.exit(1)

log("✅ Semua dependensi telah dipenuhi.")
print()


def ensure_dependency(name, instruksi, url=None):
    if importlib.util.find_spec(name) is None:
        log(f"❌ Modul '{name}' belum terinstal.")
        print(f"📌 Install dengan: {instruksi}")
        if url:
            import webbrowser

            webbrowser.open(url)
        sys.exit(1)


if sys.version_info < REQUIRED_PYTHON_VERSION:
    log(f"❌ Python minimal {REQUIRED_PYTHON_VERSION} diperlukan.")
    sys.exit(1)

ensure_dependency("pydub", "pip install pydub", "https://pypi.org/project/pydub/")
if not shutil.which("ffmpeg"):
    log("❌ 'ffmpeg' tidak ditemukan di PATH.")
    print("📌 Silakan install ffmpeg sesuai OS Anda.")
    sys.exit(1)

# ========== Config ==========
CONFIG_FILE = "config.json"
config = {"last_folder": ""}
if os.path.exists(CONFIG_FILE):
    with open(CONFIG_FILE, "r") as f:
        config.update(json.load(f))


def save_config():
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f)


# ========== Util ==========
def pilih_folder_gui():
    init_dir = config.get("last_folder") or os.getcwd()
    root = Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    selected = filedialog.askdirectory(title="Pilih Folder SET_xx", initialdir=init_dir)
    root.destroy()
    return selected


def load_audio(path):
    if not os.path.exists(path):
        raise FileNotFoundError(f"File hilang: {path}")
    return AudioSegment.from_file(path)


def play_done_sound():
    try:
        if platform.system() == "Darwin":
            subprocess.run(["afplay", "/System/Library/Sounds/Glass.aiff"])
        elif platform.system() == "Windows":
            import winsound

            winsound.MessageBeep()
    except:
        pass


def progress_bar(current, total, width=30):
    filled = int(width * current / total)
    bar = "=" * filled + " " * (width - filled)
    percent = int(100 * current / total)
    print(f"[{bar}] {percent}%", end="\r")


def cek_batal():
    global is_canceled
    if platform.system() == "Windows":
        return  # Skip pada Windows karena select tidak mendukung stdin
    if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
        line = sys.stdin.readline().strip().upper()
        if line == "X":
            root = Tk()
            root.withdraw()
            confirm = messagebox.askyesno(
                "Konfirmasi", "Yakin ingin membatalkan proses?"
            )
            root.destroy()
            if confirm:
                is_canceled = True



# ========== Proses Gabungan ==========
def proses_gabungan(set_folder):
    global is_canceled
    is_canceled = False

    log(f"🚀 Mulai proses SET: {set_folder}")
    satu_detik = AudioSegment.silent(duration=1000)
    jeda_5_detik = AudioSegment.silent(duration=5000)
    jeda_10_detik = AudioSegment.silent(duration=10000)

    base_path = os.path.dirname(os.path.dirname(set_folder))
    set_name = os.path.basename(set_folder)
    hasil_folder = os.path.join(base_path, "Hasil")
    os.makedirs(hasil_folder, exist_ok=True)
    output_file = os.path.join(hasil_folder, f"{set_name}.mp3")

    if os.path.exists(output_file):
        tanya = input(f"⚠️ File {output_file} sudah ada. Overwrite? (y/n): ")
        if tanya.strip().lower() != "y":
            log("❌ Dibatalkan oleh user.")
            return

    try:
        required_files = (
            ["intro.mp3", "outro.mp3", "bell.mp3"]
            + [f"nomor/{i}번.mp3" for i in range(21, 41)]
            + [f"audio_no_pilgan/{j}번.mp3" for j in range(1, 5)]
            + [os.path.join(set_folder, "soal", f"{i}.mp3") for i in range(21, 41)]
            + [
                os.path.join(set_folder, "jawaban", "isi", f"{i}_{j}.mp3")
                for i in range(25, 30)
                for j in range(1, 5)
            ]
        )

        log("🔍 Validasi file...")
        for idx, f in enumerate(required_files, 1):
            cek_batal()
            if is_canceled:
                log("❌ Validasi dibatalkan.")
                return
            load_audio(f)
            progress_bar(idx, len(required_files))
        print()

    except Exception as e:
        log(f"❌ Validasi gagal: {e}")
        return

    output = load_audio("intro.mp3")
    for i, nomor in enumerate(range(21, 41), 1):
        cek_batal()
        if is_canceled:
            log("❌ Proses dibatalkan.")
            return

        log(f"▶️ Proses soal {nomor} ({i}/20)")
        bell = load_audio("bell.mp3")
        nomor_audio = load_audio(f"nomor/{nomor}번.mp3")
        soal_audio = load_audio(os.path.join(set_folder, "soal", f"{nomor}.mp3"))
        output += bell + satu_detik + nomor_audio + satu_detik

        if 25 <= nomor <= 29:
            output += soal_audio + satu_detik
            for j in range(1, 5):
                no = load_audio(f"audio_no_pilgan/{j}번.mp3")
                isi = load_audio(
                    os.path.join(set_folder, "jawaban", "isi", f"{nomor}_{j}.mp3")
                )
                output += no + satu_detik + isi + satu_detik
            output += soal_audio + satu_detik
            for j in range(1, 5):
                no = load_audio(f"audio_no_pilgan/{j}번.mp3")
                isi = load_audio(
                    os.path.join(set_folder, "jawaban", "isi", f"{nomor}_{j}.mp3")
                )
                output += no + satu_detik + isi + satu_detik
            output += jeda_5_detik if nomor < 30 else jeda_10_detik
        else:
            output += soal_audio + satu_detik + soal_audio
            output += jeda_5_detik if nomor <= 29 else jeda_10_detik

    output += load_audio("outro.mp3")
    output.export(output_file, format="mp3")
    log(f"✅ File selesai: {output_file}")
    play_done_sound()

    # Buka folder hasil
    if platform.system() == "Darwin":
        subprocess.run(["open", hasil_folder])
    elif platform.system() == "Windows":
        subprocess.run(["explorer", hasil_folder.replace("/", "\\")])
    elif platform.system() == "Linux":
        subprocess.run(["xdg-open", hasil_folder])


# ========== Menu CLI ==========
def tampilkan_judul():
    CYAN = "\033[96m"
    RESET = "\033[0m"
    print("=" * 50)
    print(f"{CYAN}{'🎧 EPS-TOPIK AUDIO GENERATOR'.center(50)}{RESET}")
    print("=" * 50)


def menu():
    global is_canceled
    selected_folder = config.get("last_folder", "")
    while True:
        tampilkan_judul()
        print(
            "📁 Folder saat ini:",
            selected_folder if selected_folder else "Belum dipilih",
        )
        print("\nMenu:")
        print("1. Pilih folder SET")
        print("2. Mulai penggabungan")
        print("3. Keluar")
        print("C. Clear folder yang dipilih")
        print("H. Kembali ke menu utama")

        choice = input("\nPilihan Anda (1/2/3/C/H): ").strip().upper()

        if choice == "1":
            folder = pilih_folder_gui()
            if folder and os.path.isdir(folder):
                selected_folder = folder
                config["last_folder"] = selected_folder
                save_config()
                log(f"📂 Folder SET dipilih: {selected_folder}")
            else:
                log("❌ Tidak ada folder yang dipilih.")
        elif choice == "2":
            if not selected_folder or not os.path.isdir(selected_folder):
                log(
                    "⚠️ Anda belum memilih folder SET. Silakan pilih opsi 1 terlebih dahulu."
                )
                input("Tekan Enter untuk kembali ke menu...")
                continue
            is_canceled = False
            proses_gabungan(selected_folder)
        elif choice == "3":
            log("👋 Program ditutup.")
            break
        elif choice == "C":
            selected_folder = ""
            config["last_folder"] = ""
            save_config()
            log("🧹 Folder pilihan dikosongkan.")
        elif choice == "H":
            continue
        else:
            print("❌ Pilihan tidak valid. Silakan pilih 1, 2, 3, C, atau H.")


if __name__ == "__main__":
    menu()
