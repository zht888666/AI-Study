# 把下面的文件通过透视变换恢复扫描样式，尽量优化显示：白的更白、黑的更黑、噪声更少、红色原样。
import cv2
import numpy as np

if __name__ == '__main__':
    image_np = cv2.imread('wenjian.png')
    points = [[75, 47], [411, 132], [63, 659], [491, 592]]
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

    width = 420
    height = 600
    points = [[0, 0], [width, 0], [0, height], [width, height]]
    point2 = np.float32(points)
    M = cv2.getPerspectiveTransform(point1, point2)
    correct_image = cv2.warpPerspective(image_np, M, (width, height), cv2.INTER_LANCZOS4, cv2.BORDER_WRAP)
    image_np_gray = cv2.cvtColor(correct_image, cv2.COLOR_BGR2GRAY)
    thresh = 140
    maxval = 255

    _, image_np_gray = cv2.threshold(image_np_gray, thresh, maxval, cv2.THRESH_BINARY)

    image_np_hsv = cv2.cvtColor(correct_image, cv2.COLOR_BGR2HSV)
    red_low = np.array([0, 43, 46])  # 下限
    red_high = np.array([10, 255, 255])  # 上限
    # 制作掩膜，返回掩膜
    mask1 = cv2.inRange(
        image_np_hsv,  # 在哪张图制作掩膜
        red_low,  # 下限
        red_high  # 上限
    )
    red_low = np.array([156, 43, 46])  # 下限
    red_high = np.array([180, 255, 255])  # 上限
    # 制作掩膜，返回掩膜
    mask2 = cv2.inRange(
        image_np_hsv,  # 在哪张图制作掩膜
        red_low,  # 下限
        red_high  # 上限
    )  # 掩膜二合一：或操作
    mask = cv2.bitwise_or(mask1, mask2)

    color_image_np = cv2.bitwise_and(correct_image, correct_image, mask=mask)
    # color_image_np2 = cv2.cvtColor(image_np_gray, cv2.COLOR_GRAY2BGR)
    # color_image_np3 = cv2.add(image_np_gray, color_image_np2)
    # 像素替换：在最终结果图上，凡是 mask 是白色的位置，都把correct_image的像素填进去
    final_image = cv2.cvtColor(image_np_gray, cv2.COLOR_GRAY2BGR)
    final_image[mask > 0] = color_image_np[mask > 0]
cv2.imshow('final_image', final_image)
cv2.imwrite('final_image', final_image)
# cv2.imshow('image_lines', image_lines)
cv2.imshow('mask', mask)
# cv2.imshow('1', correct_image)
cv2.waitKey(0)
