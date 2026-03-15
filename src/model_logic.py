import tensorflow as tf
import numpy as np

class IrisPredictor:
    def __init__(self, model_path='modelo_iris.h5'):
        self.model = tf.keras.models.load_model(model_path)
        self.species = ['Setosa', 'Versicolor', 'Virginica']
        
        # Valores de referencia para normalizar (promedios del dataset Iris)
        # Esto asegura que la IA reciba los datos como espera
        self.mean = np.array([5.84, 3.05, 3.76, 1.20])
        self.std = np.array([0.83, 0.43, 1.76, 0.76])

    def predict(self, features):
        # 1. Convertir a array
        data = np.array([features], dtype=float)
        
        # 2. ESCALAR los datos (La pieza que faltaba)
        data_scaled = (data - self.mean) / self.std
        
        # 3. Predecir
        prediction = self.model.predict(data_scaled, verbose=0)
        return self.species[np.argmax(prediction)]