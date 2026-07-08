"""
电动汽车的 耗电量 (y，单位：kWh) 与 行驶里程 (x，单位：km) 之间存在明显的线性关系。
作为工程师，我们需要建立模型 y = wx + b，其中 w 代表“单位里程能耗”，b 代表“基础待机功耗”。
此前我们尝试过手动固定 b 的值进行求解，现在我们将借助强大的深度学习框架 PyTorch，让模型根据数据自动推导并学习出最合适的 w 和 b。
2. 实验数据
我们提供了厂家数据 ev_range_dataset.csv，其潜在规律为 y = wx + b。x 轴表示里程，y 轴表示实际耗电量。
3. 核心任务
使用 PyTorch 的 nn.Linear 模块构建线性回归模型，利用自动求导引擎同时优化参数 w 和 b，找到最适合的线性关系方程。"""
import torch
import numpy as np
import pandas as pd
import torch.nn as nn

# 1、数据集的输入
df = pd.read_excel("ev_range_dataset.xlsx")
# 分离特征（里程）和标签（耗电量）
x_data = df['mileage_km'].values
y_data = df['consumption_kWh'].values

# 将x_data 和 y_data 转换成tensor
x_train = torch.tensor(x_data, dtype=torch.float32).unsqueeze(1)
y_train = torch.tensor(y_data, dtype=torch.float32).unsqueeze(1)


# 2. 定义前向模型

# class LinearModel(nn.Module):
#     # 构造函数：初始化
#     def __init__(self):
#         # 调用父类的构造函数
#         super(LinearModel, self).__init__()
#         # ModuleDict，支持多网络结构（本例只有一个网络层）
#         self.layer1 = nn.Linear(1, 1)
#         # self.layer2 = nn.Linear(1, 1) # 如果是两个网络层是这样的
#
#     def forward(self, x):
#         """
#         前向传播方法
#         :param x: 输入张量
#         :return: 网络层处理后的输出张量
#         """
#         # 多个网络层连接
#         x = self.layer1(x)
#         # x = self.layer2(x)
#         return x


# 创建模型对象
model = nn.Linear(1, 1)  # 输入特征数为1，输出特征数为1

# 3. 定义损失函数和优化器
criterion = nn.MSELoss()  # 均方误差
# 定义随机梯度下降的优化器
optimizer = torch.optim.Adam(
    model.parameters(),  # 模型参数
    lr=0.1  # 学习率
)

# 4. 开始迭代
epochs = 2000  # 迭代次数
for n in range(1, epochs + 1):

    # 4.1 前向传播
    y_pre = model(x_train)  # 参数是n*m的输入矩阵
    # print(y_pre)  # 预测值
    # 计算损失函数
    loss = criterion(y_pre, y_train)
    # 清空之前优化器重存储的梯度参数，以便于本次epoch重新进行反向传播
    optimizer.zero_grad()
    # 4.2 反向传播：计算出所有参数（w和b）的梯度
    loss.backward()
    optimizer.step()
    # 5. 显示频率设置
    if n == 1 or n % 500 == 0:
        # 遍历模型参数
        for name, param in model.named_parameters():
            # 如有，取出当前计算的梯度
            if param.grad is not None:
                print(f"梯度 {name}: {param.grad.item():.8f}")  # .item()用于从只包含一个元素的张量中提取标量值
                # 如有，取出当前计算的w和b
                if param.data is not None:
                    print(f"参数 {name}: {param.data.item():.8f}")
                # 每隔10次显示一次损失函数
            print(f"epoch:{n}, loss:{loss.item():.8f}")

