import cv2
import numpy as np

if __name__ == '__main__':
    image_np = cv2.imread('img.png')
    image_np_hsv = cv2.cvtColor(image_np, cv2.COLOR_BGR2HSV)

    blue_low = np.array([100, 100, 110])
    blue_high = np.array([124, 255, 255])
    mask = cv2.inRange(image_np_hsv, blue_low, blue_high)

    kernel = cv2.getStructuringElement(cv2.MARKER_CROSS, (7, 7))
    open_mask = cv2.morphologyEx(src=mask, op=cv2.MORPH_OPEN, kernel=kernel)

    for i in range(image_np_hsv.shape[0]):
        for j in range(image_np_hsv.shape[1]):
            if open_mask[i, j] == 255:
                image_np[i, j] = (0, 0, 255)

    # image_np_hsv[open_mask == 255] = (0, 0, 255)
    cv2.imshow('image_np', image_np)
    cv2.imwrite('work3.jpg', image_np)
    cv2.waitKey(0)
