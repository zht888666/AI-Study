import cv2
import numpy as np

if __name__ == '__main__':
    image_np = cv2.imread('img.png')

    image_np_gray = cv2.cvtColor(image_np, cv2.COLOR_BGR2GRAY)
    cv2.imshow('1', image_np_gray)
    cv2.waitKey(0)
    _, image_np_thresh = cv2.threshold(image_np_gray, 127, 255, cv2.THRESH_BINARY)

    contours, hierarchy = cv2.findContours(image_np_thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    for cnt in contours:
        hull = cv2.convexHull(cnt)
        cv2.polylines(
            image_np, [hull], isClosed=True, color=(0, 255, 255), thickness=3
        )
    cv2.imshow('w', image_np)
    cv2.waitKey(0)
