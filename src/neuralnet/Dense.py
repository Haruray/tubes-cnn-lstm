import numpy as np
from neuralnet.Layer import Layer
from neuralnet.Activation import *
from neuralnet.clip_gradients import clip_gradients


class Dense(Layer):
    def __init__(self, num_units: int, input_len: int, detector_function: str):
        super().__init__()

        self.type = "dense"
        self.num_units = num_units
        self.feature_map_shape = num_units

        # detector function
        if detector_function == "relu":
            self.detector_function = Relu()
        elif detector_function == "softmax":
            self.detector_function = Softmax()
        elif detector_function == "sigmoid":
            self.detector_function = Sigmoid()
        else:
            raise Exception("Activation function not recognized.")

        # weight
        self.weights = np.random.randn(self.num_units, input_len)

        # bias
        self.biases = np.zeros(num_units)

    def __iter__(self):
        yield from {
            "type": self.type,
            "num_units": self.num_units,
            "detector_function": self.detector_function,
            "weights": self.weights.tolist(),
            "biases": self.biases.tolist(),
        }.items()

    def __str__(self):
        return json.dumps(dict(self), cls=MyEncoder, ensure_ascii=False)

    def __repr__(self):
        return self.__str__()

    def forward_propagate(self, input: np.ndarray):
        input = input.flatten()  # flatten input
        output = np.dot(input, self.weights.T) + self.biases  # forward propagate
        output = self.detector_function.calculate(output)  # activation
        self.last_input = input
        return output

    def calculate_feature_map_shape(self, input: tuple):
        return self.feature_map_shape

    def backpropagate(self, out: np.ndarray, learn_rate: float):
        """
        weight = weight - learning_rate * dE/dNet * dNet/dW
        dE/dNet adalah out
        cari dNet/dW
        net = input dari layer sebelumnya * current Weight + bias
        dNet/dW berarti input dari layer sebelumnya
        """

        dout = out.T * self.last_input  # dNet/dW * dE/dNet
        dout_bias = np.sum(out.T, axis=1).reshape(self.biases.shape)
        self.weights -= learn_rate * clip_gradients(dout)
        self.biases -= learn_rate * clip_gradients(dout_bias)
        return dout
