import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QLabel, QPushButton, QMessageBox)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QPixmap, QImage, QResizeEvent
import fitz


class PDFViewer(QWidget):
    def __init__(self, file_path, parent=None):
        super().__init__(parent)
        self.current_page = 0
        self.total_pages = 0
        self.doc = None
        self.original_pixmap = None
        self.file_path = file_path
        self.initUI()
        self.load_pdf()

    def initUI(self):
        layout = QVBoxLayout(self)
        self.setLayout(layout)

        # PDF 显示区域
        self.pdf_label = QLabel()
        self.pdf_label.setAlignment(Qt.AlignCenter)
        self.pdf_label.setMinimumSize(200, 150)
        layout.addWidget(self.pdf_label)

        # 控制栏
        controls = QHBoxLayout()
        # 上一页按钮
        self.prev_btn = QPushButton("上一页")
        self.prev_btn.clicked.connect(self.prev_page)
        controls.addWidget(self.prev_btn)
        # 下一页按钮
        self.next_btn = QPushButton("下一页")
        self.next_btn.clicked.connect(self.next_page)
        controls.addWidget(self.next_btn)
        # 页码显示
        self.page_label = QLabel()
        controls.addWidget(self.page_label)
        layout.addLayout(controls)

    def load_pdf(self):
        try:
            self.doc = fitz.open(self.file_path)
            self.total_pages = self.doc.page_count
            self.current_page = 0
            self.load_page_content()
        except Exception as e:
            QMessageBox.critical(self, "错误", f"无法加载文件：{str(e)}")
            self.close()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update_scaled_pixmap()

    def update_scaled_pixmap(self):
        if self.original_pixmap:
            available_size = self.pdf_label.size()
            scaled_pix = self.original_pixmap.scaled(
                available_size,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            self.pdf_label.setPixmap(scaled_pix)

    def load_page_content(self):
        page = self.doc.load_page(self.current_page)
        matrix = fitz.Matrix(4, 4)
        pix = page.get_pixmap(matrix=matrix)

        img_format = QImage.Format_RGB888
        qimg = QImage(pix.samples, pix.width, pix.height, pix.stride, img_format)
        self.original_pixmap = QPixmap.fromImage(qimg)

        self.update_scaled_pixmap()
        self.page_label.setText(f"第 {self.current_page + 1} 页 / 共 {self.total_pages} 页")
        self.update_buttons()

    def update_buttons(self):
        self.prev_btn.setEnabled(self.current_page > 0)
        self.next_btn.setEnabled(self.current_page < self.total_pages - 1)

    def prev_page(self):
        if self.current_page > 0:
            self.current_page -= 1
            self.load_page_content()

    def next_page(self):
        if self.current_page < self.total_pages - 1:
            self.current_page += 1
            self.load_page_content()

    def close(self):
        if self.doc:
            self.doc.close()
        super().close()

if __name__ == '__main__':
    # 在此处指定你的PDF文件路径
    pdf_path = "C:/Users/Goat/Documents/GitHub/PSP25-3/Groupies/tmp_works/tmp_20250422161246.pdf"  # 替换为你的实际路径

    app = QApplication(sys.argv)
    viewer = PDFViewer(pdf_path)
    viewer.show()
    sys.exit(app.exec_())