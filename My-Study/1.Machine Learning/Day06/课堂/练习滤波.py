import cv2
import numpy as np

if __name__ == '__main__':
    image = cv2.imread()
    np_noise_image = cv2.blur(image, (3.3))
    cv2.imshow('1', np_noise_image)
    cv2.waitKey(0)
    cv2.Ga