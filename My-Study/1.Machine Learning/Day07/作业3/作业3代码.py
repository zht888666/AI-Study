# 绘制六芒星的子轮廓，不要最外层轮廓
import cv2

if __name__ == '__main__':
    image_np = cv2.imread('img.png')
    image_np_gray = cv2.cvtColor(image_np, cv2.COLOR_BGR2GRAY)
    _, image_np_thresh = cv2.threshold(image_np_gray, 170, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    contours, hierarchy = cv2.findContours(image_np_thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    for cnt in contours:  # 在所有轮廓中把最外层轮廓踢出去
        area = cv2.contourArea(cnt)  # cv2.contourArea是一个用来算“地盘大小”的函数。作用:它计算一个轮廓（Contour）围成的区域的面积。
        if 1000 < area:  # 缩小范围，精准找到最外层轮廓
            print(area)
        if 1000 < area < 1000000:
            cv2.polylines(image_np, [cnt], isClosed=True, color=(0, 255, 0), thickness=15)
    cv2.imshow("star", image_np)
    cv2.imwrite('star.jpg', image_np)
    cv2.waitKey(0)
