import json
from neuralnet.Encoder import MyEncoder
from neuralnet.Layer import Layer
from neuralnet.clip_gradients import clip_gradients
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
        self.feature_map_shape = None
        self.last_input = None

    def __iter__(self):
        yield from {
            "type": self.type,
            "stride": self.stride,
            "mode": self.mode,
            "pool_size": self.pool_size,
        }.items()

    def __str__(self):
        return json.dumps(dict(self), cls=MyEncoder, ensure_ascii=False)

    def __repr__(self):
        return self.__str__()

    def calculate_feature_map_shape(self, input_shape: tuple):
        # input adalah feature map hasil conv layer
        height = input_shape[0]
        num_filters = input_shape[2]
        # sama kaya rumus ukuran feature map kaya ConvLayer, cuma gapakai padding
        feature_map_v = int((height - self.pool_size[0]) / self.stride) + 1
        self.feature_map_shape = (feature_map_v, feature_map_v, num_filters)
        return self.feature_map_shape

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
        features = []
        # loop matrix gambarnya buat ekstraksi fitur
        while i < new_height:
            j = 0
            while j < new_width:
                if (
                    i + self.pool_size[0] < new_height
                    and j + self.pool_size[1] < new_width
                ):
                    feat = matrix[
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
                    features.append((feat, i, j))
                j += self.stride
            i += self.stride
        return features

    def forward_propagate(self, input: np.ndarray):
        self.last_input = input
        feature_map = np.zeros(self.feature_map_shape)
        input_channels = self.get_image_channels(input)
        for channel in input_channels:
            features = self.extract_features(channel, self.feature_map_shape)
            for feat in features:
                region, i, j = feat
                # bagian (region) yang sudah di ekstrak di kalikan dengan filter yang ada. Argumen "axis" aku belum tau buat apa..
                if self.mode == "max":
                    feature_map[i, j] = np.max(region)
                elif self.mode == "avg":
                    feature_map[i, j] = np.average(region)
        return feature_map

    def backpropagate(self, din: np.ndarray, learn_rate: float):
        # gradients are passed through the indices of greatest
        # value in the original pooling during the forward step
        k_h, k_w = self.pool_size
        h_new, w_new, _ = din.shape
        _, _, num_channels = self.last_input.shape
        s_h = s_w = self.stride

        dout = np.zeros_like(self.last_input)

        for channel in range(num_channels):
            for h in range(h_new):
                for w in range(w_new):
                    if self.mode == "max":
                        tmp = self.last_input[
                            h * s_h : k_h + (h * s_h),
                            w * s_w : k_w + (w * s_w),
                            channel,
                        ]
                        mask = (tmp == np.max(tmp)).astype(int)
                        dout[
                            h * (s_h) : (h * (s_h)) + k_h,
                            w * (s_w) : (w * (s_w)) + k_w,
                            channel,
                        ] += (
                            din[h, w, channel] * mask
                        )

                    if self.mode == "avg":
                        dout = dout.astype(np.float64)
                        dout[
                            h * (s_h) : (h * (s_h)) + k_h,
                            w * (s_w) : (w * (s_w)) + k_w,
                            channel,
                        ] = (
                            dout[
                                h * (s_h) : (h * (s_h)) + k_h,
                                w * (s_w) : (w * (s_w)) + k_w,
                                channel,
                            ]
                            + (din[h, w, channel]) / k_h / k_w
                        )
        return clip_gradients(dout)
