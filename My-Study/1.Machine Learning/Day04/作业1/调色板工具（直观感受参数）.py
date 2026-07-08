import cv2
import numpy as np

# 图片路径
path = 'caihong.jpg'
img = cv2.imread(path)
hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)


def mouse_click(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:  # 当左键点击时
        # 获取点击处的 BGR 值
        b = img[y, x, 0]
        g = img[y, x, 1]
        r = img[y, x, 2]

        # 获取点击处的 HSV 值
        h = hsv[y, x, 0]
        s = hsv[y, x, 1]
        v = hsv[y, x, 2]

        print(f"坐标 ({x},{y})")
        print(f"    BGR: [{b}, {g}, {r}]")
        print(f"    HSV: [{h}, {s}, {v}]")  # <--- 重点看这里对比！

        # 视觉辅助：在点击处画个小圈
        cv2.circle(img, (x, y), 5, (0, 0, 255), 2)
        cv2.imshow('Mouse Picker', img)


cv2.imshow('Mouse Picker', img)
cv2.setMouseCallback('Mouse Picker', mouse_click)

print("请点击图片中你想分析的颜色区域...")
print("按 'q' 退出")

while True:
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()