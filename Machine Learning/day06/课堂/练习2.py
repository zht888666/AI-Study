import cv2
import numpy as np

if __name__ == '__main__':
    # 1. 图片输入
    image_np = cv2.imread('shudu.png')

    # 2. 梯度处理方式
    # 创建卷积核（水平边缘→垂直梯度）
    kernel = np.array(
        [[-1, -2, -1],
         [0, 0, 0],
         [1, 2, 1]]
    )
    # # 创建卷积核（垂直边缘→水平梯度）
    # kernel = np.array(
    #     [[-1, 0, 1],
    #      [-2, 0, 2],
    #      [-1, 0, 1]]
    # )
    # 二维滤波
    dst_image = cv2.filter2D(
        image_np,  # 要处理的图像
        -1,  # 位深度
        kernel  # 卷积核
    )

    # 3. 图片输出
    cv2.imshow('dst_image', dst_image)
    cv2.waitKey(0)
