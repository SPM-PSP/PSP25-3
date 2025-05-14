import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget
from PyQt5.QtCore import Qt, QPointF, QRectF
from PyQt5.QtGui import QPainter, QColor, QPen, QBrush
import music21


class LineSegment:
    """线段类"""

    def __init__(self, left_x, right_x, y, color):
        self.left_x = left_x  # 左端点x坐标
        self.right_x = right_x  # 右端点x坐标
        self.y = y  # y坐标（固定值）
        self.color = color  # 颜色(QColor对象)

    def contains_point(self, point: QPointF, threshold=5):
        """判断点是否在矩形范围内"""
        rect = QRectF(
            self.left_x,  # 左上角x坐标
            self.y - 20,  # 左上角y坐标
            self.right_x - self.left_x,  # 宽度
            20  # 高度
        )
        return rect.contains(point)


class LineDrawWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.lines = []  # 存储所有线段
        self.temp_line = None  # 临时线段（绘制中）
        self.grid_size = 20  # 网格大小（像素）
        self.current_color = QColor(173, 216, 230)  # 默认蓝色
        self.vertical_line_x = None  # 新增：存储竖线的x位置

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

        # 绘制竖线
        if self.vertical_line_x is not None:
            self.draw_vertical_line(painter, self.vertical_line_x)

    def draw_grid(self, painter):
        """绘制网格线"""
        # 绘制水平线
        painter.setPen(QPen(QColor(220, 220, 220), 1))
        for y in range(0, self.height(), self.grid_size):
            if y % (12 * self.grid_size) == 1 * self.grid_size:
                # 每12个格子加粗横线
                painter.setPen(QPen(QColor(220, 220, 220), 3))
            else:
                painter.setPen(QPen(QColor(220, 220, 220), 1))
            painter.drawLine(0, y, self.width(), y)

        # 绘制垂直线
        for x in range(0, self.width(), self.grid_size):
            if x % (8 * self.grid_size) == 0:
                # 每八个格子加粗竖线
                painter.setPen(QPen(QColor(220, 220, 220), 3))
            else:
                painter.setPen(QPen(QColor(220, 220, 220), 1))
            painter.drawLine(x, 0, x, self.height())

    def draw_line(self, painter, line):
        """绘制圆角矩形，带有2像素白色边框"""
        # 设置白色边框，2像素宽度
        painter.setPen(QPen(Qt.white, 2))
        # 设置填充颜色
        painter.setBrush(QBrush(line.color))

        # 创建矩形区域（与原始矩形相同）
        rect = QRectF(
            line.left_x,  # 左上角x坐标
            line.y - 20,  # 左上角y坐标
            line.right_x - line.left_x,  # 宽度
            20  # 高度
        )

        # 绘制圆角矩形，圆角半径为5像素
        painter.drawRoundedRect(rect, 5, 5)

    def draw_vertical_line(self, painter, x):
        """绘制竖线"""
        painter.setPen(QPen(Qt.red, 2))  # 设置竖线颜色为红色，宽度为2像素
        painter.drawLine(x, 0, x, self.height())

    def snap_to_grid(self, pos: QPointF):
        """坐标对齐到网格"""
        x = round(pos.x() / self.grid_size) * self.grid_size
        y = round(pos.y() / self.grid_size) * self.grid_size
        return QPointF(x, y)

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
            print(pos.y() % 20)

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
                print(i.left_x, i.right_x, i.y, end='   ')
            print(end='\n')

    def draw_vertical_line_at_x(self, x):
        """给定x位置，绘制竖线"""
        self.vertical_line_x = x
        self.update()


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

    # 示例：在x=200的位置绘制竖线
    window.canvas.draw_vertical_line_at_x(200)

    sys.exit(app.exec_())
