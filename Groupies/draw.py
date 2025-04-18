import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget
from PyQt5.QtCore import Qt, QPointF, QRectF
from PyQt5.QtGui import QPainter, QColor, QPen
import music21


class LineSegment:
    """线段类"""

    def __init__(self, left_x, right_x, y, color):
        self.left_x = left_x  # 左端点x坐标
        self.right_x = right_x  # 右端点x坐标
        self.y = y  # y坐标（固定值）
        self.color = color  # 颜色(QColor对象)

    def contains_point(self, point: QPointF, threshold=5):
        """判断点是否在线段附近"""
        # 判断y坐标是否在阈值范围内
        if abs(point.y() - self.y) > threshold:
            return False
        # 判断x坐标是否在线段范围内
        return self.left_x - threshold <= point.x() <= self.right_x + threshold


class LineDrawWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.lines = []  # 存储所有线段
        self.temp_line = None  # 临时线段（绘制中）
        self.grid_size = 20  # 网格大小（像素）
        self.current_color = QColor(0, 0, 255)  # 默认蓝色

        self.setMouseTracking(True)
        self.setMinimumSize(800, 600)

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

    def draw_grid(self, painter):
        """绘制网格线"""
        painter.setPen(QPen(QColor(220, 220, 220), 1))

                       # 水平线
        for y in range(0, self.height(), self.grid_size):
            painter.drawLine(0, y, self.width(), y)

        # 垂直线
        for x in range(0, self.width(), self.grid_size):
            painter.drawLine(x, 0, x, self.height())

    def draw_line(self, painter, line):
        """绘制单个线段"""
        painter.setPen(QPen(line.color, 3))
        painter.drawLine(
            QPointF(line.left_x, line.y),
            QPointF(line.right_x, line.y)
        )

    def snap_to_grid(self, pos: QPointF):
        """坐标对齐到网格"""
        x = round(pos.x() / self.grid_size) * self.grid_size
        y = round(pos.y() / self.grid_size) * self.grid_size
        return QPointF(x, y)

    def mousePressEvent(self, event):
        pos = self.snap_to_grid(event.pos())

        if event.button() == Qt.LeftButton:
            # 开始创建新线段
            self.temp_line = LineSegment(
                left_x=pos.x(),
                right_x=pos.x(),  # 初始长度为0
                y=pos.y(),
                color=self.current_color
            )

        elif event.button() == Qt.RightButton:
            # 查找并删除线段
            for line in self.lines[::-1]:  # 从后往前遍历
                if line.contains_point(pos):
                    self.lines.remove(line)
                    self.update()
                    break

    def mouseMoveEvent(self, event):
        pos = self.snap_to_grid(event.pos())

        if self.temp_line:  # 正在绘制新线段
            # 左端点固定，右端点跟随鼠标x坐标
            self.temp_line.right_x = max(
                self.temp_line.left_x + self.grid_size,  # 最小长度1格
                pos.x()
            )
            # y坐标固定为初始位置
            self.temp_line.y = self.temp_line.y
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self.temp_line:
            # 完成线段创建
            if self.temp_line.right_x > self.temp_line.left_x:
                self.lines.append(self.temp_line)
            self.temp_line = None
            self.update()
            for i in self.lines:
                print(i.left_x,i.right_x,i.y,end='   ')
            print(end='\n')


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("可拖动的水平线段编辑器")
        self.canvas = LineDrawWidget()
        self.setCentralWidget(self.canvas)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.resize(3000, 2000)
    window.show()
    sys.exit(app.exec_())