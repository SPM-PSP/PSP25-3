## 第五周周报



#### 1. 工作内容

1. 收集预训练模型（magenta钢琴音频转midi、spleeter人声伴奏分离、SOME人声转midi的checkpoint）；
2. 收集静态素材（sf2音频库）；
3. 部署第三方插件（基于java的谱面识别软件Audiveris、midi转音频的fluidsynth）；
4. 从技术文档中获取第三方插件的接口，并尝试用python调用终端运行。

#### 2. 工作问题

1. 命令行无法获取anaconda环境信息；
2. Audiveris容易把指法识别为多连音；
3. SOME转化后的midi存在格式错误，用music21库转化为musicxml后无法直接通过MuseScore 4打开。

#### 3. 改进方案

1. 用python内置的subprocess库创建子进程可以获取anaconda环境信息；
2. 要求用户使用没有指法的乐谱，或者自己实现一个子功能用于去除指法；
3. 用music21间接打开乐谱，MuseScore产生警告，但可以打开。