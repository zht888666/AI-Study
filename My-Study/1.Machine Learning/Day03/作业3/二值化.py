import numpy as np
import cv2
import matplotlib.pyplot as plt

if __name__ == '__main__':
    path = 'work3.png'
    image = cv2.imread(path)
    print(image.shape)
    image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    thresh = 125
    maxval = 255
    _, image_gray = cv2.threshold(
        image_gray,
        thresh,
        maxval,
        cv2.THRESH_BINARY_INV
    )
    cv2.imshow('image_gray', image_gray)
    cv2.imwrite('image1.png', image_gray)
    cv2.waitKey(0)
