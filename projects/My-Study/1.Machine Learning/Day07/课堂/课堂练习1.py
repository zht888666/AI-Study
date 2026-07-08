import cv2
import numpy as np

if __name__ == '__main__':
    image_np = cv2.imread('img_1.png')
    image_np_gray = cv2.cvtColor(image_np, cv2.COLOR_BGR2GRAY)
    # _, image_np_thresh = cv2.threshold(image_np_gray, 180, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    edges = cv2.Canny(image_np_gray, 10, 20)
    cv2.imshow('q', edges)
    cv2.waitKey(0)
    contours, hierarchy = cv2.findContours(
        edges,  # 二值化图像
        cv2.RETR_EXTERNAL,  # 轮廓查找方式（略）
        cv2.CHAIN_APPROX_SIMPLE  # 轮廓的近似办法（略）
    )

    for cnt in contours:
        hull = cv2.convexHull(cnt)
        cv2.polylines(
            image_np,  # 在哪个图上画
            [hull],  # 绘制的轮廓列表
            isClosed=True,  # 是否封闭
            color=(0, 0, 255),  # 颜色
            thickness=2  # 线宽
        )
    cv2.imshow('q', edges)
    cv2.waitKey(0)
