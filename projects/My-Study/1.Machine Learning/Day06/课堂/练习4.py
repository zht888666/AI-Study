import cv2
import numpy as np

if __name__ == '__main__':
    image_np = cv2.imread('lian3.png')
    image_np_gray = cv2.cvtColor(image_np, cv2.COLOR_BGR2GRAY)
    _, image_np_thresh = cv2.threshold(
        image_np_gray,
        40, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU
    )
    edges_image = cv2.Canny(image_np_thresh, 20, 40
                            )

cv2.imshow('dst_image', edges_image)
cv2.waitKey(0)
