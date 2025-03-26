# stream.py
from music21 import *
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton
from PyQt5.QtGui import QPainter
from PyQt5.QtCore import Qt
from note import MainWindow
import sys
from merge import SegmentStructure
def convert_notes_to_stream(Notelist):
    s=stream.Stream()
    structure=SegmentStructure()
    for noteelement in Notelist:
        #print(noteelement.left_x,noteelement.right_x,noteelement.y)
        structure.add_segment(noteelement.left_x,  noteelement.right_x , 105-noteelement.y/20)
    result = structure.compute_result()
    for element in result:
        if len(element[2])==1:
            note1=note.Note(pitch=element[2][0],quarterLength=(element[1]-element[0])/160.0)
            s.insert(element[0]/160.0, note1)
        else:
            c_major=chord.Chord()
            for i in range(len(element[2])):
                c_major.add(note.Note(pitch=element[2][i]))
            c_major.quarterLength = (element[1]-element[0])/160.0
            s.insert(element[0]/160.0, c_major)
    return s

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    btn_export = QPushButton("导出乐谱", window)
    btn_export.clicked.connect(lambda:
                               convert_notes_to_stream(window.canvas.notes).show('musicxml')
                               )
    window.show()
    sys.exit(app.exec_())