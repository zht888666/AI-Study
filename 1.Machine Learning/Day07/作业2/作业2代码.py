# 根据最小外接圆的半径找到四个大字，根据圆心坐标的x轴找到东。
import cv2

if __name__ == '__main__':
    image_np = cv2.imread('img.png')
    image_np_gray = cv2.cvtColor(image_np, cv2.COLOR_BGR2GRAY)
    _, image_np_thresh = cv2.threshold(image_np_gray, 127, 255, cv2.THRESH_BINARY_INV)

    contours, hierarchy = cv2.findContours(image_np_thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    # 在所有轮廓中把东找出来
    for cnt in contours:
        (x, y), radius = cv2.minEnclosingCircle(cnt)
        x, y, radius = int(x), int(y), int(radius)
        if radius > 200:
            print(radius)
            if 1216 < x <1533:
                cv2.circle(image_np, (x, y), radius, (0, 0, 255), 10, cv2.LINE_AA)
    cv2.imshow("East", image_np)
    cv2.imwrite('East.jpg', image_np)
    cv2.waitKey(0)
