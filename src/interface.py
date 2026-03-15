import tkinter as tk
from tkinter import messagebox

class IrisApp:
    def __init__(self, root, predictor):
        self.root = root
        self.predictor = predictor
        self.root.title("App Profesional Iris")

        tk.Label(root, text="Ingrese Medidas", font=("Arial", 12)).pack(pady=10)
        self.entries = []
        for label in ["Largo Sépalo", "Ancho Sépalo", "Largo Pétalo", "Ancho Pétalo"]:
            tk.Label(root, text=label).pack()
            e = tk.Entry(root)
            e.pack(pady=2)
            self.entries.append(e)

        tk.Button(root, text="Predecir", command=self.do_prediction, bg="green", fg="white").pack(pady=20)

    def do_prediction(self):
        try:
            vals = [float(e.get()) for e in self.entries]
            res = self.predictor.predict(vals)
            messagebox.showinfo("IA", f"Resultado: {res}")
        except:
            messagebox.showerror("Error", "Use números (ej: 5.1)")