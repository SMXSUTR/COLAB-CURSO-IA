import requests
import time

class OllamaClient:
    def __init__(self, url="http://localhost:11434/api/generate"):
        self.url = url
        # Creamos una sesión para que las peticiones sean más estables
        self.session = requests.Session()

    def send_message(self, model, prompt):
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False
        }
        
        start_time = time.time()
        
        try:
            # Usamos la sesión con un timeout de 300
            response = self.session.post(self.url, json=payload, timeout=300)
            response.raise_for_status()
            
            end_time = time.time()
            duration = round(end_time - start_time, 2)
            
            result = response.json()
            return result.get("response", "Sin respuesta."), duration
            
        except requests.exceptions.Timeout:
            return "⚠️ Error: El modelo tardó demasiado. Puedes intentar de nuevo o cambiar de modelo.", 0
        except Exception as e:
            # Si hay un error, reiniciamos la sesión para la próxima pregunta
            self.session = requests.Session()
            return f"⚠️ Error de conexión: {str(e)}. Intenta enviar el mensaje de nuevo.", 0