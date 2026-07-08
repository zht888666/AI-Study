import matplotlib.pyplot as plt
from sklearn.datasets import make_blobs
from sklearn.cluster import KMeans

# ==========================================
# 1. 加载数据集

# 返回值解析：
# X: 这是一个二维数组（NumPy array），形状为 (300, 2)。代表300个样本，每个样本有2个特征（可以理解为二维平面上的 x 坐标和 y 坐标）。这是我们要喂给模型的真实数据。
# y_true: 这是一个一维数组，形状为 (300,)。包含了这300个样本各自真实的簇标签（0, 1, 2, 3）。注意：在实际的无监督学习中，我们是拿不到这个 y_true 的，这里生成它仅仅是为了我们在脑海中验证算法效能。
X, y_true = make_blobs(n_samples=300, centers=4, cluster_std=0.60, random_state=0)

# ==========================================
# 2. 构建与训练 K-Means 模型 (Model Instantiation & Training)
# 逻辑：实例化一个模型对象，并设定其超参数（Hyperparameters）。
# n_clusters=4: 算法需要寻找的簇的数量（也就是数学公式中的 k 值）。在此例中，我们设定 k=4。
# n_init=10: K-Means 算法对初始质心的位置非常敏感，容易陷入局部最优解。n_init=10 表示算法会在底层悄悄运行 10 次（每次使用不同的随机初始质心），然后比较这 10 次的结果，最终返回误差平方和（SSE）最小的那一次作为最终结果。
# random_state=0: 再次固定随机种子，确保算法内部初始化质心的过程是可复现的。
kmeans = KMeans(n_clusters=4, n_init=10, random_state=0)

# fit() 方法是 sklearn 的核心 API。
# 逻辑：这一步正式触发底层数学运算。算法开始计算 X 中所有数据点之间的距离，不断迭代更新质心位置，直到收敛（质心不再移动）或达到最大迭代次数。
# 注意：作为无监督学习，fit() 里面只传入特征矩阵 X，绝不传入真实标签 y_true。
kmeans.fit(X)

# ==========================================
# 3. 提取聚类结果 (Extracting Results)
# 逻辑：算法迭代完成后，其学到的知识（内部状态）会保存在模型对象的属性中。sklearn 中，模型拟合后生成的属性通常以带有下划线结尾（如 labels_）。
# labels_: 提取模型为 X 中每一个样本点分配的最终簇标签。这是一个长度为 300 的一维数组，里面的值为 0、1、2 或 3。这是模型的“预测结果”。
y_kmeans = kmeans.labels_

# cluster_centers_: 提取最终收敛后的 4 个质心的坐标。
# 这是一个形状为 (4, 2) 的二维数组，代表 4 个质心各自的 x 和 y 坐标。
centers = kmeans.cluster_centers_

# ==========================================
# 4. 结果可视化展示 (Visualization)
# 逻辑：通过图表直观地检验无监督学习的分群效果。

plt.figure(figsize=(8, 6))

# c=y_kmeans: 极其关键！根据 K-Means '预测出' 的标签来为每个点上色（Color）。不同标签对应不同颜色。
# s=50: 数据点的大小（Size）设为50。
# cmap='viridis': 颜色映射表（Colormap）。'viridis' 是一种对色弱友好的渐变色系。
# alpha=0.7: 透明度，取值 0 到 1。0.7 使得数据点重叠密集的地方颜色会加深，可以体现数据密度。
plt.scatter(X[:, 0], X[:, 1], c=y_kmeans, s=50, cmap='viridis', alpha=0.7, label='Data points')

# 绘制最终确定的质心：
plt.scatter(centers[:, 0], centers[:, 1], c='red', s=200, marker='X', label='Centroids')


# 图表包含标题、轴标签和图例。
plt.title("K-Means Clustering on make_blobs Dataset")  # 图表主标题
plt.xlabel("Feature 1")  # X轴代表的物理意义（此处为通用特征1）
plt.ylabel("Feature 2")  # Y轴代表的物理意义（此处为通用特征2）
plt.legend()  # 激活图例（显示 'Data points' 和 'Centroids'）
# 添加网格线，辅助肉眼预估坐标位置。linestyle='--' 设为虚线，alpha=0.5 降低不透明度避免喧宾夺主。
plt.grid(True, linestyle='--', alpha=0.5)

# 将绘制好的图形渲染并显示在屏幕上
plt.show()
