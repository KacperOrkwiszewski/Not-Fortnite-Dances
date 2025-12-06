import sys
from tkinter.constants import CENTER

from PySide6.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout, QLabel,
    QStackedWidget, QListWidget, QListWidgetItem, QFileDialog, QHBoxLayout, QSizePolicy
)
from PySide6.QtGui import QPainter, QPen, QColor, QPixmap, QFont, QMovie, QPalette
from PySide6.QtCore import Qt, QTimer, QRectF, QObject, Signal, QSize, QUrl

from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtMultimediaWidgets import QVideoWidget


class MainMenu(QWidget):
    """Main menu widget."""
    start_exercise = Signal()
    open_options = Signal()
    open_preferences = Signal()
    open_docs = Signal()
    exit_app = Signal()
    def __init__(self):
        super().__init__()

        # background
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(self.backgroundRole(), QColor("#076e27"))
        self.setPalette(palette)

        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 30)  # left, top, right, bottom

        # window top logo
        image_label = QLabel()
        pixmap = QPixmap("cyber-trener-logo.png")
        pixmap = pixmap.scaledToWidth(200, Qt.SmoothTransformation)
        image_label.setPixmap(pixmap)
        image_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(image_label)

        # add buttons
        labels = ["ROZPOCZNIJ", "OPCJE", "PREFERENCJE", "DOKUMENTACJA", "WYJDŹ"]
        self.buttons = []
        i = 0
        for text in labels:
            row = QHBoxLayout()
            btn = QPushButton(text)
            btn.setMinimumHeight(60)
            btn.setMaximumHeight(100)
            btn.setMinimumWidth(300)
            btn.setMaximumWidth(600)
            btn.setStyleSheet("""
                        QPushButton {
                            background-color: #faf6f1;
                            color: #076e27;
                            border-radius: 15px;
                            padding: 10px 20px;
                            font-family: "Arial";
                            font-weight: bold;
                            font-size: 30px;
                        }
                        QPushButton:hover {
                            background-color: #fcfcfc;
                        }
                        QPushButton:pressed {
                            background-color: #e8e6e6;
                        }
                    """)

            # connect button to signal
            if i == 0:
                btn.clicked.connect(self.start_exercise)
            elif i == 1:
                btn.clicked.connect(self.open_options)
            elif i == 1:
                btn.clicked.connect(self.open_preferences)
            elif i == 1:
                btn.clicked.connect(self.open_docs)
            elif i == 1:
                btn.clicked.connect(self.exit_app)
            i += 1

            row.addWidget(btn)
            layout.addLayout(row)
            self.buttons.append(btn)
        # footer
        footer = QLabel("© 2025 Projekt PSIO: Cyber-Trener. Politechnika Łódzka")
        footer.setStyleSheet("color: #faf6f1; font-size: 12px;")
        footer.setAlignment(Qt.AlignCenter)
        layout.addWidget(footer)

        self.setLayout(layout)


