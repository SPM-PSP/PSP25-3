import os, shutil, subprocess
from pathlib import Path
from pydub import AudioSegment


def wav2midi(filename, isvocal=False):
    try:
        current_dir = Path(__file__).parent.resolve()
        project_root = current_dir.parent
        name = filename.split('.')[0]
        input_wav = project_root / "tmp_works" / filename
        midi_path = project_root / "tmp_works" / (name + ".mid")

        # 如果是MP3文件，先转换为WAV
        if filename.endswith('.mp3'):
            input_mp3 = input_wav  # 原代码中路径错误，这里假设用户传入的是MP3文件名
            audio = AudioSegment.from_mp3(str(input_mp3))
            input_wav = project_root / "tmp_works" / (name + ".wav")
            audio.export(str(input_wav), format="wav")
            print("mp32wav done.")

        # 此处应添加实际的WAV转MIDI逻辑
        print(f"处理WAV文件: {input_wav}")
        print(f"MIDI输出路径: {midi_path}")
        # TODO: 添加WAV转MIDI的实现代码

    except Exception as e:
        print(f"错误: {str(e)}")

        if isvocal:
            command = [
                "python", "-m", "spleeter", "separate", "-p",
                "spleeter:2stems", "-o", "output", input_wav
            ]
            os.chdir("..")
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
            )
            shutil.move(str(project_root/"output"/name), str(project_root/"assets"/"wav"))
            shutil.rmtree(str(project_root/"output"))
            if result.returncode == 0:
                print("Spleeter done.")
            else:
                print(result.stderr)
            some_infer_script = project_root/"pretrained_models"/"some"/"infer.py"
            some_model_path = project_root/"pretrained_models"/"some"/"dpcda"/"0918_continuous128_clean_3spk"/"model_ckpt_steps_104000_simplified.ckpt"
            input_vocals = project_root/"assets"/"wav"/"syst"/"vocals.wav"
            midi_tmp = project_root/"assets"/"wav"/"syst"/"vocals.mid"
            command = [
                "python", str(some_infer_script),
                "--model", str(some_model_path),
                "--wav", str(input_vocals),
            ]
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
            )
            shutil.move(str(midi_tmp), str(midi_path))
            os.rename(str(midi_path/"vocals.mid"), str(midi_path/(name+".mid")))
            if result.returncode == 0:
                print("SOME done.")
            else:
                print(result.stderr)

        else:
            magenta_model_path = project_root/"pretrained_models"/"maestro_checkpoint"

            # Windows: .../"xxx.exe"
            script_path = project_root/"scripts"/"onsets_frames_transcription_transcribe"
            command = [
                str(script_path),
                "--model_dir="+str(magenta_model_path),
                str(input_wav)
            ]
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
            )
            midi_tmp = project_root/"assets"/"wav"/(name+".wav.midi")
            shutil.move(str(midi_tmp), str(midi_path))
            os.rename(str(midi_path/(name+".wav.midi")), str(midi_path/(name+".midi")))
            if result.returncode == 0:
                print("Magenta done.")
            else:
                print(result.stderr)
    except Exception as e:
        print(f"{str(e)}")

if __name__ == '__main__':
    wav2midi("F-Sharp-Major.wav")