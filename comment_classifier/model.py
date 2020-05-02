from tensorflow.keras.layers import Dense, Input, Embedding, LSTM
from tensorflow.keras.models import Model
import config


def build_model(embedding_layer):
    input_ = Input(shape=(config.MAX_SEQUENCE_LENGTH,))
    embedding_layer = embedding_layer(input_)
    lstm_layer = LSTM(128, dropout=0.2, return_sequences=False)(embedding_layer)

    identity_hate = Dense(2, activation='softmax', name="identity_hate")(lstm_layer)
    insult = Dense(2, activation='softmax', name="insult")(lstm_layer)
    obscene = Dense(2, activation='softmax', name="obscene")(lstm_layer)
    severe_toxic = Dense(2, activation='softmax', name="severe_toxic")(lstm_layer)
    threat = Dense(2, activation='softmax', name="threat")(lstm_layer)
    toxic = Dense(2, activation='softmax', name="toxic")(lstm_layer)

    model = Model(inputs=input_, outputs=[identity_hate, insult, obscene, severe_toxic, threat, toxic])

    return model