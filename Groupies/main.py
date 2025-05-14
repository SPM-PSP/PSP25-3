from module.draw import *
from module.stream import *
from module.note import *
from pathlib import Path
import pygame
import tempfile
import sys
import os
import json
from module.piano import *
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QPushButton, QLabel, QLineEdit,
                             QTextEdit, QStatusBar, QFileDialog, QAction, qApp,
                             QScrollArea, QMessageBox, QInputDialog, QSplitter)
from PyQt5.QtGui import QIcon, QColor, QPainter, QPen, QFont, QPixmap, QImage
from PyQt5.QtCore import Qt, QPointF, QSize, QTimer

import fitz
from module.pdf_reader import PDFViewer

project_root = Path(__file__).parent.resolve()
sys.path.append(str(project_root))  # 添加项目根目录到路径


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.setWindowTitle("音乐结构编辑器")
        self.resize(1200, 800)
        self.current_midi = None
        self.pdf_viewer = None  # PDF查看器实例
        self.is_playing = False
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_play_time)
        self.bpm = 120  # 默认bpm为120
        pygame.mixer.init()
        # 新增乐曲名和作者名变量
        self.song_name = ""
        self.author_name = ""

    def initUI(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)

        # 上方面板
        top_panel = QWidget()
        top_layout = QHBoxLayout(top_panel)

        # 创建钢琴键区域并放入滚动区域
        self.piano_widget = PianoWidget(height=1760)
        piano_scroll_area = QScrollArea()
        piano_scroll_area.setWidget(self.piano_widget)
        piano_scroll_area.setWidgetResizable(False)
        # 隐藏钢琴区域的水平和垂直滚动条
        piano_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        piano_scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        top_layout.addWidget(piano_scroll_area)

        # 设置钢琴区域的宽度
        piano_width = 120  # 可根据需要修改这个值
        piano_scroll_area.setFixedWidth(piano_width)

        # 创建绘图区域并放入滚动区域
        self.draw_area = NoteDrawWidget()
        self.draw_area.main_window = self
        self.draw_area.setFixedSize(3000, 1760)
        draw_scroll_area = QScrollArea()
        draw_scroll_area.setWidget(self.draw_area)
        draw_scroll_area.setWidgetResizable(False)
        draw_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        draw_scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        top_layout.addWidget(draw_scroll_area)

        # 联动垂直滚动条
        draw_scroll_area.verticalScrollBar().valueChanged.connect(
            piano_scroll_area.verticalScrollBar().setValue)
        piano_scroll_area.verticalScrollBar().valueChanged.connect(
            draw_scroll_area.verticalScrollBar().setValue)

        # 下方PDF面板
        self.pdf_scroll = QScrollArea()
        self.pdf_scroll.setWidgetResizable(True)

        # 使用QSplitter布局上下区域
        splitter = QSplitter(Qt.Vertical)
        splitter.addWidget(top_panel)
        splitter.addWidget(self.pdf_scroll)

        main_layout = QVBoxLayout(main_widget)
        main_layout.addWidget(splitter)

        self.statusBar().showMessage("就绪")
        self.create_menus()

    def create_menus(self):
        menubar = self.menuBar()

        # 添加显示乐谱按钮到菜单栏
        self.btn_new = QAction("显示乐谱", self)
        self.btn_new.triggered.connect(self.open_xml)
        menubar.addAction(self.btn_new)

        # 添加播放乐谱按钮到菜单栏
        self.btn_play = QAction("播放乐谱", self)
        self.btn_play.triggered.connect(self.play_music)
        menubar.addAction(self.btn_play)

        # 添加暂停按钮到菜单栏
        self.btn_pause = QAction("暂停", self)
        self.btn_pause.triggered.connect(self.pause_music)
        menubar.addAction(self.btn_pause)
        self.btn_pause.setEnabled(False)

        # 添加继续按钮到菜单栏
        self.btn_resume = QAction("继续", self)
        self.btn_resume.triggered.connect(self.resume_music)
        menubar.addAction(self.btn_resume)
        self.btn_resume.setEnabled(False)

        file_menu = menubar.addMenu("文件(&F)")
        file_menu.addAction("新建").triggered.connect(self.new_project)
        file_menu.addAction("打开").triggered.connect(self.open_project)
        file_menu.addAction("保存").triggered.connect(self.save_project)
        file_menu.addAction("另存为xml").triggered.connect(self.save_asxml)
        file_menu.addSeparator()
        file_menu.addAction("退出").triggered.connect(self.close)

        # 添加设置模块
        settings_menu = menubar.addMenu("设置(&S)")
        set_bpm_action = QAction("设置BPM", self)
        set_bpm_action.triggered.connect(self.set_bpm)
        settings_menu.addAction(set_bpm_action)

        # 添加修改乐曲名菜单项
        set_song_name_action = QAction("修改乐曲名", self)
        set_song_name_action.triggered.connect(self.set_song_name)
        settings_menu.addAction(set_song_name_action)

        # 添加修改作者名菜单项
        set_author_name_action = QAction("修改作者名", self)
        set_author_name_action.triggered.connect(self.set_author_name)
        settings_menu.addAction(set_author_name_action)

        help_menu = menubar.addMenu("帮助(&H)")
        help_menu.addAction("关于").triggered.connect(self.show_about)

    def new_project(self):
        # 弹出窗口要求填写乐曲名和作者名
        song_name, ok1 = QInputDialog.getText(self, "新建项目", "请输入乐曲名:")
        if not ok1:
            return
        author_name, ok2 = QInputDialog.getText(self, "新建项目", "请输入作者名:")
        if not ok2:
            return

        self.song_name = song_name
        self.author_name = author_name

        self.draw_area.lines.clear()
        self.draw_area.notes.clear()  # 清空音符信息
        self.statusBar().showMessage("新建项目已创建，乐曲名: {}, 作者名: {}".format(song_name, author_name), 2000)
        self.update()

    def open_project(self):
        filename, _ = QFileDialog.getOpenFileName(self, "打开项目", "", "项目文件 (*.proj)")
        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as file:
                    data = json.load(file)
                    self.song_name = data.get('song_name', "")
                    self.author_name = data.get('author_name', "")
                    self.bpm = data.get('bpm', 120)
                    self.draw_area.notes = []
                    self.draw_area.lines = []  # 清空线条信息
                    for note_dict in data.get('notes', []):
                        line = LineSegment(
                            left_x=note_dict['left_x'],
                            right_x=note_dict['right_x'],
                            y=note_dict['y'],
                            color=QColor(173, 216, 230)
                        )
                        note = NoteSegment(line)
                        note.pitch.midi = note_dict['midi_value']
                        note.duration.quarterLength = note_dict['quarter_length']
                        note.timing = note_dict['timing']
                        self.draw_area.notes.append(note)
                        self.draw_area.lines.append(line)  # 更新 self.lines 列表
                    self.draw_area.update()
                    self.draw_area.repaint()
                    self.statusBar().showMessage(f"已打开项目: {filename}", 3000)
            except Exception as e:
                self.statusBar().showMessage(f"打开项目失败: {str(e)}", 5000)
                QMessageBox.critical(self, "错误", f"无法打开项目: {str(e)}")

    def save_project(self):
        # 生成默认文件名
        if self.song_name and self.author_name:
            default_filename = f"{self.song_name}_by{self.author_name}.proj"
        elif self.song_name:
            default_filename = f"{self.song_name}.proj"
        elif self.author_name:
            default_filename = f"by{self.author_name}.proj"
        else:
            default_filename = "untitled.proj"

        filename, _ = QFileDialog.getSaveFileName(self, "保存项目", default_filename, "项目文件 (*.proj)")
        if filename:
            try:
                note_dicts = [note.to_dict() for note in self.draw_area.notes]
                data = {
                    'song_name': self.song_name,
                    'author_name': self.author_name,
                    'bpm': self.bpm,
                    'notes': note_dicts
                }
                with open(filename, 'w', encoding='utf-8') as file:
                    json.dump(data, file, ensure_ascii=False, indent=4)
                self.statusBar().showMessage("项目已保存", 2000)
            except Exception as e:
                self.statusBar().showMessage(f"保存项目失败: {str(e)}", 5000)
                QMessageBox.critical(self, "错误", f"无法保存项目: {str(e)}")
    def save_asxml(self):
        save_musicxml(self.draw_area.notes,self.bpm,self.song_name,self.author_name)
        self.statusBar().showMessage("项目已保存为 XML", 2000)

    def open_xml(self):
        try:
            convert_notes_to_stream(self.draw_area.notes, self.bpm)
            tmp_xml = auto_save_musicxml(self.draw_area.notes,self.bpm,self.song_name,self.author_name)
            from converters.mxl2opt import mxl2opt
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
                self.timer.stop()
                self.is_playing = False
                self.btn_play.setText("播放乐谱")
                self.btn_pause.setEnabled(False)
                self.btn_resume.setEnabled(False)
                self.statusBar().showMessage("播放已停止", 2000)
                self.draw_area.draw_vertical_line_at_x(None)  # 停止播放时移除竖线
                return

            score_stream = convert_notes_to_stream(self.draw_area.notes, self.bpm)
            with tempfile.NamedTemporaryFile(suffix='.mid', delete=False) as midi_file:
                self.current_midi = midi_file.name
                score_stream.write('midi', self.current_midi)

            pygame.mixer.music.load(self.current_midi)
            pygame.mixer.music.play()
            self.is_playing = True
            self.btn_play.setText("停止播放")
            self.btn_pause.setEnabled(True)
            self.btn_resume.setEnabled(False)
            self.timer.start(10)  # 每10毫秒更新一次时间
            self.statusBar().showMessage("正在播放... 按播放键可停止", 2000)

        except Exception as e:
            self.statusBar().showMessage(f"播放失败: {str(e)}", 5000)

    def pause_music(self):
        if self.is_playing:
            pygame.mixer.music.pause()
            self.is_playing = False
            self.btn_pause.setEnabled(False)
            self.btn_resume.setEnabled(True)
            self.timer.stop()
            self.statusBar().showMessage("播放已暂停", 2000)

    def resume_music(self):
        if not self.is_playing:
            pygame.mixer.music.unpause()
            self.is_playing = True
            self.btn_pause.setEnabled(True)
            self.btn_resume.setEnabled(False)
            self.timer.start(10)
            self.statusBar().showMessage("继续播放...", 2000)

    def update_play_time(self):
        if self.is_playing:
            current_time = pygame.mixer.music.get_pos() / 1000
            time_info = f"当前时间: {current_time:.2f} 秒"
            self.statusBar().showMessage(time_info)

            # 根据BPM和当前时间计算竖线位置
            beats_per_minute = self.bpm
            seconds_per_beat = 60 / beats_per_minute
            current_beat = current_time / seconds_per_beat
            grid_size = self.draw_area.grid_size
            pixels_per_beat = 8 * grid_size  # 8个格子为一拍
            x_position = int(current_beat * pixels_per_beat)

            # 绘制竖线
            self.draw_area.draw_vertical_line_at_x(x_position)

            if not pygame.mixer.music.get_busy():
                self.is_playing = False
                self.btn_play.setText("播放乐谱")
                self.btn_pause.setEnabled(False)
                self.btn_resume.setEnabled(False)
                self.timer.stop()
                self.statusBar().showMessage("播放已结束", 2000)
                self.draw_area.draw_vertical_line_at_x(None)  # 播放结束时移除竖线

    def set_bpm(self):
        bpm, ok = QInputDialog.getInt(self, "设置BPM", "请输入BPM值:", self.bpm, 1, 300)
        if ok:
            self.bpm = bpm
            self.statusBar().showMessage(f"BPM已设置为: {bpm}", 3000)

    def set_song_name(self):
        song_name, ok = QInputDialog.getText(self, "修改乐曲名", "请输入新的乐曲名:", text=self.song_name)
        if ok:
            self.song_name = song_name
            self.statusBar().showMessage(f"乐曲名已修改为: {song_name}", 3000)

    def set_author_name(self):
        author_name, ok = QInputDialog.getText(self, "修改作者名", "请输入新的作者名:", text=self.author_name)
        if ok:
            self.author_name = author_name
            self.statusBar().showMessage(f"作者名已修改为: {author_name}", 3000)

    def closeEvent(self, event):
        if pygame.mixer.get_init():
            pygame.mixer.quit()
        if self.current_midi and os.path.exists(self.current_midi):
            os.remove(self.current_midi)
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    # print("Python Path:", sys.path)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())