import cv2
import numpy as np
import matplotlib.pyplot as plt

image = np.zeros((700, 700, 3), dtype=np.uint8)
block_size = 100
for i in range(0, 699, block_size):
    for j in range(0, 699, block_size):
        top_left = (j, i)
        bottom_right = (j + block_size - 1, i + block_size - 1)
        if (i // block_size == j // block_size) or (i // block_size + j // block_size == 6):
            print(top_left, bottom_right)
            # TODO 后续再筛除四个角小红色块
            cv2.rectangle(
                image,
                top_left,
                bottom_right,
                (255, 0, 0),
                -1
            )
        cv2.rectangle(
            image,
            top_left,
            bottom_right,
            (255, 255, 255)
        )
image_rgb = cv2.cvtColor(
    image,
    cv2.COLOR_BGR2RGB
)
plt.imshow(image_rgb)
plt.show()

# 拆分通道
b, g, r = cv2.split(image)
print(r)
print(r.shape)

# 准备三个全零图像，用于单独存储三通道数据
blue_channel = np.zeros((700, 700, 3), dtype=np.uint8)
blue_channel[:, :, 0] = b  # 全图蓝色像素替换
# 颜色转换
blue_channel = cv2.cvtColor(
    blue_channel,  # 参数1：要处理的图像
    cv2.COLOR_BGR2RGB  # 参数2：转换逻辑
)

green_channel = np.zeros((700, 700, 3), dtype=np.uint8)
green_channel[:, :, 1] = g  # 全图绿色像素替换、
# 颜色转换
green_channel = cv2.cvtColor(
    green_channel,  # 参数1：要处理的图像
    cv2.COLOR_BGR2RGB  # 参数2：转换逻辑
)

red_channel = np.zeros((700, 700, 3), dtype=np.uint8)
red_channel[:, :, 2] = r  # 全图红色像素替换
# 颜色转换
red_channel = cv2.cvtColor(
    red_channel,  # 参数1：要处理的图像
    cv2.COLOR_BGR2RGB  # 参数2：转换逻辑
)

# 设置一个一行三列的统计图：子图
plt.subplot(131)  # 1行3列的第1张图
plt.imshow(blue_channel)
plt.axis('off')  # 取消坐标轴
plt.title('blue_channel')

plt.subplot(132)  # 1行3列的第2张图
plt.imshow(green_channel)
plt.axis('off')  # 取消坐标轴
plt.title('green_channel')

plt.subplot(133)  # 1行3列的第3张图
plt.imshow(red_channel)
plt.axis('off')  # 取消坐标轴
plt.title('red_channel')

plt.show()


