import pandas as pd
import os
import numpy as np
from sklearn.utils import class_weight
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
import config


def load(path: str, filename: str, col_list: list) -> pd.DataFrame:
    train = pd.read_csv(os.path.join(path, filename), usecols=col_list)

    return train


def extract_max_length(df: pd.DataFrame, feature_col: str):
    splitted = np.array([len(x) for x in df[feature_col].str.split(" ").values])
    MAX_SEQUENCE_LENGTH = splitted.max()

    return MAX_SEQUENCE_LENGTH


def compute_class_weights(labels: list, df: pd.DataFrame) -> list[dict]:
    class_weights = []

    for target in df[labels].columns:
        weights = class_weight.compute_class_weight('balanced', np.array([0.0, 1.0]), df[target].values)
        cls = dict(enumerate(weights))
        class_weights.append(cls)

    return class_weights


def tokenize(df: pd.DataFrame)-> np.array:
    sentences = df["comment_text"].fillna("DUMMY_VALUE").values
    # convert the sentences (strings) into integers
    tokenizer = Tokenizer(num_words=config.MAX_VOCAB_SIZE)
    tokenizer.fit_on_texts(sentences)
    sequences = tokenizer.texts_to_sequences(sentences)
    # get word -> integer mapping
    word2idx = tokenizer.word_index
    print('Found %s unique tokens.' % len(word2idx))

    # pad sequences so that we get a N x T matrix
    data = pad_sequences(sequences, maxlen=MAX_SEQUENCE_LENGTH)
    print('Shape of data tensor:', data.shape)

    return data