class CircleTimer(QWidget):
    """Timer with animated circle ."""
    finished = Signal()

    def __init__(self, duration_seconds=10):
        super().__init__()
        self.duration = duration_seconds
        self.time_left = duration_seconds

        # background
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(self.backgroundRole(), QColor("#076e27"))
        self.setPalette(palette)

        self.timer = QTimer()
        self.timer.timeout.connect(self.tick)

        # header
        self.header_label = QLabel("ODPOCZNIJ")
        self.header_label.setAlignment(Qt.AlignCenter)
        header_font = QFont("Arial", 40, QFont.Bold)
        self.header_label.setFont(header_font)
        self.header_label.setStyleSheet("color: #faf6f1;")

        layout = QVBoxLayout()
        layout.setContentsMargins(100, 60, 100, 10)
        layout.addWidget(self.header_label)
        layout.addStretch(1)
        self.setLayout(layout)

    def start(self):
        self.time_left = self.duration
        self.timer.start(1000)
        self.update()

    def tick(self):
        self.time_left -= 1
        self.update()

        if self.time_left <= 0:
            self.timer.stop()
            self.finished.emit()

    def paintEvent(self, event):
        """Circular time indicator."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        w = self.width()
        h = self.height()
        size = 300
        x = (w - size) / 2
        y = (h - size) / 2
        rect = QRectF(x, y + 60, size, size)

        # progress
        ratio = self.time_left / self.duration
        angle = int(360 * ratio * 16)

        pen_fg = QPen(QColor("#faf6f1"), 20)
        painter.setPen(pen_fg)
        painter.drawArc(rect, 90 * 16, -angle)

        # time
        painter.setPen(QColor("#faf6f1"))
        font = QFont("Arial", 40, QFont.Bold)
        painter.setFont(font)

        text = f"{self.time_left // 60:02d}:{self.time_left % 60:02d}"
        text_rect = painter.boundingRect(rect, Qt.AlignCenter, text)
        painter.drawText(text_rect, Qt.AlignCenter, text)


class VideoList(QWidget):
    """Ekran z miniaturkami nagrań + odtwarzanie."""
    back = Signal()

    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()

        self.list_widget = QListWidget()
        btn_load = QPushButton("Wczytaj wideo")
        btn_back = QPushButton("Powrót")

        btn_load.clicked.connect(self.load_video)
        btn_back.clicked.connect(self.back)

        layout.addWidget(self.list_widget)
        layout.addWidget(btn_load)
        layout.addWidget(btn_back)

        self.setLayout(layout)

    def load_video(self):
        filename, _ = QFileDialog.getOpenFileName(
            self, "Wybierz wideo", "", "Video Files (*.mp4 *.avi)"
        )
        if not filename:
            return

        item = QListWidgetItem(filename)
        item.setData(Qt.UserRole, filename)
        self.list_widget.addItem(item)


class VideoPlayer(QWidget):
    """Odtwarzacz wideo."""
    back = Signal()

    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()

        self.video_widget = QVideoWidget()
        self.player = QMediaPlayer()
        audio = QAudioOutput()
        self.player.setAudioOutput(audio)
        self.player.setVideoOutput(self.video_widget)

        self.btn_back = QPushButton("Powrót")
        self.btn_back.clicked.connect(self.back)

        layout.addWidget(self.video_widget)
        layout.addWidget(self.btn_back)
        self.setLayout(layout)

    def play_file(self, filename):
        self.player.setSource(filename)
        self.player.play()

class GifWindow(QWidget):
    """Window to show during exercise with MP4 video of the exercise"""
    finish = Signal()
    def __init__(self):
        super().__init__()
        self.video_path = "curl_gif.gif"
        # Background color
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor("#076e27"))
        self.setPalette(palette)

        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(0, 20, 20, 20)

        # Video widget
        self.video_widget = QVideoWidget()
        self.video_widget.setFixedSize(600,600)
        self.video_widget.setAutoFillBackground(True)
        layout.addWidget(self.video_widget,alignment=Qt.AlignCenter)

        # Media player
        self.media_player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.media_player.setAudioOutput(self.audio_output)
        self.media_player.setVideoOutput(self.video_widget)

        # Load video
        self.media_player.setSource(QUrl.fromLocalFile(self.video_path))
        self.media_player.setLoops(-1)  # Loop indefinitely
        self.media_player.play()

        # button
        button_layout = QHBoxLayout()
        button_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.button = QPushButton("ZAKOŃCZ ĆWICZENIE")
        self.button.setStyleSheet("""
                                        QPushButton {
                                            background-color: #faf6f1;
                                            color: #076e27;
                                            border-radius: 15px;
                                            padding: 10px 20px;
                                            font-family: "Arial";
                                            font-weight: bold;
                                            font-size: 30px;
                                        }
                                        QPushButton:hover {
                                            background-color: #fcfcfc;
                                        }
                                        QPushButton:pressed {
                                            background-color: #e8e6e6;
                                        }
                                    """)
        self.button.clicked.connect(self.finish)
        button_layout.addWidget(self.button)
        layout.addLayout(button_layout)
        self.setLayout(layout)

    def change_gif(self,code):
        if code == 1:
            self.video_path = "lateral_gif.gif"
        elif code == 2:
            self.video_path = "barbell_gif.gif"
        elif code == 3:
            self.video_path = "dumbbell_gif.gif"

class App(QStackedWidget):
    """Główne okno aplikacji."""
    def __init__(self):
        super().__init__()
        # ekrany
        self.menu = MainMenu()
        self.gif_screen = GifWindow()
        self.timer_screen = CircleTimer(duration_seconds=100)
        self.video_list = VideoList()
        self.player = VideoPlayer()

        # dodajemy ekrany
        self.addWidget(self.menu)         # index 0
        self.addWidget(self.timer_screen) # index 1
        self.addWidget(self.video_list)   # index 2
        self.addWidget(self.player)       # index 3
        self.addWidget(self.gif_screen) # index 4

        # połączenia sygnałów
        self.menu.start_exercise.connect(self.goto_gif)
        self.timer_screen.finished.connect(self.goto_menu)

        self.menu.open_docs.connect(lambda: print("TODO: dokumentacja"))
        self.menu.exit_app.connect(lambda: sys.exit(0))

        self.video_list.list_widget.itemDoubleClicked.connect(self.open_video)

    def goto_timer(self):
        self.setCurrentIndex(1)
        self.timer_screen.start()

    def goto_menu(self):
        self.setCurrentIndex(0)

    def open_video(self, item):
        filename = item.data(Qt.UserRole)
        self.player.play_file(filename)
        self.setCurrentIndex(3)

    def goto_gif(self):
        self.setCurrentIndex(4)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = App()
    window.resize(800, 600)
    window.show()
    sys.exit(app.exec())
