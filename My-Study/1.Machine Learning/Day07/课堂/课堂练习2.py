import cv2
import numpy as np

if __name__ == '__main__':
    image_np = cv2.imread('img_2.png')
    image_np_hsv = cv2.cvtColor(image_np, cv2.COLOR_BGR2HSV)
    lower_green = np.array([35, 43, 46])
    upper_green = np.array([85, 255, 255])
    mask = cv2.inRange(image_np_hsv, lower_green, upper_green)
    # cv2.imshow('Gray Image', mask)
    mask_objects = cv2.bitwise_not(mask)

    contours, hierarchy = cv2.findContours(
        mask_objects,  # 二值化图像
        cv2.RETR_TREE,  # 轮廓查找方式
        cv2.CHAIN_APPROX_TC89_L1  # 轮廓的近似办法
    )

    cv2.drawContours(image_np, contours, contourIdx=-1, color=(0, 0, 255), thickness=2)
    cv2.imshow('w', image_np)
    cv2.waitKey(0)
