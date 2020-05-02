import tensorflow.keras.backend as K
from tensorflow.data import Dataset
from itertools import product
from functools import partial
from sklearn.utils import class_weight
import pandas as pd
import numpy as np
import config
import tensorflow as tf


def weights_for_loss(train: pd.DataFrame):
    # class_weights_aggr = []
    weights_loss = []
    for target in config.POSSIBLE_LABELS:
        weight = class_weight.compute_class_weight('balanced', np.array([0.0, 1.0]), train[target].values)
        weight_unit = weight / weight[0]
        w = np.ones((2, 2))
        w[1, 0] = weight_unit[1]
        w[1, 1] = weight_unit[1]
        # class_weights = dict(enumerate(weight_unit))
        # class_weights_aggr.append(class_weights)
        weights_loss.append(w)

    return weights_loss


def weighted_categorical_crossentropy(y_true, y_pred, weights):
    nb_cl = len(weights)
    final_mask = K.zeros_like(y_pred[:, 0])
    y_pred_max = K.max(y_pred, axis=1)
    y_pred_max = K.reshape(y_pred_max, (K.shape(y_pred)[0], 1))
    y_pred_max_mat = K.cast(K.equal(y_pred, y_pred_max), K.floatx())
    for c_p, c_t in product(range(nb_cl), range(nb_cl)):
        final_mask += (weights[c_t, c_p] * y_pred_max_mat[:, c_p] * y_true[:, c_t])
    return K.categorical_crossentropy(y_pred, y_true) * final_mask


def create_losses(weights_loss):
    losses = {}
    i = 0
    for label in config.POSSIBLE_LABELS:
        losses[label] = partial(weighted_categorical_crossentropy, weights=weights_loss[i])
        losses[label].__name__ = 'loss' + '_' + label
        i += 1

    return losses


def preprocess_sample(features, labels):
    label1, label2, label3, label4, label5, label6 = labels
    label1 = tf.one_hot(label1, 2)
    label2 = tf.one_hot(label2, 2)
    label3 = tf.one_hot(label3, 2)
    label4 = tf.one_hot(label4, 2)
    label5 = tf.one_hot(label5, 2)
    label6 = tf.one_hot(label6, 2)

    return features, (label1, label2, label3, label4, label5, label6)
