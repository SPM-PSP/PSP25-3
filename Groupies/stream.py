# stream.py
from music21 import stream, metadata, tempo
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton
from PyQt5.QtGui import QPainter
from PyQt5.QtCore import Qt
from note import MainWindow
import sys
def convert_notes_to_stream(note_segments):
    score_stream = stream.Score()
    md = metadata.Metadata()
    md.title = "生成乐谱"
    md.composer = "AI Composer"
    score_stream.insert(0, md)
    part = stream.Part()
    sorted_notes = sorted(note_segments, key=lambda x: x.timing)
    time_map = {}
    for note in sorted_notes:
        time = note.timing
        if time not in time_map:
            time_map[time] = []
        time_map[time].append(note)
    for time in sorted(time_map.keys()):
        if len(time_map[time]) > 1:
            chord = stream.Chord(time_map[time])
            part.insert(time, chord)
        else:
            part.insert(time, time_map[time][0])
    score_stream.metronome = tempo.MetronomeMark(number=120)
    #part.insert(0, score_stream.metronome)
    #part.insert(0, stream.TimeSignature('4/4'))
    score_stream.insert(0, part)
    return score_stream

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    btn_export = QPushButton("导出乐谱", window)
    btn_export.clicked.connect(lambda:
                               convert_notes_to_stream(window.canvas.notes).show('musicxml')
                               )
    window.show()
    sys.exit(app.exec_())