from module.draw import *
from module.stream import *
from module.note import *
from module.ran_midi import *
from converters.mxl2proj import *
from converters.midi2mxl import *
from converters.wav2midi import *
from converters.opt2mxl import *
from pathlib import Path
import pygame
import tempfile
import sys
import os
import json
from module.piano import *
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QGroupBox,QComboBox,
                             QHBoxLayout, QPushButton, QLabel, QLineEdit, QSpinBox,
                             QTextEdit, QStatusBar, QFileDialog, QAction, qApp, QDialogButtonBox,
                             QScrollArea, QMessageBox, QInputDialog, QSplitter, QDialog)
from PyQt5.QtGui import QIcon, QColor, QPainter, QPen, QFont, QPixmap, QImage
from PyQt5.QtCore import Qt, QPointF, QSize, QTimer

import fitz
from module.pdf_reader import PDFViewer

project_root = Path(__file__).parent.resolve()
sys.path.append(str(project_root))  # 添加项目根目录到路径
MAX_DRAW_WIDTH = 800000

class AIDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("AI助手 - MIDI生成")
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        # 音乐类型选择
        music_type_group = QGroupBox("音乐类型")
        type_layout = QVBoxLayout()
        self.type_combo = QComboBox()
        self.type_combo.addItem("旋律", "mel")
        self.type_combo.addItem("三重奏", "trio")
        type_layout.addWidget(QLabel("选择音乐类型:"))
        type_layout.addWidget(self.type_combo)
        music_type_group.setLayout(type_layout)
        layout.addWidget(music_type_group)

        # 生成数量选择
        batch_group = QGroupBox("生成设置")
        batch_layout = QVBoxLayout()
        self.batch_spin = QSpinBox()
        self.batch_spin.setRange(1, 10)
        self.batch_spin.setValue(1)
        batch_layout.addWidget(QLabel("生成数量:"))
        batch_layout.addWidget(self.batch_spin)
        batch_group.setLayout(batch_layout)
        layout.addWidget(batch_group)

        # 按钮
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        self.setLayout(layout)

    def get_selected_type(self):
        return self.type_combo.currentData()

    def get_batch_size(self):
        return self.batch_spin.value()


