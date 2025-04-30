# piano.py
from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPainter, QColor, QFont, QPen
from PyQt5.QtCore import Qt, QRectF


class PianoWidget(QWidget):
    def __init__(self, height=1760, grid_size=20, parent=None):
        super().__init__(parent)
        self.setFixedSize(120, height)
        self.grid_size = grid_size
        self.start_midi = 108  # C8 → 顶部
        self.end_midi = 21     # A0 → 底部
        self.total_keys = self.start_midi - self.end_midi + 1  # = 88
        self.key_map = self.build_key_map()
        self.c4_midi = 60  # MIDI 60 是 C4

    def build_key_map(self):
        """生成键盘按键映射"""
        key_map = []
        for midi in range(self.start_midi, self.end_midi - 1, -1):
            name = self.get_note_name(midi)
            is_black = '#' in name
            key_map.append((midi, name, is_black))
        return key_map

    def get_note_name(self, midi_num):
        names = ['C', 'C#', 'D', 'D#', 'E', 'F',
                 'F#', 'G', 'G#', 'A', 'A#', 'B']
        return f"{names[midi_num % 12]}{(midi_num // 12) - 1}"

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        font = QFont("Arial", 8)
        painter.setFont(font)

        white_key_width = self.width()
        black_key_width = white_key_width * 0.6
        black_key_offset = (white_key_width - black_key_width) / 2
        black_key_height = self.grid_size

        for i, (midi, name, is_black) in enumerate(self.key_map):
            y = i * self.grid_size

            if is_black:
                painter.setBrush(QColor(0, 0, 0))
                painter.setPen(Qt.NoPen)
                painter.drawRect(
                    QRectF(
                        black_key_offset,
                        y,
                        black_key_width,
                        black_key_height
                    )
                )
            else:
                # 白键背景
                painter.setBrush(QColor(255, 255, 255))
                painter.setPen(QColor(0, 0, 0))
                painter.drawRect(
                    QRectF(0, y, white_key_width, self.grid_size)
                )
                # 音名
                painter.drawText(QRectF(5, y, white_key_width, self.grid_size),
                                 Qt.AlignVCenter | Qt.AlignLeft,
                                 name)

        # ✅ 画红线：C4 对应 midi=60，index = 108-60 = 48
        c4_index = self.start_midi - self.c4_midi
        red_y = c4_index * self.grid_size + self.grid_size  # 红线在C4下方一格
        painter.setPen(QPen(Qt.red, 2))
        painter.drawLine(0, red_y, white_key_width, red_y)