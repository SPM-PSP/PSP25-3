## 第十五周周报

#### 1. 工作内容

1. 在2000数据集上分别测试FCN、CNN和transformer.

#### 2. 工作问题

三者的训练曲线如下

![FCN](D:\codes\groupies\res\curves\2000\FCN.jpg)

![CNN](D:\codes\groupies\res\curves\2000\CNN.jpg)

![TF](D:\codes\groupies\res\curves\2000\TF.jpg)

#### 3. 改进方案

目前只能认为，FCN在该问题上表现最为优秀。有两种可能性：音乐生成任务并不如想象中那样复杂，或者bert和musicvae承担了该问题的大部分复杂度。