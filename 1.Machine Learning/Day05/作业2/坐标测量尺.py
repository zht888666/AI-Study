import cv2

# 用这两个全局变量记录点击的坐标
points = []


def mouse_callback(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        points.append((x, y))
        # 在图上画个点提醒自己点过了
        cv2.circle(img_copy, (x, y), 3, (0, 0, 255), -1)
        cv2.imshow('Find_ROI', img_copy)

        if len(points) == 2:
            x1, y1 = points[0]
            x2, y2 = points[1]
            # 自动排序，防止先点右下角导致切片错误
            start_x, end_x = min(x1, x2), max(x1, x2)
            start_y, end_y = min(y1, y2), max(y1, y2)

            print("-" * 30)
            print(f"检测到区域！坐标如下：")
            print(f"x 范围: {start_x} -> {end_x}")
            print(f"y 范围: {start_y} -> {end_y}")
            print(f"roi = img[{start_y}:{end_y}, {start_x}:{end_x}]")
            points.clear()


if __name__ == '__main__':
    img = cv2.imread('yingpan.png')  # 换成你的图片名
    img_copy = img.copy()
    cv2.namedWindow('Find_ROI')
    cv2.setMouseCallback('Find_ROI', mouse_callback)

    print("操作提示：在图片上点击两个点（左上和右下）来确定 ROI 范围。按 'q' 退出。")

    while True:
        cv2.imshow('Find_ROI', img_copy)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cv2.destroyAllWindows()