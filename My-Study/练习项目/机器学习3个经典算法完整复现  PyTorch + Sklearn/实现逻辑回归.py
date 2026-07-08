# 第一步：导入必要的库
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import TensorDataset, DataLoader
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import f1_score
import matplotlib.pyplot as plt

# 第二步：数据准备与预处理
data = load_breast_cancer()
# 加载乳腺癌数据集，返回一个类似字典的对象，包含特征数据 data.data 和标签 data.target
# 数据集包含569个样本，30个特征，目标是预测肿瘤是良性(0)还是恶性(1)

X_scaled = StandardScaler().fit_transform(data.data)
# 创建 StandardScaler 对象并立即调用 fit_transform 方法：
# fit(): 计算训练数据的均值和标准差
# transform(): 使用计算出的统计量对数据进行标准化：(x - mean) / std
# 结果存储在 X_scaled 中，所有特征现在都具有零均值和单位方差

y = data.target
# --- 数据集划分：首先分离出测试集（20%），剩下的作为临时训练集 ---
X_temp, X_test, y_temp, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)
# 使用 train_test_split 将数据划分为临时集和测试集：

# --- 将临时训练集进一步划分为训练集和验证集 ---
X_train, X_val, y_train, y_val = train_test_split(X_temp, y_temp, test_size=0.25, random_state=42)
# 将 X_temp 和 y_temp（占总数据80%）再次划分：
# test_size=0.25: 验证集占临时集的25%，即总数据的20%（约114个样本）
# 因此最终划分比例为：训练集60%，验证集20%，测试集20%

X_train_tensor = torch.tensor(X_train, dtype=torch.float32)
# 将训练集特征从 NumPy 数组转换为 PyTorch 张量：
y_train_tensor = torch.tensor(y_train, dtype=torch.float32).view(-1, 1)

X_val_tensor = torch.tensor(X_val, dtype=torch.float32)
y_val_tensor = torch.tensor(y_val, dtype=torch.float32).view(-1, 1)
X_test_tensor = torch.tensor(X_test, dtype=torch.float32)
y_test_tensor = torch.tensor(y_test, dtype=torch.float32).view(-1, 1)


# --- 创建数据加载器，用于批量训练 ---
train_loader = DataLoader(dataset=TensorDataset(X_train_tensor, y_train_tensor), batch_size=32, shuffle=True)

# 创建训练数据加载器：
# TensorDataset(X_train_tensor, y_train_tensor): 将特征和标签配对包装成数据集
# batch_size=32: 每批加载32个样本，这是常见的批量大小，平衡了内存使用和梯度估计稳定性
# shuffle=True: 每个 epoch 开始时打乱数据顺序，防止模型学习到数据的顺序模式，提高泛化能力


# ==========================================
# 第三步：定义逻辑回归模型

class LogisticRegressionModel(nn.Module):
    # 定义一个名为 LogisticRegressionModel 的类，继承自 nn.Module

    def __init__(self, input_features):
        # 构造函数，在创建模型实例时调用
        # input_features: 输入特征的维度（这里是30，对应乳腺癌数据集的30个特征）
        super(LogisticRegressionModel, self).__init__()
        # 调用父类 nn.Module 的构造函数，这是必须的初始化步骤
        # 它会设置内部的机制，用于跟踪模型的参数和子模块

        self.linear = nn.Linear(input_features, 1)
        # 定义一个线性层（全连接层）：
        # input_features: 输入维度（30）
        # 1: 输出维度（1），因为是二分类问题，只需要一个输出值
        # 该层包含权重矩阵 W（形状 1×30）和偏置向量 b（形状 1×1），会自动初始化

    def forward(self, x):
        # 定义前向传播函数，这是模型的核心计算逻辑
        # x: 输入张量，形状为 (batch_size, input_features)

        return torch.sigmoid(self.linear(x))
        # 计算流程：
        # 1. self.linear(x): 执行线性变换 z = x·W^T + b，输出形状 (batch_size, 1)
        # 2. torch.sigmoid(): 应用 Sigmoid 激活函数，将输出压缩到 (0, 1) 区间
        #    Sigmoid 公式：σ(z) = 1 / (1 + e^(-z))
        # 最终输出表示样本属于正类（恶性）的概率


# --- 实例化模型、定义损失函数和优化器 ---

model = LogisticRegressionModel(X_train.shape[1])
# 创建模型实例：
# X_train.shape[1]: 获取训练集特征数量（30），作为输入维度传递给模型构造函数
# 此时模型已经创建，包含随机初始化的权重和偏置

