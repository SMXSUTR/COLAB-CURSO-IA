import tkinter as tk
from tkinter import ttk, scrolledtext

class ChatUI:
    def __init__(self, root, client):
        self.root = root
        self.client = client
        self.root.title("Ollama Chat Client - Tarea Final")
        self.root.geometry("600x750") # Un poco más alto para el botón extra

        # 1. Selector de Modelo (Dropdown)
        tk.Label(root, text="Seleccionar Modelo Ollama:", font=("Arial", 10, "bold")).pack(pady=5)
        self.model_var = tk.StringVar()
        self.model_dropdown = ttk.Combobox(root, textvariable=self.model_var, state="readonly")
        # Los 3 modelos para tu comparativa
        self.model_dropdown['values'] = ("gemma2:2b", "llama3.2:3b", "llama3.1:8b")
        self.model_dropdown.current(0)
        self.model_dropdown.pack(pady=5, fill=tk.X, padx=20)

        # 2. Historial de Chat con Scroll
        self.chat_history = scrolledtext.ScrolledText(root, state='disabled', wrap=tk.WORD, font=("Consolas", 10))
        self.chat_history.pack(padx=20, pady=10, fill=tk.BOTH, expand=True)

        # 3. Campo de entrada de texto y Botón Enviar
        self.input_frame = tk.Frame(root)
        self.input_frame.pack(fill=tk.X, padx=20, pady=10)
        
        self.entry = tk.Entry(self.input_frame, font=("Arial", 11))
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.entry.bind("<Return>", lambda e: self.send())

        self.send_btn = tk.Button(self.input_frame, text="Enviar", command=self.send, bg="#27ae60", fg="white", width=12)
        self.send_btn.pack(side=tk.RIGHT)

        # 4. Botón Limpiar Historial (Ya integrado correctamente)
        self.clear_btn = tk.Button(root, text="Limpiar Historial", command=self.clear_history, bg="#e74c3c", fg="white", width=20)
        self.clear_btn.pack(pady=10)

    def send(self):
        user_text = self.entry.get().strip()
        if not user_text:
            return

        # Mostrar mensaje del usuario
        self.update_history(f"Usted: {user_text}\n")
        self.entry.delete(0, tk.END)
        
        # Obtener modelo seleccionado
        model_selected = self.model_var.get()
        
        # Feedback visual: Bloqueamos botones y cambiamos texto
        self.send_btn.config(state="disabled", text="Pensando...")
        self.clear_btn.config(state="disabled")
        self.root.update_idletasks()

        # Llamada al cliente (con el timeout que ya configuramos en client.py)
        response, duration = self.client.send_message(model_selected, user_text)
        
        # Mostrar respuesta e información técnica
        self.update_history(f"Ollama ({model_selected}): {response}\n")
        self.update_history(f">>> Tiempo de respuesta: {duration}s\n" + "-"*40 + "\n")
        
        # Rehabilitar botones
        self.send_btn.config(state="normal", text="Enviar")
        self.clear_btn.config(state="normal")

    def update_history(self, text):
        self.chat_history.config(state='normal')
        self.chat_history.insert(tk.END, text)
        self.chat_history.config(state='disabled')
        self.chat_history.see(tk.END)

    def clear_history(self):
        # Función para limpiar el historial visualmente
        self.chat_history.config(state='normal')
        self.chat_history.delete(1.0, tk.END)
        self.chat_history.config(state='disabled')