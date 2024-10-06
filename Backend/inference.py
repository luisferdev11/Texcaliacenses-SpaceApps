import os
import numpy as np
import cv2
import tensorflow as tf
from tensorflow.keras.models import load_model

# Definir las etiquetas de las clases en el orden correcto
CLASS_LABELS = ['Blight', 'Common_Rust', 'Gray_Leaf_Spot', 'Healthy']

# Ruta al modelo entrenado
MODEL_PATH = os.path.join('models', 'Corn_efficientnet_modelBueno.h5')

# Cargar el modelo al iniciar el módulo
if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError(f"No se encontró el modelo en la ruta especificada: {MODEL_PATH}")

MODEL = load_model(MODEL_PATH)

# Función de mejora de imagen
def enhance_image(image):
    image = cv2.addWeighted(image, 1.5, image, -0.5, 0)
    kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
    image = cv2.filter2D(image, -1, kernel)
    
    # Ajuste de HSV
    hsv = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
    hue, saturation, value = cv2.split(hsv)
    value = np.clip(value * 1.25, 0, 255).astype(np.uint8)
    hsv = cv2.merge([hue, saturation, value])
    image = cv2.cvtColor(hsv, cv2.COLOR_HSV2RGB)
    
    return image

# Función para realizar la inferencia
def predict_image(image_path):
    # Verifica si el archivo existe
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"El archivo {image_path} no existe.")
    
    # Carga la imagen utilizando OpenCV
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError(f"No se pudo cargar la imagen {image_path}.")
    
    # Convierte la imagen de BGR a RGB
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
    # Redimensiona la imagen a 256x256
    image_resized = cv2.resize(image_rgb, (256, 256))
    
    # Aplica la función de mejora de imagen
    image_enhanced = enhance_image(image_resized)
    
    # Normaliza la imagen
    image_normalized = image_enhanced / 255.0
    
    # Expande las dimensiones para que sea compatible con el modelo
    image_batch = np.expand_dims(image_normalized, axis=0)
    
    # Realiza la predicción
    predictions = MODEL.predict(image_batch)
    
    # Obtiene el índice de la clase con mayor probabilidad
    predicted_index = np.argmax(predictions, axis=1)[0]
    
    # Obtiene la confianza de la predicción
    confidence = float(predictions[0][predicted_index])
    
    # Obtiene la etiqueta de la clase
    predicted_label = CLASS_LABELS[predicted_index]
    
    return predicted_label, confidence