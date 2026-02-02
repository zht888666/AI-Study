import cv2
import numpy as np

if __name__ == '__main__':
    image_np = cv2.imread('作业1/caihong.jpg')
    print(image_np.shape)

    image_np_hsv = cv2.cvtColor(image_np, cv2.COLOR_BGR2HSV)
    print(image_np_hsv.shape)

    blue_low = np.array([0, 43, 46])
    blue_high = np.array([10, 255, 255])

    mask1 = cv2.inRange(image_np_hsv, blue_low, blue_high)
    blue_low = np.array([156, 43, 46])
    blue_high = np.array([180, 255, 255])

    mask2 = cv2.inRange(image_np_hsv, blue_low, blue_high)
    mask = cv2.bitwise_or(mask1, mask2)
    image_np_hsv1 = cv2.bitwise_and(image_np, image_np, None, mask)
    cv2.imshow('mask', mask)
    cv2.imshow('image_np_hsv1', image_np_hsv1)
    cv2.waitKey(0)