criterion = nn.BCELoss()
# 定义损失函数为二元交叉熵损失（Binary Cross Entropy Loss）：
# 公式：BCE = -[y·log(p) + (1-y)·log(1-p)]
# 其中 y 是真实标签，p 是模型预测的概率
# 这个损失函数专门用于二分类问题，衡量预测概率与真实标签的差异

optimizer = optim.Adam(model.parameters(), lr=0.01, weight_decay=0.01)
# 定义优化器为 Adam（Adaptive Moment Estimation）：
# model.parameters(): 传入模型中所有需要训练的参数（权重 W 和偏置 b）
# lr=0.01: 学习率（learning rate），控制每次参数更新的步长，0.01是相对较大的学习率
# weight_decay=0.01: L2 正则化系数（权重衰减），防止过拟合，会在损失中加入 λ·||W||² 项
# Adam 结合了动量和自适应学习率的优点，是常用的优化算法


# ==========================================
# 第四步：模型训练循环（包含动态可视化）

num_epochs = 200
# 设置训练的总轮数（epoch）
# 200 轮足够让模型收敛，可以配合早停机制可以防止过拟合

train_loss_history = []
val_loss_history = []
# 创建空列表，用于存储每一轮验证集的损失，用于检测过拟合


print("开始训练模型并生成动态图表...")
# 打印训练开始提示信息，让用户知道程序正在执行


# --- 动态可视化准备工作 ---

plt.ion()
fig = plt.figure(figsize=(8, 6))


# --- 主训练循环 ---

for epoch in range(num_epochs):
    # 外层循环，遍历每一个训练轮次，epoch 从 0 到 299

    # --- 训练阶段：前向传播、计算损失、反向传播、参数更新 ---

    model.train()
    # 将模型设置为训练模式：
    # 这会启用 Dropout（如果有）和 BatchNorm（如果有）的训练行为
    # 对于当前这个简单模型，这主要是良好的编程习惯，确保行为一致

    epoch_loss = 0.0
    # 初始化当前 epoch 的累计损失为 0，用于计算该轮的平均损失

    for batch_X, batch_y in train_loader:
        # 内层循环，遍历训练数据加载器，每次取出一个批次的数据
        # batch_X: 当前批次的特征，形状 (32, 30) 或最后一批可能不足32
        # batch_y: 当前批次的标签，形状 (32, 1) 或最后一批可能不足32

        outputs = model(batch_X)
        # 前向传播：将批次数据输入模型，计算预测概率
        # outputs 形状为 (batch_size, 1)，值域 (0, 1)

        loss = criterion(outputs, batch_y)
        # 计算当前批次的二元交叉熵损失：
        # 比较模型预测 outputs 和真实标签 batch_y 的差异

        optimizer.zero_grad()
        # 清空（归零）优化器中存储的梯度：
        # PyTorch 默认会累积梯度，所以每个批次开始前必须清零
        # 否则梯度会累加，导致训练错误

        loss.backward()
        # 反向传播：计算损失函数对模型所有参数的梯度
        # PyTorch 的 autograd 系统自动构建计算图并应用链式法则
        # 计算完成后，model.parameters() 中的每个参数都会有 .grad 属性

        optimizer.step()
        # 执行参数更新：使用计算出的梯度和 Adam 算法更新权重和偏置
        # 更新公式大致为：param = param - lr * gradient (Adam 会有更复杂的自适应调整)

        epoch_loss += loss.item() * batch_X.size(0)
        # 累加当前批次的损失：
        # loss.item(): 将张量转换为 Python 标量数值
        # batch_X.size(0): 获取当前批次的实际样本数（处理最后一个不完整的批次）
        # 乘以样本数是为了后续计算加权平均损失

    avg_epoch_loss = epoch_loss / len(train_loader.dataset)
    # 计算当前 epoch 的平均训练损失：
    # len(train_loader.dataset): 获取训练集总样本数（341）
    # 用累计损失除以总样本数，得到每个样本的平均损失

    train_loss_history.append(avg_epoch_loss)
    # 将当前 epoch 的平均训练损失添加到历史记录列表中

    # --- 验证阶段：评估模型在验证集上的表现（不更新参数）---

    model.eval()
    # 将模型设置为评估模式：
    # 这会禁用 Dropout 和 BatchNorm 的随机行为
    # 对于当前模型，这确保评估时行为一致

    with torch.no_grad():
        # 上下文管理器，临时禁用梯度计算：
        # 验证阶段不需要计算梯度，可以节省内存和加速计算
        # 在这个块内的操作不会构建计算图

        val_outputs = model(X_val_tensor)
        # 前向传播：将验证集所有数据输入模型，计算预测概率

        val_loss = criterion(val_outputs, y_val_tensor)
        # 计算验证集的二元交叉熵损失

        val_loss_history.append(val_loss.item())
        # 将验证损失转换为标量并添加到历史记录

        # --- 控制台输出进度（每10轮打印一次）---

        if (epoch + 1) % 10 == 0:
            # 检查是否是第10、20、30...轮（epoch+1 因为 epoch 从0开始）

            val_predicted = val_outputs.round()
            # 将验证集的预测概率四舍五入为 0 或 1，得到离散类别预测
            # 概率 >= 0.5 预测为 1（恶性），< 0.5 预测为 0（良性）

            val_accuracy = val_predicted.eq(y_val_tensor).sum().item() / y_val_tensor.size(0)
            # 计算验证集准确率：
            # .eq(): 比较预测值和真实值是否相等，返回布尔张量
            # .sum(): 统计相等（True）的数量
            # .item(): 转换为 Python 整数
            # / y_val_tensor.size(0): 除以验证集样本总数，得到准确率比例

            print(f'Epoch [{epoch + 1}/{num_epochs}], 训练损失: {avg_epoch_loss:.4f}, 验证损失: {val_loss.item():.4f}')
            # 打印当前训练进度，显示：
            # - 当前轮次 / 总轮次
            # - 训练损失（保留4位小数）
            # - 验证损失（保留4位小数）

    # --- 动态可视化：实时更新图表 ---

    plt.clf()
    # 清除当前图形（Clear Figure）上的所有内容：
    # 这是为了移除旧的曲线，准备绘制新的曲线
    # 不清除的话，新曲线会叠加在旧曲线上造成混乱

    plt.plot(train_loss_history, label='Train Loss', color='blue')
    # 绘制训练损失曲线：
    # train_loss_history: x轴隐式为 epoch 索引（0, 1, 2...），y轴为损失值
    # label: 图例标签
    # color='blue': 蓝色线条

    plt.plot(val_loss_history, label='Validation Loss', color='red')
    # 绘制验证损失曲线，使用红色线条

    plt.title(f'Dynamic Learning Curve (Epoch {epoch + 1}/{num_epochs})')
    # 设置图表标题，动态显示当前轮次，让用户知道训练进度

    plt.xlabel('Epochs')
    # 设置 x 轴标签为 "Epochs"（轮次）

    plt.ylabel('Binary Cross Entropy Loss')
    # 设置 y 轴标签为 "Binary Cross Entropy Loss"（二元交叉熵损失）

    plt.legend(loc='upper right')
    # 显示图例，位置固定在右上角
    # loc='upper right' 确保图例不会随着曲线变化而跳动

    plt.grid(True, linestyle='--', alpha=0.6)
    # 添加网格线：
    # True: 启用网格
    # linestyle='--': 虚线样式
    # alpha=0.6: 透明度60%，使网格不那么突兀

    plt.pause(0.01)
    # 暂停 0.01 秒：
    # 这是动态显示的关键！暂停让 GUI 事件循环处理绘图更新
    # 如果没有暂停，图表不会实时刷新
    # 0.01 秒足够短，不会明显拖慢训练，又足够长让图形界面更新

