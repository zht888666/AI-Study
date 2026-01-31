import cv2
import numpy as np
import matplotlib.pyplot as plt

x, y = 'image.jpg', 'image 1.jpg'


def A(num):
    img = cv2.imread(num)
    h, w, c = img.shape
    b, g, r = cv2.split(img)
    blue = np.zeros((h, w, 3), dtype=np.uint8)
    blue[:, :, 0] = b
    blue = cv2.cvtColor(blue, cv2.COLOR_BGR2RGB)
    cv2.imwrite("blue.png",blue)

    green = np.zeros((h, w, 3), dtype=np.uint8)
    green[:, :, 1] = g
    green = cv2.cvtColor(green, cv2.COLOR_BGR2RGB)
    cv2.imwrite("green.png", green)

    red = np.zeros((h, w, 3), dtype=np.uint8)
    red[:, :, 2] = r
    red = cv2.cvtColor(red, cv2.COLOR_BGR2RGB)
    cv2.imwrite("red.png", red)

    plt.subplot(131)
    plt.imshow(blue)
    plt.axis('off')
    plt.title('blue_channel')
    plt.subplot(132)
    plt.imshow(green)
    plt.axis('off')
    plt.title('blue_channel')

    plt.subplot(133)
    plt.imshow(red)
    plt.axis('off')
    plt.title('blue_channel')
    plt.show()


A('image.jpg')
A('image 1.jpg')
