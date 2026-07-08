import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

# AI 续航规划师 —— 电动车里程与能耗建模
# 1. 实验背景
# 电动汽车的 耗电量 (y，单位：kWh) 与 行驶里程 (x，单位：km) 之间存在明显的线性关系。
# 作为工程师，我们需要建立模型 y = wx + b，其中 w 代表“百公里能耗”，b 代表“基础待机功耗”。但目前厂家只能做到基础待机功耗为2kWh。
# 2. 实验数据
# 我们提供了厂家数据https://docs.qq.com/sheet/DTWR4QWF4dmtHZkRj ，其潜在规律为 y = wx + b。
# x 轴表示里程，y 轴表示实际耗电量。
# 3. 核心任务
# 找到最适合的线性关系方程。

# 1、数据集的输入
df = pd.read_excel("ev_range_dataset.xlsx")
# 分离特征（里程）和标签（耗电量）
x_data = df['mileage_km'].values
y_data = df['consumption_kWh'].values

# 2、前向计算
# y = w * x + b
w = 0
w_old = w
b = 2
y_hat = w * x_data + b
learning_rate = 0.00001

# 3、单点误差
e = y_data - y_hat
print(f"单点误差e：{e}")

# 4、均方误差（损失函数）以及图像的绘制
# 计算均方误差
# 平方在里面!!!
e_bar = np.mean((y_data - y_hat) ** 2)
print("e_bar:", e_bar)

# 绘制图像
fig = plt.figure(figsize=(12, 5))
ax1 = fig.add_subplot(1, 2, 1)
ax2 = fig.add_subplot(1, 2, 2)

step = 30

for i in range(step):
    ax1.cla()
    ax2.cla()
    gradient = 2 * w_old * np.mean(x_data ** 2) - 2 * np.mean(x_data * y_data)+ 2 * b * np.mean(x_data)  # w_old所在的点的切线的斜率
    w_new = w_old - learning_rate * gradient

    # 求出w_new处的损失值
    y_hat_new = w_new * x_data + b
    e_bar_new = np.mean((y_hat_new - y_data) ** 2)

    print(f"第 {i + 1} 次：w = {w_new:.10f}，Loss = {e_bar_new:.10f}")

    # 装饰坐标轴
    ax1.set_xlim(0, 550)  # 稍微放大一点 x 轴范围，让点不要贴着边缘
    ax1.set_ylim(0, 100)  # 稍微放大一点 y 轴范围
    ax1.set_xlabel("Km")
    ax1.set_ylabel("kWh")
    # 绘制数据集散点
    ax1.scatter(x_data, y_data, color="b", s=10, alpha=0.5)
    # 计算并绘制拟合线
    y_lower = w_new * 0 + b
    y_upper = w_new * 550 + b
    ax1.plot([0, 550], [y_lower, y_upper], color="r", linewidth=3)

    # 左侧图点到线的竖直线（距离）
    for x, y_true, y_pre in zip(x_data, y_data, y_hat_new):
        ax1.plot([x, x], [y_true, y_pre], color="g", linestyle="--", alpha=0.5)

    # 绘制右侧w和e的曲线
    w_values = np.linspace(0, 0.3, 100)
    e_values = [np.mean((y_data - (w_value * x_data + b)) ** 2) for w_value in w_values]
    ax2.plot(w_values, e_values, color="g", linewidth=3)
    # 在曲线上绘制w的点
    ax2.plot(w_new, e_bar_new, marker="o", color="r", markersize=8)
    ax2.set_xlabel("w axis label")
    ax2.set_ylabel("e axis label")
    plt.pause(0.2)
    w_old = w_new
print("\n最适合的线性关系方程为: y = {:.10f} * x + 2".format(w_new))
plt.show()
