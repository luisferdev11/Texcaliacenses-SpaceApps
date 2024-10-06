import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os
import cv2
from sklearn.model_selection import train_test_split
import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications import EfficientNetB0
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Dense, BatchNormalization, Dropout
from tensorflow.keras.optimizers import Adamax
from sklearn.metrics import confusion_matrix
import seaborn as sns
import json

# ---- 1. Data Preparation ----

# Define paths for each class relative to the current working directory
base_path = 'Data'
Blight = [os.path.join(base_path, 'Blight')]
Common_Rust = [os.path.join(base_path, 'Common_Rust')]
Gray_Leaf_Spot = [os.path.join(base_path, 'Gray_Leaf_Spot')]
Healthy = [os.path.join(base_path, 'Healthy')]
dict_lists = [Blight, Common_Rust, Gray_Leaf_Spot, Healthy]
class_labels = ['Blight', 'Common_Rust', 'Gray_Leaf_Spot', 'Healthy']

file_p = []
labels = []

# Collect file paths and labels
for i, dir_list in enumerate(dict_lists):
    for j in dir_list:
        list_f = os.listdir(j)
        for name in list_f:
            fpath = os.path.join(j, name)
            file_p.append(fpath)
            labels.append(class_labels[i])

# Create DataFrame
failpath = pd.Series(file_p, name="filepaths")
Labelss = pd.Series(labels, name="labels")
data = pd.concat([failpath, Labelss], axis=1)
df = pd.DataFrame(data)

# Split data into train, test, and validation sets
train_df, test_df = train_test_split(df, test_size=0.25, random_state=42, stratify=df.labels)
train_df, val_df = train_test_split(train_df, test_size=0.15, random_state=42, stratify=train_df.labels)

# ---- 2. Image Data Generators ----

# Enhance image function
def enhance_image(image):
    image = cv2.addWeighted(image, 1.5, image, -0.5, 0)
    kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
    image = cv2.filter2D(image, -1, kernel)
    
    # HSV adjustment
    hue = image[:, :, 0]
    saturation = image[:, :, 1]
    value = image[:, :, 2]
    value = np.clip(value * 1.25, 0, 255)
    
    image[:, :, 2] = value
    return image

# ImageDataGenerator for data augmentation and preprocessing
image_gen = ImageDataGenerator(
    rescale=1./255,
    preprocessing_function=lambda image: enhance_image(image)
)

# Creating train, validation, and test generators
train = image_gen.flow_from_dataframe(
    dataframe=train_df, x_col="filepaths", y_col="labels",
    target_size=(256, 256), color_mode='rgb',
    class_mode="categorical", batch_size=32, shuffle=False
)

val = image_gen.flow_from_dataframe(
    dataframe=val_df, x_col="filepaths", y_col="labels",
    target_size=(256, 256), color_mode='rgb',
    class_mode="categorical", batch_size=32, shuffle=False
)

test = image_gen.flow_from_dataframe(
    dataframe=test_df, x_col="filepaths", y_col="labels",
    target_size=(256, 256), color_mode='rgb',
    class_mode="categorical", batch_size=32, shuffle=False
)

# ---- 3. Model Creation ----

# Load pre-trained EfficientNetB0 model without the top layers
base_model = EfficientNetB0(weights='imagenet', include_top=False, input_shape=(256, 256, 3), pooling='max')

# Add custom layers
x = base_model.output
x = BatchNormalization(axis=-1, momentum=0.99, epsilon=0.001)(x)
x = Dense(64, activation='relu')(x)
x = Dropout(0.4)(x)
predictions = Dense(4, activation='softmax')(x)

# Create model
model = Model(inputs=base_model.input, outputs=predictions)

# Compile model
optimizer = Adamax(learning_rate=0.001)
model.compile(optimizer=optimizer, loss='categorical_crossentropy', metrics=['accuracy'])

# ---- 4. Model Training ----

history = model.fit(train, epochs=20, validation_data=val)

# ---- 5. Model Evaluation ----

# Evaluate model on test set
loss, accuracy = model.evaluate(test)
print("Test Loss:", loss)
print("Test Accuracy:", accuracy)

# ---- 6. Visualization of Training ----

# Plot accuracy
plt.plot(history.history['accuracy'], label='Training Accuracy')
plt.plot(history.history['val_accuracy'], label='Validation Accuracy')
plt.xlabel('Epoch')
plt.ylabel('Accuracy')
plt.title('Training and Validation Accuracy')
plt.legend()
plt.show()

# Plot loss
plt.plot(history.history['loss'], label='Training Loss')
plt.plot(history.history['val_loss'], label='Validation Loss')
plt.xlabel('Epoch')
plt.ylabel('Loss')
plt.title('Training and Validation Loss')
plt.legend()
plt.show()

# ---- 7. Confusion Matrix ----

# Get predictions for the test data
y_pred = model.predict(test)
y_pred_classes = np.argmax(y_pred, axis=1)

# Get true labels for the test data
true_classes = test.classes

# Compute confusion matrix
conf_matrix = confusion_matrix(true_classes, y_pred_classes)

# Plot confusion matrix
plt.figure(figsize=(8, 8))
sns.heatmap(conf_matrix, annot=True, fmt='d', cmap='Blues', square=True, 
            xticklabels=test.class_indices.keys(), yticklabels=test.class_indices.keys())
plt.xlabel('Predicted')
plt.ylabel('Actual')
plt.title('Confusion Matrix')
plt.show()

# ---- 8. Save the Model ----


model.save("Corn_efficientnet_model.h5")

# Print Keras and TensorFlow versions
print(f"Keras version: {tf.keras.__version__}")
print(f"TensorFlow version: {tf.__version__}")
