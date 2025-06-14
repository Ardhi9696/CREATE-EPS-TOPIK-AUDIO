import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QMessageBox, QComboBox, QProgressBar, QHBoxLayout
)
from gtts import gTTS
from pydub import AudioSegment
from pydub.playback import play
import tempfile

class TTSGenerator(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Text to Speech (Korean) EPS-TOPIK")
        self.setGeometry(200, 200, 500, 650)

        layout = QVBoxLayout()

        self.combo_nomor = QComboBox()
        self.combo_nomor.addItems([str(i) for i in range(25, 30)])
        layout.addWidget(QLabel("🔢 Pilih Nomor Soal (25-29)"))
        layout.addWidget(self.combo_nomor)

        self.voice_gender = QComboBox()
        self.voice_gender.addItems(["Default (Google)", "(info) Tidak tersedia pilihan suara pria/wanita di gTTS"])
        layout.addWidget(QLabel("🎙️ Pilihan Suara (catatan: hanya default tersedia untuk Korean)"))
        layout.addWidget(self.voice_gender)

        self.fields = {}
        self.preview_buttons = {}
        field_names = ["Soal", "Pilihan 1", "Pilihan 2", "Pilihan 3", "Pilihan 4"]

        for name in field_names:
            label = QLabel(name)
            entry = QLineEdit()
            hlayout = QHBoxLayout()
            hlayout.addWidget(entry)
            preview_btn = QPushButton("▶ Preview")
            preview_btn.clicked.connect(lambda _, n=name: self.preview_audio(n))
            hlayout.addWidget(preview_btn)
            layout.addWidget(label)
            layout.addLayout(hlayout)
            self.fields[name] = entry
            self.preview_buttons[name] = preview_btn

        self.progress = QProgressBar()
        self.progress.setValue(0)
        layout.addWidget(self.progress)

        self.btn_generate = QPushButton("🔊 Generate dan Simpan MP3")
        self.btn_generate.clicked.connect(self.generate_audio)
        layout.addWidget(self.btn_generate)

        self.setLayout(layout)

    def preview_audio(self, label):
        try:
            text = self.fields[label].text().strip()
            if not text:
                QMessageBox.warning(self, "Kosong", f"Isi terlebih dahulu field {label}.")
                return
            tts = gTTS(text=text, lang='ko')
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
                tts.save(tmp.name)
                audio = AudioSegment.from_file(tmp.name, format="mp3")
                play(audio)
                os.unlink(tmp.name)
        except Exception as e:
            QMessageBox.critical(self, "Error Preview", f"Gagal memutar suara: {e}")

    def generate_audio(self):
        try:
            nomor = self.combo_nomor.currentText()
            soal_folder = os.path.abspath("soal_baru")
            jawaban_folder = os.path.abspath("jawaban_baru")
            os.makedirs(soal_folder, exist_ok=True)
            os.makedirs(jawaban_folder, exist_ok=True)

            total = len(self.fields)
            current = 0

            for label, line_edit in self.fields.items():
                text = line_edit.text().strip()
                if not text:
                    continue
                tts = gTTS(text=text, lang='ko')
                if label == "Soal":
                    file_path = os.path.join(soal_folder, f"{nomor}.mp3")
                else:
                    idx = label.split()[-1]  # Ambil nomor dari "Pilihan X"
                    file_path = os.path.join(jawaban_folder, f"{nomor}_{idx}.mp3")
                tts.save(file_path)

                current += 1
                self.progress.setValue(int((current / total) * 100))
                QApplication.processEvents()

            self.progress.setValue(100)
            QMessageBox.information(
                self,
                "Berhasil",
                f"✅ File soal disimpan di 'soal_baru/{nomor}.mp3'\n"
                f"✅ File jawaban di 'jawaban_baru/{nomor}_1.mp3' dst"
            )
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Terjadi kesalahan: {e}")

if __name__ == '__main__':
    from PyQt5.QtCore import Qt
    app = QApplication(sys.argv)
    window = TTSGenerator()
    window.show()
    sys.exit(app.exec_())
