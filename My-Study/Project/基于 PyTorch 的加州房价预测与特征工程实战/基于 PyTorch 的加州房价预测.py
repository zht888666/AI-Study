# ================= 导入所需的依赖包 =================

# 导入基础数据处理和计算库
import pandas as pd  # 用于数据清洗、处理和分析（构建 DataFrame）
import numpy as np  # 用于高性能的数值计算和数组操作
# 导入 PyTorch 深度学习框架及相关核心模块
import torch
import torch.nn as nn  # 包含构建神经网络层（如线性层）的类
import torch.optim as optim  # 包含各种优化算法（如本代码中使用的 Adam）
# 导入可视化库，用于绘制图表和数据看板
import matplotlib.pyplot as plt
# 导入 PyTorch 的数据加载工具，用于构建可迭代的 Mini-Batch（小批量数据）
from torch.utils.data import TensorDataset, DataLoader
# 导入 sklearn 机器学习工具箱中的相关模块
from sklearn.model_selection import train_test_split  # 用于将数据集划分为训练集和测试集
from sklearn.preprocessing import PolynomialFeatures, StandardScaler  # 用于多项式特征生成和特征标准化
from sklearn.datasets import fetch_california_housing  # 用于下载“加州房价”经典数据集
# 导入模型评估指标：平均绝对误差(MAE)、均方误差(MSE)和 R² 决定系数
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

# ================= 1. 数据准备与特征工程 =================
print("正在加载数据并进行数据清洗...")

# 获取加州房价数据集（包含了房屋的各种特征如房龄、房间数等）
data = fetch_california_housing()
# 将原始的特征数据转换为 Pandas 的 DataFrame 格式，方便后续查看和处理，并指定列名为特征名
df = pd.DataFrame(data.data, columns=data.feature_names)
# 在 DataFrame 中新增一列 'Price' 作为我们要预测的目标变量（标签）。原数据集的单位是 10 万美元。
df['Price'] = data.target

# 【优化 1：清洗异常值】
# 数据集中可能存在被人为截断的最高房价（例如所有大于等于 5.0 的都被标记为 5.0）。
# 为了防止模型学习到这种错误的人工边界，我们将这部分数据剔除。
df_clean = df[df['Price'] < 5.0].copy()
print(f"清洗完成：去除了 {len(df) - len(df_clean)} 条异常数据。")

# 分离特征和标签：X 包含所有用来预测的特征，y_log 包含我们要预测的目标
X = df_clean.drop('Price', axis=1)  # 删掉 Price 列，剩下的就是特征

# 【优化 2：对数变换】
# 房价数据通常呈现“长尾分布”（少数特别贵的房子会拉偏整体分布）。
# 使用 np.log1p (即 log(1 + x)) 对标签取对数，可以让数据分布更接近正态分布，有利于模型稳定收敛。
y_log = np.log1p(df_clean['Price'])

# 将数据随机划分为训练集 (80%) 和测试集 (20%)
# random_state=42 确保每次运行代码时划分的结果一致，方便复现
X_train, X_test, y_train, y_test = train_test_split(X, y_log, test_size=0.2, random_state=42)

# 特征扩充：使用 2次多项式组合现有的特征（例如特征 A 和 B，会生成 A^2, B^2, A*B 等新特征）
# include_bias=False 表示不自动添加全为 1 的偏置列（因为 PyTorch 的 nn.Linear 自带偏置项）
poly = PolynomialFeatures(degree=2, include_bias=False)
X_train_poly = poly.fit_transform(X_train)  # 在训练集上拟合并转换
X_test_poly = poly.transform(X_test)  # 使用在训练集上学到的规则直接转换测试集（防止数据泄露）
feature_names = poly.get_feature_names_out(X.columns)  # 获取展开后的新特征名称

# 特征标准化（Z-Score 标准化）：将特征缩放到均值为 0，标准差为 1 的范围，消除不同特征量纲（单位）带来的影响
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train_poly)  # 拟合训练集并转换
X_test_scaled = scaler.transform(X_test_poly)  # 使用同样的均值和方差转换测试集

# ================= 2. PyTorch 环境与 DataLoader =================
# 自动检测当前环境是否支持 Nvidia GPU 计算。如果有 CUDA，则使用 'cuda' 加速，否则退回使用 'cpu'
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f"当前使用的计算设备: {device}")

