from music21 import *
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton
from PyQt5.QtGui import QPainter
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QFileDialog
import sys
import os
from module.merge import SegmentStructure
from datetime import datetime
from music21 import stream, note, chord, tempo
from module.merge import SegmentStructure


def convert_notes_to_stream(Notelist, bpm=120):
    s = stream.Stream()
    # 设置bpm
    mm = tempo.MetronomeMark(number=bpm)
    s.insert(0, mm)

    structure = SegmentStructure()
    for noteelement in Notelist:
        structure.add_segment(noteelement.left_x, noteelement.right_x, 109 - noteelement.y / 20)
    result, rest = structure.compute_result()
    for element in result:
        if len(element[2]) == 1:
            note1 = note.Note(pitch=element[2][0], quarterLength=(element[1] - element[0]) / 160.0)
            s.insert(element[0] / 160.0, note1)
        else:
            c_major = chord.Chord()
            for i in range(len(element[2])):
                c_major.add(note.Note(pitch=element[2][i]))
            c_major.quarterLength = (element[1] - element[0]) / 160.0
            s.insert(element[0] / 160.0, c_major)
    for element in rest:
        s.insert(element[0] / 160.0, note.Rest(quarterLength=(element[1] - element[0]) / 160.0))
    return s


def save_musicxml(notes, bpm, song_name="untitled", author_name="unnamed"):
    """保存为MusicXML文件"""
    # 获取保存路径
    filepath, _ = QFileDialog.getSaveFileName(
        None, "保存乐谱",
        "untitled.xml",
        "MusicXML文件 (*.xml)"
    )

    if not filepath:  # 用户取消保存
        return

    # 生成乐谱流
    score_stream = convert_notes_to_stream(notes, bpm)

    # 设置元数据
    meta = metadata.Metadata()
    meta.title = song_name
    meta.composer = author_name
    score_stream.insert(0, meta)

    # 保存文件
    score_stream.write('musicxml', fp=filepath)

    # 可选：提示保存成功
    window.statusBar().showMessage(f"乐谱已保存至：{filepath}", 3000)

    # 可选：自动打开文件
    score_stream.show('musicxml')


def auto_save_musicxml(notes, bpm, song_name="untitled", author_name="unnamed"):
    """自动保存乐谱到tmp_works目录"""

    # 创建保存目录（如果不存在）
    save_dir = "tmp_works"
    os.makedirs(save_dir, exist_ok=True)

    # 生成带时间戳的文件名
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    filename = f"tmp_{timestamp}.xml"
    filepath = os.path.join(save_dir, filename)

    # 生成乐谱流
    score_stream = convert_notes_to_stream(notes, bpm)

    # 设置元数据
    meta = metadata.Metadata()
    meta.title = song_name
    meta.composer = author_name
    score_stream.insert(0, meta)

    # 保存文件
    score_stream.write('musicxml', fp=filepath)

    # 保留最近20个文件
    files = sorted(os.listdir(save_dir), reverse=True)
    for old_file in files[20:]:
        os.remove(os.path.join(save_dir, old_file))

    return filename


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    btn_export = QPushButton("导出乐谱", window)
    btn_export.clicked.connect(lambda:
                               convert_notes_to_stream(window.canvas.notes).show('musicxml')
                               )
    window.show()
    sys.exit(app.exec_())