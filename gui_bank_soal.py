import sys
import pandas as pd
import json
import os
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QLabel,
    QLineEdit,
    QPushButton,
    QFileDialog,
    QVBoxLayout,
    QMessageBox,
    QComboBox,
    QSpinBox,
    QTextEdit,
    QGridLayout,
    QScrollArea,
    QHBoxLayout,
    QListWidget,
    QSizePolicy,
    QTextBrowser,
)
from PyQt5.QtCore import Qt

READING_LIST = [
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
]

LISTENING_LIST = [
    "[21–24] 들은 것을 고르십시오.",
    "[25–29] 그림을 보고 알맞은 대답을 고르십시오.",
    "[30–33] 다음을 듣고 질문에 알맞은 대답을 고르십시오.",
    "[34–35] 다음을 듣고 이어지는 말을 고르십시오.",
    "[36–37] 잘 듣고 들은 내용과 관계있는 그림을 고르십시오.",
    "[38–40] 이야기를 듣고 질문에 알맞은 대답을 고르십시오.",
]


class SoalInput(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("EPS-TOPIK Bank Soal Input (PyQt5)")
        self.setGeometry(
            100, 100, 1400, 800
        )  # Diperbesar untuk tampilan yang lebih baik
        self.unsaved = False
        self.edit_mode = False
        self.file_path = "bank_soal.json"
        self.all_data = []

        self.init_ui()
        self.load_all_soal()

    def init_ui(self):
        main_layout = QHBoxLayout()

        # Left Panel (Filter + List)
        left_panel = QVBoxLayout()
        left_panel.setContentsMargins(5, 5, 5, 5)

        # Filter Section
        filter_group = QVBoxLayout()
        filter_group.addWidget(QLabel("🔍 Filter & Search"))

        self.filter_box = QLineEdit()
        self.filter_box.setPlaceholderText(
            "Cari soal berdasarkan ID, nomor, atau petunjuk..."
        )
        self.filter_box.textChanged.connect(self.update_list)
        filter_group.addWidget(self.filter_box)

        # List Widget with Delete Button
        list_group = QVBoxLayout()
        self.list_widget = QListWidget()
        self.list_widget.itemClicked.connect(self.on_item_selected)
        list_group.addWidget(self.list_widget)

        # Delete Button
        self.delete_btn = QPushButton("🗑️ Delete Soal")
        self.delete_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #ff4444;
                color: white;
                padding: 5px;
                border-radius: 4px;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
        """
        )
        self.delete_btn.clicked.connect(self.delete_soal)
        self.delete_btn.setEnabled(False)
        list_group.addWidget(self.delete_btn)

        left_panel.addLayout(filter_group)
        left_panel.addLayout(list_group)

        # Middle Panel (Input Form)
        middle_panel = QVBoxLayout()
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        form_container = QWidget()
        self.form_layout = QVBoxLayout(form_container)

        # ID Soal
        self.id_soal = QSpinBox()
        self.id_soal.setRange(1, 9999)
        self.add_form_row("🆔 ID Soal", self.id_soal)

        # Tipe Soal
        self.combo_tipe = QComboBox()
        self.combo_tipe.addItems(["Reading", "Listening"])
        self.combo_tipe.currentIndexChanged.connect(self.update_petunjuk)
        self.add_form_row("📘 Tipe Soal", self.combo_tipe)

        # Petunjuk Soal
        self.combo_petunjuk = QComboBox()
        self.add_form_row("📚 Petunjuk Soal", self.combo_petunjuk)

        # Nomor Soal
        self.nomor_soal = QSpinBox()
        self.nomor_soal.setRange(1, 40)
        self.add_form_row("🔢 Nomor Soal (1-40)", self.nomor_soal)

        # Isi Soal
        self.entry_soal = QTextEdit()
        self.entry_soal.setMinimumHeight(100)
        self.add_form_row("📌 Isi Soal", self.entry_soal)

        # Opsi Jawaban
        self.opsi = []
        self.transkrip_opsi = []
        for i in range(4):
            opsi = QTextEdit()
            opsi.setMaximumHeight(60)
            transkrip = QTextEdit()
            transkrip.setMaximumHeight(60)
            self.opsi.append(opsi)
            self.transkrip_opsi.append(transkrip)

            hbox = QHBoxLayout()
            hbox.addWidget(QLabel(f"{i+1}번 보기:"), 1)
            hbox.addWidget(opsi, 3)
            hbox.addWidget(QLabel(f"🗣️ Transkrip:"), 1)
            hbox.addWidget(transkrip, 3)
            self.form_layout.addLayout(hbox)

        # Kunci Jawaban
        self.kunci_combo = QComboBox()
        self.kunci_combo.addItems(["1", "2", "3", "4"])
        self.add_form_row("✅ Kunci Jawaban", self.kunci_combo)

        # Transkrip Soal
        self.transkrip_soal = QTextEdit()
        self.transkrip_soal.setMaximumHeight(80)
        self.add_form_row("🗣️ Transkrip Soal (Listening)", self.transkrip_soal)

        # Action Buttons
        btn_layout = QHBoxLayout()
        self.simpan_btn = QPushButton("💾 Simpan")
        self.simpan_btn.clicked.connect(self.simpan_soal)
        btn_layout.addWidget(self.simpan_btn)

        self.clear_btn = QPushButton("🧹 Clear")
        self.clear_btn.clicked.connect(self.clear_fields)
        btn_layout.addWidget(self.clear_btn)

        self.export_btn = QPushButton("📤 Export Excel")
        self.export_btn.clicked.connect(self.export_to_excel)
        btn_layout.addWidget(self.export_btn)

        self.form_layout.addLayout(btn_layout)
        scroll.setWidget(form_container)
        middle_panel.addWidget(scroll)

        # Right Panel (Preview)
        right_panel = QVBoxLayout()
        right_panel.addWidget(QLabel("🖥️ Preview Soal"))

        self.preview_browser = QTextBrowser()
        self.preview_browser.setStyleSheet(
            """
            QTextBrowser {
                background-color: #f9f9f9;
                border: 1px solid #ddd;
                padding: 10px;
            }
        """
        )
        right_panel.addWidget(self.preview_browser)

        # Add panels to main layout
        main_layout.addLayout(left_panel, 1)
        main_layout.addLayout(middle_panel, 2)
        main_layout.addLayout(right_panel, 1)

        self.setLayout(main_layout)
        self.update_petunjuk()

    def add_form_row(self, label, widget):
        self.form_layout.addWidget(QLabel(label))
        self.form_layout.addWidget(widget)

    def update_petunjuk(self):
        self.combo_petunjuk.clear()
        tipe = self.combo_tipe.currentText()

        if tipe == "Reading":
            self.combo_petunjuk.addItems(READING_LIST)
            self.transkrip_soal.hide()
            for e in self.transkrip_opsi:
                e.hide()
        else:
            self.combo_petunjuk.addItems(LISTENING_LIST)
            self.transkrip_soal.show()
            for e in self.transkrip_opsi:
                e.show()

        self.update_preview()

    def on_item_selected(self, item):
        self.load_soal_from_list(item)
        self.delete_btn.setEnabled(True)

    def load_all_soal(self):
        try:
            self.list_widget.clear()
            self.delete_btn.setEnabled(False)

            if os.path.exists(self.file_path):
                with open(self.file_path, "r", encoding="utf-8") as f:
                    self.all_data = json.load(f)

                for d in self.all_data:
                    self.list_widget.addItem(
                        f"SET: {d['id']} - No: {d['nomor']} - {d['tipe'].capitalize()}"
                    )
            else:
                self.all_data = []

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Gagal memuat data:\n{str(e)}")

    def update_list(self):
        query = self.filter_box.text().lower()
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            item.setHidden(query not in item.text().lower())

    def load_soal_from_list(self, item):
        idx = self.list_widget.row(item)
        soal = self.all_data[idx]

        self.id_soal.setValue(soal.get("id", 1))
        self.nomor_soal.setValue(soal.get("nomor", 1))

        tipe = soal.get("tipe", "reading").capitalize()
        self.combo_tipe.setCurrentText(tipe)
        self.combo_petunjuk.setCurrentText(soal.get("petunjuk", ""))

        self.entry_soal.setPlainText(soal.get("soal", ""))

        for i in range(4):
            self.opsi[i].setPlainText(soal.get("opsi", ["", "", "", ""])[i])

        self.kunci_combo.setCurrentText(soal.get("kunci", "1"))

        if tipe == "Listening":
            self.transkrip_soal.setPlainText(soal.get("transkrip_soal", ""))
            for i in range(4):
                self.transkrip_opsi[i].setPlainText(
                    soal.get("transkrip_jawaban", ["", "", "", ""])[i]
                )

        self.edit_mode = True
        self.simpan_btn.setText("🔄 Update Soal")
        self.update_preview()

    def delete_soal(self):
        current_item = self.list_widget.currentItem()
        if not current_item:
            return

        idx = self.list_widget.row(current_item)
        soal = self.all_data[idx]

        reply = QMessageBox.question(
            self,
            "Konfirmasi Hapus",
            f"Yakin hapus soal ID {soal['id']} nomor {soal['nomor']}?",
            QMessageBox.Yes | QMessageBox.No,
        )

        if reply == QMessageBox.Yes:
            try:
                del self.all_data[idx]

                with open(self.file_path, "w", encoding="utf-8") as f:
                    json.dump(self.all_data, f, ensure_ascii=False, indent=2)

                self.load_all_soal()
                self.clear_fields()
                QMessageBox.information(self, "Berhasil", "Soal berhasil dihapus.")

            except Exception as e:
                QMessageBox.critical(self, "Error", f"Gagal menghapus soal:\n{str(e)}")

    def simpan_soal(self):
        try:
            soal_data = {
                "id": self.id_soal.value(),
                "nomor": self.nomor_soal.value(),
                "tipe": self.combo_tipe.currentText().lower(),
                "petunjuk": self.combo_petunjuk.currentText(),
                "soal": self.entry_soal.toPlainText(),
                "opsi": [o.toPlainText() for o in self.opsi],
                "kunci": self.kunci_combo.currentText(),
            }

            if soal_data["tipe"] == "listening":
                soal_data["transkrip_soal"] = self.transkrip_soal.toPlainText()
                soal_data["transkrip_jawaban"] = [
                    t.toPlainText() for t in self.transkrip_opsi
                ]

            # Validasi
            if not soal_data["soal"] and all(not o for o in soal_data["opsi"]):
                QMessageBox.warning(
                    self, "Peringatan", "Isi soal atau opsi jawaban harus diisi!"
                )
                return

            if soal_data["tipe"] == "listening" and (
                not soal_data["transkrip_soal"]
                or any(not t for t in soal_data["transkrip_jawaban"])
            ):
                QMessageBox.warning(
                    self,
                    "Peringatan",
                    "Transkrip soal dan jawaban harus diisi untuk listening!",
                )
                return

            # Load existing data
            if os.path.exists(self.file_path):
                with open(self.file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
            else:
                data = []

            # Cek apakah soal sudah ada
            existing_idx = -1
            for i, item in enumerate(data):
                if (
                    item["id"] == soal_data["id"]
                    and item["nomor"] == soal_data["nomor"]
                ):
                    existing_idx = i
                    break

            if existing_idx >= 0:
                data[existing_idx] = soal_data
                action = "diupdate"
            else:
                data.append(soal_data)
                action = "ditambahkan"

            # Simpan ke file
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            QMessageBox.information(
                self,
                "Berhasil",
                f"Soal ID {soal_data['id']} nomor {soal_data['nomor']} berhasil {action}!",
            )

            self.load_all_soal()
            if not self.edit_mode:
                self.clear_fields()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Gagal menyimpan soal:\n{str(e)}")

    def update_preview(self):
        try:
            tipe = self.combo_tipe.currentText()
            nomor = self.nomor_soal.value()
            petunjuk = self.combo_petunjuk.currentText()
            kunci = self.kunci_combo.currentText()

            html = f"""
            <html>
            <head>
            <style>
                body {{ font-family: Arial; margin: 10px; }}
                h3 {{ color: #2c3e50; }}
                h4 {{ color: #3498db; }}
                hr {{ border: 1px solid #eee; }}
                .kunci {{ color: #27ae60; font-weight: bold; }}
            </style>
            </head>
            <body>
            <h3>Soal Nomor {nomor} - {tipe}</h3>
            <h4>Petunjuk: {petunjuk}</h4>
            <hr>
            <h4>Isi Soal:</h4>
            {self.entry_soal.toHtml()}
            <hr>
            <h4>Opsi Jawaban:</h4>
            <ol>
            """

            for i in range(4):
                kunci_marker = (
                    " <span class='kunci'>(Kunci)</span>" if str(i + 1) == kunci else ""
                )
                html += f"<li>{self.opsi[i].toHtml()}{kunci_marker}</li>"

            html += "</ol>"

            if tipe.lower() == "listening":
                html += """
                <hr>
                <h4>Transkrip Soal:</h4>
                <p>{}</p>
                <h4>Transkrip Jawaban:</h4>
                <ol>
                """.format(
                    self.transkrip_soal.toPlainText().replace("\n", "<br>")
                )

                for i in range(len(self.transkrip_opsi)):
                    teks_rapi = (
                        self.transkrip_opsi[i].toPlainText().replace("\n", "<br>")
                    )
                    html += f"<li>{teks_rapi}</li>"

                html += "</ol>"

            html += "</body></html>"

            self.preview_browser.setHtml(html)

        except Exception as e:
            print(f"Error generating preview: {str(e)}")

    def clear_fields(self):
        self.id_soal.setValue(1)
        self.nomor_soal.setValue(1)
        self.entry_soal.clear()

        for opsi in self.opsi:
            opsi.clear()

        for transkrip in self.transkrip_opsi:
            transkrip.clear()

        self.kunci_combo.setCurrentIndex(0)
        self.transkrip_soal.clear()
        self.edit_mode = False
        self.simpan_btn.setText("💾 Simpan")
        self.delete_btn.setEnabled(False)
        self.update_preview()

    def export_to_excel(self):
        try:
            if not self.all_data:
                QMessageBox.warning(
                    self, "Data Kosong", "Tidak ada data soal untuk diekspor"
                )
                return

            path, _ = QFileDialog.getSaveFileName(
                self, "Simpan Excel", "", "Excel Files (*.xlsx)"
            )

            if not path:
                return

            # Prepare data
            rows = []
            for soal in self.all_data:
                row = {
                    "ID": soal["id"],
                    "Nomor": soal["nomor"],
                    "Tipe": soal["tipe"],
                    "Petunjuk": soal["petunjuk"],
                    "Soal": soal["soal"],
                    "Kunci": soal["kunci"],
                }

                # Add options
                for i in range(4):
                    row[f"Opsi {i+1}"] = (
                        soal["opsi"][i] if i < len(soal["opsi"]) else ""
                    )

                # Add transcripts if listening
                if soal["tipe"] == "listening":
                    row["Transkrip Soal"] = soal.get("transkrip_soal", "")
                    for i in range(4):
                        row[f"Transkrip Jawaban {i+1}"] = (
                            soal["transkrip_jawaban"][i]
                            if i < len(soal.get("transkrip_jawaban", []))
                            else ""
                        )

                rows.append(row)

            # Create DataFrame and save
            df = pd.DataFrame(rows)
            df.to_excel(path, index=False)

            QMessageBox.information(
                self, "Berhasil", f"Data berhasil diekspor ke:\n{path}"
            )

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Gagal mengekspor data:\n{str(e)}")

    def closeEvent(self, event):
        if self.unsaved:
            reply = QMessageBox.question(
                self,
                "Perubahan Belum Disimpan",
                "Anda memiliki perubahan yang belum disimpan. Simpan sebelum keluar?",
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel,
            )

            if reply == QMessageBox.Save:
                self.simpan_soal()
                event.accept()
            elif reply == QMessageBox.Discard:
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SoalInput()
    window.show()
    sys.exit(app.exec_())
