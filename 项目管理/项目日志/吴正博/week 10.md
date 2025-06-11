## 第十周周报

#### 1. 工作内容

1. 编写dataset.py，用于提取MidiCaps数据集的信息，整合为便于训练的数据文件。

#### 2. 工作问题

1. 相比于文本向量的生成，音乐向量的生成速度更加缓慢（平均每个midi大约4s）。

#### 3. 改进方案

1. 规定batch大小为100，即每个数据文件包含100个midi文件的信息（包含转换失败的midi，若转换失败则不存储在文件中），并编写config.yaml调控数据清洗过程（段编号BATCH_ID, MODE: train/validation, TRIM: True/False）