# 【进阶优化：显存管理】
# 将处理好的 Numpy 数组转换为 PyTorch 的 Tensor（张量）。
# 此时不急着把所有数据移动到 GPU 上，而是留在 CPU 内存中，这样即使数据量极大也不会撑爆 GPU 显存。
X_train_tensor = torch.tensor(X_train_scaled, dtype=torch.float32)
X_test_tensor = torch.tensor(X_test_scaled, dtype=torch.float32)
# 对标签数据进行变形，view(-1, 1) 表示将其变成 [样本数, 1] 的二维矩阵形状，以匹配模型输出要求
y_train_tensor = torch.tensor(y_train.values, dtype=torch.float32).view(-1, 1)
y_test_tensor = torch.tensor(y_test.values, dtype=torch.float32).view(-1, 1)

# 构建 Dataset 和 DataLoader
batch_size = 128  # 每次同时送入模型训练的样本数量
# 将特征和标签打包成一个张量数据集
train_dataset = TensorDataset(X_train_tensor, y_train_tensor)
# 创建数据加载器，它可以自动按照 batch_size 帮我们分批次获取数据，shuffle=True 表示每个 epoch 都会打乱数据顺序
train_loader = DataLoader(dataset=train_dataset, batch_size=batch_size, shuffle=True)


# ================= 3. 定义模型、损失与优化器 =================
# 定义一个继承自 nn.Module 的线性回归类
class LinearRegressionModel(nn.Module):
    def __init__(self, input_size):
        super(LinearRegressionModel, self).__init__()  # 初始化父类
        # 定义一个全连接线性层，输入特征数为 input_size，输出特征数为 1（即预测的房价）
        self.linear = nn.Linear(input_size, 1)

    def forward(self, x):
        # 前向传播逻辑：数据直接通过线性层
        return self.linear(x)


# 实例化模型。输入大小为训练集特征的列数。
# .to(device) 会将模型内部的权重参数推送到对应的硬件（CPU或GPU）上
model = LinearRegressionModel(X_train_tensor.shape[1]).to(device)
# 定义损失函数：均方误差（Mean Squared Error），用于衡量预测值与真实值之间的差距
criterion = nn.MSELoss()
# 定义优化器：使用 Adam 优化器来更新模型参数，学习率设定为 0.001
optimizer = optim.Adam(model.parameters(), lr=0.001)

# ================= 4. 模型训练 (融合验证集与动态显存) =================
num_epochs = 200  # 完整遍历训练数据集的次数
l1_lambda = 0.002  # L1 正则化的强度系数。L1正则化有助于让不重要的特征权重变为 0（实现特征选择）
# 用于记录每个 Epoch 的平均训练集损失和验证集损失，方便后续画图
train_losses = []
val_losses = []

