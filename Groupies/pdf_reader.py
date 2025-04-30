import sys
from PyQt5.QtWidgets import (QWidget, QVBoxLayout,
                             QHBoxLayout, QLabel, QPushButton, QMessageBox,
                             QScrollArea)
from PyQt5.QtCore import Qt, QSize, QTimer
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

        # PDF 显示区域，使用 QScrollArea
        self.scroll_area = QScrollArea()
        self.pdf_label = QLabel()
        self.pdf_label.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
        self.scroll_area.setWidget(self.pdf_label)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        layout.addWidget(self.scroll_area, 1)


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
            available_width = self.scroll_area.viewport().width()
            # 计算缩放后的高度
            aspect_ratio = self.original_pixmap.height() / self.original_pixmap.width()
            scaled_height = int(available_width * aspect_ratio)
            scaled_pix = self.original_pixmap.scaled(
                available_width, scaled_height,
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

        # 在这里根据当前窗口宽度进行初始缩放
        QTimer.singleShot(0, self.update_scaled_pixmap)

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