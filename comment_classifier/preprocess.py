import pandas as pd
import os
import numpy as np
from sklearn.utils import class_weight
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
import config
import custom_loss
import pickle
from sklearn.model_selection import train_test_split
from tensorflow.data import Dataset


def load(path: str, filename: str, col_list: list, dtypes) -> pd.DataFrame:
    train = pd.read_csv(os.path.join(path, filename), usecols=col_list, dtype=dtypes)

    return train


def extract_max_length(df: pd.DataFrame, feature_col: str):
    splitted = np.array([len(x) for x in df[feature_col].str.split(" ").values])
    MAX_SEQUENCE_LENGTH = splitted.max()

    return MAX_SEQUENCE_LENGTH


def compute_class_weights(labels: list, df: pd.DataFrame):
    class_weights = []

    for target in df[labels].columns:
        weights = class_weight.compute_class_weight('balanced', np.array([0.0, 1.0]), df[target].values)
        cls = dict(enumerate(weights))
        class_weights.append(cls)

    return class_weights


def tokenize(df: pd.DataFrame, path: str) -> np.array:
    sentences = df["comment_text"].fillna("DUMMY_VALUE").values
    # convert the sentences (strings) into integers
    tokenizer = Tokenizer(num_words=config.MAX_VOCAB_SIZE)
    tokenizer.fit_on_texts(sentences)
    sequences = tokenizer.texts_to_sequences(sentences)
    # get word -> integer mapping
    word2idx = tokenizer.word_index
    # save tokenizer
    with open(os.path.join(path, 'tokenizer.pkl'), 'wb') as f:
        pickle.dump(tokenizer, f)
    print('Found %s unique tokens.' % len(word2idx))

    # pad sequences so that we get a N x T matrix
    data = pad_sequences(sequences, maxlen=config.MAX_SEQUENCE_LENGTH, padding=config.PADDING)
    print('Shape of data tensor:', data.shape)

    return data


def split_train_valid(data, targets):
    X_train, X_valid, y_train, y_valid = train_test_split(data, targets, test_size=0.2, random_state=42)

    return X_train, X_valid, y_train, y_valid


def create_final_datasets(X_train, X_valid, y_train, y_valid):
    train = Dataset.from_tensor_slices((X_train, (y_train.identity_hate.values, y_train.insult.values,
                                                  y_train.obscene.values, y_train.severe_toxic.values,
                                                  y_train.threat.values, y_train.toxic.values))).map(
        custom_loss.preprocess_sample).batch(config.BATCH_SIZE).repeat()

    valid = Dataset.from_tensor_slices((X_valid, (y_valid.identity_hate.values, y_valid.insult.values,
                                                  y_valid.obscene.values, y_valid.severe_toxic.values,
                                                  y_valid.threat.values, y_valid.toxic.values))).map(
        custom_loss.preprocess_sample).batch(config.BATCH_SIZE).repeat()

    return train, valid
