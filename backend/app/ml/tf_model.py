"""Optional lightweight TensorFlow (CPU) model. Imported lazily only if USE_TENSORFLOW=true."""
import numpy as np


def train(X, y, path):
    import tensorflow as tf
    tf.get_logger().setLevel("ERROR")
    model = tf.keras.Sequential([
        tf.keras.layers.Input(shape=(X.shape[1],)),
        tf.keras.layers.Dense(16, activation="relu"),
        tf.keras.layers.Dense(8, activation="relu"),
        tf.keras.layers.Dense(1, activation="sigmoid"),
    ])
    model.compile(optimizer="adam", loss="binary_crossentropy", metrics=["accuracy"])
    model.fit(X, y, epochs=30, batch_size=32, verbose=0, validation_split=0.2)
    model.save(path)
    return model


def load(path):
    import tensorflow as tf
    return tf.keras.models.load_model(path)


def predict(model, x):
    return float(model.predict(np.array([x], dtype="float32"), verbose=0)[0][0])
