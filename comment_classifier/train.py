import preprocess
import config
import custom_loss
import word_embeddings
import model
import os
import pickle


def run_training():
    train = preprocess.load(path=config.PATH, filename=config.FILENAME, col_list=[0, 2, 3, 4, 6, 7, 8, 9],
                            dtypes=config.DTYPES)
    targets = train[config.POSSIBLE_LABELS]
    class_weights = custom_loss.calculating_class_weights(targets.values, 6)
    with open(os.path.join(config.PATH, "class_weights.pkl"), "wb") as f:
        pickle.dump(class_weights, f)

    # extract and load pretrained wordembeddings
    word2vec = word_embeddings.load_pretr_wv()
    # tokenize and pad sequences
    data = preprocess.tokenize(train, config.PATH)
    # apply embeddings to layer weights
    embedding_layer = word_embeddings.apply_embeddings(word2vec)
    # build model
    m = model.build_model(embedding_layer)
    # apply class weights via custom loss
    m.compile(loss=custom_loss.get_weighted_loss(class_weights), optimizer='adam', metrics=['accuracy'])

    X_train, X_valid, y_train, y_valid = preprocess.split_train_valid(data, train[config.POSSIBLE_LABELS])


    # fitting the model
    print('Training model...')
    r = m.fit(
        X_train, y_train, epochs=config.EPOCHS,  batch_size=config.BATCH_SIZE,
        validation_data=(X_valid, y_valid), verbose=2,
        callbacks=[config.callback_checkpoint, config.callback_earlystop]
    )

if __name__ == "__main__":
    run_training()
