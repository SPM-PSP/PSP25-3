from pathlib import Path
from music21 import converter

def mxl2midi(filename):
    try:
        current_dir = Path(__file__).parent.resolve()
        project_root = current_dir.parent
        name = filename.split('.')[0]
        input_mxl = project_root/"tmp_works"/filename
        mxl_path = project_root/"tmp_works"/(name+".mid")
        score = converter.parse(input_mxl)
        score.write('mid', mxl_path)
        print("Music21 done.")
    except Exception as e:
        print(f"{str(e)}")

    return mxl_path

if __name__ == '__main__':
    mxl2midi("c-flat.mxl")