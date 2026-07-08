import cv2
import numpy as np

if __name__ == '__main__':
    image = cv2.imread('img.png')
    sigama = 100
    no_noise_image = cv2.medianBlur(image, 11)
    # np_noise_image = cv2.bilateralFilter(image, 29, sigama, sigama)
    cv2.imshow('1', no_noise_image)
    cv2.imwrite('2.jpg', no_noise_image)
    cv2.waitKey(0)