print(f"开始训练模型 (共 {num_epochs} Epochs)...")
for epoch in range(num_epochs):

    # --- 训练阶段 ---
    model.train()  # 明确告知 PyTorch 模型现在处于训练模式（这会启用梯度计算等相关机制）
    epoch_loss = 0.0  # 累加当前 epoch 中所有 batch 的损失

    # 从 DataLoader 中遍历获取每个批次的数据
    for batch_X, batch_y in train_loader:
        # 【进阶优化：显存管理】在循环内部，只将当前这一批(batch)需要用到的数据搬运到 GPU 上
        batch_X, batch_y = batch_X.to(device), batch_y.to(device)

        # 1. 梯度清零：防止上一批次的梯度累积干扰当前批次
        optimizer.zero_grad()
        # 2. 前向传播：将数据输入模型，获得预测输出
        output = model(batch_X)
        # 3. 计算基础损失：预测值与真实值之间的均方误差
        mse_loss = criterion(output, batch_y)
        # 【进阶优化：算法逻辑】计算 L1 正则化项。
        # 注意：通常正则化只惩罚权重矩阵 (weight)，不惩罚偏置项 (bias)。
        l1_norm = torch.abs(model.linear.weight).sum()
        # 4. 计算总损失 = 基础误差 + 正则化惩罚项
        loss = mse_loss + l1_lambda * l1_norm
        # 5. 反向传播：根据损失计算每个参数的梯度
        loss.backward()
        # 6. 参数更新：优化器根据梯度调整模型内部的权重
        optimizer.step()
        # 累加损失。loss.item() 取出具体的数值，乘以 batch 大小是为了后面准确计算整个 epoch 的平均损失
        epoch_loss += loss.item() * batch_X.size(0)

    # 计算并保存当前 epoch 在训练集上的平均损失
    avg_epoch_loss = epoch_loss / len(train_dataset)
    train_losses.append(avg_epoch_loss)

    # --- 验证阶段 ---
    model.eval()  # 明确告知 PyTorch 模型现在处于评估模式（会关闭 Dropout/BatchNorm的训练行为，虽然这里没有用到）
    with torch.no_grad():  # 在此区块内不计算也不存储梯度，节省内存，加速计算
        # 将整个测试集作为验证集搬运到 GPU 进行前向推理
        val_X, val_y = X_test_tensor.to(device), y_test_tensor.to(device)
        val_output = model(val_X)

        # 计算验证集的纯 MSE 损失 (验证集的目的是客观评估模型效果，所以不加 L1 惩罚项)
        val_loss = criterion(val_output, val_y)
        val_losses.append(val_loss.item())

    # 每 20 个 Epoch 打印一次训练进度和当前损失日志
    if (epoch + 1) % 20 == 0:
        print(f'Epoch [{epoch + 1}/{num_epochs}], Train Loss: {avg_epoch_loss:.4f}, Val Loss: {val_loss.item():.4f}')

# ================= 5. 模型评估与参数提取 =================
model.eval()  # 确保模型在评估模式
with torch.no_grad():  # 不计算梯度
    val_X = X_test_tensor.to(device)
    # 对测试集进行最终预测，得到的是对数变换后的价格
    predictions_log = model(val_X)

    # 【对数变换还原】
    # 使用 np.expm1 (即 exp(x) - 1) 将预测的对数价格转回真实尺度的房价
    # .cpu().numpy() 将 GPU 上的 Tensor 移回 CPU 并转为 Numpy 数组，.flatten() 将其变为一维数组
    predictions_real = np.expm1(predictions_log.cpu().numpy()).flatten()
    # 真实测试标签本身就在 CPU 上，直接还原尺度
    y_test_real = np.expm1(y_test_tensor.numpy()).flatten()

# 【进阶优化：引入回归指标】计算各种评估指标
# MAE: 平均绝对误差，预测值与真实值差值的绝对值的平均数（最直观的误差表现）
mae = mean_absolute_error(y_test_real, predictions_real)
# RMSE: 均方根误差，MSE的平方根，惩罚大的误差
rmse = np.sqrt(mean_squared_error(y_test_real, predictions_real))
# R²: 决定系数，反映模型对数据方差的解释程度，越接近 1 说明模型拟合越好
r2 = r2_score(y_test_real, predictions_real)

# 提取模型学到的特征权重
# .squeeze() 去除多余的维度，.tolist() 转为普通的 Python 列表
weights = model.linear.weight.squeeze().cpu().tolist()
# 将特征名称和其对应的权重打包在一起
feature_weights = list(zip(feature_names, weights))
# 统计因为 L1 正则化而变成 0（或者非常接近0，小于 1e-3）的权重数量，即被剔除的特征数量
zeroed_features = sum(1 for w in weights if abs(w) < 1e-3)

# 打印最终的评估报告
print("\n" + "=" * 50)
print("          训练结果与参数报告")
print("=" * 50)
print(f"被 L1 正则化自动剔除的特征数: {zeroed_features} / {len(weights)}")
# 因为数据集的单位是 10 万美元，这里乘以 100,000 将误差换算成了具体的美元金额，方便理解
print(f"平均绝对误差 (MAE): ${mae * 100000:,.2f}")
print(f"均方根误差 (RMSE): ${rmse * 100000:,.2f}")
print(f"R² 决定系数 (越接近1越好): {r2:.4f}")
print("=" * 50)

# 根据权重的绝对值对特征进行降序排序，找出对房价影响最大的特征
feature_weights.sort(key=lambda x: abs(x[1]), reverse=True)
top_10_features = [x[0] for x in feature_weights[:10]]  # 取出前 10 名特征的名字
top_10_weights = [x[1] for x in feature_weights[:10]]  # 取出前 10 名特征的权重值

