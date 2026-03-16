import tkinter as tk
from app.client import OllamaClient
from app.ui import ChatUI

def main():
    # 1. Crear la raíz de la interfaz de usuario (Tkinter)
    root = tk.Tk()
    
    # 2. Instanciar el cliente de Ollama (La lógica)
    # Baja dependencia: la interfaz no sabe cómo funciona la API, solo usa este cliente
    client = OllamaClient()
    
    # 3. Instanciar la interfaz pasando el cliente (Alta cohesión)
    app = ChatUI(root, client)
    
    # 4. Iniciar el bucle principal de la aplicación
    root.mainloop()

if __name__ == "__main__":
    main()