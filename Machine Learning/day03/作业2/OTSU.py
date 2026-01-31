import cv2

if __name__ == '__main__':
    path = "image 1.jpg"
    image_np = cv2.imread(path)
    image_np_gary = cv2.cvtColor(image_np, cv2.COLOR_BGR2GRAY)
    rows, cols = image_np_gary.shape
    sum1 = rows * cols
    a, thresh = 0, 0
    for x in range(0, 256):
        n0, n1, m0, m1 = 0, 0, 0, 0
        for i in range(rows):
            for j in range(cols):
                if image_np_gary[i, j] < x:
                    n0 += 1
                    m0 += image_np_gary[i, j]
                else:
                    n1 += 1
                    m1 += image_np_gary[i, j]
        if n0 == 0 or n1 == 0:
            continue
        w0 = n0 / sum1
        w1 = n1 / sum1
        u0 = m0 / n0
        u1 = m1 / n1
        u = (m1 + m0) / sum1
        g = w0 * (u0 - u) ** 2 + w1 * (u1 - u) ** 2
        if g >= a:
            a = g
            thresh = x

    maxval = 255
    _, image_np_gary = cv2.threshold(image_np_gary, thresh, maxval, cv2.THRESH_BINARY_INV)

    cv2.imshow('image_np_gray', image_np_gary)
    cv2.imwrite('image2.jpg', image_np_gary)
    cv2.waitKey(0)
