# audio_trim.py

import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QFileDialog,
    QVBoxLayout, QWidget, QLabel, QHBoxLayout, QSlider
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QIcon
from pydub import AudioSegment
from pydub.playback import play
import threading
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import os

class AudioTrimApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Audio Trim Pro")
        self.setGeometry(200, 100, 900, 600)
        self.setStyleSheet("background-color: #1e1e1e; color: white;")
        self.audio = None
        self.audio_path = ""
        self.start_trim = 0
        self.end_trim = 0
        self.initUI()

    def initUI(self):
        main_layout = QVBoxLayout()
        control_layout = QHBoxLayout()

        self.label = QLabel("No audio loaded")
        self.label.setStyleSheet("font-size: 18px;")

        self.load_btn = QPushButton("Load Audio")
        self.load_btn.clicked.connect(self.load_audio)

        self.play_btn = QPushButton("Play")
        self.play_btn.clicked.connect(self.play_audio)

        self.trim_btn = QPushButton("Export Trim")
        self.trim_btn.clicked.connect(self.export_trim)

        self.slider_start = QSlider(Qt.Horizontal)
        self.slider_start.setRange(0, 100)
        self.slider_start.setValue(0)
        self.slider_start.valueChanged.connect(self.update_start)

        self.slider_end = QSlider(Qt.Horizontal)
        self.slider_end.setRange(0, 100)
        self.slider_end.setValue(100)
        self.slider_end.valueChanged.connect(self.update_end)

        self.canvas = FigureCanvas(plt.figure())

        control_layout.addWidget(self.load_btn)
        control_layout.addWidget(self.play_btn)
        control_layout.addWidget(self.trim_btn)

        main_layout.addWidget(self.label)
        main_layout.addWidget(self.canvas)
        main_layout.addWidget(QLabel("Start Trim"))
        main_layout.addWidget(self.slider_start)
        main_layout.addWidget(QLabel("End Trim"))
        main_layout.addWidget(self.slider_end)
        main_layout.addLayout(control_layout)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

    def load_audio(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open Audio", "", "Audio Files (*.mp3 *.wav *.ogg *.flac)")
        if file_path:
            self.audio_path = file_path
            self.audio = AudioSegment.from_file(file_path)
            self.label.setText(f"Loaded: {os.path.basename(file_path)}")
            self.plot_waveform()
            self.slider_start.setValue(0)
            self.slider_end.setValue(100)

    def plot_waveform(self):
        if not self.audio:
            return
        samples = np.array(self.audio.get_array_of_samples())
        samples = samples[::max(1, len(samples) // 1000)]  # downsample for performance

        self.canvas.figure.clear()
        ax = self.canvas.figure.add_subplot(111)
        ax.plot(samples, color='cyan')
        ax.set_facecolor('#2e2e2e')
        self.canvas.draw()

    def play_audio(self):
        if not self.audio:
            return

        start_ms = int(len(self.audio) * self.start_trim / 100)
        end_ms = int(len(self.audio) * self.end_trim / 100)
        segment = self.audio[start_ms:end_ms]

        threading.Thread(target=play, args=(segment,)).start()

    def update_start(self, value):
        self.start_trim = value
        if self.start_trim > self.end_trim:
            self.slider_end.setValue(value)

    def update_end(self, value):
        self.end_trim = value
        if self.end_trim < self.start_trim:
            self.slider_start.setValue(value)

    def export_trim(self):
        if not self.audio:
            return

        start_ms = int(len(self.audio) * self.start_trim / 100)
        end_ms = int(len(self.audio) * self.end_trim / 100)
        trimmed = self.audio[start_ms:end_ms]

        export_path, _ = QFileDialog.getSaveFileName(self, "Export Trimmed Audio", "trimmed_audio.mp3", "MP3 Files (*.mp3)")
        if export_path:
            trimmed.export(export_path, format="mp3")
            self.label.setText("Exported Successfully!")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AudioTrimApp()
    window.show()
    sys.exit(app.exec_())
