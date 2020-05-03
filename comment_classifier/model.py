import os
from tensorflow.keras.layers import Dense, Input, Embedding, LSTM
from tensorflow.keras.models import Model
import config


def build_model(embedding_layer):
    input_ = Input(shape=(config.MAX_SEQUENCE_LENGTH,))
    embedding_layer = embedding_layer(input_)
    lstm_layer = LSTM(128, dropout=0.2, return_sequences=False)(embedding_layer)

    output = Dense(6, activation='sigmoid')(lstm_layer)

    model = Model(inputs=input_, outputs=output)

    return model


def load_model(filename, custom_objects, path=config.PATH):
    model = load_model(os.path.join(path, 'ckpt', filename),
                       custom_objects=custom_objects)

    return model
