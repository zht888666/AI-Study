import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

plt.rcParams['font.sans-serif'] = ['SimHei']  # 设置 Matplotlib 的中文字体，确保图表中的中文能正常显示

# 1. 数据读取
m = pd.read_excel('source.xlsx')  # 从 Excel 文件读取原始成绩数据

# 2. 数据清洗
m['exam'] = m['exam'].fillna(0)
m['attendance'] = m['attendance'].fillna(0)  # 将考试成绩和考勤成绩中的空值（NaN）填充为 0，防止计算出错

# 3. 成绩计算
# 按照 考勤 30% + 考试 70% 的比例计算最终总评成绩
m['Final grade'] = m['attendance'] * 0.3 + m['exam'] * 0.7

# 4. 逻辑判断
# 使用 numpy 的 where 函数判断成绩是否及格（大于等于 60 分为通过，否则为未通过）
m['Pass or not'] = np.where(m['Final grade'] >= 60, "通过", "未通过")

# 5. 保存处理后的完整数据
# 将计算好总分和结论的数据保存到新的 Excel 文件中，不保存行索引
m.to_excel('text.xlsx', index=False)

# 6. 数据可视化 - 直方图
# 绘制学生最终总评成绩的分布直方图
plt.hist(m['Final grade'])
plt.title("学生总评成绩分布")  # 添加标题以增强可读性
plt.show()

# 7. 数据可视化 - 饼图
# 统计“通过”与“未通过”的人数
counts = m['Pass or not'].value_counts()
# 绘制饼图，labels 为分类名称，autopct 用于显示百分比格式
plt.pie(counts, labels=counts.index, autopct='%1.1f%%')
plt.title("学生通过率统计")
plt.show()

# 8. 异常数据处理（补考名单）
# 筛选出所有“未通过”的学生记录
fail_list = m[m['Pass or not'] == '未通过']
# 在控制台输出补考统计信息
print(f"共有 {len(fail_list)} 位同学需要参加补考。")
print(fail_list[['name', 'Final grade']])

# 将需要补考的学生名单导出为独立的 Excel 文件
fail_list.to_excel('makeup_exam_list.xlsx', index=False)
print("补考名单已生成：makeup_exam_list.xlsx")

# 9. 分析不及格原因
# 9. 分析不及格原因
print("\n" + "=" * 50)
print("【不及格原因分析】")
print("=" * 50)


def analyze_fail_reason(row):
    attendance_fail = row['attendance'] < 60
    exam_fail = row['exam'] < 60

    if attendance_fail and exam_fail:
        return "考勤和考试均不及格"
    elif attendance_fail:
        return "仅考勤不及格"
    elif exam_fail:
        return "仅考试不及格"
    else:
        return "平时表现不佳（两项都及格但总评不及格）"


if len(fail_list) > 0:
    # 关键修复：创建 fail_list 的深拷贝，避免 SettingWithCopyWarning
    fail_list_analysis = fail_list.copy()

    # 使用 .loc 方式安全地添加新列
    fail_list_analysis.loc[:, '不及格原因'] = fail_list_analysis.apply(analyze_fail_reason, axis=1)

    reason_counts = fail_list_analysis['不及格原因'].value_counts()
    print(reason_counts)
    print("\n详细情况：")
    print(fail_list_analysis[['name', 'attendance', 'exam', 'Final grade', '不及格原因']])

    plt.figure(figsize=(8, 6))
    plt.pie(reason_counts, labels=reason_counts.index, autopct='%1.1f%%', startangle=90)
    plt.title("不及格原因分布")
    plt.show()
else:
    print("恭喜！本次没有不及格学生。")

# 10. 成绩分段统计
print("\n" + "=" * 50)
print("【成绩分段统计】")
print("=" * 50)

bins = [0, 70, 80, 90, 100]
labels = ['<70分', '70-79分(中等)', '80-89分(良好)', '90-100分(优秀)']

m['成绩分段'] = pd.cut(m['Final grade'], bins=bins, labels=labels, right=False)
segment_counts = m['成绩分段'].value_counts().sort_index()

print("各分数段人数及占比：")
segment_percent = (segment_counts / len(m) * 100).round(2)
for label, count, percent in zip(segment_counts.index, segment_counts.values, segment_percent.values):
    print(f"{label}: {count}人 ({percent}%)")

plt.figure(figsize=(10, 6))
colors = ['#ff6b6b', '#feca57', '#48dbfb', '#1dd1a1']
bars = plt.bar(segment_counts.index, segment_counts.values, color=colors, edgecolor='black')
plt.title("成绩分段分布", fontsize=14)
plt.xlabel("分数段")
plt.ylabel("人数")
plt.xticks(rotation=15)
for bar in bars:
    height = bar.get_height()
    plt.text(bar.get_x() + bar.get_width() / 2., height, f'{int(height)}人', ha='center', va='bottom')
plt.tight_layout()
plt.show()

plt.figure(figsize=(8, 6))
plt.pie(segment_counts, labels=segment_counts.index, autopct='%1.1f%%', colors=colors, startangle=90)
plt.title("成绩分段占比")
plt.show()

# 11. 对比两个学生的成绩
print("\n" + "=" * 50)
print("【学生成绩对比】")
print("=" * 50)

all_names = m['name'].tolist()
print(f"班级学生名单：{all_names}")

