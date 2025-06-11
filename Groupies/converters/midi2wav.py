import subprocess
from pathlib import Path

def midi2wav(filename, fontname):
    try:
        current_dir = Path(__file__).parent.resolve()
        project_root = current_dir.parent
        name = filename.split('.')[0]
        input_midi = project_root/"tmp_works"/filename
        font_path = project_root/"sound_font"/fontname
        wav_path = project_root/"tmp_works"/(name+".wav")
        command = [
            "fluidsynth",  # Windows: str(project_root/'plugins'/'fluidsynth'/'bin'/'fluidsynth.exe')
            "-ni", "-F", str(wav_path), "-r", "48000", str(font_path), str(input_midi)
        ]
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            print("FluidSynth done.")
        else:
            print(result.stderr)
    except Exception as e:
        print(f"{str(e)}")
if __name__ == '__main__':
    midi2wav("c-flat.mid", "organs.sf2")