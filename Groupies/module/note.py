from module.draw import *
from music21.note import Note
from music21 import pitch, duration, tempo
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtGui import QPainter
from PyQt5.QtCore import Qt, pyqtSignal, QPoint
import pygame
import tempfile
import numpy as np
from scipy.signal import butter, lfilter
from module.stream import *
import copy

class NoteSegment(LineSegment, Note):
    def __init__(self, line_inst):
        # 初始化图形部分
        LineSegment.__init__(
            self,
            left_x=line_inst.left_x,
            right_x=line_inst.right_x,
            y=line_inst.y,
            color=line_inst.color
        )

        # 初始化音乐属性
        midi_value = 109-self.y/20
        quarter_length = (self.right_x - self.left_x) / 160.0
        self.timing=int(self.left_x/20.0)

        Note.__init__(
            self,
            pitch=pitch.Pitch(midi=midi_value),
            duration=duration.Duration(quarterLength=quarter_length)
        )

        pygame.mixer.init()

    def to_dict(self):
        return {
            "left_x": self.left_x,
            "right_x": self.right_x,
            "y": self.y,
            #"color": self.color,
            "midi_value": self.pitch.midi,
            "quarter_length": self.duration.quarterLength,
            "timing": self.timing
        }


class NoteDrawWidget(LineDrawWidget):
    mouseMoveSignal = pyqtSignal(QPoint)
    def __init__(self):
        super().__init__()  # 使用super()正确初始化父类
        self.notes = []
        self.main_window = None
        self.margin = 0
        self.Width = 3000
        self.setMinimumSize(self.Width, 1760)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # 绘制网格
        self.draw_grid(painter)

        # 绘制所有线段
        for line in self.lines:
            self.draw_line(painter, line)

        # 绘制临时线段
        if self.temp_line:
            self.draw_line(painter, self.temp_line)

        # 绘制音符
        for note in self.notes:
            self.draw_line(painter, note)  # 假设音符的绘制逻辑和线段相同

        # 绘制竖线
        if self.vertical_line_x is not None:
            self.draw_vertical_line(painter, self.vertical_line_x)

    def draw_grid(self, painter):
        super().draw_grid(painter)
        painter.setPen(Qt.red)
        painter.drawLine(0, 980, self.width(), 980)

    def play_a_music(self, notes):
        """播放给定的音符列表"""
        try:
            if pygame.mixer.music.get_busy():
                pygame.mixer.music.stop()

            # 转换音符为流并生成MIDI
            from module.stream import convert_notes_to_stream
            score_stream = convert_notes_to_stream(notes)
            with tempfile.NamedTemporaryFile(suffix='.mid', delete=False) as midi_file:
                current_midi = midi_file.name
                score_stream.write('midi', current_midi)

            # 加载并播放MIDI
            pygame.mixer.music.load(current_midi)
            pygame.mixer.music.play()

            # 更新状态栏
            if self.main_window:
                self.main_window.statusBar().showMessage("播放中...", 2000)

        except Exception as e:
            error_msg = f"播放失败: {str(e)}"
            if self.main_window:
                self.main_window.statusBar().showMessage(error_msg, 5000)
            else:
                print(error_msg)


    def mousePressEvent(self, event):
        pos = event.pos()

        if event.button() == Qt.LeftButton:
            # 开始创建新线段
            self.temp_line = LineSegment(
                left_x=round(pos.x() / self.grid_size) * self.grid_size,
                right_x=round(pos.x() / self.grid_size) * self.grid_size,  # 初始长度为0
                y=round(pos.y() / self.grid_size) * self.grid_size if pos.y() % 20 > 10 else round(
                    pos.y() / self.grid_size) * self.grid_size + 20,
                color=self.current_color
            )

        elif event.button() == Qt.RightButton:
            # 反向遍历避免索引错乱
            for i in reversed(range(len(self.lines))):
                if self.lines[i].contains_point(pos):
                    del self.lines[i]
                    del self.notes[i]
                    self.update()
                    break

    def mouseMoveEvent(self, event):
        self.mouseMoveSignal.emit(event.pos())
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self.temp_line:
            # 确保最小长度
            if self.temp_line.right_x <= self.temp_line.left_x:
                self.temp_line.right_x = self.temp_line.left_x + 10

            self.lines.append(self.temp_line)
            cur_note = NoteSegment(self.temp_line)
            self.notes.append(cur_note)

            tmp_line = copy.copy(self.temp_line)

            tmp_line.right_x -= tmp_line.left_x
            tmp_line.left_x = 0
            temp_note = NoteSegment(tmp_line)

            # print("Python Path:", sys.path)

            self.play_a_music([temp_note])


            self.temp_line = None
            self.update()

            # 打印当前乐谱
            print("当前乐谱:")
            for note in self.notes:
                print(f"{note.name} {note.duration.type} {note.timing}", end=" | ")
            print("\n" + "-" * 50)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("乐谱可视化编辑器")
        self.canvas = NoteDrawWidget()
        self.setCentralWidget(self.canvas)
        self.resize(3000, 2000)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())