import sys
import json
import os
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton, QFileDialog,
    QVBoxLayout, QMessageBox, QComboBox
)
from PyQt5.QtCore import Qt

PETUNJUK_LIST = [
    "[1–2] 다음 그림을 보고 맞는 단어나 문장을 고르십시오.",
    "[3–4] 다음 단어와 관계있는 것은 고르십시오.",
    "[3–4] 다음 단어의 비슷말은 무엇입니까?",
    "[3–4] 다음 단어의 반대말은 무엇입니까?",
    "[5–8] 빈칸에 들아갈 가장 알맞은 것을 고르십시오.",
    "[9–12] 다음 질문에 답하십시오.",
    "[13–14] 다음 중 밑줄 친 부분이 맞는 문장을 고르십시오.",
    "[15–16] 다음 글을 읽고 무엇에 대한 글인지 고르십시오.",
    "[17–18] 다음 글을 읽고 내용과 같은 것을 고르십시오.",
    "[19–20] 다음 설명에 알맞은 어휘를 고르십시오.",
    "[21–24] 들은 것을 고르십시오.",
    "[25–29] 그림을 보고 알맞은 대답을 고르십시오.",
    "[30–33] 다음을 듣고 질문에 알맞은 대답을 고르십시오.",
    "[34–35] 다음을 듣고 이어지는 말을 고르십시오.",
    "[36–37] 잘 듣고 들은 내용과 관계있는 그림을 고르십시오.",
    "[38–40] 이야기를 듣고 질문에 알맞은 대답을 고르십시오."
]

class SoalInput(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("EPS-TOPIK Bank Soal Input (PyQt5)")
        self.setGeometry(100, 100, 600, 600)

        self.unsaved = False

        layout = QVBoxLayout()

        self.combo_petunjuk = QComboBox()
        self.combo_petunjuk.addItems(PETUNJUK_LIST)
        layout.addWidget(QLabel("📚 Petunjuk Soal"))
        layout.addWidget(self.combo_petunjuk)

        self.combo_jenis = QComboBox()
        self.combo_jenis.addItems(["Tulisan", "Gambar"])
        layout.addWidget(QLabel("📂 Jenis Soal"))
        layout.addWidget(self.combo_jenis)

        self.entry_soal = QLineEdit()
        self.entry_soal.textChanged.connect(self.mark_unsaved)
        layout.addWidget(QLabel("📌 Isi Soal (Teks atau Path Gambar)"))
        layout.addWidget(self.entry_soal)
        btn_gambar_soal = QPushButton("📁 Pilih Gambar Soal")
        btn_gambar_soal.clicked.connect(lambda: self.pilih_gambar(self.entry_soal))
        layout.addWidget(btn_gambar_soal)

        self.opsi = []
        for i in range(1, 5):
            opsi_entry = QLineEdit()
            opsi_entry.textChanged.connect(self.mark_unsaved)
            layout.addWidget(QLabel(f"{i}번 보기"))
            layout.addWidget(opsi_entry)
            btn = QPushButton("📁 Pilih Gambar")
            btn.clicked.connect(lambda _, e=opsi_entry: self.pilih_gambar(e))
            layout.addWidget(btn)
            self.opsi.append(opsi_entry)

        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: gray;")
        layout.addWidget(self.status_label)

        simpan_btn = QPushButton("✅ Simpan Soal")
        simpan_btn.clicked.connect(self.simpan_soal)
        layout.addWidget(simpan_btn)

        self.setLayout(layout)

    def mark_unsaved(self):
        self.unsaved = True
        self.status_label.setText("📝 Perubahan belum disimpan.")
        self.status_label.setStyleSheet("color: orange;")

    def pilih_gambar(self, entry):
        path, _ = QFileDialog.getOpenFileName(self, "Pilih Gambar", "", "Images (*.png *.jpg *.jpeg)")
        if path:
            entry.setText(path)
            self.mark_unsaved()

    def simpan_soal(self):
        petunjuk = self.combo_petunjuk.currentText()
        jenis = self.combo_jenis.currentText()
        soal = self.entry_soal.text().strip()
        opsi = [e.text().strip() for e in self.opsi]

        if not petunjuk or not soal or any(not o for o in opsi):
            QMessageBox.critical(
    self,
    "Field Kosong",
    "Semua kolom wajib diisi!\n\nPastikan kolom soal dan keempat pilihan jawaban sudah terisi."
)

            return

        soal_data = {
            "petunjuk": petunjuk,
            "jenis": "gambar_teks" if jenis == "Gambar" else "teks",
            "soal_gambar": soal if jenis == "Gambar" else None,
            "soal": soal if jenis == "Tulisan" else None,
            "opsi": opsi
        }

        file_path = "bank_soal.json"
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        else:
            data = []

        data.append(soal_data)

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        QMessageBox.information(self, "Berhasil", "✅ Soal berhasil disimpan ke bank_soal.json")
        self.status_label.setText("✅ Soal disimpan.")
        self.status_label.setStyleSheet("color: green;")
        self.unsaved = False
        self.clear_fields()

    def clear_fields(self):
        self.entry_soal.clear()
        for e in self.opsi:
            e.clear()

    def closeEvent(self, event):
        if self.unsaved:
            reply = QMessageBox.question(
                self,
                "Konfirmasi Keluar",
                "Anda memiliki data yang belum disimpan. Yakin ingin keluar?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = SoalInput()
    window.show()
    sys.exit(app.exec_())
