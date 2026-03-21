# ◈ EmotiScan — Detector de Emociones Faciales En CLAUDE

Aplicación de escritorio que analiza emociones en imágenes estáticas usando **DeepFace** e inteligencia artificial. Interfaz oscura estilo HUD/sci-fi construida con Tkinter.

---

## 📋 Requisitos del sistema

| Componente | Versión mínima |
|---|---|
| Python | 3.9 o superior |
| Sistema operativo | Windows 10/11, macOS 12+, Ubuntu 20.04+ |
| RAM | 4 GB (8 GB recomendado) |
| Espacio en disco | ~2 GB (modelos de IA se descargan automáticamente) |

---

## 🚀 Instalación paso a paso

### Paso 1 — Verificar Python

Abre una terminal (cmd / PowerShell / Terminal) y ejecuta:

```bash
python --version
```

Si no tienes Python instalado, descárgalo desde [python.org](https://www.python.org/downloads/).

---

### Paso 2 — Clonar o descargar el proyecto

**Opción A — Con Git:**
```bash
git clone https://github.com/tu-usuario/emotiscan.git
cd emotiscan
```

**Opción B — Sin Git:**
Descarga el ZIP del proyecto, descomprímelo y navega a la carpeta desde la terminal.

---

### Paso 3 — Crear un entorno virtual (recomendado)

```bash
# Crear entorno virtual
python -m venv venv

# Activar en Windows
venv\Scripts\activate

# Activar en macOS / Linux
source venv/bin/activate
```

Verás `(venv)` al inicio de la línea de comandos cuando esté activo.

---

### Paso 4 — Instalar dependencias

```bash
pip install -r requirements.txt
```

> ⚠️ **Nota:** La primera instalación puede tardar varios minutos ya que descarga TensorFlow y otros componentes pesados.

---

### Paso 5 — Ejecutar la aplicación

```bash
python app.py
```

> ⚠️ **Primera ejecución:** DeepFace descargará automáticamente los modelos de IA (~300 MB) al analizar la primera imagen. Esto solo ocurre una vez.

---

## 🖥️ Uso de la aplicación

1. **Cargar foto** — Haz clic en `⊕ CARGAR FOTO` y selecciona una imagen (JPG, PNG, BMP, WEBP).
2. **Analizar** — Haz clic en `◉ ANALIZAR` y espera el procesamiento.
3. **Ver resultados** — La imagen mostrará un rectángulo alrededor del rostro y el panel derecho mostrará:
   - La emoción dominante en español
   - El porcentaje de confianza de cada emoción

---

## 📁 Estructura del proyecto

```
emotiscan/
├── app.py              # Punto de entrada principal
├── analyzer.py         # Lógica de análisis con DeepFace
├── ui_components.py    # Interfaz gráfica con Tkinter
├── requirements.txt    # Dependencias del proyecto
└── README.md           # Este archivo
```

---

## 🎭 Emociones detectadas

| Inglés | Español |
|---|---|
| happy | 😄 Felicidad |
| sad | 😢 Tristeza |
| angry | 😠 Enojo |
| surprise | 😲 Sorpresa |
| fear | 😨 Miedo |
| disgust | 🤢 Asco |
| neutral | 😐 Neutral |

---

## ❗ Solución de problemas comunes

### Error: `No se detectó ningún rostro`
- Asegúrate de que la imagen muestre un rostro **frontal** con buena iluminación.
- Evita imágenes muy oscuras, borrosas o de perfil.

### Error al instalar `opencv-python` en Linux
```bash
sudo apt-get install libgl1-mesa-glx libglib2.0-0
```

### Error `tkinter not found` en Linux
```bash
sudo apt-get install python3-tk
```

### La aplicación es lenta en el primer análisis
Es normal: DeepFace carga el modelo en memoria la primera vez. Los análisis posteriores son más rápidos.

---

## 🏗️ Arquitectura del código

El proyecto sigue principios de **alta cohesión y bajo acoplamiento**:

- **`app.py`** — Solo inicializa y conecta los componentes.
- **`analyzer.py`** — Solo lógica de DeepFace y procesamiento de imágenes. No depende de Tkinter.
- **`ui_components.py`** — Solo presentación visual. Se comunica con el analyzer por interfaz limpia.

---

## 📄 Licencia

MIT License — libre para uso personal y comercial.
