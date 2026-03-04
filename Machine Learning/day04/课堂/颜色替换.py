import cv2
import numpy as np

if __name__ == '__main__':
    image_np = cv2.imread('zaodian.png')
    print(image_np.shape)

    image_np_hsv = cv2.cvtColor(image_np, cv2.COLOR_BGR2HSV)
    print(image_np_hsv.shape)

    red_low = np.array([0, 43, 46])
    red_high = np.array([10, 255, 255])

    mask1 = cv2.inRange(image_np_hsv, red_low, red_high)
    red_low = np.array([156, 43, 46])
    red_high = np.array([180, 255, 255])

    mask2 = cv2.inRange(image_np_hsv, red_low, red_high)
    mask = cv2.bitwise_or(mask1, mask2)
    kernel = cv2.getStructuringElement(cv2.MARKER_CROSS, (7, 7))

    open_mask = cv2.morphologyEx(src=mask, op=cv2.MORPH_OPEN, kernel=kernel)

    image_np_hsv1 = cv2.bitwise_and(image_np, image_np, None, mask)
    cv2.imshow('mask', mask)
    cv2.imshow('image_np', image_np)
    cv2.waitKey(0)
