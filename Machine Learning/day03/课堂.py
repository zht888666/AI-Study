import numpy as np
import cv2

if __name__ == '__main__':
    path = 'lena.png'
    image = cv2.imread(path)
    print(image.shape)

    image_gray = image.copy()
    