import numpy as np
import cv2
import matplotlib.pyplot as plt

if __name__ == '__main__':
    path = 'work4.jpg'
    image = cv2.imread(path)
    print(image.shape)
    image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    thresh = 125
    maxval = 255
    _, image_gray = cv2.threshold(
        image_gray,
        thresh,
        maxval,
        cv2.THRESH_BINARY
    )
    a = image_gray
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
    a2 = cv2.erode(a, kernel, iterations=8)

    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (12, 12))
    a3 = cv2.dilate(a2, kernel, iterations=3)
cv2.imshow('morph_image', a3)
cv2.waitKey(0)
cv2.imwrite("image1.jpg", a3)
