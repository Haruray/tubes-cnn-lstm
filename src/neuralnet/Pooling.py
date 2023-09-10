from neuralnet.Layer import Layer
import numpy as np


class Pooling(Layer):
    # intinya sama kaya ConvLayer, yaitu pada proses ekstraksinya. Yang berbeda adalah pada pemrosesannya, yaitu max/avg pooling
    def __init__(self, mode: str, pool_size: tuple, stride: int):
        super().__init__()
        # type check
        if mode != "avg" and mode != "max":
            raise Exception("Mode not recognized.")
        self.type = "pooling"
        self.mode = mode
        self.pool_size = pool_size
        self.stride = stride

    def get_image_channels(self, matrix: np.ndarray):
        channels = []
        if len(matrix.shape) == 3:
            for i in range(matrix.shape[2]):
                channels.append(matrix[:, :, i])
        else:
            return [matrix]  # berarti dia single channel
        return channels

    def extract_features(self, matrix: np.ndarray, output_shape: tuple):
        new_height = output_shape[0]
        new_width = output_shape[1]
        i = j = 0
        # loop matrix gambarnya buat ekstraksi fitur
        while i < new_height:
            j = 0
            while j < new_width:
                if (
                    i + self.pool_size[0] < new_height
                    and j + self.pool_size[1] < new_width
                ):
                    region = matrix[
                        i
                        * self.pool_size[0] : (
                            i * self.pool_size[0] + self.pool_size[0]
                        ),
                        j
                        * self.pool_size[1] : (
                            j * self.pool_size[1] + self.pool_size[1]
                        ),
                    ]
                    # bagian (region) dari matrix yang sudah di ekstrak , koordinat x pada feature map, koordinat y pada feature map
                    yield region, i, j
                j += self.stride
            i += self.stride

    def forward_propagate(self, input: np.ndarray):
        # input adalah feature map hasil conv layer
        height = input.shape[0]
        num_filters = input.shape[2]
        # sama kaya rumus ukuran feature map kaya ConvLayer, cuma gapakai padding
        feature_map_v = int((height - self.pool_size[0]) / self.stride) + 1
        feature_map_shape = (feature_map_v, feature_map_v, num_filters)
        feature_map = np.zeros(feature_map_shape)
        input_channels = self.get_image_channels(input)
        for channel in input_channels:
            for region, i, j in self.extract_features(channel, feature_map_shape):
                # bagian (region) yang sudah di ekstrak di kalikan dengan filter yang ada. Argumen "axis" aku belum tau buat apa..
                if self.mode == "max":
                    feature_map[i, j] = np.max(region)
                elif self.mode == "avg":
                    feature_map[i, j] = np.average(region)
        return feature_map
