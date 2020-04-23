from __future__ import absolute_import, division, print_function, \
    unicode_literals

import tensorflow as tf
import numpy as np

def load_mnist():
    #文件路径
    path = r'dataset/mnist.npz'
    f = np.load(path)
    x_train, y_train = f['x_train'],f['y_train']
    x_test, y_test = f['x_test'],f['y_test']
    f.close()
    return (x_train, y_train), (x_test, y_test)

def train_model():
    ###自动下载###
    #mnist = tf.keras.datasets.mnist
    #(x_train, y_train), (x_test, y_test) = mnist.load_data()

    ###导入本地的###
    (x_train, y_train), (x_test, y_test)=load_mnist()
    x_train, x_test = x_train / 255.0, x_test / 255.0

    with tf.device('/gpu:0'):
        model = tf.keras.models.Sequential([
            tf.keras.layers.Flatten(input_shape=(28, 28)),
            tf.keras.layers.Dense(128, activation='relu'),
            tf.keras.layers.Dropout(0.2),
            tf.keras.layers.Dense(10, activation='softmax')
        ])

        model.compile(optimizer='adam',
                      loss='sparse_categorical_crossentropy',
                      metrics=['accuracy'])
        model.fit(x_train, y_train, epochs=5)
        model.evaluate(x_test, y_test)


if __name__ == '__main__':
    train_model()
