import os
import pickle
import comment_classifier.preprocess as preprocess
from comment_classifier.preprocess import Tokenize_Object
import comment_classifier.config as config
import comment_classifier.custom_loss as custom_loss
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from comment_classifier.model import load_model
import numpy as np
import pandas as pd


class Predictor:

    def __init__(self, model, data: pd.DataFrame):
        self.model = model
        self.data = data

    def run_pred(self, path=config.PATH):
        preds = self.model.predict(self.data)
        with open(os.path.join(path, "preds.pkl"), "wb") as f:
            pickle.dump(preds, f)

        predictions = np.where(preds < 0.5, 0, 1)

        return predictions

    @staticmethod
    def build_pred_df(test: pd.DataFrame, predictions: np.array) -> pd.DataFrame:
        test_pred = pd.concat([test, pd.DataFrame(predictions, columns=config.POSSIBLE_LABELS)], axis=1)

        return test_pred

    @staticmethod
    def save_to_file(test_pred: pd.DataFrame, filename, path=config.PATH):
        test_pred.to_csv(os.path.join(path, filename))

        print("file was saved in %sd" % filename)


def run_prediction():
    test = preprocess.load(path=config.PATH, filename="test_preprocessed.csv", col_list=[0])

    # tokenize the texts
    tokenizer = Tokenize_Object.load_tokenizer(config.PATH)
    data = Tokenize_Object.tokenize_testdata(test, tokenizer)
    # load model and custom losses
    with open(os.path.join(config.PATH, "class_weights.pkl"), "rb") as f:
        class_weights = pickle.load(f)
    model = load_model(filename=config.SAVED_MODEL,
                       custom_objects={"weighted_loss": custom_loss.get_weighted_loss(class_weights)})
    predictor = Predictor(model, test)
    predictions = predictor.run_pred()
    test_pred = predictor.build_pred_df(test, predictions)
    Predictor.save_to_file(test_pred, "test_predictions.csv")

    return test_pred


if __name__ == "__main__":
    test_pred = run_prediction()
