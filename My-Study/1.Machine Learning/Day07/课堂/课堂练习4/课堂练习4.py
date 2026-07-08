# 使用最小外接圆把东字圈起来。
import cv2

if __name__ == '__main__':
    image_np = cv2.imread('img.png')
    image_np_gray = cv2.cvtColor(image_np, cv2.COLOR_BGR2GRAY)
    _, image_np_thresh = cv2.threshold(image_np_gray, 127, 255, cv2.THRESH_BINARY_INV)

    contours, hierarchy = cv2.findContours(
        image_np_thresh,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )
    # 在所有轮廓中把东找出来
    for cnt in contours:
        area = cv2.contourArea(cnt)
        # cv2.contourArea是一个用来算“地盘大小”的函数。作用:它计算一个轮廓（Contour）围成的区域的面积。
        if 100000 < area:  # 缩小范围，精准找到东
            print(area)
        if 130000 < area < 140000:
            (x, y), radius = cv2.minEnclosingCircle(cnt)
            x, y, radius = int(x), int(y), int(radius)
            cv2.circle(image_np, (x, y), radius, (0, 0, 255), 10, cv2.LINE_AA)
    cv2.imshow("East", image_np)
    cv2.imwrite('East.jpg', image_np)
    cv2.waitKey(0)
