import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *


class Note:
    def __init__(self, start=0, duration=1, pitch=60):
        self.start = start  # 起始时间（单位：拍）
        self.duration = duration  # 持续时间
        self.pitch = pitch  # 音高（MIDI编号）


class PianoRollWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.notes = [
            Note(2, 4, 60),
            Note(6, 2, 64),
            Note(8, 3, 67)
        ]
        self.selected_note = None
        self.drag_mode = None
        self.pixels_per_beat = 50  # 每拍像素数
        self.pitch_height = 20  # 每个音高像素高度

        self.setMinimumSize(800, 600)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # 绘制网格
        self.draw_grid(painter)

        # 绘制音符
        for note in self.notes:
            self.draw_note(painter, note)

    def draw_grid(self, painter):
        painter.setPen(QColor(200, 200, 200))
        # 绘制横向音高线
        for y in range(0, self.height(), self.pitch_height):
            painter.drawLine(0, y, self.width(), y)

        # 绘制纵向时间线
        for x in range(0, self.width(), self.pixels_per_beat):
            painter.drawLine(x, 0, x, self.height())

    def draw_note(self, painter, note):
        x = note.start * self.pixels_per_beat
        y = (127 - note.pitch) * self.pitch_height  # 倒置音高
        width = note.duration * self.pixels_per_beat

        color = QColor(255, 0, 0) if note == self.selected_note else QColor(0, 150, 255)
        painter.setBrush(color)
        painter.setPen(QPen(Qt.black, 1))
        painter.drawRect(QRectF(x, y, width, self.pitch_height))

        # 绘制可调整手柄
        if note == self.selected_note:
            painter.setBrush(Qt.white)
            painter.drawRect(x - 3, y, 6, self.pitch_height)  # 左调整柄
            painter.drawRect(x + width - 3, y, 6, self.pitch_height)  # 右调整柄

    def get_note_at(self, pos):
        for note in self.notes:
            rect = QRectF(
                note.start * self.pixels_per_beat,
                (127 - note.pitch) * self.pitch_height,
                note.duration * self.pixels_per_beat,
                self.pitch_height
            )
            if rect.contains(pos):
                return note
        return None

    def mousePressEvent(self, event):
        pos = event.pos()
        self.selected_note = self.get_note_at(pos)

        if self.selected_note:
            x = self.selected_note.start * self.pixels_per_beat
            width = self.selected_note.duration * self.pixels_per_beat

            # 判断拖动模式
            if abs(pos.x() - x) < 5:
                self.drag_mode = "resize_left"
            elif abs(pos.x() - (x + width)) < 5:
                self.drag_mode = "resize_right"
            else:
                self.drag_mode = "move"

            self.drag_start_pos = pos
            self.drag_start_state = (self.selected_note.start,
                                     self.selected_note.duration,
                                     self.selected_note.pitch)
        self.update()

    def mouseMoveEvent(self, event):
        if self.selected_note and self.drag_mode:
            delta = event.pos() - self.drag_start_pos
            start, duration, pitch = self.drag_start_state

            if self.drag_mode == "move":
                new_start = start + delta.x() / self.pixels_per_beat
                new_pitch = pitch - delta.y() / self.pitch_height
                self.selected_note.start = max(0, new_start)
                self.selected_note.pitch = int(max(0, min(127, new_pitch)))

            elif self.drag_mode == "resize_left":
                delta_beat = delta.x() / self.pixels_per_beat
                new_start = start + delta_beat
                new_duration = duration - delta_beat
                if new_duration > 0 and new_start >= 0:
                    self.selected_note.start = new_start
                    self.selected_note.duration = new_duration

            elif self.drag_mode == "resize_right":
                delta_beat = delta.x() / self.pixels_per_beat
                new_duration = duration + delta_beat
                if new_duration > 0:
                    self.selected_note.duration = new_duration

            self.update()

    def mouseReleaseEvent(self, event):
        self.drag_mode = None
        self.update()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("钢琴卷帘")
        self.piano_roll = PianoRollWidget()
        self.setCentralWidget(self.piano_roll)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.resize(1000, 800)
    window.show()
    sys.exit(app.exec_())