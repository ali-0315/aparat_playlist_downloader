import os
import platform
import re
import subprocess
import sys

from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QComboBox,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QLabel,
    QFileDialog,
    QFrame,
    QStyle,
    QListView,
    QMessageBox,
    QProgressBar,
)

from core import AparatDownloader


class DownloadWorker(QThread):
    finished = pyqtSignal(bool, str)  # success, message

    def __init__(self, playlist_id, quality, for_download_manager, destination_path):
        super().__init__()
        self.playlist_id = playlist_id
        self.quality = quality
        self.for_download_manager = for_download_manager
        self.destination_path = destination_path

    def run(self):
        try:
            downloader = AparatDownloader(
                playlist_id=self.playlist_id,
                quality=self.quality,
                for_download_manager=self.for_download_manager,
                destination_path=self.destination_path,
            )
            downloader.download_playlist()
            self.finished.emit(True, "عملیات با موفقیت به پایان رسید.")
        except Exception as e:
            error_msg = f"ارور هنگام انجام عملیات: {str(e)}\nلطفا جزئیات ارور رو به عنوان issue در گیت هاب ارسال کنید تا بررسی کنیم."
            self.finished.emit(False, error_msg)


class LoadingDialog(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("در حال پردازش...")
        self.setFixedSize(300, 120)
        self.setWindowFlags(Qt.Dialog | Qt.WindowTitleHint)
        self.setWindowModality(Qt.ApplicationModal)

        # Center the dialog
        if parent:
            parent_geo = parent.geometry()
            x = parent_geo.x() + (parent_geo.width() - self.width()) // 2
            y = parent_geo.y() + (parent_geo.height() - self.height()) // 2
            self.move(x, y)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Loading label
        self.loading_label = QLabel("در حال پردازش...")
        self.loading_label.setAlignment(Qt.AlignCenter)
        font = QFont()
        font.setFamily("Segoe UI")
        font.setPointSize(12)
        self.loading_label.setFont(font)
        layout.addWidget(self.loading_label)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        self.progress_bar.setStyleSheet("""
        QProgressBar {
            border: 2px solid #e0e0e0;
            border-radius: 5px;
            text-align: center;
            background-color: #f5f5f5;
        }
        QProgressBar::chunk {
            background-color: #2196F3;
            border-radius: 3px;
        }
        """)
        layout.addWidget(self.progress_bar)

        # Animated dots for loading text
        self.dots_timer = QTimer()
        self.dots_timer.timeout.connect(self.animate_dots)
        self.dots_count = 0
        self.base_text = "در حال پردازش"

    def show(self):
        super().show()
        self.dots_timer.start(500)  # Update every 500ms

    def hide(self):
        super().hide()
        self.dots_timer.stop()

    def animate_dots(self):
        self.dots_count = (self.dots_count + 1) % 4
        dots = "." * self.dots_count
        self.loading_label.setText(f"{self.base_text}{dots}")


class ModernApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.quality_input = None
        self.browse_button = None
        self.folder_input = None
        self.link_input = None
        self.run_button = None
        self.combo_box = None
        self.frame_style = None
        self.worker = None
        self.loading_dialog = None
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("دانلود لیست پخش آپارات")
        self.setFixedSize(600, 500)

        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        self.setLayoutDirection(Qt.RightToLeft)

        self.frame_style = """
        QFrame {
            background-color: #f5f5f5;
            border-radius: 8px;
            border: 1px solid #e0e0e0;
        }
        """

        font = QFont()
        font.setFamily("Segoe UI")
        font.setPointSize(10)

        combo_frame = QFrame()
        combo_frame.setStyleSheet(self.frame_style)
        combo_layout = QVBoxLayout(combo_frame)

        combo_label = QLabel("عملیات:")
        combo_label.setFont(font)
        combo_label.setStyleSheet("""
        QLabel {
            border: 0;
        }
        """)
        self.combo_box = QComboBox()
        self.combo_box.addItems(["دانلود", "استخراج لینک ها"])
        self.combo_box.setMinimumHeight(35)
        self.combo_box.setFont(font)
        self.combo_box.setView(QListView())

        combo_layout.addWidget(combo_label)
        combo_layout.addWidget(self.combo_box)
        main_layout.addWidget(combo_frame)

        link_frame = QFrame()
        link_frame.setStyleSheet(self.frame_style)
        link_layout = QVBoxLayout(link_frame)

        link_label = QLabel("لینک و یا شناسه لیست پخش (playlist) آپارات را وارد کنید:")
        link_label.setStyleSheet("""
        QLabel {
            border: 0;
        }
        """)
        link_label.setFont(font)
        self.link_input = QLineEdit()
        self.link_input.setPlaceholderText(
            "نمونه: 822374 یا https://www.aparat.com/playlist/822374"
        )
        self.link_input.setMinimumHeight(35)
        self.link_input.setFont(font)
        self.link_input.setStyleSheet("""
        QLineEdit {
            border: 1px solid #bdbdbd;
            border-radius: 4px;
            padding: 5px 10px;
            background-color: white;
        }
        QLineEdit:hover {
            border: 1px solid #2196F3;
        }
        QLineEdit:focus {
            border: 1px solid #2196F3;
        }
        """)

        link_layout.addWidget(link_label)
        link_layout.addWidget(self.link_input)
        main_layout.addWidget(link_frame)

        quality_frame = QFrame()
        quality_frame.setStyleSheet(self.frame_style)
        link_layout = QVBoxLayout(quality_frame)

        quality_label = QLabel("کیفیت مورد نظر را وارد کنید:")
        quality_label.setStyleSheet("""
        QLabel {
            border: 0;
        }
        """)
        quality_label.setFont(font)
        self.quality_input = QLineEdit()
        self.quality_input.setPlaceholderText(
            "نمونه: 144 , 240 , 360 , 480 , 720 , 1080"
        )
        self.quality_input.setMinimumHeight(35)
        self.quality_input.setFont(font)
        self.quality_input.setStyleSheet("""
        QLineEdit {
            border: 1px solid #bdbdbd;
            border-radius: 4px;
            padding: 5px 10px;
            background-color: white;
        }
        QLineEdit:hover {
            border: 1px solid #2196F3;
        }
        QLineEdit:focus {
            border: 1px solid #2196F3;
        }
        """)

        link_layout.addWidget(quality_label)
        link_layout.addWidget(self.quality_input)
        main_layout.addWidget(quality_frame)

        folder_frame = QFrame()
        folder_frame.setStyleSheet(self.frame_style)
        folder_layout = QVBoxLayout(folder_frame)

        folder_label = QLabel("مسیر:")
        folder_label.setStyleSheet("""
        QLabel {
            border: 0;
        }
        """)
        folder_label.setFont(font)

        folder_input_layout = QHBoxLayout()
        self.folder_input = QLineEdit()
        self.folder_input.setPlaceholderText("مسیر خروجی را وارد کنید...")
        self.folder_input.setMinimumHeight(35)
        self.folder_input.setFont(font)
        self.folder_input.setStyleSheet("""
        QLineEdit {
            border: 1px solid #bdbdbd;
            border-radius: 4px;
            padding: 5px 10px;
            background-color: white;
        }
        QLineEdit:hover {
            border: 1px solid #2196F3;
        }
        """)

        self.browse_button = QPushButton("انتخاب")
        self.browse_button.setMinimumHeight(35)
        self.browse_button.setFont(font)
        self.browse_button.setIcon(self.style().standardIcon(QStyle.SP_DirOpenIcon))
        self.browse_button.setCursor(Qt.PointingHandCursor)
        self.browse_button.setStyleSheet("""
        QPushButton {
            background-color: #e0e0e0;
            border-radius: 4px;
            border: none;
            padding: 5px 15px;
        }
        QPushButton:hover {
            background-color: #d0d0d0;
        }
        QPushButton:pressed {
            background-color: #c0c0c0;
        }
        """)
        self.browse_button.clicked.connect(self.browse_folder)

        folder_input_layout.addWidget(self.folder_input)
        folder_input_layout.addWidget(self.browse_button)

        folder_layout.addWidget(folder_label)
        folder_layout.addLayout(folder_input_layout)
        main_layout.addWidget(folder_frame)

        self.run_button = QPushButton("اجرا")
        self.run_button.setMinimumHeight(45)
        self.run_button.setFont(font)
        self.run_button.setCursor(Qt.PointingHandCursor)
        self.run_button.setStyleSheet("""
        QPushButton {
            background-color: #2196F3;
            color: white;
            border-radius: 5px;
            border: none;
            padding: 5px 15px;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #1976D2;
        }
        QPushButton:pressed {
            background-color: #0D47A1;
        }
        QPushButton:disabled {
            background-color: #bdbdbd;
        }
        """)
        self.run_button.clicked.connect(self.run_action)

        main_layout.addWidget(self.run_button)

        main_layout.addStretch()

        self.center()
        self.show()

    def center(self):
        frame_geometry = self.frameGeometry()
        screen_center = QApplication.desktop().availableGeometry().center()
        frame_geometry.moveCenter(screen_center)
        self.move(frame_geometry.topLeft())

    def browse_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, "انتخاب پوشه")
        if folder_path:
            self.folder_input.setText(folder_path)

    @staticmethod
    def show_error_message(errors):
        error_msg = QMessageBox()
        error_msg.setIcon(QMessageBox.Critical)
        error_msg.setWindowTitle("خطا")
        error_msg.setText("لطفاً خطاهای زیر را برطرف کنید:")

        error_text = "\n".join([f"- {err}" for err in errors])
        error_msg.setInformativeText(error_text)

        error_msg.setStandardButtons(QMessageBox.Ok)
        ok_button = error_msg.button(QMessageBox.Ok)
        ok_button.setText("باشه")
        error_msg.exec_()

    def set_ui_enabled(self, enabled):
        """Enable/disable UI elements during operation"""
        self.link_input.setEnabled(enabled)
        self.quality_input.setEnabled(enabled)
        self.folder_input.setEnabled(enabled)
        self.browse_button.setEnabled(enabled)
        self.combo_box.setEnabled(enabled)
        self.run_button.setEnabled(enabled)

        if not enabled:
            self.run_button.setText("در حال پردازش...")
        else:
            self.run_button.setText("اجرا")

    def on_download_finished(self, success, message):
        """Handle download completion"""
        # Hide loading dialog
        if self.loading_dialog:
            self.loading_dialog.hide()

        # Re-enable UI
        self.set_ui_enabled(True)

        # Show result message
        if success:
            msg_box = QMessageBox()
            msg_box.setWindowTitle("موفقیت")
            msg_box.setText(message)
            msg_box.addButton("تایید", QMessageBox.AcceptRole)
            show_output_button = msg_box.addButton(
                "نمایش خروجی", QMessageBox.ActionRole
            )
            msg_box.exec_()
            if msg_box.clickedButton() == show_output_button:
                folder_path = self.folder_input.text()
                if os.path.exists(folder_path):
                    if platform.system() == "Windows":
                        os.startfile(folder_path)
                    elif platform.system() == "Darwin":
                        subprocess.call(["open", folder_path])
                    else:
                        subprocess.call(["xdg-open", folder_path])
        else:
            msg_box = QMessageBox()
            msg_box.setWindowTitle("ناموفق")
            msg_box.setText(message)
            msg_box.addButton("تایید", QMessageBox.AcceptRole)
            msg_box.exec_()

        self.link_input.clear()
        self.folder_input.clear()

        # Clean up worker
        if self.worker:
            self.worker.deleteLater()
            self.worker = None

    def run_action(self):
        selected_option = self.combo_box.currentText()
        link = self.link_input.text()
        quality = self.quality_input.text()
        folder_path = self.folder_input.text()

        errors = []

        if not link:
            errors.append("لطفاً لینک و یا شناسه را وارد کنید.")
            self.link_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #f44336;
                border-radius: 6px;
                padding: 8px 15px;
                background-color: #ffebee;
            }
            """)
        else:
            is_valid = False

            if link.isdigit():
                is_valid = True
            else:
                aparat_pattern = re.compile(
                    r"^https://www\.aparat\.com/playlist/\d+/?$"
                )
                if aparat_pattern.match(link):
                    is_valid = True

            if not is_valid:
                errors.append(
                    "ورودی باید شناسه عددی و یا به فرمت https://www.aparat.com/playlist/822374 باشد."
                )
                self.link_input.setStyleSheet("""
                QLineEdit {
                    border: 1px solid #f44336;
                    border-radius: 6px;
                    padding: 8px 15px;
                    background-color: #ffebee;
                }
                """)
            else:
                self.link_input.setStyleSheet("""
                QLineEdit {
                    border: 1px solid #bdbdbd;
                    border-radius: 6px;
                    padding: 8px 15px;
                    background-color: white;
                }
                QLineEdit:hover {
                    border: 1px solid #2196F3;
                }
                """)

        if not quality:
            errors.append("لطفاً کیفیت را وارد کنید.")
            self.quality_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #f44336;
                border-radius: 6px;
                padding: 8px 15px;
                background-color: #ffebee;
            }
            """)
        else:
            if not quality.isdigit():
                errors.append("ورودی باید عددی باشد.")
                self.quality_input.setStyleSheet("""
                QLineEdit {
                    border: 1px solid #f44336;
                    border-radius: 6px;
                    padding: 8px 15px;
                    background-color: #ffebee;
                }
                """)
            else:
                self.quality_input.setStyleSheet("""
                QLineEdit {
                    border: 1px solid #bdbdbd;
                    border-radius: 6px;
                    padding: 8px 15px;
                    background-color: white;
                }
                QLineEdit:hover {
                    border: 1px solid #2196F3;
                }
                """)

        if not folder_path:
            errors.append("لطفاً مسیر خروجی را وارد کنید.")
            self.folder_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #f44336;
                border-radius: 6px;
                padding: 8px 15px;
                background-color: #ffebee;
            }
            """)
            self.browse_button.setStyleSheet("""
            QPushButton {
                border: 1px solid #f44336;
                border-radius: 6px;
                padding: 8px 15px;
                background-color: #ffebee;
            }
            """)
        else:
            if not os.path.exists(folder_path) or not os.path.isdir(folder_path):
                errors.append("مسیر پوشه وارد شده وجود ندارد یا یک پوشه نیست.")
                self.folder_input.setStyleSheet("""
                QLineEdit {
                    border: 1px solid #f44336;
                    border-radius: 6px;
                    padding: 8px 15px;
                    background-color: #ffebee;
                }
                """)
            else:
                self.folder_input.setStyleSheet("""
                QLineEdit {
                    border: 1px solid #bdbdbd;
                    border-radius: 6px;
                    padding: 8px 15px;
                    background-color: white;
                }
                QLineEdit:hover {
                    border: 1px solid #2196F3;
                }
                """)
                self.browse_button.setStyleSheet("""
                QPushButton {
                    border: 1px solid #bdbdbd;
                    border-radius: 6px;
                    padding: 8px 15px;
                    background-color: white;
                }
                """)

        if errors:
            self.show_error_message(errors)
            return

        # Disable UI during operation
        self.set_ui_enabled(False)

        # Show loading dialog
        self.loading_dialog = LoadingDialog(self)
        self.loading_dialog.show()

        # Start download in background thread
        playlist_id = link if link.isdigit() else link.split("/")[-1]
        for_download_manager = selected_option == "استخراج لینک ها"

        self.worker = DownloadWorker(
            playlist_id=playlist_id,
            quality=quality,
            for_download_manager=for_download_manager,
            destination_path=folder_path
        )

        self.worker.finished.connect(self.on_download_finished)
        self.worker.start()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    app.setStyleSheet("""
    QMainWindow {
        background-color: white;
    }
    QLabel {
        color: #424242;
    }
    """)

    window = ModernApp()
    sys.exit(app.exec_())
