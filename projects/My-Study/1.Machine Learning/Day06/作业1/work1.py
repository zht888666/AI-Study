import cv2

if __name__ == '__main__':
    image_np = cv2.imread('Keyboard.png')
    # 改变尺寸
    resize_image = cv2.resize(image_np, (0, 0), fx=0.5, fy=0.5, interpolation=cv2.INTER_LANCZOS4)
    # 灰度化
    image_np_gray = cv2.cvtColor(resize_image, cv2.COLOR_BGR2GRAY)
    # 膨胀，消纹路
    kernel = cv2.getStructuringElement(
        cv2.MORPH_RECT,
        (3, 3)
    )
    dilate_image = cv2.dilate(image_np_gray, kernel, iterations=2)
    # 高斯
    noise_image = cv2.GaussianBlur(dilate_image, (5, 5), 0)
    edge_image = cv2.Canny(
        noise_image, 50, 150
    )
    # 放大看还可以，保存后不显眼，再膨胀一下
    dilate_image1 = cv2.dilate(edge_image, kernel, iterations=1)
    cv2.imshow('dilate_image1', dilate_image1)
    cv2.imwrite('dilate_image1.jpg', dilate_image1)
    cv2.waitKey(0)
