from pydub import AudioSegment   # Library untuk manipulasi audio
import os                        # Untuk manipulasi file & folder

# Fungsi pembantu untuk memuat audio dari file path
def load(file_path):
    return AudioSegment.from_file(file_path)

# Fungsi utama untuk menggabungkan audio soal EPS-TOPIK
# Parameter:
# - output_path: path hasil file output (misal "Hasil/SET01.mp3")
# - update_progress: fungsi callback untuk update status (opsional)
# - is_cancelled: fungsi callback boolean untuk cek apakah proses dibatalkan
def proses_gabungan(output_path, update_progress=None, is_cancelled=None):
    # Inisialisasi jeda (silence)
    satu_detik = AudioSegment.silent(duration=1000)
    jeda_5_detik = AudioSegment.silent(duration=5000)
    jeda_10_detik = AudioSegment.silent(duration=10000)

    # Awali dengan intro.mp3
    output = load("intro.mp3")

    # Iterasi untuk soal nomor 21–40
    for nomor in range(21, 41):
        # Jika proses dibatalkan (misalnya dari tombol cancel di GUI)
        if is_cancelled and is_cancelled():
            return

        # Update progress status jika callback tersedia
        if update_progress:
            update_progress(f"🔊 Memproses soal {nomor}번...")

        # Load audio untuk bel, nomor soal, dan soal
        bell = load("bell.mp3")
        nomor_audio = load(f"nomor/{nomor}번.mp3")
        soal_audio = load(f"soal/{nomor}.mp3")

        # Tambahkan ke output: bel + nomor + soal
        output += bell + satu_detik + nomor_audio + satu_detik

        # Jika nomor 25–29, gunakan format soal + pilihan jawaban
        if 25 <= nomor <= 29:
            output += soal_audio + satu_detik

            # Tambahkan jawaban 1–4
            for i in range(1, 5):
                nomor_jawab = load(f"audio_no_pilgan/{i}번.mp3")
                isi_jawab = load(f"jawaban/isi/{nomor}_{i}.mp3")
                output += nomor_jawab + satu_detik + isi_jawab + satu_detik

            # Ulangi soal dan pilihan jawaban
            output += soal_audio + satu_detik
            for i in range(1, 5):
                nomor_jawab = load(f"audio_no_pilgan/{i}번.mp3")
                isi_jawab = load(f"jawaban/isi/{nomor}_{i}.mp3")
                output += nomor_jawab + satu_detik + isi_jawab + satu_detik

            # Tambahkan jeda 5 atau 10 detik sesuai nomor
            output += jeda_5_detik if nomor < 30 else jeda_10_detik
        else:
            # Soal biasa: soal diputar 2x lalu jeda
            output += soal_audio + satu_detik + soal_audio
            output += jeda_5_detik if nomor <= 29 else jeda_10_detik

    # Tambahkan outro di akhir file
    output += load("outro.mp3")

    # Pastikan folder output tersedia
    output_dir = os.path.dirname(output_path)
    os.makedirs(output_dir, exist_ok=True)

    # Simpan hasil audio gabungan ke file MP3
    output.export(output_path, format="mp3")
