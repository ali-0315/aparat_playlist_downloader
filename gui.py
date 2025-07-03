
import os
import platform
import re
import subprocess
import sys
import asyncio
from urllib.parse import urlparse

from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer, QMimeData
from PyQt5.QtGui import QFont, QDragEnterEvent, QDropEvent
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
    QListWidget,
    QListWidgetItem,
    QTextEdit,
    QTabWidget,
    QCheckBox,
    QSpinBox,
    QGroupBox,
    QSplitter,
)

from core import AparatDownloader


class PreviewWorker(QThread):
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)

    def __init__(self, playlist_id):
        super().__init__()
        self.playlist_id = playlist_id

    def run(self):
        try:
            downloader = AparatDownloader(playlist_id=self.playlist_id)
            info = downloader.get_playlist_info()
            if info:
                self.finished.emit(info)
            else:
                self.error.emit("خطا در دریافت اطلاعات پلی‌لیست")
        except Exception as e:
            self.error.emit(f"خطا: {str(e)}")


class DownloadWorker(QThread):
    finished = pyqtSignal(bool, str)
    progress_update = pyqtSignal(str, float, int, int)  # title, progress, downloaded, total

    def __init__(self, playlist_id, quality, for_download_manager, destination_path, auto_quality=False, max_concurrent=3):
        super().__init__()
        self.playlist_id = playlist_id
        self.quality = quality
        self.for_download_manager = for_download_manager
        self.destination_path = destination_path
        self.auto_quality = auto_quality
        self.max_concurrent = max_concurrent

    def progress_callback(self, title, progress, downloaded, total):
        self.progress_update.emit(title, progress, downloaded, total)

    def run(self):
        try:
            downloader = AparatDownloader(
                playlist_id=self.playlist_id,
                quality=self.quality,
                for_download_manager=self.for_download_manager,
                destination_path=self.destination_path,
                progress_callback=self.progress_callback,
                auto_quality=self.auto_quality,
                max_concurrent_downloads=self.max_concurrent,
            )
            
            # Use async version
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(downloader.download_playlist_async())
            loop.close()
            
            if result:
                self.finished.emit(True, "عملیات با موفقیت به پایان رسید.")
            else:
                self.finished.emit(False, "خطا در دانلود پلی‌لیست")
        except Exception as e:
            error_msg = f"ارور هنگام انجام عملیات: {str(e)}\nلطفا جزئیات ارور رو به عنوان issue در گیت هاب ارسال کنید تا بررسی کنیم."
            self.finished.emit(False, error_msg)


class ProgressWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.downloads = {}  # Track individual downloads

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)

        # Title
        title = QLabel("صف دانلود")
        title.setStyleSheet("font-weight: bold; font-size: 14px; padding: 5px;")
        layout.addWidget(title)

        # Download list
        self.download_list = QListWidget()
        self.download_list.setStyleSheet("""
        QListWidget {
            border: 1px solid #e0e0e0;
            border-radius: 5px;
            background-color: white;
        }
        QListWidgetItem {
            padding: 5px;
            border-bottom: 1px solid #f0f0f0;
        }
        """)
        layout.addWidget(self.download_list)

    def add_download(self, title):
        """Add a new download to the queue"""
        item = QListWidgetItem()
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(5, 5, 5, 5)

        # Title
        title_label = QLabel(title)
        title_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(title_label)

        # Progress bar
        progress_bar = QProgressBar()
        progress_bar.setRange(0, 100)
        progress_bar.setValue(0)
        progress_bar.setStyleSheet("""
        QProgressBar {
            border: 1px solid #bdbdbd;
            border-radius: 3px;
            text-align: center;
            height: 20px;
        }
        QProgressBar::chunk {
            background-color: #4CAF50;
            border-radius: 2px;
        }
        """)
        layout.addWidget(progress_bar)

        # Status label
        status_label = QLabel("در انتظار...")
        status_label.setStyleSheet("color: #666; font-size: 10px;")
        layout.addWidget(status_label)

        item.setSizeHint(widget.sizeHint())
        self.download_list.addItem(item)
        self.download_list.setItemWidget(item, widget)

        self.downloads[title] = {
            'item': item,
            'widget': widget,
            'progress_bar': progress_bar,
            'status_label': status_label
        }

    def update_progress(self, title, progress, downloaded, total):
        """Update download progress"""
        if title in self.downloads:
            download_info = self.downloads[title]
            download_info['progress_bar'].setValue(int(progress))
            
            # Format file sizes
            downloaded_mb = downloaded / (1024 * 1024)
            total_mb = total / (1024 * 1024)
            status_text = f"{downloaded_mb:.1f} MB / {total_mb:.1f} MB ({progress:.1f}%)"
            download_info['status_label'].setText(status_text)

    def mark_completed(self, title):
        """Mark download as completed"""
        if title in self.downloads:
            download_info = self.downloads[title]
            download_info['progress_bar'].setValue(100)
            download_info['status_label'].setText("تکمیل شد")
            download_info['status_label'].setStyleSheet("color: #4CAF50; font-size: 10px; font-weight: bold;")

    def clear_downloads(self):
        """Clear all downloads"""
        self.download_list.clear()
        self.downloads.clear()


class PreviewWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)

        # Title
        title = QLabel("پیش‌نمایش پلی‌لیست")
        title.setStyleSheet("font-weight: bold; font-size: 14px; padding: 5px;")
        layout.addWidget(title)

        # Info display
        self.info_display = QTextEdit()
        self.info_display.setReadOnly(True)
        self.info_display.setMaximumHeight(200)
        self.info_display.setStyleSheet("""
        QTextEdit {
            border: 1px solid #e0e0e0;
            border-radius: 5px;
            background-color: #f9f9f9;
            padding: 10px;
        }
        """)
        layout.addWidget(self.info_display)

    def show_playlist_info(self, info):
        """Display playlist information"""
        html_content = f"""
        <div style="direction: rtl; text-align: right;">
            <h3 style="color: #2196F3;">{info['title']}</h3>
            <p><strong>تعداد ویدئوها:</strong> {info['video_count']}</p>
            <p><strong>شناسه پلی‌لیست:</strong> {info.get('playlist_id', 'نامشخص')}</p>
            <hr>
            <h4>فهرست ویدئوها:</h4>
            <ul>
        """
        
        video_count = 0
        for video in info['videos']:
            if video['type'] == 'Video' and video_count < 10:  # Show first 10 videos
                title = video['attributes']['title']
                html_content += f"<li>{title}</li>"
                video_count += 1
        
        if info['video_count'] > 10:
            html_content += f"<li><em>... و {info['video_count'] - 10} ویدئوی دیگر</em></li>"
        
        html_content += """
            </ul>
        </div>
        """
        
        self.info_display.setHtml(html_content)

    def clear_info(self):
        """Clear preview information"""
        self.info_display.clear()


class ModernApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.quality_input = None
        self.browse_button = None
        self.folder_input = None
        self.link_input = None
        self.run_button = None
        self.preview_button = None
        self.combo_box = None
        self.auto_quality_checkbox = None
        self.concurrent_spinbox = None
        self.frame_style = None
        self.worker = None
        self.preview_worker = None
        self.progress_widget = None
        self.preview_widget = None
        self.tab_widget = None
        
        self.setAcceptDrops(True)  # Enable drag and drop
        self.init_ui()

    def dragEnterEvent(self, event: QDragEnterEvent):
        """Handle drag enter event"""
        if event.mimeData().hasText():
            text = event.mimeData().text().strip()
            if self.is_valid_playlist_url(text):
                event.acceptProposedAction()
            else:
                event.ignore()
        else:
            event.ignore()

    def dropEvent(self, event: QDropEvent):
        """Handle drop event"""
        text = event.mimeData().text().strip()
        if self.is_valid_playlist_url(text):
            self.link_input.setText(text)
            self.link_input.setStyleSheet("""
            QLineEdit {
                border: 2px solid #4CAF50;
                border-radius: 4px;
                padding: 5px 10px;
                background-color: #E8F5E8;
            }
            """)
            
            # Auto-trigger preview
            QTimer.singleShot(500, self.preview_playlist)
            
            event.acceptProposedAction()

    def is_valid_playlist_url(self, text):
        """Check if text is a valid playlist URL or ID"""
        if text.isdigit():
            return True
        
        aparat_pattern = re.compile(r"^https://www\.aparat\.com/playlist/\d+/?$")
        return bool(aparat_pattern.match(text))

    def init_ui(self):
        self.setWindowTitle("دانلود لیست پخش آپارات - نسخه پیشرفته")
        self.setFixedSize(900, 700)

        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        self.setLayoutDirection(Qt.RightToLeft)

        # Create splitter for resizable panels
        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)

        # Left panel - Controls
        left_panel = self.create_controls_panel()
        splitter.addWidget(left_panel)

        # Right panel - Progress and Preview
        right_panel = self.create_info_panel()
        splitter.addWidget(right_panel)

        # Set splitter proportions
        splitter.setSizes([400, 480])

        self.center()
        self.show()

    def create_controls_panel(self):
        """Create the main controls panel"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)

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

        # Operation selection
        combo_frame = QFrame()
        combo_frame.setStyleSheet(self.frame_style)
        combo_layout = QVBoxLayout(combo_frame)

        combo_label = QLabel("عملیات:")
        combo_label.setFont(font)
        combo_label.setStyleSheet("QLabel { border: 0; }")
        
        self.combo_box = QComboBox()
        self.combo_box.addItems(["دانلود", "استخراج لینک ها"])
        self.combo_box.setMinimumHeight(35)
        self.combo_box.setFont(font)
        self.combo_box.setView(QListView())

        combo_layout.addWidget(combo_label)
        combo_layout.addWidget(self.combo_box)
        layout.addWidget(combo_frame)

        # Playlist URL input with drag & drop hint
        link_frame = QFrame()
        link_frame.setStyleSheet(self.frame_style)
        link_layout = QVBoxLayout(link_frame)

        link_label = QLabel("لینک و یا شناسه لیست پخش (drag & drop پشتیبانی می‌شود):")
        link_label.setStyleSheet("QLabel { border: 0; }")
        link_label.setFont(font)
        
        self.link_input = QLineEdit()
        self.link_input.setPlaceholderText("نمونه: 822374 یا https://www.aparat.com/playlist/822374")
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

        # Preview button
        preview_layout = QHBoxLayout()
        self.preview_button = QPushButton("پیش‌نمایش")
        self.preview_button.setMinimumHeight(30)
        self.preview_button.setFont(font)
        self.preview_button.setCursor(Qt.PointingHandCursor)
        self.preview_button.setStyleSheet("""
        QPushButton {
            background-color: #FF9800;
            color: white;
            border-radius: 4px;
            border: none;
            padding: 5px 15px;
        }
        QPushButton:hover {
            background-color: #F57C00;
        }
        QPushButton:pressed {
            background-color: #E65100;
        }
        """)
        self.preview_button.clicked.connect(self.preview_playlist)
        
        preview_layout.addWidget(self.link_input)
        preview_layout.addWidget(self.preview_button)

        link_layout.addWidget(link_label)
        link_layout.addLayout(preview_layout)
        layout.addWidget(link_frame)

        # Quality settings
        quality_frame = QFrame()
        quality_frame.setStyleSheet(self.frame_style)
        quality_layout = QVBoxLayout(quality_frame)

        quality_label = QLabel("تنظیمات کیفیت:")
        quality_label.setStyleSheet("QLabel { border: 0; }")
        quality_label.setFont(font)

        # Auto quality checkbox
        self.auto_quality_checkbox = QCheckBox("انتخاب خودکار بهترین کیفیت")
        self.auto_quality_checkbox.setFont(font)
        self.auto_quality_checkbox.stateChanged.connect(self.toggle_quality_input)

        self.quality_input = QLineEdit()
        self.quality_input.setPlaceholderText("نمونه: 144, 240, 360, 480, 720, 1080")
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

        quality_layout.addWidget(quality_label)
        quality_layout.addWidget(self.auto_quality_checkbox)
        quality_layout.addWidget(self.quality_input)
        layout.addWidget(quality_frame)

        # Advanced settings
        advanced_frame = QFrame()
        advanced_frame.setStyleSheet(self.frame_style)
        advanced_layout = QVBoxLayout(advanced_frame)

        advanced_label = QLabel("تنظیمات پیشرفته:")
        advanced_label.setStyleSheet("QLabel { border: 0; }")
        advanced_label.setFont(font)

        # Concurrent downloads
        concurrent_layout = QHBoxLayout()
        concurrent_layout.addWidget(QLabel("دانلود همزمان:"))
        self.concurrent_spinbox = QSpinBox()
        self.concurrent_spinbox.setRange(1, 10)
        self.concurrent_spinbox.setValue(3)
        self.concurrent_spinbox.setMinimumHeight(30)
        concurrent_layout.addWidget(self.concurrent_spinbox)
        concurrent_layout.addStretch()

        advanced_layout.addWidget(advanced_label)
        advanced_layout.addLayout(concurrent_layout)
        layout.addWidget(advanced_frame)

        # Output folder
        folder_frame = QFrame()
        folder_frame.setStyleSheet(self.frame_style)
        folder_layout = QVBoxLayout(folder_frame)

        folder_label = QLabel("مسیر خروجی:")
        folder_label.setStyleSheet("QLabel { border: 0; }")
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
        layout.addWidget(folder_frame)

        # Run button
        self.run_button = QPushButton("شروع دانلود")
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

        layout.addWidget(self.run_button)
        layout.addStretch()

        return panel

    def create_info_panel(self):
        """Create the information panel with tabs"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(5, 5, 5, 5)

        # Tab widget
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
        QTabWidget::pane {
            border: 1px solid #e0e0e0;
            border-radius: 5px;
        }
        QTabBar::tab {
            background-color: #f5f5f5;
            padding: 8px 16px;
            margin-right: 2px;
            border-top-left-radius: 5px;
            border-top-right-radius: 5px;
        }
        QTabBar::tab:selected {
            background-color: #2196F3;
            color: white;
        }
        """)

        # Preview tab
        self.preview_widget = PreviewWidget()
        self.tab_widget.addTab(self.preview_widget, "پیش‌نمایش")

        # Progress tab
        self.progress_widget = ProgressWidget()
        self.tab_widget.addTab(self.progress_widget, "پیشرفت دانلود")

        layout.addWidget(self.tab_widget)
        return panel

    def toggle_quality_input(self, state):
        """Toggle quality input based on auto quality checkbox"""
        self.quality_input.setEnabled(state != Qt.Checked)
        if state == Qt.Checked:
            self.quality_input.setPlaceholderText("کیفیت به طور خودکار انتخاب می‌شود")
        else:
            self.quality_input.setPlaceholderText("نمونه: 144, 240, 360, 480, 720, 1080")

    def preview_playlist(self):
        """Preview playlist information"""
        link = self.link_input.text().strip()
        if not link:
            return

        playlist_id = link if link.isdigit() else link.split("/")[-1]
        
        self.preview_button.setEnabled(False)
        self.preview_button.setText("در حال بارگذاری...")
        
        self.preview_worker = PreviewWorker(playlist_id)
        self.preview_worker.finished.connect(self.on_preview_finished)
        self.preview_worker.error.connect(self.on_preview_error)
        self.preview_worker.start()

    def on_preview_finished(self, info):
        """Handle preview completion"""
        self.preview_widget.show_playlist_info(info)
        self.tab_widget.setCurrentIndex(0)  # Switch to preview tab
        
        self.preview_button.setEnabled(True)
        self.preview_button.setText("پیش‌نمایش")

    def on_preview_error(self, error):
        """Handle preview error"""
        self.preview_widget.clear_info()
        self.show_error_message([error])
        
        self.preview_button.setEnabled(True)
        self.preview_button.setText("پیش‌نمایش")

    def center(self):
        """Center the window on screen"""
        frame_geometry = self.frameGeometry()
        screen_center = QApplication.desktop().availableGeometry().center()
        frame_geometry.moveCenter(screen_center)
        self.move(frame_geometry.topLeft())

    def browse_folder(self):
        """Browse for output folder"""
        folder_path = QFileDialog.getExistingDirectory(self, "انتخاب پوشه")
        if folder_path:
            self.folder_input.setText(folder_path)

    @staticmethod
    def show_error_message(errors):
        """Show error message dialog"""
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
        self.quality_input.setEnabled(enabled and not self.auto_quality_checkbox.isChecked())
        self.folder_input.setEnabled(enabled)
        self.browse_button.setEnabled(enabled)
        self.combo_box.setEnabled(enabled)
        self.auto_quality_checkbox.setEnabled(enabled)
        self.concurrent_spinbox.setEnabled(enabled)
        self.preview_button.setEnabled(enabled)
        self.run_button.setEnabled(enabled)

        if not enabled:
            self.run_button.setText("در حال پردازش...")
        else:
            self.run_button.setText("شروع دانلود")

    def on_download_progress(self, title, progress, downloaded, total):
        """Handle download progress updates"""
        self.progress_widget.update_progress(title, progress, downloaded, total)

    def on_download_finished(self, success, message):
        """Handle download completion"""
        # Re-enable UI
        self.set_ui_enabled(True)

        # Switch to progress tab
        self.tab_widget.setCurrentIndex(1)

        # Show result message
        if success:
            msg_box = QMessageBox()
            msg_box.setWindowTitle("موفقیت")
            msg_box.setText(message)
            msg_box.addButton("تایید", QMessageBox.AcceptRole)
            show_output_button = msg_box.addButton("نمایش خروجی", QMessageBox.ActionRole)
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

        # Clean up worker
        if self.worker:
            self.worker.deleteLater()
            self.worker = None

    def run_action(self):
        """Execute download action"""
        selected_option = self.combo_box.currentText()
        link = self.link_input.text().strip()
        quality = self.quality_input.text().strip()
        folder_path = self.folder_input.text().strip()
        auto_quality = self.auto_quality_checkbox.isChecked()
        max_concurrent = self.concurrent_spinbox.value()

        errors = []

        # Validate inputs
        if not link:
            errors.append("لطفاً لینک و یا شناسه را وارد کنید.")
        elif not self.is_valid_playlist_url(link):
            errors.append("ورودی باید شناسه عددی و یا به فرمت https://www.aparat.com/playlist/822374 باشد.")

        if not auto_quality and not quality:
            errors.append("لطفاً کیفیت را وارد کنید یا گزینه انتخاب خودکار را فعال کنید.")
        elif not auto_quality and not quality.isdigit():
            errors.append("کیفیت باید عددی باشد.")

        if not folder_path:
            errors.append("لطفاً مسیر خروجی را وارد کنید.")
        elif not os.path.exists(folder_path) or not os.path.isdir(folder_path):
            errors.append("مسیر پوشه وارد شده وجود ندارد یا یک پوشه نیست.")

        if errors:
            self.show_error_message(errors)
            return

        # Clear previous progress and prepare for new download
        self.progress_widget.clear_downloads()
        
        # Disable UI during operation
        self.set_ui_enabled(False)

        # Start download in background thread
        playlist_id = link if link.isdigit() else link.split("/")[-1]
        for_download_manager = selected_option == "استخراج لینک ها"

        self.worker = DownloadWorker(
            playlist_id=playlist_id,
            quality=quality if not auto_quality else "720",  # Default for auto
            for_download_manager=for_download_manager,
            destination_path=folder_path,
            auto_quality=auto_quality,
            max_concurrent=max_concurrent
        )

        self.worker.finished.connect(self.on_download_finished)
        self.worker.progress_update.connect(self.on_download_progress)
        self.worker.start()

        # Switch to progress tab
        self.tab_widget.setCurrentIndex(1)


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
