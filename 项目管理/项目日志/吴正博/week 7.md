## 第七周周报



#### 1. 工作内容

1. 构建自己训练文本生成midi的技术路线；
2. 寻找文本生成midi的开源模型，并调试运行。

#### 2. 工作问题

1. 检索到MozartsTouch多模态midi生成模型，支持文本、图片和视频作为输入（该模型实际上是先把视频采样为图片组，然后把图片转化为文本，最后用文本作为输入），有一个子功能需要调用OpenAI的API，出现网络连接问题；
2. 在HuggingFace上找到了MidiCaps数据集，虽然数据很全面，但过于庞杂，一时难以抉择使用哪一部分用于训练。

#### 3. 改进方案

1. 尝试将WSL2模式从NAT切换为Mirrored，挂载本机代理，但出现502错误。原因是OpenAI近期在维护ChatCompletion，暂时关闭了接口。决定本地部署RedPajama-INCITE-Chat-3B-v1模型代替ChatCompletion；
2. 优先使用成熟的MozartsTouch，若时间充裕，再自己训练。