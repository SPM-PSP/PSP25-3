## 第十二周周报

#### 1. 工作内容

1. 在wsl中整合格式转换功能。

#### 2. 工作问题

1. 缺少MIDI合成器；
2. Audiveris和Fluidsynth须重新配置linux版。

#### 3. 改进方案

关于MIDI合成器：

若出现报错

```
Couldn't open timidity.cfg
```

说明系统缺少MIDI合成器`timidity`及其配置文件。

安装合成器及音色库

```bash
sudo apt update
sudo apt install -y timidity freepats
```

配置默认音色库

```bash
sudo nano /etc/timidity/timidity.cfg
# 添加以下内容，指定freepats音色库路径
dir /usr/share/sounds/freepats/
source freepats.cfg
```

在~/.bashrc中配置Pygame使用Timidity后端

```bash
export SDL_SOUNDFONTS="/usr/share/sounds/sf2/FluidR3_GM.sf2"
export SDL_AUDIODRIVER="pulse"
```

关于plugins配置：

Audiveris和Fluidsynth在Windows上的文件（`Audiveris.bat`, `fluidsynth.exe`）通常不能在wsl中直接运行，因此需要额外配置。

Audiveris直接去github上下载ubuntu发行版，然后运行

```bash
sudo dpkg -i <FILENAME>
```

使用dpkg安装的文件一般会默认安装到/opt中。

Fluidsynth在github上是没有linux发行版的，因为它可以直接通过命令安装

```bash
sudo apt-get install fluidsynth
```

在终端运行可能会出现如下提示

```bash
ALSA lib seq_hw.c:466:(snd_seq_hw_open) open /dev/snd/seq failed: No such file or directory
fluidsynth: error: Error opening ALSA sequencer
Failed to create the MIDI thread; no MIDI input
will be available. You can access the synthesizer
through the console.
Type 'help' for help topics.

fluidsynth: warning: Failed to set thread to high priority
```

但ALSA属于高级音频设置，不影响本项目的midi2wav功能。