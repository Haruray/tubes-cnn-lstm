from glob import glob
import numpy as np
import cv2
import random


class ImageData:
    def __init__(self, image=None, label=None) -> None:
        self.image = image
        self.label = label


class ImageDataset:
    def __init__(self, data: list = []) -> None:
        self.data = data

    def shuffle(self):
        random.shuffle(self.data)

    def get_images(self):
        return np.array([data.image for data in self.data])

    def get_labels(self):
        return np.array([[data.label] for data in self.data])


class Preprocess:
    def __init__(self, folder_name: str, k_fold: bool, k: int = 10) -> None:
        self.folder_name = folder_name
        self.k_fold = k_fold
        self.k = k

    def get_data(self, shuffle: bool = False):
        if self.k_fold:
            return self.get_data_kfold(shuffle)
        else:
            return self.get_data_normal(shuffle)

    def get_data_normal(self, shuffle: bool = False):
        train = ImageDataset()
        test = ImageDataset()
        directories_train_bears = glob(f"../{self.folder_name}/Train/Bears/*.jpeg")
        directories_test_bears = glob(f"../{self.folder_name}/Test/Bears/*.jpeg")
        directories_train_pandas = glob(f"../{self.folder_name}/Train/Pandas/*.jpeg")
        directories_test_pandas = glob(f"../{self.folder_name}/Test/Pandas/*.jpeg")

        for directory in directories_train_bears:
            image = cv2.imread(directory)
            data = ImageData(image, 0)
            train.data.append(data)
        for directory in directories_test_bears:
            image = cv2.imread(directory)
            data = ImageData(image, 0)
            test.data.append(data)
        for directory in directories_train_pandas:
            image = cv2.imread(directory)
            data = ImageData(image, 1)
            train.data.append(data)
        for directory in directories_test_pandas:
            image = cv2.imread(directory)
            data = ImageData(image, 1)
            test.data.append(data)

        if shuffle:
            train.shuffle()
            test.shuffle()
        return train, test

    def get_data_kfold(self):
        train, test = self.get_data_normal()
        train_test_combined = ImageDataset(train.data + test.data)
        train_test_combined.shuffle()
        # split into k fold
        data_split = ImageDataset()
        fold_size = int(len(train_test_combined.data) / self.k)
        for i in range(self.k):
            fold = ImageDataset()
            for j in range(fold_size):
                fold.data.append(train_test_combined.data[i * fold_size + j])
            data_split.data.append(fold)
        return data_split
