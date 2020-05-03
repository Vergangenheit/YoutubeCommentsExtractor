import numpy as np
import os
from tensorflow.keras.callbacks import ModelCheckpoint, EarlyStopping

MAX_VOCAB_SIZE = 20000
EMBEDDING_DIM = 100
VALIDATION_SPLIT = 0.2
BATCH_SIZE = 128
EPOCHS = 10
MAX_SEQUENCE_LENGTH = 300
PADDING = "post"
POSSIBLE_LABELS = ["identity_hate", "insult", "obscene", "severe_toxic", "threat", "toxic"]
PATH = "drive/My Drive/ToxicCommentsDataset"
FILENAME = "train_preprocessed.csv"
LOSSES_FILE = "losses.pkl"
DTYPES = dict(zip(POSSIBLE_LABELS, [np.int32]*len(POSSIBLE_LABELS)))

callback_checkpoint = ModelCheckpoint(os.path.join(path, 'ckpt', "toxic_comments_lstm-epoch{epoch:03d}-loss{loss:.4f}-val_acc{val_accuracy:.4f}.hdf5"),
                                      monitor='loss', verbose=2, save_best_only=True, mode='min', period=2)

callback_earlystop = EarlyStopping(monitor='loss', patience=10, mode='min', verbose=1)