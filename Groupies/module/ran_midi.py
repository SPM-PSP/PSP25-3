import yaml, subprocess
from pathlib import Path


"""生成一段随机的乐曲，mel单声部trio多声部"""
def ran_midi(batch = 1, option = "mel"):
    project_root = Path(config['BASIC_CONFIG']['PROJECT_ROOT'])
    model_name = ""
    config_name = ""
    if option == "trio":
        model_name = "hierdec-trio_16bar.tar"
        config_name = "hierdec-trio_16bar"
    elif option == "mel":
        model_name = "hierdec-mel_16bar.tar"
        config_name = "hierdec-mel_16bar"
    command = [
        "music_vae_generate",
        "--config="+config_name,
        "--checkpoint_file="+str(project_root/"pretrained_models"/"musicvae_checkpoint"/model_name),
        "--mode=sample",
        "--num_outputs="+str(batch),
        "--output_dir="+str(project_root/"assets"/"midi")
    ]
    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
    )
    if result.returncode == 0:
        print("Musicvae done.")
    else:
        print(result.stderr)