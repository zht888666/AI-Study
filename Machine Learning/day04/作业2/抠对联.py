import cv2
import numpy as np

if __name__ == '__main__':
    image_np = cv2.imread('dianti.jpg')
    y_min, y_min1, y_min2 = 138, 376, 379
    y_max, y_max1, y_max2 = 295, 1155, 1182
    x_min, x_min1, x_min2 = 448, 45, 1083
    x_max, x_max1, x_max2 = 866, 203, 1265
    duilian1 = image_np[y_min:y_max, x_min:x_max]
    duilian2 = image_np[y_min1:y_max1, x_min1:x_max1]
    duilian3 = image_np[y_min2:y_max2, x_min2:x_max2]
    cv2.imshow('duilian1', duilian1)
    cv2.imshow('duilian2', duilian2)
    cv2.imshow('duilian3', duilian3)
    cv2.imwrite('duilian1.jpg', duilian1)
    cv2.imwrite('duilian2.jpg', duilian2)
    cv2.imwrite('duilian3.jpg', duilian3)
    cv2.waitKey(0)
