import cv2
import numpy as np
import os
from tkinter import Tk, filedialog, simpledialog


def safe_tk_dialog(dialog_func, *args, **kwargs):
    root = Tk()
    root.withdraw()
    root.attributes('-alpha', 0.0)  # 透明度设为0（完全不可见）
    result = dialog_func(*args, **kwargs)  # 执行对话框函数，获取用户选择结果
    root.update_idletasks()  # 强制处理所有待处理的UI事件，确保状态更新
    root.destroy()  # 安全销毁窗口，释放资源
    try:
        import ctypes
        ctypes.windll.user32.SetCursor(ctypes.windll.user32.LoadCursorW(0, 32512))
    except Exception:
        pass  # 非Windows系统或调用失败时忽略错误
    return result


class ImageToolbox:
    def __init__(self):
        self.original_image = None  # 原始图像（备份，用于重置）
        self.current_image = None  # 当前处理的图像
        self.working_image = None  # 工作副本（用于显示和交互）
        self.window_name = "Image Toolbox"  # 窗口名称
        self.selected_points = []  # 存储鼠标点击的点坐标
        self.roi_rect = None  # 存储ROI矩形
        self.temp_drawing = None  # 临时绘图用副本

    def load_image(self):
        file_path = safe_tk_dialog(
            filedialog.askopenfilename,
            title="选择图片文件",
            filetypes=[
                ("图片文件", "*.jpg *.jpeg *.png *.bmp *.tiff"),
                ("JPEG文件", "*.jpg *.jpeg"),
                ("PNG文件", "*.png"),
                ("所有文件", "*.*")
            ],
            initialdir=os.path.expanduser("~")  # 默认打开用户主目录
        )

        # 使用OpenCV读取图像
        self.original_image = cv2.imread(file_path)
        # 创建当前图像的副本用于处理
        self.current_image = self.original_image.copy()
        self.working_image = self.original_image.copy()
        return True

    def save_image(self):
        """
        功能8：保存当前图像到指定位置
        """
        file_path = safe_tk_dialog(
            filedialog.asksaveasfilename,
            title="保存图像",
            defaultextension=".png",
            filetypes=[
                ("PNG格式", "*.png"),
                ("JPEG格式", "*.jpg *.jpeg"),
                ("BMP格式", "*.bmp"),
                ("TIFF格式", "*.tiff"),
                ("所有文件", "*.*")
            ]
        )

        # 根据扩展名调整保存参数
        extension = os.path.splitext(file_path)[1].lower()

        try:
            if extension in ['.jpg', '.jpeg']:
                cv2.imwrite(file_path, self.current_image, [cv2.IMWRITE_JPEG_QUALITY, 95])
            else:
                cv2.imwrite(file_path, self.current_image)

            print(f"图像已保存至：{file_path}")
            return True

        except Exception as e:
            print(f"保存失败：{str(e)}")
            return False

    def _mouse_callback_perspective(self, event, x, y, flags, param):
        """
        鼠标回调函数：用于透视变换的4点选择
        参数说明：
            event: 鼠标事件类型（点击、移动、释放）
            x, y: 鼠标当前坐标
        """
        # 左键点击事件
        if event == cv2.EVENT_LBUTTONDOWN:
            if len(self.selected_points) < 4:
                # 记录点击坐标
                self.selected_points.append((x, y))
                print(f"  已选择点 {len(self.selected_points)}: ({x}, {y})")
                # 在图像上绘制标记
                cv2.circle(self.working_image, (x, y), 8, (0, 0, 255), -1)
                cv2.putText(self.working_image, str(len(self.selected_points)),
                            (x + 10, y - 10), cv2.FONT_HERSHEY_SIMPLEX,
                            1, (0, 255, 0), 2)
                if len(self.selected_points) == 4:
                    pts = np.array(self.selected_points, np.int32)
                    pts = pts.reshape((-1, 1, 2))
                    cv2.polylines(self.working_image, [pts], True, (255, 0, 0), 2)
                cv2.imshow(self.window_name, self.working_image)

    def _mouse_callback_roi(self, event, x, y, flags, param):
        """
        鼠标回调函数：用于ROI矩形选择
        支持拖拽绘制矩形
        """
        if event == cv2.EVENT_LBUTTONDOWN:
            # 鼠标按下：记录起点，开始绘制
            self.selected_points = [(x, y)]
            self.temp_drawing = self.working_image.copy()
            print(f"  ROI起点：({x}, {y})")

        elif event == cv2.EVENT_MOUSEMOVE and len(self.selected_points) == 1:
            # 鼠标移动：实时显示矩形框
            if self.temp_drawing is not None:
                self.working_image = self.temp_drawing.copy()
                x0, y0 = self.selected_points[0]
                cv2.rectangle(self.working_image, (x0, y0), (x, y), (0, 255, 0), 2)
                cv2.imshow(self.window_name, self.working_image)

        elif event == cv2.EVENT_LBUTTONUP:
            # 鼠标释放：确定终点，完成选择
            if len(self.selected_points) == 1:
                x0, y0 = self.selected_points[0]
                x1, y1 = max(x0, x), max(y0, y)
                x0, y0 = min(x0, x), min(y0, y)

                self.roi_rect = (x0, y0, x1, y1)
                print(f"  ROI终点：({x}, {y})")
                print(f"  选中区域：({x0}, {y0}) 到 ({x1}, {y1})")

                cv2.rectangle(self.working_image, (x0, y0), (x1, y1), (0, 0, 255), 3)
                cv2.imshow(self.window_name, self.working_image)
                print("  按任意键确认选择")

    def _mouse_callback_watermark(self, event, x, y, flags, param):
        """
        鼠标回调函数：用于选择水印位置
        只需单击选择中心点
        """
        if event == cv2.EVENT_LBUTTONDOWN:
            self.selected_points = [(x, y)]
            print(f"  水印位置：({x}, {y})")
            # 绘制十字标记
            size = 20
            color = (0, 255, 255)
            cv2.line(self.working_image, (x - size, y), (x + size, y), color, 2)
            cv2.line(self.working_image, (x, y - size), (x, y + size), color, 2)
            cv2.circle(self.working_image, (x, y), 5, color, -1)
            cv2.imshow(self.window_name, self.working_image)
            print("  按任意键确认位置")

    def perspective_transform(self):
        """
        功能1：通用透视变换（畸变纠正）
        原理：通过4个点建立透视映射关系，将倾斜的平面拉正
        """
        # 重置工作图像和选择点
        self.working_image = self.current_image.copy()
        self.selected_points = []
        # 创建窗口并设置鼠标回调
        cv2.namedWindow(self.window_name)
        cv2.setMouseCallback(self.window_name, self._mouse_callback_perspective)
        while True:
            cv2.imshow(self.window_name, self.working_image)
            key = cv2.waitKey(1) & 0xFF

            if key == ord('r'):
                self.working_image = self.current_image.copy()
                self.selected_points = []
                print("  已重置，请重新选择4个点")

            elif key == 27:
                print("操作取消")
                cv2.destroyWindow(self.window_name)
                return

            elif len(self.selected_points) == 4 and key != 255:
                break

        # 执行透视变换
        try:
            h, w = self.current_image.shape[:2]

            dst_points = np.float32([
                [0, 0],
                [w, 0],
                [w, h],
                [0, h]
            ])

            src_points = np.float32(self.selected_points)
            matrix = cv2.getPerspectiveTransform(src_points, dst_points)

            result = cv2.warpPerspective(
                self.current_image,
                matrix,
                (w, h),
                borderMode=cv2.BORDER_CONSTANT,
                borderValue=(128, 128, 128)
            )

            self.current_image = result
            self.working_image = result.copy()
            cv2.imshow(self.window_name, self.current_image)
            cv2.waitKey(0)

        except Exception as e:
            print(f"透视变换失败：{str(e)}")
        cv2.destroyWindow(self.window_name)

    def rotate_image(self):
        """
        功能2：图像旋转（带边缘填充）
        """
        angle = safe_tk_dialog(
            simpledialog.askfloat,
            "输入旋转角度",
            "请输入旋转角度（正值为逆时针，负值为顺时针）：\n例如：45 或 -90",
            initialvalue=0,
            minvalue=-360,
            maxvalue=360
        )

        print(f"旋转角度：{angle}度")
        (h, w) = self.current_image.shape[:2]
        center = (w // 2, h // 2)
        rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
        abs_cos = abs(rotation_matrix[0, 0])
        abs_sin = abs(rotation_matrix[0, 1])
        new_w = int(h * abs_sin + w * abs_cos)
        new_h = int(h * abs_cos + w * abs_sin)
        rotation_matrix[0, 2] += (new_w - w) / 2
        rotation_matrix[1, 2] += (new_h - h) / 2
        rotated = cv2.warpAffine(
            self.current_image,
            rotation_matrix,
            (new_w, new_h),
            flags=cv2.INTER_LINEAR,
            borderMode=cv2.BORDER_REPLICATE
        )
        self.current_image = rotated
        self.working_image = rotated.copy()

        cv2.imshow("旋转结果", self.current_image)
        cv2.waitKey(0)
        cv2.destroyWindow("旋转结果")

    def enhance_contrast(self):
        """
        功能3：对比度增强
        """
        lab = cv2.cvtColor(self.current_image, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)

        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        l_enhanced = clahe.apply(l)

        lab_enhanced = cv2.merge([l_enhanced, a, b])
        result = cv2.cvtColor(lab_enhanced, cv2.COLOR_LAB2BGR)

        self.current_image = result
        self.working_image = result.copy()

        cv2.imshow("对比度增强结果", self.current_image)
        cv2.waitKey(0)
        cv2.destroyWindow("对比度增强结果")

    def enhance_brightness(self):
        """
        功能4：亮度增强（简单增益调整）
        原理：通过乘法（对比度）和加法（亮度）调整
        """

        img_float = self.current_image.astype(np.float32)
        gain = 1.2

        brightened = img_float * gain
        brightened = np.clip(brightened, 0, 255)
        result = brightened.astype(np.uint8)

        self.current_image = result
        self.working_image = result.copy()

        cv2.imshow("亮度增强结果", self.current_image)
        cv2.waitKey(0)
        cv2.destroyWindow("亮度增强结果")

    def add_watermark(self):
        """
        功能5：添加文字水印
        """
        text = safe_tk_dialog(
            simpledialog.askstring,
            "输入水印文字",
            "请输入要添加的水印文字：",
            initialvalue="happy"
        )

        h, w = self.current_image.shape[:2]
        short_side = min(h, w)
        font_scale = (short_side * 0.1) / 30

        # 准备交互选择位置
        self.working_image = self.current_image.copy()
        self.selected_points = []
        cv2.namedWindow(self.window_name)
        cv2.setMouseCallback(self.window_name, self._mouse_callback_watermark)

        while True:
            cv2.imshow(self.window_name, self.working_image)
            key = cv2.waitKey(1) & 0xFF

            if key == 27:
                print("操作取消")
                cv2.destroyWindow(self.window_name)
                return

            if len(self.selected_points) == 1 and key != 255:
                break

        cv2.destroyWindow(self.window_name)
        x, y = self.selected_points[0]

        font = cv2.FONT_HERSHEY_SIMPLEX
        thickness = max(1, int(font_scale * 2))
        (text_w, text_h), baseline = cv2.getTextSize(text, font, font_scale, thickness)

        x = int(x - text_w / 2)
        y = int(y + text_h / 2)

        result = self.current_image.copy()
        cv2.putText(
            result,
            text,
            (x, y),
            font,
            font_scale,
            (0, 0, 255),
            thickness,
            cv2.LINE_AA
        )
        self.current_image = result
        self.working_image = result.copy()

        cv2.imshow("水印效果", self.current_image)
        cv2.waitKey(0)
        cv2.destroyWindow("水印效果")

    def extract_roi(self):
        """
        功能6：ROI区域提取（交互式矩形选择）
        """
        self.working_image = self.current_image.copy()
        self.selected_points = []
        self.roi_rect = None
        self.temp_drawing = None

        cv2.namedWindow(self.window_name)
        cv2.setMouseCallback(self.window_name, self._mouse_callback_roi)

        while True:
            cv2.imshow(self.window_name, self.working_image)
            key = cv2.waitKey(1) & 0xFF
            if key == 27:
                print("操作取消")
                cv2.destroyWindow(self.window_name)
                return

            if self.roi_rect is not None and key != 255:
                break

        cv2.destroyWindow(self.window_name)

        if self.roi_rect:
            x0, y0, x1, y1 = self.roi_rect

            h, w = self.current_image.shape[:2]
            x0, y0 = max(0, x0), max(0, y0)
            x1, y1 = min(w, x1), min(h, y1)
            roi = self.current_image[y0:y1, x0:x1]

            print(f"提取区域尺寸：{roi.shape[1]} x {roi.shape[0]}")
            save_path = safe_tk_dialog(
                filedialog.asksaveasfilename,
                title="保存ROI区域",
                defaultextension=".png",
                filetypes=[("PNG格式", "*.png"), ("JPEG格式", "*.jpg"), ("所有文件", "*.*")]
            )

            if save_path:
                try:
                    cv2.imwrite(save_path, roi)
                    print(f"ROI已保存至：{save_path}")
                    cv2.imshow("提取的ROI", roi)
                    cv2.waitKey(0)
                    cv2.destroyWindow("提取的ROI")

                except Exception as e:
                    print(f"保存失败：{str(e)}")
            else:
                print("保存取消")

    def resize_image(self):
        """
        功能7：图像缩放（指定比例，保持长宽比）
        使用双线性插值，保持图像质量
        """
        scale = safe_tk_dialog(
            simpledialog.askfloat,
            "输入缩放比例",
            "请输入缩放比例（0.1-5.0）：\n例如：0.5=缩小一半，2.0=放大两倍",
            initialvalue=1.0,
            minvalue=0.1,
            maxvalue=5.0
        )
        h, w = self.current_image.shape[:2]

        new_w = int(w * scale)
        new_h = int(h * scale)
        if scale < 1.0:
            interp = cv2.INTER_AREA
        else:
            interp = cv2.INTER_CUBIC

        resized = cv2.resize(self.current_image, (new_w, new_h), interpolation=interp)

        self.current_image = resized
        self.working_image = resized.copy()

        cv2.imshow("缩放结果", self.current_image)
        cv2.waitKey(0)
        cv2.destroyWindow("缩放结果")

    def show_menu(self):
        print("\n" + "=" * 50)
        print("            图像处理工具箱")
        print("0. 加载图片")
        print("1. 透视变换（畸变纠正）- 手动指定4点")
        print("2. 图像旋转 ")
        print("3. 对比度增强 ")
        print("4. 亮度增强 - 简单增益调整")
        print("5. 添加文字水印 - 红色，点击选位置")
        print("6. ROI区域提取 - 拖拽选择，单独保存")
        print("7. 图像缩放 - 指定比例，保持长宽比")
        print("8. 保存当前图像")
        print("q. 退出程序")

        if self.current_image is not None:
            h, w = self.current_image.shape[:2]
            print(f"当前图像：{w} x {h} | 已加载")
        else:
            print("当前状态：未加载图像")
        return input("请选择操作（输入数字或q）：").strip().lower()


def main():
    """
    主函数：程序入口
    """
    toolbox = ImageToolbox()
    while True:
        choice = toolbox.show_menu()
        if choice == 'q':
            cv2.destroyAllWindows()
            break
        elif choice == '0':
            toolbox.load_image()
        elif choice == '1':
            toolbox.perspective_transform()
        elif choice == '2':
            toolbox.rotate_image()
        elif choice == '3':
            toolbox.enhance_contrast()
        elif choice == '4':
            toolbox.enhance_brightness()
        elif choice == '5':
            toolbox.add_watermark()
        elif choice == '6':
            toolbox.extract_roi()
        elif choice == '7':
            toolbox.resize_image()
        elif choice == '8':
            toolbox.save_image()
        else:
            print("无效选择，请重新输入")


if __name__ == "__main__":
    main()
