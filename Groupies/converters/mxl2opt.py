import subprocess
from pathlib import Path

MUSESCORE_PATH = "C:/Program Files/MuseScore 4/bin/MuseScore4.exe"

def mxl2opt(filename, isPDF = True):
    try:
        current_dir = Path(__file__).parent.resolve()
        project_root = current_dir.parent
        name = filename.split('.')[0]
        input_mxl = project_root/"tmp_works"/filename
        opt_type = None
        if isPDF:
            opt_type = ".pdf"
        else:
            opt_type = ".jpg"
        opt_path = project_root/"tmp_works"/(name+opt_type)
        command = [
            MUSESCORE_PATH,
            "-o", opt_path, input_mxl
        ]
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            print("MuseScore done.")
        else:
            print(result.stderr)
    except Exception as e:
        print(f"{str(e)}")

    return opt_path