from draw import *
from music21.note import Note
from music21 import pitch, duration
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtGui import QPainter
from PyQt5.QtCore import Qt
import pygame
import numpy as np

class AudioEngine:  # 新增音频引擎类
    def __init__(self, bpm=60):
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=2048)
        self.bpm = bpm

    def get_note_properties(self, note_segment):
        """从NoteSegment获取音频属性"""
        try:
            # 直接从music21对象获取频率
            frequency = note_segment.pitch.frequency
        except:
            frequency = 440.0

        try:
            # 计算时值（秒）
            mt = pygame.tempo.MetronomeMark(number=self.bpm)
            seconds = note_segment.duration.quarterLength * mt.secondsPerQuarter()
        except:
            seconds = 1.0

        return frequency, seconds

    def play_note(self, note_segment):
        """生成并播放音符"""
        freq, secs = self.get_note_properties(note_segment)

        # 生成音频数据
        sample_rate = 44100
        t = np.linspace(0, secs, int(sample_rate * secs), False)
        wave = np.sin(2 * np.pi * freq * t)

        # 添加淡出效果
        fade_samples = int(sample_rate * 0.05)
        wave[-fade_samples:] *= np.linspace(1, 0, fade_samples)

        # 转换音频格式
        audio = (wave * 32767).astype(np.int16)
        stereo_audio = np.repeat(audio.reshape(-1, 1), 2, axis=1)
        sound = pygame.sndarray.make_sound(stereo_audio)

        # 播放声音
        channel = pygame.mixer.find_channel()
        if channel:
            channel.play(sound)

class AudioEngine:  # 新增音频引擎类
    def __init__(self, bpm=60):
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=2048)
        self.bpm = bpm

    def get_note_properties(self, note_segment):
        """从NoteSegment获取音频属性"""
        try:
            # 直接从music21对象获取频率
            frequency = note_segment.pitch.frequency
        except:
            frequency = 440.0

        try:
            # 计算时值（秒）
            mt = pygame.tempo.MetronomeMark(number=self.bpm)
            seconds = note_segment.duration.quarterLength * mt.secondsPerQuarter()
        except:
            seconds = 1.0

        return frequency, seconds

    def play_note(self, note_segment):
        """生成并播放音符"""
        freq, secs = self.get_note_properties(note_segment)

        # 生成音频数据
        sample_rate = 44100
        t = np.linspace(0, secs, int(sample_rate * secs), False)
        wave = np.sin(2 * np.pi * freq * t)

        # 添加淡出效果
        fade_samples = int(sample_rate * 0.05)
        wave[-fade_samples:] *= np.linspace(1, 0, fade_samples)

        # 转换音频格式
        audio = (wave * 32767).astype(np.int16)
        stereo_audio = np.repeat(audio.reshape(-1, 1), 2, axis=1)
        sound = pygame.sndarray.make_sound(stereo_audio)

        # 播放声音
        channel = pygame.mixer.find_channel()
        if channel:
            channel.play(sound)

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
                notes=NoteSegment(self.temp_line)
                self.notes.append(notes)
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