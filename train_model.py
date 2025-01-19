# Connect to Google Drive
from google.colab import drive
drive.mount('/content/drive')

# Import required libraries
from google.colab import files
import os
import tensorflow as tf
assert tf.__version__.startswith('2')

from mediapipe_model_maker import gesture_recognizer

import matplotlib.pyplot as plt

# Set path of dataset
dataset_path = "./drive/MyDrive/dataset"

# Load dataset and extract hand landmarks
data = gesture_recognizer.Dataset.from_folder(
    dirname=dataset_path,
    hparams=gesture_recognizer.HandDataPreprocessingParams()
)
# 80% for trainning, 10% for validation, and 10% for testing
train_data, rest_data = data.split(0.8)
validation_data, test_data = rest_data.split(0.5)

# Set model and train model
hparams = gesture_recognizer.HParams(export_dir = "exported_model", epochs = 20, batch_size = 64)
model_options = gesture_recognizer.ModelOptions(layer_widths = [14, 64, 128])
options = gesture_recognizer.GestureRecognizerOptions(model_options = model_options, hparams = hparams)
model = gesture_recognizer.GestureRecognizer.create(
    train_data=train_data,
    validation_data=validation_data,
    options=options
)

# Test
loss, acc = model.evaluate(test_data, batch_size = 1)
print(f"Test loss:{loss}, Test accuracy:{acc}")

# Export model
model.export_model()

# Download model
files.download('exported_model/gesture_recognizer.task')