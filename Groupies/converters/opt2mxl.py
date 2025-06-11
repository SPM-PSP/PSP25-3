import os
import subprocess
import shutil
from pathlib import Path

# 默认配置
DEFAULT_CONFIG = {
    # 项目根目录（默认为当前文件所在目录的父目录）
    "PROJECT_ROOT": Path(__file__).parent.parent.resolve(),

    # Audiveris OMR软件路径
    "AUDIVERIS_PATH": "Audiveris",

    # 临时工作目录
    "TEMP_WORK_DIR": "tmp_works",

    # 处理PDF时默认使用的页面范围（空字符串表示所有页面）
    "DEFAULT_SHEETS": "",

    # 是否在处理后清理临时文件
    "CLEANUP_TEMP_FILES": True,

    # 要清理的临时文件扩展名
    "TEMP_FILE_EXTENSIONS": ['.omr', '.log', '.omr.zip']
}


def opt2mxl(filename, sheets=None, isPDF=True, config=None):
    # 使用默认配置或用户提供的配置
    if config is None:
        config = DEFAULT_CONFIG

    try:
        # 获取项目路径和文件路径
        project_root = config["PROJECT_ROOT"]
        audiveris_path = project_root / config["AUDIVERIS_PATH"]
        temp_work_dir = project_root / config["TEMP_WORK_DIR"]

        # 确保临时工作目录存在
        temp_work_dir.mkdir(parents=True, exist_ok=True)

        # 获取输入文件路径
        input_file = temp_work_dir / filename

        # 如果文件不存在于临时目录中，尝试从当前目录复制
        if not input_file.exists():
            current_dir = Path(__file__).parent.resolve()
            source_file = current_dir / filename
            if source_file.exists():
                shutil.copy2(source_file, input_file)
                print(f"已复制文件: {source_file} -> {input_file}")
            else:
                raise FileNotFoundError(f"文件不存在: {filename}")

        # 确定Audiveris执行文件路径
        if os.name == 'nt':  # Windows系统
            model_path = audiveris_path / "bin" / "Audiveris.bat"
        else:  # Linux/Mac系统
            model_path = audiveris_path / "bin" / "Audiveris"

        # 确保Audiveris可执行文件存在
        if not model_path.exists():
            raise FileNotFoundError(f"Audiveris执行文件不存在: {model_path}")

        # 设置输出目录
        output_dir = temp_work_dir

        # 设置页面范围（如果未指定则使用默认值）
        if sheets is None:
            sheets = config["DEFAULT_SHEETS"]

        # 构建命令
        if isPDF and sheets:
            command = [
                str(model_path), "-batch", "-export",
                "-output", str(output_dir),
                "-sheets", sheets,
                str(input_file)
            ]
        else:
            command = [
                str(model_path), "-batch", "-export",
                "-output", str(output_dir),
                str(input_file)
            ]

        # 执行命令
        print(f"执行命令: {' '.join(command)}")
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=300  # 设置超时时间为5分钟
        )

        # 清理临时文件
        if config["CLEANUP_TEMP_FILES"]:
            for name in os.listdir(str(output_dir)):
                file_path = output_dir / name
                if any(name.endswith(ext) for ext in config["TEMP_FILE_EXTENSIONS"]):
                    try:
                        os.remove(file_path)
                        print(f"已删除临时文件: {file_path}")
                    except Exception as e:
                        print(f"无法删除文件 {file_path}: {e}")

        # 检查执行结果
        if result.returncode == 0:
            print("Audiveris处理完成")

            # 查找生成的MXL文件
            mxl_files = list(output_dir.glob(f"{input_file.stem}*.mxl"))
            if mxl_files:
                print(f"找到转换后的MXL文件: {mxl_files[0].name}")
                return mxl_files[0]
            else:
                print("警告: 未找到生成的MXL文件")
                return None
        else:
            print(f"Audiveris执行失败: {result.stderr}")
            return None

    except Exception as e:
        print(f"处理文件时出错: {str(e)}")
        return None


if __name__ == '__main__':
    # 示例：处理当前目录下的c-flat.pdf文件
    result = opt2mxl("c-flat.pdf")
    if result:
        print(f"成功生成文件: {result}")