# ================= 6. 进阶可视化数据看板 =================
# 计算残差（真实值与预测值的差）
residuals = y_test_real - predictions_real

# 设置画板大小
plt.figure(figsize=(18, 10))
# 设置整个画板的大标题
plt.suptitle('Optimized Linear Regression Model Evaluation', fontsize=16, fontweight='bold')

# --- 图 1：学习曲线 (观察模型学习状态) ---
plt.subplot(2, 3, 1)  # 2行3列的第1张子图
plt.plot(train_losses, color='orange', label='Train Loss')  # 绘制训练损失
plt.plot(val_losses, color='blue', label='Validation Loss')  # 绘制验证损失
plt.xlabel('Epochs')
plt.ylabel('Loss')
plt.title('1. Learning Curves (Train vs Val)')
plt.legend()
plt.grid(True, alpha=0.3)

# --- 图 2：真实值 vs 预测值散点图 (评估整体拟合情况) ---
plt.subplot(2, 3, 2)
plt.scatter(y_test_real, predictions_real, color='blue', alpha=0.4, s=15)
# 绘制一条红色的对角虚线，点越靠近这条线说明预测越准确
plt.plot([y_test_real.min(), y_test_real.max()], [y_test_real.min(), y_test_real.max()], 'r--', lw=2)
plt.xlabel('Actual Prices (Real Scale)')
plt.ylabel('Predicted Prices (Real Scale)')
plt.title('2. Actual vs Predicted')
plt.grid(True, alpha=0.3)

# --- 图 3：残差散点图 (检查误差是否存在特定模式) ---
plt.subplot(2, 3, 3)
plt.scatter(predictions_real, residuals, color='purple', alpha=0.4, s=15)
# 绘制 y=0 的红线，理想情况下，残差应该随机散布在这条线上下方
plt.axhline(y=0, color='r', linestyle='--', lw=2)
plt.xlabel('Predicted Prices')
plt.ylabel('Residuals')
plt.title('3. Residual Plot')
plt.grid(True, alpha=0.3)

# --- 图 4：误差分布直方图 (检查误差是否符合正态分布) ---
plt.subplot(2, 3, 4)
plt.hist(residuals, bins=50, color='teal', edgecolor='black', alpha=0.7)
plt.xlabel('Residual Value')
plt.ylabel('Frequency')
plt.title('4. Error Distribution (Histogram)')
plt.grid(True, alpha=0.3)

# --- 图 5：Top 10 特征重要性柱状图 ---
plt.subplot(2, 3, 5)
# [::-1] 是为了将最大的排在最上面（条形图是从下往上画的）
bars = plt.barh(top_10_features[::-1], top_10_weights[::-1], color='coral')
plt.xlabel('Weight (Coefficient)')
plt.title('5. Top 10 Feature Importance')
plt.grid(True, axis='x', alpha=0.3)

# --- 图 6：局部数据对比折线图 (直观对比部分样本) ---
plt.subplot(2, 3, 6)
sample_size = 80  # 仅取前 80 个样本进行展示，避免折线过于密集
plt.plot(y_test_real[:sample_size], label='Actual', marker='o', markersize=4, linestyle='-', alpha=0.8)
plt.plot(predictions_real[:sample_size], label='Predicted', marker='x', markersize=4, linestyle='--', alpha=0.8)
plt.xlabel('Sample Index (First 80)')
plt.ylabel('Price (Real Scale)')
plt.title('6. Actual vs Predicted (Subset)')
plt.legend()
plt.grid(True, alpha=0.3)

# 自动调整子图间的间距，防止重叠
plt.tight_layout(rect=[0, 0.03, 1, 0.95])
# 渲染并显示出图像
plt.show()

# ================= 7. 保存模型参数 =================
print("\n正在保存模型参数...")

# 定义保存文件的路径和名称，通常使用 .pth 或 .pt 作为后缀名
model_save_path = 'california_housing_optimized_model.pth'

# 获取模型的状态字典（包含所有学习到的 weight 和 bias）
# 将其保存到指定的路径
torch.save(model.state_dict(), model_save_path)

print(f"模型参数已成功保存至当前目录下的: {model_save_path}")
