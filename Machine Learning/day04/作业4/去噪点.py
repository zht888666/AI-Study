import cv2
import numpy as np

if __name__ == '__main__':
    image_np = cv2.imread('image (3).jpg')
    gary = cv2.cvtColor(image_np, cv2.COLOR_BGR2GRAY)

    _, gary = cv2.threshold(gary, 240, 255, cv2.THRESH_BINARY_INV)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (9, 9))
    open_mask = cv2.morphologyEx(src=gary, op=cv2.MORPH_OPEN, kernel=kernel)
    image_np[open_mask == 0] = (255, 255, 255)

    cv2.imshow('image_np', image_np)
    cv2.imwrite('work4.jpg', image_np)
    cv2.waitKey(0)
