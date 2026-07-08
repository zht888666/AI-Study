# 卫星扫描了一张遥感图，需要增强显示效果。
import cv2
import numpy as np


# 直方图绘制函数
def draw_hist(image, color):
    """
    绘制直方图
    :param image: 哪个图的直方图图像（灰度化之后的）
    :param color: 直方图柱子什么颜色，BGR元组
    :return: 直方图图像
    """
    hist = cv2.calcHist(
        [image],  # 计算直方图的图像，支持多图像输入，因此一个图像也要写成列表
        [0],  # 要计算的图像灰度值通道需要，灰度图直接传0
        None,  # 掩膜，全图计算不需要
        [256],  # 直方图x轴的精细程度，256表示分为256份
        [0, 255]  # x轴的范围
    )
    print(hist.shape)  # (256, 1) 256表示有256个灰度频数数据
    # 提取关键数据
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(hist)
    # print('min_val:', min_val)  # 0.0，最小的灰度频数
    print('max_val:', max_val)  # 471606.0，最大的灰度频数
    # print('min_loc:', min_loc)  # (0, 255)，最小的灰度频数对应的灰度值
    # print('max_loc:', max_loc)  # (0, 1)，最大的灰度频数对应的灰度值
    # 创建一张纯黑图，画柱子
    hist_img = np.zeros([256, 256, 3], np.uint8)
    # 为了让y轴最高的柱子留一部门空白，最高柱子的高度
    hpt = int(256 * 0.9)
    for h in range(256):  # 从0到255，每个灰度画柱子
        # 柱子高度（整数） = 直方图的最高值hpt * 每个灰度的频数/最高的频数
        intensity = int(hpt * hist[h] / max_val)
        # print(intensity)
        # 画柱子（线）
        cv2.line(
            hist_img,
            (h, 256),  # x轴的起始点
            (h, 256 - intensity),  # 线段从下往上画的终点
            color
        )
    return hist_img


if __name__ == '__main__':
    image_np = cv2.imread('img.png')
    image_gray = cv2.cvtColor(image_np, cv2.COLOR_BGR2GRAY)
    image_hist = draw_hist(image_gray, (0, 255, 0))
    cv2.imshow('image_hist', image_hist)

    clahe = cv2.createCLAHE(clipLimit=3, tileGridSize=(8, 8))
    equ_image_np = clahe.apply(image_gray)

    equ_image_hist = draw_hist(equ_image_np, (255, 255, 255))
    cv2.imshow('equ_image_hist', equ_image_hist)
    cv2.imshow('equ_image_np', equ_image_np)
    cv2.waitKey(0)
