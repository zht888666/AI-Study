# 给坤坤一只鸡
import cv2
import numpy as np

if __name__ == '__main__':
    img = cv2.imread('kunkun.png')
    chicken = cv2.imread('chicken1.png')

    ice_gray = cv2.cvtColor(chicken, cv2.COLOR_BGR2GRAY)
    _, mask = cv2.threshold(ice_gray, 70, 255, cv2.THRESH_BINARY_INV)

    rows, cols = chicken.shape[:2]
    rol = img[240:240+rows, 200:200+cols]

    img_and = cv2.bitwise_and(rol, rol, mask=mask)

    dat = cv2.add(img_and, chicken)

    img[240:240+rows, 200:200+cols] = dat

    cv2.imshow('img', img)
    cv2.imwrite('homework1.jpg', img)
    cv2.waitKey(0)