## 第九周周报

#### 1. 工作内容

1. 评估MozartsTouch的性能，判断其是否满足本项目的需求；
2. 制定文本转midi的机器学习路线。

#### 2. 工作问题

1. MozartsTouch适合创意型生成（如支持多模态），但在专业任务上表现不佳（如对流派和节奏不敏感）；
2. 部分midi文件会导致midi2mv函数转换失败（具体报错为：ValueError: max() arg is an empty sequence）。

#### 3. 改进方案

1. 尝试用trim函数，先剪裁原文件，然后执行转换，发现能解决约90%的情况（平均下来，每100个midi约有88个能被成功转换）；
2. 部分midi文件存在不同的节拍和速度导致量化失败，此时通过强制规定全局节拍和速度的方法解决。