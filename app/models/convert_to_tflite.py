import tensorflow as tf

# Load your Keras model
model = tf.keras.models.load_model('food_classifier_ft.h5')

# Convert to TFLite
converter = tf.lite.TFLiteConverter.from_keras_model(model)
tflite_model = converter.convert()

# Save the TFLite model
with open('food_classifier_ft.tflite', 'wb') as f:
    f.write(tflite_model)