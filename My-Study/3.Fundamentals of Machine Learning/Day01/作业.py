from sklearn.neighbors import KNeighborsClassifier
import numpy as np
import matplotlib.pyplot as plt

point_blue = [[1, 1], [2, 1], [2, 2]]
point_red = [[3, 1], [4, 1], [3, 2], [4, 2], [4, 3], [3, 3]]
point_green = [[5, 1], [6, 1], [5, 2], [6, 2]]
point_test = [[2.5, 2.5], [2.5, 1], [4.5, 1]]

np_train_data = np.concatenate((point_blue, point_red, point_green))
np_train_label = np.array([0] * len(point_blue) + [1] * len(point_red) + [2] * len(point_green))

knn_clf = KNeighborsClassifier(3, p=1)
knn_clf.fit(np_train_data, np_train_label)

for point in point_test:
    test_point = np.array(point).reshape(1, -1)

    test_predict = knn_clf.predict(test_point)
    test_label = ['蓝色', '红色', '绿色'][test_predict[0]]

    print(f"坐标为{point}分到：{test_label}")

    axis = [0, 7, 0, 4]

    x0, x1 = np.meshgrid(
        np.linspace(axis[0], axis[1], int(axis[1] - axis[0]) * 10).reshape(-1, 1),
        np.linspace(axis[2], axis[3], int(axis[3] - axis[2]) * 10).reshape(-1, 1)
    )

    x_new = np.c_[x0.ravel(), x1.ravel()]
    y_predict = knn_clf.predict(x_new)
    zz = y_predict.reshape(x0.shape)

    cn = plt.contour(x0, x1, zz)
    plt.scatter(np_train_data[np_train_label == 0, 0], np_train_data[np_train_label == 0, 1], marker='*')
    plt.scatter(np_train_data[np_train_label == 1, 0], np_train_data[np_train_label == 1, 1], marker='^')
    plt.scatter(np_train_data[np_train_label == 2, 0], np_train_data[np_train_label == 2, 1], marker='s')

    plt.scatter(test_point[:, 0], test_point[:, 1], marker='o', c='black', s=100)
    plt.show()