import os
from music21 import converter, note, chord, meter, tempo, stream
from PyQt5.QtGui import QColor

# 确保导入自定义模块
from module.draw import LineSegment
from module.note import NoteSegment


def read_music_metadata(xml_file_path):
    """
    从MusicXML文件中读取歌曲元数据

    参数:
        xml_file_path (str): MusicXML文件路径

    返回:
        tuple: (song_name, author_name, bpm)
    """
    score = converter.parse(xml_file_path, forceSource=True)
    metadata_dict = {}

    # 1. 歌曲名称
    if score.metadata and score.metadata.title:
        metadata_dict['song_name'] = score.metadata.title
    else:
        base_name = os.path.splitext(os.path.basename(xml_file_path))[0]
        metadata_dict['song_name'] = base_name.replace('_', ' ')

    # 2. 作者名称
    if score.metadata and score.metadata.composer:
        metadata_dict['author_name'] = score.metadata.composer
    else:
        for contributor in score.metadata.contributors:
            if contributor.role == 'composer':
                metadata_dict['author_name'] = contributor.name
                break
        else:
            metadata_dict['author_name'] = "未知作者"

    # 3. BPM(速度)
    metadata_dict['bpm'] = 120  # 默认值
    for element in score.recurse(classFilter='MetronomeMark'):
        if element.number:
            metadata_dict['bpm'] = element.number
            break

    return metadata_dict['song_name'], metadata_dict['author_name'], metadata_dict['bpm']


def extract_notes_with_offsets(score):
    """
    提取音符数据并转换为LineSegment和NoteSegment对象，支持和弦(音程)

    参数:
        score (music21.stream.Score): 解析后的乐谱对象

    返回:
        tuple: (lines, notes) - LineSegment对象列表和NoteSegment对象列表
    """
    lines = []
    notes = []

    # 1. 计算小节偏移量和拍号信息
    measure_offsets = {}
    current_offset = 0.0
    measures = score.recurse().getElementsByClass(stream.Measure)
    current_time_signature = meter.TimeSignature('4/4')

    for measure in measures:
        # 检查并更新拍号变化
        for element in measure:
            if isinstance(element, meter.TimeSignature):
                current_time_signature = element

        # 记录当前小节的偏移量
        measure_offsets[measure.number] = current_offset
        current_offset += current_time_signature.barDuration.quarterLength

    # 2. 获取初始速度
    initial_tempo = 120
    for element in score.recurse():
        if isinstance(element, tempo.MetronomeMark):
            initial_tempo = element.number
            break

    # 3. 处理所有音符元素
    for element in score.recurse():
        if isinstance(element, note.Note):
            measure_obj = element.getContextByClass(stream.Measure)
            measure_num = measure_obj.number if measure_obj else 1
            absolute_offset = measure_offsets.get(measure_num, 0.0) + element.offset
            _process_note(element, absolute_offset, initial_tempo, lines, notes)

        # 处理和弦(音程)
        elif isinstance(element, chord.Chord):
            measure_obj = element.getContextByClass(stream.Measure)
            measure_num = measure_obj.number if measure_obj else 1
            absolute_offset = measure_offsets.get(measure_num, 0.0) + element.offset
            for n in element.notes:
                _process_note(n, absolute_offset, initial_tempo, lines, notes)
                print(absolute_offset)

    return lines, notes


def _process_note(note_element, offset, initial_tempo, lines, notes):

    # 获取音符属性
    pitch_midi = note_element.pitch.midi
    duration = note_element.duration.quarterLength

    # 获取当前速度
    tempo_mark = note_element.getContextByClass(tempo.MetronomeMark)
    current_bpm = tempo_mark.number if tempo_mark else initial_tempo

    # 计算坐标参数
    y = (109 - pitch_midi) * 20  # MIDI音高转换为Y坐标
    left_x = offset * 160  # 时间转换为X坐标
    right_x = left_x + duration * 160  # 时值转换为宽度

    # 创建LineSegment对象
    line = LineSegment(
        left_x=left_x,
        right_x=right_x,
        y=y,
        color=QColor(173, 216, 230)  # 浅蓝色
    )

    # 创建NoteSegment对象
    note_obj = NoteSegment(line)

    # 设置音乐属性
    note_obj.pitch.midi = pitch_midi
    note_obj.duration.quarterLength = duration
    note_obj.timing = offset

    # 添加到结果列表
    lines.append(line)
    notes.append(note_obj)

    # 打印调试信息
    #print(f"音符: MIDI={pitch_midi}, 时间={absolute_offset:.2f}拍, "
          #f"时值={duration}拍 -> 坐标: ({left_x:.1f}, {right_x:.1f}, {y:.1f})")


# 示例使用
if __name__ == "__main__":
    # 加载乐谱文件
    file_path = "../tmp_works/tmp_20250528164839.xml"

    try:
        # 读取元数据
        song_name, author_name, bpm = read_music_metadata(file_path)
        print(f"歌曲名称: {song_name}")
        print(f"作者姓名: {author_name}")
        print(f"BPM(速度): {bpm}")

        # 解析乐谱
        score = converter.parse(file_path)

        # 提取音符数据(包括音程/和弦)
        lines, notes = extract_notes_with_offsets(score)

        # 输出统计信息
        print(f"\n提取完成: 共找到 {len(notes)} 个音符和 {len([n for n in notes if hasattr(n, 'chord')])} 个和弦")

        # 打印前几个音符信息
        print("\n前10个音符信息:")
        for i, note_obj in enumerate(notes[:10]):
            print(
                f"{i + 1}. MIDI音高: {note_obj.pitch.midi}, 时间: {note_obj.timing:.2f}拍, 时值: {note_obj.duration.quarterLength:.2f}拍")

    except Exception as e:
        print(f"处理错误: {e}")