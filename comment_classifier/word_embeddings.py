import os
import numpy as np
import config
import pickle
from tensorflow.keras.layers import Embedding


def load_pretr_wv(path, filename):
    # load in pre-trained word vectors
    print('Loading word vectors...')
    word2vec = {}
    with open(os.path.join(path, '/glove.6B.%sd.txt' % config.EMBEDDING_DIM), encoding="utf8") as f:
        # is just a space-separated text file in the format:
        # word vec[0] vec[1] vec[2] ...
        for line in f:
            values = line.split()
            word = values[0]
            vec = np.asarray(values[1:], dtype='float32')
            word2vec[word] = vec
    print('Found %s word vectors.' % len(word2vec))

    return word2vec


def apply_embeddings(path, word2idx_file, word2vec):
    with open(os.path.join(path, word2idx_file), 'rb') as f:
        word2idx = pickle.load(f)
    # prepare embedding matrix
    print('Filling pre-trained embeddings...')
    num_words = min(config.MAX_VOCAB_SIZE, len(word2idx) + 1)
    embedding_matrix = np.zeros((num_words, config.EMBEDDING_DIM))
    for word, i in word2idx.items():
        if i < config.MAX_VOCAB_SIZE:
            embedding_vector = word2vec.get(word)
            if embedding_vector is not None:
                # words not found in embedding index will be all zeros.
                embedding_matrix[i] = embedding_vector

    embedding_layer = Embedding(
        num_words,
        config.EMBEDDING_DIM,
        weights=[embedding_matrix],
        input_length=config.MAX_SEQUENCE_LENGTH,
        trainable=False
    )

    return embedding_layer
