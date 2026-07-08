# ==========================================
# 导入所需的库和模块
# ==========================================
# 从 sklearn 的数据集模块中导入乳腺癌数据集（一个经典的二分类数据集，包含30个特征）
from sklearn.datasets import load_breast_cancer
# 导入数据划分工具，用于将完整数据集随机打乱并切分为不同的部分（训练、验证、测试）
from sklearn.model_selection import train_test_split
# 导入高斯朴素贝叶斯模型，这是一种基于贝叶斯定理的分类算法，假设特征之间相互独立且服从高斯分布
from sklearn.naive_bayes import GaussianNB
# SelectKBest 是一种特征选择方法，用于保留得分最高的 K 个特征；f_classif 是用于分类任务的评分函数（方差分析 F 值）
from sklearn.feature_selection import SelectKBest, f_classif
# 导入准确率计算工具，用于评估模型预测结果与真实标签的匹配程度
from sklearn.metrics import accuracy_score

# [新增] 导入 Python 最强大的基础绘图库 matplotlib，pyplot 是其最常用的绘图接口，通常简写为 plt
import matplotlib.pyplot as plt

# ==========================================
# 第一阶段：数据加载与严格的三集划分
# ==========================================
# 实例化/加载乳腺癌数据集对象
data = load_breast_cancer()
# 提取特征矩阵（通常用大写 X 表示，因为它是二维数组/矩阵，包含多个样本的多个特征）
X = data.data
# 提取目标标签数组（通常用小写 y 表示，因为它是一维数组/向量，代表良性或恶性）
y = data.target

# 第一次划分：将整体数据集 X 和 y 划分为“临时集”(temp)和“测试集”(test)
# test_size=0.2 表示留出 20% 作为最终测试集，剩余 80% 作为临时集
# random_state=42 设置随机种子，确保每次运行代码时划分的结果完全一致，便于复现和调试
X_temp, X_test, y_temp, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 第二次划分：将刚才的“临时集”进一步划分为“训练集”(train)和“验证集”(val)
# 注意这里的 test_size=0.25：因为临时集占总量的 80%，80% 的 25% 刚好是总体数据的 20%
# 这样划分后，整体数据的比例为：训练集 60%，验证集 20%，测试集 20%。这是一个非常规范的比例。
X_train, X_val, y_train, y_val = train_test_split(X_temp, y_temp, test_size=0.25, random_state=42)

# ==========================================
# 第二阶段：核心优化模块 —— 利用【验证集】寻找最佳特征数量 K
# ==========================================

# 初始化变量，用于记录能带来最高准确率的特征数量 K
best_k = 1
# 初始化变量，用于记录在验证集上达到的最高准确率（初始设为0.0）
best_val_acc = 0.0

# [新增] 准备两个空列表，用来收集画图所需的 X 轴数据 (K值) 和 Y 轴数据 (准确率)
k_values_list = []
val_accuracies_list = []

print("--- 开始寻找最佳特征数量 K ---")

# 开始循环，遍历特征数量 K 从 1 到 30（因为该数据集总共只有30个特征，range 的右边界是开区间所以写31）
for k in range(1, 31):
    # 实例化特征选择器：指定评分函数为 f_classif，并设定当前循环要保留的特征个数为 k
    selector = SelectKBest(score_func=f_classif, k=k)

    # 重点：在训练集上进行 fit（计算特征得分并找出前 k 个）并 transform（应用选择，剔除掉不要的特征）
    X_train_selected = selector.fit_transform(X_train, y_train)
    # 重点：在验证集上只能 transform（直接应用在训练集上找出的那 k 个特征），绝对不能用验证集的标签去 fit，否则会导致数据泄露
    X_val_selected = selector.transform(X_val)

    # 实例化高斯朴素贝叶斯分类器
    gnb = GaussianNB()
    # 使用筛选出 k 个特征后的训练集数据，来训练（拟合）朴素贝叶斯模型
    gnb.fit(X_train_selected, y_train)

    # 使用训练好的模型，对经过同样特征筛选的验证集进行预测
    y_val_pred = gnb.predict(X_val_selected)
    # 将模型在验证集上的预测标签与真实的验证集标签进行对比，计算准确率
    val_acc = accuracy_score(y_val, y_val_pred)

    # [新增] 将当前的 k 和算出的准确率塞进列表中保存，为后续画图准备数据
    k_values_list.append(k)
    val_accuracies_list.append(val_acc)

    # 判断当前 k 值带来的准确率是否打破了之前的最高记录
    if val_acc > best_val_acc:
        # 如果是，则更新最高准确率的记录
        best_val_acc = val_acc
        # 同时记录下这个创纪录的 k 值
        best_k = k

print(f"验证集反馈：保留前 {best_k} 个特征时，模型效果最好！")
print(f"此时验证集的准确率为: {best_val_acc:.4f}")
print("-" * 30)

# ==========================================
# [新增模块] 可视化：绘制 K 值与验证集准确率的关系图
# ==========================================
print("--- 正在生成可视化图表 ---")

# 1. 创建一个画布，设置大小 (宽10英寸，高6英寸)
plt.figure(figsize=(10, 6))

# 2. 绘制折线图：X轴是 K 值，Y轴是准确率。设置点标记为圆圈(o)，线段颜色为蓝色(b)
plt.plot(k_values_list, val_accuracies_list, marker='o', linestyle='-', color='b', label='Validation Accuracy')

# 3. 画一根垂直的红色虚线，明确标出我们找到的那个“最佳 K”的位置，axvline 代表 axis vertical line
plt.axvline(x=best_k, color='red', linestyle='--', label=f'Best K = {best_k}')

# 4. 给图表添加标题和坐标轴标签 (让别人一眼看懂图的意思)
plt.title('Validation Accuracy vs. Number of Selected Features (K)', fontsize=14)
plt.xlabel('Number of Features (K)', fontsize=12)
plt.ylabel('Validation Accuracy', fontsize=12)

# 5. 显示图例 (左上角或右上角的小提示框，解释不同颜色线条的含义)
plt.legend()

# 6. 开启背景网格线，方便在阅读图表时肉眼对齐 X 轴和 Y 轴的具体数值
plt.grid(True)

# 7. 渲染并正式把图表窗口显示出来（程序会在此处暂停，直到关闭图表窗口）
plt.show()

print("-" * 30)

# ==========================================
# 第三阶段：终极评估 —— 在【测试集】上进行期末考试
# ==========================================
# 使用在验证集上确定的最佳 K 值，重新实例化一个最终的特征选择器
final_selector = SelectKBest(score_func=f_classif, k=best_k)

# 使用训练集重新训练特征选择器，并对训练集进行降维转换（注意：这里存在逻辑漏洞，详情见下文）
X_train_final = final_selector.fit_transform(X_train, y_train)
# 对之前一直封存未动的测试集进行相同的特征转换（只转换，不 fit）
X_test_final = final_selector.transform(X_test)

# 实例化最终的高斯朴素贝叶斯模型
final_gnb = GaussianNB()
# 使用降维后的训练集重新训练最终模型
final_gnb.fit(X_train_final, y_train)

# 用训练好的最终模型对测试集进行预测
y_test_pred = final_gnb.predict(X_test_final)
# 计算并得出模型在测试集上的最终准确率（这是评估模型真实泛化能力的最终指标）
test_accuracy = accuracy_score(y_test, y_test_pred)

print(f"最终评估：")
print(f"原数据特征数：{X.shape[1]} -> 优化后特征数：{best_k}")
print(f"测试集最终准确率 (Test Accuracy): {test_accuracy:.4f}")