
from music21 import converter
from pathlib import Path

# 翻译人声midi时会出现bug，待修复
def midi2mxl(filename):
    try:
        current_dir = Path(__file__).parent.resolve()
        project_root = current_dir.parent
        name = filename.split('.')[0]
        input_midi = project_root/"tmp_works"/filename
        mxl_path = project_root/"tmp_works"/(name+".mxl")
        score = converter.parse(input_midi)
        score.write('mxl', mxl_path)
        print("Music21 done.")
    except Exception as e:
        print(f"{str(e)}")

    return mxl_path

if __name__ == '__main__':
    midi2mxl("F-Sharp-Major.midi")