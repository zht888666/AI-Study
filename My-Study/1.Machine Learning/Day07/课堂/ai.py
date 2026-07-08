import cv2
import numpy as np
import random  # 导入随机数库用于生成颜色

if __name__ == '__main__':
    # 1. 读取和预处理
    image_np = cv2.imread('img_1.png')
    if image_np is None:
        print("Error: Could not read image.")
        exit()

    image_np_gray = cv2.cvtColor(image_np, cv2.COLOR_BGR2GRAY)

    # 2. 边缘检测 (使用你设定的低阈值，能有效检测到所有图形)
    edges = cv2.Canny(image_np_gray, 10, 20)

    # 调试：查看边缘检测结果 (按任意键继续)
    # cv2.imshow('Canny Edges', edges)
    # cv2.waitKey(0)

    # 3. 查找轮廓
    # 【修正点1】这里要用 'edges'，而不是不存在的 'image_np_thresh'
    contours, hierarchy = cv2.findContours(
        edges,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )

    print(f"检测到前景轮廓数量: {len(contours)}")

    # 创建一个副本用于绘制，避免修改原图
    output_image = image_np.copy()

    # 4. 遍历每个轮廓，计算凸包并绘制
    for i, cnt in enumerate(contours):
        # 计算凸包
        hull = cv2.convexHull(cnt)

        # 【修正点2】生成随机颜色 (B, G, R)
        # 为了保证颜色在灰色背景上清晰可见，我们让最小值大一点 (例如 > 50)
        b = random.randint(50, 255)
        g = random.randint(50, 255)
        r = random.randint(50, 255)
        random_color = (b, g, r)

        print(f"轮廓 {i + 1} 的凸包形状: {hull.shape}, 颜色: {random_color}")

        # 绘制凸包
        cv2.polylines(
            output_image,  # 在副本上画
            [hull],  # 凸包点集
            isClosed=True,  # 封闭图形
            color=random_color,  # 使用随机颜色
            thickness=2  # 线宽
        )

    # 5. 显示最终结果
    cv2.imshow('Convex Hulls with Random Colors', output_image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()