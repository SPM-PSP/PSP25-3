from draw import *
from music21.note import Note
from music21 import pitch, duration
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtGui import QPainter
from PyQt5.QtCore import Qt


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
        midi_value = 1500-int(self.y / 2 + 30)
        quarter_length = (self.right_x - self.left_x) / 160.0
        self.timing=int(self.left_x/20.0)

        Note.__init__(
            self,
            pitch=pitch.Pitch(midi=midi_value),
            duration=duration.Duration(quarterLength=quarter_length)
        )


class NoteDrawWidget(LineDrawWidget):
    def __init__(self):
        super().__init__()  # 使用super()正确初始化父类
        self.notes = []

    def draw_grid(self, painter):
        super().draw_grid(painter)
        painter.setPen(Qt.red)
        painter.drawLine(0, 900, self.width(), 900)

    def mousePressEvent(self, event):
        pos = self.snap_to_grid(event.pos())

        if event.button() == Qt.LeftButton:
            self.temp_line = LineSegment(
                left_x=pos.x(),
                right_x=pos.x(),
                y=pos.y(),
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

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self.temp_line:
            # 确保最小长度
            if self.temp_line.right_x <= self.temp_line.left_x:
                self.temp_line.right_x = self.temp_line.left_x + 10

            self.lines.append(self.temp_line)
            try:
                self.notes.append(NoteSegment(self.temp_line))
            except Exception as e:
                print(f"创建Note失败: {str(e)}")
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