class HorizontalScrollArea(QScrollArea):
    """自定义滚动区域：默认鼠标滚轮控制水平滚动，按住Ctrl控制竖直滚动，滚动到边界时扩展画布"""
    extendCanvas = pyqtSignal(int)  # 扩展画布信号，参数为扩展量

    def wheelEvent(self, event):
        if event.modifiers() & Qt.ControlModifier:
            super().wheelEvent(event)  # 按住Ctrl时使用默认竖直滚动
        else:
            # 控制水平滚动
            delta = event.angleDelta().y()
            h_scroll = self.horizontalScrollBar()

            # 检测是否在最右端并继续向右滚动
            if delta < 0:  # 滚轮向下（向右滚动）
                current_pos = h_scroll.value()
                max_pos = h_scroll.maximum()
                if current_pos >= max_pos - 10:  # 接近最右端时
                    self.extendCanvas.emit(200)  # 发送扩展信号（200像素）
                    return  # 消耗事件，避免滚动条跳动

            h_scroll.setValue(h_scroll.value() - delta // 2)  # 正常滚动
            event.accept()

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
        self.draw_scroll_area = HorizontalScrollArea()
        self.draw_scroll_area.setWidget(self.draw_area)
        self.draw_scroll_area.setWidgetResizable(False)
        self.draw_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.draw_scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.draw_area.mouseMoveSignal.connect(self.handle_mouse_move)
        top_layout.addWidget(self.draw_scroll_area)
        # 联动垂直滚动条
        self.draw_scroll_area.verticalScrollBar().valueChanged.connect(
            piano_scroll_area.verticalScrollBar().setValue)
        piano_scroll_area.verticalScrollBar().valueChanged.connect(
            self.draw_scroll_area.verticalScrollBar().setValue)

        # **新增水平滚动条事件处理**
        h_scroll = self.draw_scroll_area.horizontalScrollBar()
        h_scroll.valueChanged.connect(self.handle_horizontal_scroll)

        self.draw_scroll_area.extendCanvas.connect(self.expand_draw_area)

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

        try:
            with open('style.qss', 'r', encoding='utf-8') as f:
                self.setStyleSheet(f.read())
        except Exception as e:
            print(f"加载样式表失败: {e}")
    def handle_mouse_move(self, pos):
        """处理鼠标移动自动滚动（完全禁止向左滚动）"""
        # 坐标系转换
        container_pos = self.draw_area.mapTo(self.draw_area, pos)

        # 获取滚动条和视口参数
        h_scroll = self.draw_scroll_area.horizontalScrollBar()
        current_value = h_scroll.value()
        viewport_width = self.draw_scroll_area.viewport().width()

        # 计算理想滚动位置（鼠标在视口右20像素处）
        ideal_target = container_pos.x() - viewport_width + 20

        # 当需要向右滚动时
        if ideal_target > current_value:  # 修改判断条件
            # 动态扩展区域（当接近右边界时）
            if container_pos.x() > self.draw_area.width() - viewport_width // 2:
                self.expand_draw_area(20)

            # 计算安全滚动位置（限制在最大值范围内）
            safe_target = min(ideal_target, h_scroll.maximum())
            h_scroll.setValue(safe_target)
        else:
            # 主动锁定滚动条位置（核心修改）
            h_scroll.setValue(current_value)  # 强制保持当前位置

        # 完全禁止向左滚动（即使通过其他方式操作滚动条）
        if h_scroll.value() < current_value:
            h_scroll.setValue(current_value)

    def handle_horizontal_scroll(self, value):
        """处理水平滚动条拖动事件，到达右端时自动扩展画布"""
        h_scroll = self.draw_scroll_area.horizontalScrollBar()
        max_value = h_scroll.maximum()
        viewport_width = self.draw_scroll_area.viewport().width()

        # 当滚动条值达到最大值且用户继续向右拖动时
        if value == max_value and h_scroll.isSliderDown():
            # 计算当前画布右侧可见区域（预留100像素缓冲）
            visible_right = self.draw_area.width() - (max_value + viewport_width)
            if visible_right <= 100:  # 剩余可见区域小于100像素时触发扩展
                self.expand_draw_area(20)
    def expand_draw_area(self, x):
        """安全扩展绘制区域"""
        current_width = self.draw_area.width()

        if current_width >= MAX_DRAW_WIDTH:
            return

        new_width = min(current_width + x, MAX_DRAW_WIDTH)
        self.draw_area.setFixedWidth(new_width)

        # 强制布局更新
        self.draw_scroll_area.widget().updateGeometry()
        self.draw_scroll_area.viewport().update()

        # 确保滚动条更新后跳转
        QTimer.singleShot(10, lambda:
        self.draw_scroll_area.horizontalScrollBar().setValue(
            self.draw_scroll_area.horizontalScrollBar().maximum()
        ))

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

        # 创建"另存为"子菜单
        save_as_menu = file_menu.addMenu("另存为")
        save_as_menu.addAction("另存为XML").triggered.connect(self.save_as_xml)
        save_as_menu.addAction("另存为PDF").triggered.connect(self.save_as_pdf)
        save_as_menu.addAction("另存为MIDI").triggered.connect(self.save_as_midi)  # 新增菜单项

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

        # 添加AI助手菜单项
        ai_assistant_action = QAction("AI助手", self)
        ai_assistant_action.triggered.connect(self.open_ai_assistant)
        help_menu.addAction(ai_assistant_action)

    def open_ai_assistant(self):
        """打开AI助手对话框"""
        try:
            dialog = AIDialog(self)
            if dialog.exec_() == QDialog.Accepted:
                music_type = dialog.get_selected_type()
                batch_size = dialog.get_batch_size()

                # 显示生成中提示
                QMessageBox.information(self, "AI生成中",
                                        f"正在使用AI生成{batch_size}首{music_type}类型音乐...\n\n"
                                        "这可能需要一些时间，请稍候...",
                                        QMessageBox.Ok)

                # 调用MIDI生成函数
                generated_files = ran_midi(batch=batch_size, option=music_type)

                if generated_files:
                    file_list = "\n".join([str(f) for f in generated_files])
                    QMessageBox.information(self, "生成成功",
                                            f"成功生成了{batch_size}首MIDI音乐！\n\n"
                                            f"生成的文件路径:\n{file_list}\n\n"
                                            "这些文件可以在'assets/midi'目录中找到。",
                                            QMessageBox.Ok)
                else:
                    QMessageBox.warning(self, "生成失败",
                                        "MIDI生成失败，请检查控制台输出或日志文件。",
                                        QMessageBox.Ok)

        except Exception as e:
            QMessageBox.critical(self, "错误", f"AI助手运行失败: {str(e)}")
    def save_as_midi(self):
        """将当前乐谱另存为MIDI文件"""
        try:
            # 生成默认文件名
            if self.song_name and self.author_name:
                default_filename = f"{self.song_name}_by{self.author_name}.mid"
            elif self.song_name:
                default_filename = f"{self.song_name}.mid"
            elif self.author_name:
                default_filename = f"by{self.author_name}.mid"
            else:
                default_filename = "untitled.mid"

            filename, _ = QFileDialog.getSaveFileName(self, "保存为MIDI", default_filename, "MIDI文件 (*.mid)")
            if not filename:
                return

            # 先创建临时XML文件
            tmp_xml = auto_save_musicxml(self.draw_area.notes, self.bpm, self.song_name, self.author_name)

            # 使用mxl2midi转换为MIDI
            from converters.mxl2midi import mxl2midi  # 导入MIDI转换函数
            tmp_midi = mxl2midi(tmp_xml)

            # 将临时MIDI文件复制到用户指定位置
            import shutil
            shutil.copy2(tmp_midi, filename)

            self.statusBar().showMessage(f"已保存为MIDI: {filename}", 3000)
        except Exception as e:
            self.statusBar().showMessage(f"保存MIDI失败: {str(e)}", 5000)
            QMessageBox.critical(self, "错误", f"无法保存为MIDI: {str(e)}")
    def save_as_pdf(self):
        """将当前乐谱另存为PDF文件"""
        try:
            # 生成默认文件名
            if self.song_name and self.author_name:
                default_filename = f"{self.song_name}_by{self.author_name}.pdf"
            elif self.song_name:
                default_filename = f"{self.song_name}.pdf"
            elif self.author_name:
                default_filename = f"by{self.author_name}.pdf"
            else:
                default_filename = "untitled.pdf"

            filename, _ = QFileDialog.getSaveFileName(self, "保存为PDF", default_filename, "PDF文件 (*.pdf)")
            if not filename:
                return

            # 先创建临时XML文件
            tmp_xml = auto_save_musicxml(self.draw_area.notes, self.bpm, self.song_name, self.author_name)

            # 使用mxl2opt转换为PDF
            from converters.mxl2opt import mxl2opt
            tmp_pdf = mxl2opt(tmp_xml)

            # 将临时PDF文件复制到用户指定位置
            import shutil
            shutil.copy2(tmp_pdf, filename)

            self.statusBar().showMessage(f"已保存为PDF: {filename}", 3000)
        except Exception as e:
            self.statusBar().showMessage(f"保存PDF失败: {str(e)}", 5000)
            QMessageBox.critical(self, "错误", f"无法保存为PDF: {str(e)}")
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
        filename, _ = QFileDialog.getOpenFileName(
            self,
            "打开文件",
            "",
            "所有支持格式 (*.proj *.xml *.mid *.midi *.pdf);;"
            "项目文件 (*.proj);;"
            "MusicXML文件 (*.xml);;"
            "MIDI文件 (*.mid *.midi);;"
            "PDF文件 (*.pdf)"
        )
        try:
            if filename.endswith('.proj'):
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
            elif filename.endswith('.xml'):
                score = converter.parse(filename)
                self.song_name, self.author_name, self.bpm = read_music_metadata(filename)
                self.draw_area.lines, self.draw_area.notes = extract_notes_with_offsets(score)
                self.draw_area.update()
                self.draw_area.repaint()
                self.statusBar().showMessage(f"已打开项目: {filename}", 3000)
            elif filename.endswith(('.mid', '.midi')):
                try:
                    # 解析MIDI文件
                    score = converter.parse(filename)

                    # 提取BPM信息
                    bpm = 120  # 默认值
                    for item in score.flat:
                        if isinstance(item, tempo.MetronomeMark):
                            bpm = item.number
                            break
                    self.bpm = bpm

                    # 提取元数据
                    metadata = score.metadata
                    self.song_name = metadata.title if metadata.title else "未命名"
                    self.author_name = metadata.composer if metadata.composer else "未知作者"

                    # 提取音符和线条信息
                    self.draw_area.lines, self.draw_area.notes = extract_notes_with_offsets(score)

                    # 更新显示
                    self.draw_area.update()
                    self.draw_area.repaint()

                    self.statusBar().showMessage(f"已打开MIDI文件: {filename}", 3000)
                except Exception as e:
                    self.statusBar().showMessage(f"打开MIDI文件失败: {str(e)}", 5000)
                    QMessageBox.critical(self, "错误", f"无法解析MIDI文件: {str(e)}")

            elif filename.endswith('.pdf'):
                # 处理PDF文件
                self.statusBar().showMessage("正在识别PDF文件...", 2000)

                # 提取文件名(不带扩展名)
                name = Path(filename).stem

                # 复制PDF到临时工作目录
                current_dir = Path(__file__).resolve()
                project_root = current_dir.parent
                tmp_pdf_path = project_root / "tmp_works" / f"{name}.pdf"
                shutil.copy2(filename, tmp_pdf_path)

                # 调用Opt2Mxl进行PDF转MusicXML
                sheets = ""  # 用户可以指定需要处理的页面，这里留空表示处理所有页面
                opt2mxl(f"{name}.pdf", sheets, True)

                # 查找转换后的MusicXML文件
                mxl_files = list((project_root / "tmp_works").glob(f"{name}*.mxl"))
                if not mxl_files:
                    raise FileNotFoundError("未找到转换后的MusicXML文件")

                # 使用第一个找到的MXL文件
                mxl_path = mxl_files[0]

                # 解析MusicXML文件
                score = converter.parse(str(mxl_path))

                # 提取元数据
                self.song_name = name  # 默认使用文件名作为歌曲名
                self.author_name = "未知作者"  # 默认作者
                self.bpm = 120  # 默认BPM

                # 尝试从MusicXML中提取实际元数据
                if hasattr(score, 'metadata'):
                    if score.metadata.title:
                        self.song_name = score.metadata.title
                    if score.metadata.composer:
                        self.author_name = score.metadata.composer

                # 尝试提取BPM
                for item in score.flat:
                    if isinstance(item, tempo.MetronomeMark):
                        self.bpm = item.number
                        break

                # 提取音符和线条信息
                self.draw_area.lines, self.draw_area.notes = extract_notes_with_offsets(score)

                # 更新显示
                self.draw_area.update()
                self.draw_area.repaint()

                self.statusBar().showMessage(f"已打开PDF文件: {filename}", 3000)

        except Exception as e:
            self.statusBar().showMessage(f"打开文件失败: {str(e)}", 5000)
            QMessageBox.critical(self, "错误", f"无法打开文件: {str(e)}")

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

    def save_as_xml(self):
        """将当前乐谱另存为XML文件"""
        # 生成默认文件名
        if self.song_name and self.author_name:
            default_filename = f"{self.song_name}_by{self.author_name}.xml"
        elif self.song_name:
            default_filename = f"{self.song_name}.xml"
        elif self.author_name:
            default_filename = f"by{self.author_name}.xml"
        else:
            default_filename = "untitled.xml"

        filename, _ = QFileDialog.getSaveFileName(self, "保存为XML", default_filename, "XML文件 (*.xml)")
        if filename:
            try:
                save_musicxml(self.draw_area.notes, self.bpm, self.song_name, self.author_name, filename)
                self.statusBar().showMessage(f"项目已保存为 XML: {filename}", 2000)
            except Exception as e:
                self.statusBar().showMessage(f"保存XML失败: {str(e)}", 5000)
                QMessageBox.critical(self, "错误", f"无法保存为XML: {str(e)}")

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