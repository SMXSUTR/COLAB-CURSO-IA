# Ollama Chat Client - Cliente de Chat para Modelos LLM

Este proyecto es una aplicación de escritorio desarrollada en **Python** utilizando **Tkinter** para interactuar con modelos de lenguaje locales a través de la API de **Ollama**. La arquitectura del sistema sigue principios de **limpieza de código**, **baja dependencia** y **alta cohesión**.

## 🚀 Características
* **Arquitectura Modular:** Separación clara entre la lógica de comunicación (`client.py`) y la interfaz de usuario (`ui.py`).
* **Medición de Rendimiento:** Calcula y muestra el tiempo de respuesta de cada modelo en segundos.
* **Selector Dinámico:** Permite alternar entre los modelos `gemma2:2b`, `llama3.2:3b` y `llama3.1:8b`.
* **Gestión de Historial:** Incluye funciones para visualizar el historial con scroll y un botón para limpiar la conversación.

## 📁 Estructura del Proyecto
```text
samuel_2/
├── main.py              # Punto de entrada de la aplicación
├── app/                 # Módulo principal
│   ├── __init__.py      # Identificador de paquete Python
│   ├── client.py        # Lógica de conexión con la API de Ollama
│   └── ui.py            # Definición de la interfaz gráfica (Tkinter)
└── README.md            # Documentación