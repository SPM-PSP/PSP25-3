## 第十三周周报

#### 1. 工作内容

1. 初步构建训练代码train.py和推理代码reference.py

#### 2. 工作问题

1. 我们首先使用最简单的全连接层FCN对齐文本向量和音乐向量，发现对于规模为1000的数据集，验证集的平均loss竟然低于训练集。

![FCN](D:\codes\groupies\res\curves\1000\FCN.jpg)

#### 3. 改进方案

1. 仔细检查代码后，发现没有问题，说明是验证集没有涵盖训练集的全部类别。