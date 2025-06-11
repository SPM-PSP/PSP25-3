## 第十一周周报

#### 1. 工作内容

1. 在wsl中整合Qt画面显示和声音播放的有关功能。

#### 2. 工作问题

1. wsl无法直接播放声音；
2. libGL出现报错`libGL error: failed to load driver: swrast`;
3. Qt中文显示乱码。

#### 3. 改进方案

关于wsl声卡：参考如下文章在本地windows和远端wsl分别配置pulseaudio

[WSL2连接windows音频设备_wsl 麦克风-CSDN博客](https://blog.csdn.net/2302_78058012/article/details/144395634)

每次重启电脑时请执行如下操作激活wsl声卡：

1. 在wsl终端修改权限

```bash
sudo chmod 0700 /mnt/wslg/runtime-dir
```

2. 管理员权限打开powershell，cd到pulseaudio的bin文件夹中，输入

```bash
.\pulseaudio.exe --exit-idle-time=-1 -vvvv
```

此步骤可能需要尝试多次。

3. 管理员权限打开另一个powershell，cd到pulseaudio的bin文件夹中，测试

```
.\paplay.exe -p --server=tcp:localhost C:\Windows\Media\ding.wav
```

4. 在wsl终端测试

```bash
paplay -p /mnt/c/Windows/Media/ding.wav
```

关于libGL：若出现如下报错：

```
libGL error: failed to load driver: swrast
```

说明系统强制使用了Anaconda中低版本的`libstdc++.so.6`.

请在~/.bashrc中添加

```bash
export LIBGL_DRIVERS_PATH=/usr/lib/x86_64-linux-gnu/dri/
export LD_LIBRARY_PATH="/usr/lib/x86_64-linux-gnu:$LD_LIBRARY_PATH"
export LD_PRELOAD=/usr/lib/x86_64-linux-gnu/libstdc++.so.6
```

并重新应用

```bash
source ~/.bashrc
```

关于Qt中文乱码：安装开源中文字体包

```bash
sudo apt install fonts-wqy-microhei fonts-noto-cjk
```

显式设置字体

```python
# ...
app = QApplication([])
font = QFont("WenQuanYi Micro Hei", 12)
app.setFont(font)
```

