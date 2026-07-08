# 恢复硬盘包装盒的正面显示，越像真实的越好。
import cv2
import numpy as np

if __name__ == '__main__':
    image_np = cv2.imread('yingpan.png')
    points = [[704, 514], [1093, 368], [817, 1347], [1148, 1157]]
    point1 = np.float32(points)

    image_lines = image_np.copy()
    # 在拷贝的图像上画红框（四条红色直线——端点分别是四个角点）
    cv2.line(
        image_lines,  # 在哪个图像上画线
        points[0],  # 端点1：此处要list
        points[1],  # 端点2：此处要list
        (0, 0, 255),  # 颜色
        2,  # 粗细
        cv2.LINE_AA  # 是否抗锯齿
    )
    cv2.line(
        image_lines,  # 在哪个图像上画线
        points[1],  # 端点1：此处要list
        points[3],  # 端点2：此处要list
        (0, 0, 255),  # 颜色
        2,  # 粗细
        cv2.LINE_AA  # 是否抗锯齿
    )
    cv2.line(
        image_lines,  # 在哪个图像上画线
        points[3],  # 端点1：此处要list
        points[2],  # 端点2：此处要list
        (0, 0, 255),  # 颜色
        2,  # 粗细
        cv2.LINE_AA  # 是否抗锯齿
    )
    cv2.line(
        image_lines,  # 在哪个图像上画线
        points[2],  # 端点1：此处要list
        points[0],  # 端点2：此处要list
        (0, 0, 255),  # 颜色
        2  # 粗细
    )
    width = 200
    height = 280

    points = [[0, 0], [width, 0], [0, height], [width, height]]
    point2 = np.float32(points)
    M = cv2.getPerspectiveTransform(point1, point2)
    correct_image = cv2.warpPerspective(image_np, M, (width, height), cv2.INTER_LANCZOS4, cv2.BORDER_WRAP)
    # 垂直反转图片
    filp_image = cv2.flip(correct_image, 0)
    cv2.imshow('filp_image', filp_image)
    # 开始玩消除光影
    hsv_image = cv2.cvtColor(filp_image, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsv_image)
    lower_bright = np.array([0, 0, 180])  # H, S 忽略，只看 V > 180
    upper_bright = np.array([180, 255, 255])

    # 生成掩膜：图里太亮的地方是白色(255)，正常地方是黑色(0)
    mask = cv2.inRange(hsv_image, lower_bright, upper_bright)

    # 操作 V 通道：
    # 找到 bright_mask 为 255 (太亮) 的位置，把它们的亮度减去
    v[mask == 255] -= 60
    hsv_fixed = cv2.merge((h, s, v))
    image_final = cv2.cvtColor(hsv_fixed, cv2.COLOR_HSV2BGR)
    cv2.imshow('image_final', image_final)
    cv2.imshow('l', image_lines)
    cv2.imwrite('image_final.jpg', image_final)
    cv2.waitKey(0)
