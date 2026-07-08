import cv2
import numpy as np

if __name__ == '__main__':
    image_np = cv2.imread('坤坤.png')
    print(image_np.shape)

    print(image_np.shape)

    y_start = 270
    y_end = 360
    x_start = 500
    x_end = 600
    roi_img = image_np[y_start:y_end, x_start:x_end]
    cv2.imshow('roi_img', roi_img)
    cv2.waitKey(0)
