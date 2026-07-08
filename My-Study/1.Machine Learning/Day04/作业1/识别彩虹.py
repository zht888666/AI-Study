import cv2
import numpy as np

if __name__ == '__main__':
    image_np = cv2.imread('caihong.jpg')
    print(image_np.shape)

    image_np_hsv = cv2.cvtColor(image_np, cv2.COLOR_BGR2HSV)
    print(image_np_hsv.shape)

    orange_low = np.array([11, 43, 46])
    orange_high = np.array([25, 255, 255])
    mask1 = cv2.inRange(image_np_hsv, orange_low, orange_high)

    blue_low = np.array([109, 43, 63])
    blue_high = np.array([124, 255, 255])
    mask2 = cv2.inRange(image_np_hsv, blue_low, blue_high)

    mask = cv2.bitwise_or(mask1, mask2)
    image_np_hsv1 = cv2.bitwise_and(image_np, image_np, None, mask)

    kernel = cv2.getStructuringElement(
        cv2.MORPH_CROSS,
        (7, 7)
    )

    open_mask = cv2.morphologyEx(
        src=mask,
        op=cv2.MORPH_OPEN,
        kernel=kernel
    )

    work1 = cv2.bitwise_and(image_np, image_np, mask=open_mask)
    cv2.imshow('open_mask', open_mask)
    cv2.imshow('work1', work1)
    cv2.imwrite('work1.jpg', work1)
    cv2.waitKey(0)
