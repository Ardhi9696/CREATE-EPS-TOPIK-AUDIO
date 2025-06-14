# Import pustaka yang diperlukan
import customtkinter as ctk
from tkinter import messagebox, filedialog
import threading
from pydub import AudioSegment
from pydub.playback import play
import os
import sys
import platform
import subprocess

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.title("EPS-TOPIK Audio Generator")
app.geometry("440x420")

is_canceled = False
selected_set_folder = ""

# Fungsi untuk memutar suara notifikasi selesai
def play_done_sound():
    try:
        if platform.system() == "Darwin":
            subprocess.run(["afplay", "/System/Library/Sounds/Glass.aiff"])
        elif platform.system() == "Windows":
            import winsound
            winsound.MessageBeep()
        else:
            play(AudioSegment.silent(duration=500) + AudioSegment.sine(frequency=1000, duration=200))
    except:
        pass

def load(file_path):
    if not os.path.exists(file_path):
        messagebox.showerror("파일 오류", f"파일을 찾을 수 없습니다: {file_path}")
        raise FileNotFoundError(file_path)
    return AudioSegment.from_file(file_path)

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

    try:
        output = load(os.path.join(base_path, "intro.mp3"))
    except FileNotFoundError:
        return

    total = 20
    nomor_soal_tersedia = 0

    for i, nomor in enumerate(range(21, 41), 1):
        if is_canceled:
            status_label.configure(text="⛔ 작업이 취소되었습니다.")
            progressbar.set(0)
            label_persen.configure(text="")
            label_nomor.configure(text="")
            btn_start.configure(state="normal")
            btn_cancel.configure(state="disabled")
            return

        percent = int((i / total) * 100)
        progressbar.set(i / total)
        label_persen.configure(text=f"🔢 {percent}% 완료")
        label_nomor.configure(text=f"📍 현재 번호: {nomor}번")
        status_label.configure(text=f"🔄 {nomor}번 처리 중...")
        app.update_idletasks()

        try:
            bell = load(os.path.join(base_path, "bell.mp3"))
            nomor_audio = load(os.path.join(base_path, "nomor", f"{nomor}번.mp3"))
            soal_audio = load(os.path.join(set_folder_path, "soal", f"{nomor}.mp3"))
        except FileNotFoundError:
            return

        nomor_soal_tersedia += 1
        output += bell + satu_detik + nomor_audio + satu_detik

        if 25 <= nomor <= 29:
            output += soal_audio + satu_detik
            for j in range(1, 5):
                try:
                    nomor_jawab = load(os.path.join(base_path, "audio_no_pilgan", f"{j}번.mp3"))
                    isi_jawab = load(os.path.join(set_folder_path, "jawaban", "isi", f"{nomor}_{j}.mp3"))
                except FileNotFoundError:
                    return
                output += nomor_jawab + satu_detik + isi_jawab + satu_detik
            output += soal_audio + satu_detik
            for j in range(1, 5):
                try:
                    nomor_jawab = load(os.path.join(base_path, "audio_no_pilgan", f"{j}번.mp3"))
                    isi_jawab = load(os.path.join(set_folder_path, "jawaban", "isi", f"{nomor}_{j}.mp3"))
                except FileNotFoundError:
                    return
                output += nomor_jawab + satu_detik + isi_jawab + satu_detik
            output += jeda_5_detik if nomor < 30 else jeda_10_detik
        else:
            output += soal_audio + satu_detik + soal_audio
            output += jeda_5_detik if nomor <= 29 else jeda_10_detik

    if nomor_soal_tersedia < 20:
        messagebox.showerror("❌ 오류", f"총 {nomor_soal_tersedia}개의 문제가 준비되었습니다. 20문제가 필요합니다.")
        return

    try:
        output += load(os.path.join(base_path, "outro.mp3"))
    except FileNotFoundError:
        return

    output.export(output_file, format="mp3")
    status_label.configure(text=f"✅ 완료: Hasil/{set_name}.mp3 저장됨")
    label_persen.configure(text="✅ 100% 완료")
    label_nomor.configure(text="")
    btn_start.configure(state="normal")
    btn_cancel.configure(state="disabled")
    play_done_sound()

def pilih_set_folder():
    global selected_set_folder
    selected_set_folder = filedialog.askdirectory(title="📁 Pilih Folder SET (RAW_QUESTION/SET_xx)")
    label_set.configure(text=selected_set_folder if selected_set_folder else "Belum dipilih")

def mulai_proses(event=None):
    global is_canceled
    is_canceled = False

    if not selected_set_folder:
        messagebox.showwarning("입력 오류", "📁 Pilih folder SET terlebih dahulu!")
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

def cancel_proses():
    global is_canceled
    if messagebox.askyesno("❌ 취소 확인", "정말로 작업을 취소하시겠습니까?"):
        is_canceled = True
        status_label.configure(text="⏳ 취소 중...")

def on_closing():
    if messagebox.askyesno("종료 확인", "작업을 종료하시겠습니까? 저장되지 않은 데이터가 있을 수 있습니다."):
        app.destroy()

btn_set = ctk.CTkButton(app, text="📁 Pilih Folder SET (RAW_QUESTION/SET_xx)", command=pilih_set_folder)
btn_set.pack(pady=5)
label_set = ctk.CTkLabel(app, text="Belum dipilih")
label_set.pack()

btn_start = ctk.CTkButton(app, text="▶️ 생성 시작", command=mulai_proses)
btn_start.pack(pady=10)

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

app.protocol("WM_DELETE_WINDOW", on_closing)
app.mainloop()