# --- 训练结束后的收尾工作 ---

plt.ioff()
# 关闭 Matplotlib 的交互模式（Interactive Off）
# 恢复为标准模式，此时 plt.show() 会阻塞程序直到关闭窗口


# ==========================================
# 第五步：测试集评估与 F1 分数计算
# ==========================================

print("\n开始在测试集上评估模型...")
# 打印空行和测试阶段提示信息

model.eval()
# 将模型设置为评估模式，确保测试时行为一致

with torch.no_grad():
    # 禁用梯度计算，节省内存和计算资源

    test_predicted = model(X_test_tensor).round().numpy()
    # 测试阶段的前向传播和预测：
    # model(X_test_tensor): 输入测试集，得到预测概率
    # .round(): 四舍五入为 0 或 1
    # .numpy(): 将 PyTorch 张量转换为 NumPy 数组，供 sklearn 使用

    f1 = f1_score(y_test_tensor.numpy(), test_predicted)
    # 计算 F1 分数：
    # y_test_tensor.numpy(): 将真实标签转换为 NumPy 数组
    # test_predicted: 预测标签
    # F1 = 2 * (precision * recall) / (precision + recall)
    # F1 分数综合考虑了精确率和召回率，是二分类问题的重要指标

    print(f'测试集 F1 分数 (F1 Score): {f1:.4f}')
    # 打印 F1 分数，保留4位小数

print("训练完成！请关闭图表窗口以结束程序。")
# 提示用户训练已完成，需要手动关闭图表窗口

plt.show()
# 显示最终的静态图表窗口：
# 由于之前关闭了交互模式，这会阻塞程序直到用户关闭窗口
# 这确保用户有机会查看最终的损失曲线
