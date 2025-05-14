import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QMainWindow, QScrollArea,
    QVBoxLayout, QLabel
)
from PyQt5.QtGui import QPainter, QBrush, QColor
from PyQt5.QtCore import Qt


class LargeWidget(QWidget):
    def __init__(self, width=3000, height=4000):
        super().__init__()
        self.setFixedSize(width, height)

class ScrollableWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.resize(1200, 800)

        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(False)

        large_widget = LargeWidget()
        scroll_area.setWidget(large_widget)

        self.setCentralWidget(scroll_area)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ScrollableWindow()
    window.show()
    sys.exit(app.exec_())
