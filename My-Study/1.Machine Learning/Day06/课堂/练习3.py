import cv2

image_np = cv2.imread('lian3.png')

# 中值滤波(针对椒盐噪声)
no_noise_img = cv2.medianBlur(
    image_np,  # 要处理的图片
    5  # 核尺寸
)

sigma = 50
# 双边滤波
no_noise_img = cv2.bilateralFilter(
    no_noise_img,  # 要处理的图片
    9,  # 滤波核尺寸
    sigma,  # SigmaColor
    sigma  # SigmaSpace
)

# 灰度化
image_np_gray = cv2.cvtColor(no_noise_img, cv2.COLOR_BGR2GRAY)

# 二值化
thresh = 150  # 阈值
maxval = 255  # 最大值
_, image_np_gray = cv2.threshold(
    image_np_gray,  # 要处理的灰度图
    thresh,  # 阈值
    maxval,  # 最大值
    cv2.THRESH_BINARY  # 二值化方法：阈值法(反阈值法：THRESH_BINARY_INV)
)

# Sobel算子
dst_image = cv2.Laplacian(
    image_np_gray,  # 要处理的灰度图
    -1  # 位深度
)

cv2.imshow('no_noise_img', no_noise_img)
cv2.imshow('dst_image', dst_image)
cv2.waitKey(0)