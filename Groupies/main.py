from draw import *
from stream import convert_notes_to_stream
from stream import save_musicxml, auto_save_musicxml
from note import *
from pathlib import Path
import pygame
import tempfile
import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QPushButton, QLabel, QLineEdit,
                             QTextEdit, QStatusBar, QFileDialog, QAction, qApp,
                             QScrollArea, QMessageBox)
from PyQt5.QtGui import QIcon, QColor, QPainter, QPen, QFont, QPixmap, QImage
from PyQt5.QtCore import Qt, QPointF, QSize
import fitz

target_dir = Path(__file__).parent.resolve() / "converters"
sys.path.append(str(target_dir))
from mxl2opt import mxl2opt
from pdf_reader import PDFViewer


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.setWindowTitle("音乐结构编辑器")
        self.resize(1200, 800)
        self.current_midi = None
        self.pdf_viewer = None  # PDF查看器实例
        pygame.mixer.init()

    def initUI(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)

        # 左侧面板
        left_panel = QVBoxLayout()

        # 项目控制区
        project_layout = QVBoxLayout()
        project_layout.addWidget(QLabel("项目名称:"))
        self.project_name = QLineEdit()
        project_layout.addWidget(self.project_name)

        self.btn_new = QPushButton("显示乐谱")
        self.btn_new.clicked.connect(self.open_xml)
        project_layout.addWidget(self.btn_new)

        self.btn_play = QPushButton("播放乐谱", self)
        self.btn_play.clicked.connect(self.play_music)
        project_layout.addWidget(self.btn_play)

        # 绘图滚动区
        self.draw_area = NoteDrawWidget()
        self.draw_area.setFixedSize(3000, 2000)
        scroll_area = QScrollArea()
        scroll_area.setWidget(self.draw_area)
        scroll_area.setWidgetResizable(False)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        # 添加左侧组件
        left_panel.addLayout(project_layout)
        left_panel.addWidget(QLabel("音乐结构编辑区:"))
        left_panel.addWidget(scroll_area)

        # 右侧PDF面板
        right_panel = QVBoxLayout()
        right_panel.addWidget(QLabel("乐谱预览:"))

        # PDF滚动区域
        self.pdf_scroll = QScrollArea()
        self.pdf_scroll.setWidgetResizable(True)
        right_panel.addWidget(self.pdf_scroll)

        # 设置主布局比例
        main_layout.addLayout(left_panel, stretch=1)
        main_layout.addLayout(right_panel, stretch=1)

        self.statusBar().showMessage("就绪")
        self.create_menus()

    def create_menus(self):
        menubar = self.menuBar()
        file_menu = menubar.addMenu("文件(&F)")
        file_menu.addAction("新建").triggered.connect(self.new_project)
        file_menu.addAction("打开").triggered.connect(self.open_project)
        file_menu.addAction("保存").triggered.connect(self.save_project)
        file_menu.addSeparator()
        file_menu.addAction("退出").triggered.connect(self.close)
        help_menu = menubar.addMenu("帮助(&H)")
        help_menu.addAction("关于").triggered.connect(self.show_about)

    def new_project(self):
        self.draw_area.lines.clear()
        self.project_name.clear()
        self.statusBar().showMessage("新建项目已创建", 2000)
        self.update()

    def open_project(self):
        filename, _ = QFileDialog.getOpenFileName(self, "打开项目", "", "项目文件 (*.proj)")
        if filename:
            self.statusBar().showMessage(f"已打开项目: {filename}", 3000)

    def save_project(self):
        save_musicxml(self.draw_area.notes)
        if self.project_name.text():
            self.statusBar().showMessage("项目已保存", 2000)

    def open_xml(self):
        try:
            convert_notes_to_stream(self.draw_area.notes)
            tmp_xml = auto_save_musicxml(self.draw_area.notes)
            tmp_pdf = mxl2opt(tmp_xml)

            # 清理旧PDF部件
            if self.pdf_viewer:
                self.pdf_viewer.close()
                self.pdf_scroll.takeWidget()

            # 创建新PDF查看器
            self.pdf_viewer = PDFViewer(tmp_pdf)
            self.pdf_scroll.setWidget(self.pdf_viewer)
            self.statusBar().showMessage("乐谱生成成功", 3000)
        except Exception as e:
            self.statusBar().showMessage(f"生成失败: {str(e)}", 5000)
            QMessageBox.critical(self, "错误", f"无法生成乐谱: {str(e)}")

    def show_about(self):
        self.statusBar().showMessage("音乐结构编辑器 v1.0 - 支持钢琴卷帘编辑和音乐结构分析", 5000)

    def play_music(self):
        try:
            if pygame.mixer.music.get_busy():
                pygame.mixer.music.stop()

            score_stream = convert_notes_to_stream(self.draw_area.notes)
            with tempfile.NamedTemporaryFile(suffix='.mid', delete=False) as midi_file:
                self.current_midi = midi_file.name
                score_stream.write('midi', self.current_midi)

            pygame.mixer.music.load(self.current_midi)
            pygame.mixer.music.play()
            self.statusBar().showMessage("正在播放... 按播放键可停止", 2000)

        except Exception as e:
            self.statusBar().showMessage(f"播放失败: {str(e)}", 5000)

    def closeEvent(self, event):
        if pygame.mixer.get_init():
            pygame.mixer.quit()
        if self.current_midi and os.path.exists(self.current_midi):
            os.remove(self.current_midi)
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())