try:
    student1_name = input("\n请输入第一个学生姓名：").strip()
    student2_name = input("请输入第二个学生姓名：").strip()

    student1 = m[m['name'] == student1_name]
    student2 = m[m['name'] == student2_name]

    if student1.empty:
        print(f"错误：找不到学生 '{student1_name}'")
    elif student2.empty:
        print(f"错误：找不到学生 '{student2_name}'")
    else:
        s1 = student1.iloc[0]
        s2 = student2.iloc[0]

        print(f"\n【{student1_name} vs {student2_name} 成绩对比】")
        print("-" * 60)

        categories = ['考勤成绩', '考试成绩', '总评成绩', '是否通过']
        s1_values = [s1['attendance'], s1['exam'], s1['Final grade'], s1['Pass or not']]
        s2_values = [s2['attendance'], s2['exam'], s2['Final grade'], s2['Pass or not']]

        print(f"{'项目':<12} {student1_name:<15} {student2_name:<15} {'差距':<10}")
        print("-" * 60)
        for cat, v1, v2 in zip(categories, s1_values, s2_values):
            if cat == '是否通过':
                diff = "-"
            else:
                diff = f"{v1 - v2:+.1f}"
            print(f"{cat:<12} {str(v1):<15} {str(v2):<15} {diff:<10}")

        fig, ax = plt.subplots(figsize=(10, 6))
        x = np.arange(3)
        width = 0.35

        scores1 = [s1['attendance'], s1['exam'], s1['Final grade']]
        scores2 = [s2['attendance'], s2['exam'], s2['Final grade']]

        bars1 = ax.bar(x - width / 2, scores1, width, label=student1_name, color='#3498db')
        bars2 = ax.bar(x + width / 2, scores2, width, label=student2_name, color='#e74c3c')

        ax.set_xlabel('考核项目')
        ax.set_ylabel('分数')
        ax.set_title(f'{student1_name} vs {student2_name} 成绩对比')
        ax.set_xticks(x)
        ax.set_xticklabels(['考勤', '考试', '总评'])
        ax.legend()
        ax.axhline(y=60, color='green', linestyle='--', alpha=0.7, label='及格线(60)')

        for bars in [bars1, bars2]:
            for bar in bars:
                height = bar.get_height()
                ax.annotate(f'{height:.1f}',
                            xy=(bar.get_x() + bar.get_width() / 2, height),
                            xytext=(0, 3), textcoords="offset points",
                            ha='center', va='bottom', fontsize=9)

        plt.tight_layout()
        plt.show()
except Exception as e:
    print(f"对比过程中出现错误：{e}")

# 12. 平均分以下学生分析
print("\n" + "=" * 50)
print("【平均分以下学生分析】")
print("=" * 50)

avg_attendance = m['attendance'].mean()
avg_exam = m['exam'].mean()
avg_final = m['Final grade'].mean()

print(f"班级平均成绩：")
print(f"  考勤平均分：{avg_attendance:.2f}")
print(f"  考试平均分：{avg_exam:.2f}")
print(f"  总评平均分：{avg_final:.2f}")

below_avg = m[m['Final grade'] < avg_final].copy()

print(f"\n总评低于平均分的学生共 {len(below_avg)} 人（班级共{len(m)}人，占比{len(below_avg) / len(m) * 100:.1f}%）")

below_avg_sorted = below_avg.sort_values('Final grade')
print("\n低于平均分学生名单（按成绩从低到高）：")
print(below_avg_sorted[['name', 'attendance', 'exam', 'Final grade', 'Pass or not']])

print("\n【特征分析】")
print(f"低于平均分组平均考勤：{below_avg['attendance'].mean():.2f}（班级平均：{avg_attendance:.2f}）")
print(f"低于平均分组平均考试：{below_avg['exam'].mean():.2f}（班级平均：{avg_exam:.2f}）")

pass_count = (below_avg['Pass or not'] == '通过').sum()
fail_count = (below_avg['Pass or not'] == '未通过').sum()
print(f"\n其中及格：{pass_count}人，不及格：{fail_count}人")

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

categories = ['考勤', '考试', '总评']
class_avgs = [avg_attendance, avg_exam, avg_final]
below_avgs = [below_avg['attendance'].mean(), below_avg['exam'].mean(), below_avg['Final grade'].mean()]

x = np.arange(len(categories))
width = 0.35

bars1 = ax1.bar(x - width / 2, class_avgs, width, label='班级平均', color='#2ecc71')
bars2 = ax1.bar(x + width / 2, below_avgs, width, label='低于平均分组', color='#e74c3c')

ax1.set_ylabel('分数')
ax1.set_title('低于平均分组 vs 班级整体水平')
ax1.set_xticks(x)
ax1.set_xticklabels(categories)
ax1.legend()
ax1.axhline(y=60, color='gray', linestyle='--', alpha=0.5)

for bars in [bars1, bars2]:
    for bar in bars:
        height = bar.get_height()
        ax1.annotate(f'{height:.1f}',
                     xy=(bar.get_x() + bar.get_width() / 2, height),
                     xytext=(0, 3), textcoords="offset points",
                     ha='center', va='bottom', fontsize=9)

ax2.hist(below_avg['Final grade'], bins=10, color='#e74c3c', edgecolor='black', alpha=0.7)
ax2.axvline(x=avg_final, color='green', linestyle='--', linewidth=2, label=f'班级平均({avg_final:.1f})')
ax2.axvline(x=60, color='red', linestyle='--', linewidth=2, label='及格线(60)')
ax2.set_xlabel('总评成绩')
ax2.set_ylabel('人数')
ax2.set_title('低于平均分学生的成绩分布')
ax2.legend()

plt.tight_layout()
plt.show()

below_avg_sorted.to_excel('below_average_list.xlsx', index=False)
print("\n低于平均分学生名单已保存至：below_average_list.xlsx")


