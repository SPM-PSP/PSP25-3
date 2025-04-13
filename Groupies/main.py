from draw import *
from stream import convert_notes_to_stream
from stream import save_musicxml, auto_save_musicxml
from note import *

import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QPushButton, QLabel, QLineEdit,
                             QTextEdit, QStatusBar, QFileDialog, QAction, qApp,
                             QScrollArea, QScrollBar)
from PyQt5.QtGui import QIcon, QColor, QPainter, QPen, QFont
from PyQt5.QtCore import Qt, QPointF
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.setWindowTitle("音乐结构编辑器")
        self.resize(1200, 800)

    def initUI(self):
        # 主界面布局
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

        # 绘图滚动区
        self.draw_area = NoteDrawWidget()
        scroll = QScrollArea()
        scroll.setWidget(self.draw_area)
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)

        # 组合左侧布局
        left_panel.addLayout(project_layout)
        left_panel.addWidget(QLabel("音乐结构编辑区:"))
        left_panel.addWidget(scroll)

        # 右侧日志面板
        right_panel = QVBoxLayout()
        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        right_panel.addWidget(QLabel("操作日志:"))
        right_panel.addWidget(self.log_area)

        # 组合主布局
        main_layout.addLayout(left_panel, stretch=3)
        main_layout.addLayout(right_panel, stretch=1)

        # 状态栏
        self.statusBar().showMessage("就绪")

        # 创建菜单
        self.create_menus()

    def create_menus(self):
        menubar = self.menuBar()

        # 文件菜单
        file_menu = menubar.addMenu("文件(&F)")
        file_menu.addAction("新建").triggered.connect(self.new_project)
        file_menu.addAction("打开").triggered.connect(self.open_project)
        file_menu.addAction("保存").triggered.connect(self.save_project)
        file_menu.addSeparator()
        file_menu.addAction("退出").triggered.connect(self.close)

        # 帮助菜单
        help_menu = menubar.addMenu("帮助(&H)")
        help_menu.addAction("关于").triggered.connect(self.show_about)

    def new_project(self):
        self.draw_area.lines.clear()
        self.project_name.clear()
        self.log_area.clear()
        self.update()

    def open_project(self):
        filename, _ = QFileDialog.getOpenFileName(self, "打开项目", "", "项目文件 (*.proj)")
        if filename:
            self.log_area.append(f"已打开项目: {filename}")

    def save_project(self):
        save_musicxml(self.draw_area.notes)
        if self.project_name.text():
            self.log_area.append("项目已保存")
            self.statusBar().showMessage("保存成功", 2000)

    def open_xml(self):
        convert_notes_to_stream(self.draw_area.notes)
        auto_save_musicxml(self.draw_area.notes)

    def show_about(self):
        self.log_area.append("音乐结构编辑器 v1.0\n支持钢琴卷帘编辑和音乐结构分析")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())