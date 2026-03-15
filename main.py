import tkinter as tk
from src.model_logic import IrisPredictor
from src.interface import IrisApp

if __name__ == "__main__":
    root = tk.Tk()
    predictor = IrisPredictor() 
    app = IrisApp(root, predictor)
    root.mainloop()