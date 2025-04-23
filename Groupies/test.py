from music21 import note, stream, meter

# 创建乐谱结构
s = stream.Score()
p = stream.Part()
m = stream.Measure()
m.append(meter.TimeSignature('4/4'))

# 添加音符
n = note.Note("C4", quarterLength=1)
m.append(n)

# 组装乐谱
p.append(m)
s.append(p)

# 保存为 MusicXML
s.write('musicxml', 'my_score.xml')  # 或 s.write('my_score.xml')