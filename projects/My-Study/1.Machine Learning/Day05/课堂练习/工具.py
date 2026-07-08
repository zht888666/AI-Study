import cv2
import numpy as np

# 全局变量记录旋转角度和缩放
angle = 0
scale = 0.6  # 稍微缩小一点，防止旋转时边角被切掉


def nothing(x):
    pass


if __name__ == '__main__':
    # 1. 读取图片 (记得换成你上传的文件名 image_72f325.jpg)
    image_np = cv2.imread('img.png')

    if image_np is None:
        print("图片未找到，请检查文件名")
        exit()

    # 获取原图尺寸
    h, w = image_np.shape[:2]
    # 计算图片中心点 (Center)
    center = (w // 2, h // 2)

    cv2.namedWindow('Rotate & Cut')
    # 创建旋转角度滑动条 (0到360度)
    cv2.createTrackbar('Angle', 'Rotate & Cut', 0, 360, nothing)

    while True:
        # 1. 获取滑动条的角度
        angle = cv2.getTrackbarPos('Angle', 'Rotate & Cut')

        # 2. 计算旋转矩阵 (钉住中心 center 旋转)
        # 参数：旋转中心，旋转角度，缩放比例
        M = cv2.getRotationMatrix2D(center, angle, scale)

        # 3. 执行旋转
        # borderMode=cv2.BORDER_CONSTANT 让背景变黑，方便看清边缘
        rotated_img = cv2.warpAffine(image_np, M, (w, h), borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0))

        # 4. 显示
        cv2.imshow('Rotate & Cut', rotated_img)

        # 按 's' 键保存当前结果并退出
        if cv2.waitKey(1) & 0xFF == ord('s'):
            print(f"最终选定角度: {angle}")
            # 保存一下旋转后的图，方便你下一步去测量坐标
            cv2.imwrite('rotated_tissue.jpg', rotated_img)
            break

    cv2.destroyAllWindows()