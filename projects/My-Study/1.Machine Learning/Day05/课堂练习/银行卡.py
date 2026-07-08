import cv2
import numpy as np

if __name__ == '__main__':
    img1 = cv2.imread('img_1.png')
    point = [[110, 60],  # 左上 (Point 0)
             [330, 88],  # 右上 (Point 1)
             [72, 185],  # 左下 (Point 2)
             [320, 220]]  # 右下 (Point 3)
    point1 = np.float32(point)

    image1 = img1.copy()
    cv2.line(image1, point[0], point[1], (0, 0, 255), 2, cv2.LINE_AA)
    cv2.line(image1, point[1], point[3], (0, 0, 255), 2, cv2.LINE_AA)
    cv2.line(image1, point[3], point[2], (0, 0, 255), 2, cv2.LINE_AA)
    cv2.line(image1, point[2], point[0], (0, 0, 255), 2, cv2.LINE_AA)
    width = 850
    height = 540

    point = [[0, 0], [width, 0], [0, height], [width, height]]
    point2 = np.float32(point)

    M = cv2.getPerspectiveTransform(point1, point2)
    img2 = cv2.warpAffine(img1, M, (width, height),cv2.I)
