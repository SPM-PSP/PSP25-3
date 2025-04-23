from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QHBoxLayout, QPushButton, QLabel, QLineEdit,
    QTextEdit, QFileDialog, QScrollArea,
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from music21 import converter
from note import *
from stream import convert_notes_to_stream
import sys


class PitchScaleWidget(QWidget):
    def __init__(self, height=2000, grid_size=20, parent=None):
        super().__init__(parent)
        self.setFixedSize(100, height)
        self.grid_size = grid_size
        self.notes = ['C', 'D', 'E', 'F', 'G', 'A', 'B']
        self.start_octave = 1
        self.end_octave = 8

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        font = QFont("Arial", 10)
        painter.setFont(font)

        y = 0
        for i in range(self.start_octave, self.end_octave + 1):
            for note in self.notes:
                label = f"{note}{i}"
                y_pos = 2000 - y - self.grid_size  # 反向绘制
                if y_pos < 0:
                    break
                painter.drawText(10, y_pos, label)
                y += self.grid_size
