import tensorflow.keras.backend as K
from tensorflow.data import Dataset
from itertools import product
from functools import partial
from sklearn.utils import class_weight
import pandas as pd
import numpy as np
import config
import tensorflow as tf


def calculating_class_weights(y_true, number_dim):
    number_dim = np.shape(y_true)[1]
    weights = np.empty([number_dim, 2])
    for i in range(number_dim):
        weights[i] = class_weight.compute_class_weight('balanced', [0., 1.], y_true[:, i])
    return weights


def get_weighted_loss(weights):
    def weighted_loss(y_true, y_pred):
        return K.mean(
            (weights[:, 0] ** (1 - y_true)) * (weights[:, 1] ** (y_true)) * K.binary_crossentropy(y_true, y_pred),
            axis=-1)

    return weighted_loss
