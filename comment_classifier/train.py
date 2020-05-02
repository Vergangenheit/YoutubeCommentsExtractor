import preprocess
import config
import custom_loss
import word_embeddings
import model
from tensorflow.data import Dataset


def run_training():
    train = preprocess.load(path=config.PATH, filename=config.FILENAME, col_list=[0, 2, 3, 4, 6, 7, 8, 9],
                            dtypes=config.DTYPES)

    weights_loss = custom_loss.weights_for_loss(train)
    losses = custom_loss.create_losses(weights_loss)
    # extract and load pretrained wordembeddings
    word2vec = word_embeddings.load_pretr_wv()
    # tokenize and pad sequences
    data = preprocess.tokenize(train, config.PATH)
    # apply embeddings to layer weights
    embedding_layer = word_embeddings.apply_embeddings(word2vec)
    # build model
    m = model.build_model(embedding_layer)
    # apply class weights via custom loss
    m.compile(loss=losses, optimizer='adam', metrics=['accuracy'])

    X_train, X_valid, y_train, y_valid = preprocess.split_train_valid(data, train[config.POSSIBLE_LABELS])

    train, valid = preprocess.create_final_datasets(X_train, X_valid, y_train, y_valid)

    # fitting the model
    print('Training model...')
    r = m.fit(
        train, epochs=config.EPOCHS, steps_per_epoch=X_train.shape[0] // config.BATCH_SIZE,
        validation_data=valid, validation_steps=1, verbose=2,
        callbacks=[config.callback_checkpoint, config.callback_earlystop]
    )

if __name__ == "__main__":
    run_training()
