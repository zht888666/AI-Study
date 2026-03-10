import cv2
import numpy as np

if __name__ == '__main__':
    image_np = cv2.imread('img.png')
    h, w = image_np.shape[:2]
    angle = 317
    scale = 1
    ratatoion = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(ratatoion, angle, scale)
    print(M)

    ratatoion_image = cv2.warpAffine(image_np, M, (w, h), borderValue=(0, 0, 0))
    y_min, y_max = 735, 950
    x_min, x_max = 465, 782
    image_np_roi = ratatoion_image[y_min: y_max, x_min: x_max]
    top, bottom, left, right = 600, 600, 700, 700

    image1 = cv2.copyMakeBorder(image_np_roi, top, bottom, left, right, cv2.BORDER_WRAP)
    # ratatoion_image1 = cv2.warpAffine(image_np_roi, None, (image_np_roi.shape[1], image_np_roi.shape[0]),
    #                                   flags=cv2.INTER_LANCZOS4, borderMode=cv2.BORDER_WRAP)
    roi = image1[172:1030, 64:1333]
    cv2.imshow('ratatoion_image', roi)
    cv2.imwrite('image1.jpg', roi)
    cv2.waitKey(0)
