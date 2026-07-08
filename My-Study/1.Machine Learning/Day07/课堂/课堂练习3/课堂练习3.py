# 给星星绘制最小外接圆
import cv2

if __name__ == '__main__':
    image_np = cv2.imread('img.png')
    image_np_gray = cv2.cvtColor(image_np, cv2.COLOR_BGR2GRAY)
    _, image_np_thresh = cv2.threshold(image_np_gray, 127, 255, cv2.THRESH_BINARY)

    contours, hierarchy = cv2.findContours(
        image_np_thresh,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )
    # 把星星和白条区别开
    for cnt in contours:
        area = cv2.contourArea(cnt)
        # cv2.contourArea是一个用来算“地盘大小”的函数。作用:它计算一个轮廓（Contour）围成的区域的面积。
        print(area)  # 看看星星的面积，小的是星星，把大的去掉
        if area < 1000:
            (x, y), radius = cv2.minEnclosingCircle(cnt)
            x, y, radius = int(x), int(y), int(radius)
            cv2.circle(image_np, (x, y), radius, (0, 0, 255), 2, cv2.LINE_AA)
    cv2.imshow("image_np", image_np)
    cv2.imwrite('image_np.jpg', image_np)
    cv2.waitKey(0)
