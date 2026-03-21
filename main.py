"""
EmotiScan - Detector de Emociones Faciales
==========================================
Aplicación de escritorio con Tkinter + DeepFace para análisis
de emociones en imágenes estáticas.

Todo el código en un solo archivo: lógica de análisis, UI y punto de entrada.
Ejecutar: python main.py
"""

import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk, ImageDraw
import threading
import numpy as np
from deepface import DeepFace


# ══════════════════════════════════════════════════════════════════════════════
#  SECCIÓN 1 — CONSTANTES Y DATOS
# ══════════════════════════════════════════════════════════════════════════════

# Traducción de etiquetas de emociones (inglés → español)
EMOCIONES_ES = {
    "angry":    "Enojo",
    "disgust":  "Asco",
    "fear":     "Miedo",
    "happy":    "Felicidad",
    "sad":      "Tristeza",
    "surprise": "Sorpresa",
    "neutral":  "Neutral",
}

# Emoji representativo por emoción
EMOCIONES_EMOJI = {
    "angry":    "😠",
    "disgust":  "🤢",
    "fear":     "😨",
    "happy":    "😄",
    "sad":      "😢",
    "surprise": "😲",
    "neutral":  "😐",
}

# Paleta de colores de la interfaz (estética dark sci-fi / HUD)
COLORES = {
    "bg_dark":      "#0A0E1A",   # fondo principal (casi negro azulado)
    "bg_panel":     "#111827",   # paneles secundarios
    "bg_card":      "#1A2235",   # tarjetas / zona de imagen
    "accent":       "#00D4FF",   # cyan neon (acento principal)
    "accent2":      "#7C3AED",   # violeta (acento secundario)
    "text_primary": "#E2E8F0",   # texto principal
    "text_muted":   "#64748B",   # texto secundario
    "success":      "#00E676",   # verde éxito
    "border":       "#1E3A5F",   # bordes sutiles
    "bar_bg":       "#1E293B",   # fondo de barras de progreso
}

# Definición de fuentes
FUENTE_TITULO    = ("Courier New", 22, "bold")
FUENTE_SUBTITULO = ("Courier New", 11)
FUENTE_LABEL     = ("Courier New", 10, "bold")
FUENTE_VALOR     = ("Courier New", 10)
FUENTE_BOTON     = ("Courier New", 11, "bold")
FUENTE_EMOCION   = ("Courier New", 28, "bold")

# Colores del bounding box según emoción detectada
COLORES_BBOX = {
    "happy":    "#00E676",   # verde brillante
    "sad":      "#42A5F5",   # azul
    "angry":    "#EF5350",   # rojo
    "surprise": "#FFCA28",   # amarillo
    "fear":     "#AB47BC",   # púrpura
    "disgust":  "#FF7043",   # naranja
    "neutral":  "#78909C",   # gris azulado
}

# Colores de las barras de porcentaje (una por emoción, en orden)
COLORES_BARRAS = [
    "#00D4FF", "#7C3AED", "#00E676", "#FFCA28",
    "#EF5350", "#FF7043", "#78909C",
]


# ══════════════════════════════════════════════════════════════════════════════
#  SECCIÓN 2 — LÓGICA DE ANÁLISIS (EmotionAnalyzer)
# ══════════════════════════════════════════════════════════════════════════════

class EmotionAnalyzer:
    """
    Responsable de:
    - Analizar emociones faciales con DeepFace.
    - Dibujar el bounding box sobre la imagen.
    - Traducir los resultados al español.

    No depende de Tkinter; puede reutilizarse de forma independiente.
    """

    def analyze(self, image_path: str) -> dict:
        """
        Analiza las emociones del rostro en la imagen indicada.

        Args:
            image_path: Ruta al archivo de imagen (JPG, PNG, BMP, etc.).

        Returns:
            dict con:
                - 'imagen_anotada'   : PIL.Image con el bounding box dibujado.
                - 'emocion_dominante': str con la emoción principal en español.
                - 'emocion_key'      : str clave en inglés (para seleccionar emoji/color).
                - 'porcentajes'      : dict {nombre_es: float} ordenado de mayor a menor.

        Raises:
            ValueError : Si no se detecta ningún rostro en la imagen.
            Exception  : Para cualquier otro error inesperado de DeepFace.
        """
        # 1. Abrir imagen con PIL para preservar colores originales
        pil_img = Image.open(image_path).convert("RGB")

        # 2. Convertir a array NumPy (DeepFace acepta RGB o BGR)
        img_array = np.array(pil_img)

        # 3. Ejecutar el análisis con DeepFace
        try:
            resultados = DeepFace.analyze(
                img_path=img_array,
                actions=["emotion"],
                enforce_detection=True,    # Lanza ValueError si no hay rostro
                detector_backend="opencv", # Detector rápido y estable
            )
        except ValueError as e:
            raise ValueError(
                "No se detectó ningún rostro en la imagen.\n"
                "Asegúrate de que la foto muestre un rostro frontal con buena iluminación."
            ) from e

        # DeepFace puede devolver lista o dict según la versión; normalizamos
        if isinstance(resultados, dict):
            resultados = [resultados]

        # Tomamos el primer rostro detectado
        resultado     = resultados[0]
        emociones_raw = resultado["emotion"]          # {str: float}  inglés
        emocion_key   = resultado["dominant_emotion"] # str en inglés
        region        = resultado["region"]           # {x, y, w, h}

        # 4. Dibujar bounding box sobre una copia de la imagen original
        imagen_anotada = self._dibujar_bounding_box(pil_img.copy(), region, emocion_key)

        # 5. Traducir y ordenar porcentajes de mayor a menor
        porcentajes_es = {
            EMOCIONES_ES.get(k, k): round(v, 1)
            for k, v in sorted(emociones_raw.items(), key=lambda x: -x[1])
        }

        return {
            "imagen_anotada":    imagen_anotada,
            "emocion_dominante": EMOCIONES_ES.get(emocion_key, emocion_key),
            "emocion_key":       emocion_key,
            "porcentajes":       porcentajes_es,
        }

    def _dibujar_bounding_box(
        self,
        imagen: Image.Image,
        region: dict,
        emocion_key: str,
    ) -> Image.Image:
        """
        Dibuja un rectángulo HUD alrededor del rostro detectado.

        Incluye esquinas decorativas y una etiqueta con la emoción en español.

        Args:
            imagen     : Imagen PIL sobre la que se dibujará.
            region     : Diccionario con x, y, w, h del rostro.
            emocion_key: Clave de la emoción dominante en inglés.

        Returns:
            PIL.Image con el bounding box dibujado.
        """
        color  = COLORES_BBOX.get(emocion_key, "#FFFFFF")
        draw   = ImageDraw.Draw(imagen)
        x, y, w, h = region["x"], region["y"], region["w"], region["h"]

        # Grosor de líneas proporcional al tamaño de la imagen
        grosor = max(3, min(imagen.width, imagen.height) // 120)

        # Rectángulo principal (bounding box)
        draw.rectangle([x, y, x + w, y + h], outline=color, width=grosor)

        # Esquinas decorativas estilo HUD
        tam_esquina = max(12, w // 6)
        for cx, cy, dx, dy in [
            (x,     y,     1,  1),   # Superior izquierda
            (x + w, y,    -1,  1),   # Superior derecha
            (x,     y + h, 1, -1),   # Inferior izquierda
            (x + w, y + h,-1, -1),   # Inferior derecha
        ]:
            draw.line([(cx, cy), (cx + dx * tam_esquina, cy)], fill=color, width=grosor + 2)
            draw.line([(cx, cy), (cx, cy + dy * tam_esquina)], fill=color, width=grosor + 2)

        # Etiqueta con emoji y nombre de la emoción
        emoji   = EMOCIONES_EMOJI.get(emocion_key, "")
        label   = f"{emoji} {EMOCIONES_ES.get(emocion_key, emocion_key)}"
        label_y = max(0, y - 28)
        draw.rectangle([x, label_y, x + w, label_y + 26], fill=color)
        draw.text((x + 6, label_y + 4), label, fill="#000000")

        return imagen


# ══════════════════════════════════════════════════════════════════════════════
#  SECCIÓN 3 — INTERFAZ GRÁFICA (EmotiScanUI)
# ══════════════════════════════════════════════════════════════════════════════

class EmotiScanUI:
    """
    Interfaz gráfica de EmotiScan.

    Gestiona el layout, los eventos de usuario y la actualización de resultados.
    Solo se ocupa de la presentación; delega el análisis a EmotionAnalyzer.
    """

    def __init__(self, root: tk.Tk, analyzer: EmotionAnalyzer):
        self.root      = root
        self.analyzer  = analyzer
        self.imagen_path: str | None = None
        self.imagen_tk  = None   # Referencia para evitar garbage collection en Tkinter

        self._configurar_ventana()
        self._construir_ui()

    # ── Configuración de la ventana ───────────────────────────────────────────

    def _configurar_ventana(self):
        """Aplica el tema oscuro a la ventana raíz."""
        self.root.configure(bg=COLORES["bg_dark"])

    # ── Construcción del layout ───────────────────────────────────────────────

    def _construir_ui(self):
        """Punto de entrada que construye toda la interfaz."""
        self._construir_header()
        self._construir_contenido_principal()
        self._construir_footer()

    def _construir_header(self):
        """Encabezado con línea decorativa, logo y título."""
        header = tk.Frame(self.root, bg=COLORES["bg_dark"], pady=16)
        header.pack(fill="x", padx=30)

        # Línea cyan decorativa en la parte superior
        tk.Frame(header, bg=COLORES["accent"], height=2).pack(fill="x", pady=(0, 14))

        # Contenedor del título
        titulo_frame = tk.Frame(header, bg=COLORES["bg_dark"])
        titulo_frame.pack()

        tk.Label(
            titulo_frame,
            text="◈ EMOTISCAN",
            font=FUENTE_TITULO,
            fg=COLORES["accent"],
            bg=COLORES["bg_dark"],
        ).pack(side="left")

        tk.Label(
            titulo_frame,
            text="  //  ANÁLISIS FACIAL DE EMOCIONES",
            font=FUENTE_SUBTITULO,
            fg=COLORES["text_muted"],
            bg=COLORES["bg_dark"],
        ).pack(side="left", padx=(4, 0))

    def _construir_contenido_principal(self):
        """Área central con dos columnas: imagen (izq.) y resultados (der.)."""
        contenido = tk.Frame(self.root, bg=COLORES["bg_dark"])
        contenido.pack(fill="both", expand=True, padx=30, pady=(0, 10))
        contenido.columnconfigure(0, weight=3)
        contenido.columnconfigure(1, weight=2)
        contenido.rowconfigure(0, weight=1)

        self._construir_panel_imagen(contenido)
        self._construir_panel_resultados(contenido)

    def _construir_panel_imagen(self, parent):
        """Panel izquierdo: área de previsualización y botones de acción."""
        panel = tk.Frame(parent, bg=COLORES["bg_panel"], bd=0)
        panel.grid(row=0, column=0, sticky="nsew", padx=(0, 12), pady=4)

        # Título del panel
        header_panel = tk.Frame(panel, bg=COLORES["bg_panel"])
        header_panel.pack(fill="x", padx=16, pady=(14, 0))
        tk.Label(
            header_panel,
            text="▸ IMAGEN",
            font=FUENTE_LABEL,
            fg=COLORES["accent"],
            bg=COLORES["bg_panel"],
        ).pack(side="left")

        # Zona de imagen (Label que actúa como canvas)
        self.canvas_imagen = tk.Label(
            panel,
            bg=COLORES["bg_card"],
            text="[ Sin imagen cargada ]\n\nHaz clic en CARGAR FOTO\npara comenzar el análisis.",
            fg=COLORES["text_muted"],
            font=FUENTE_VALOR,
            justify="center",
            relief="flat",
        )
        self.canvas_imagen.pack(fill="both", expand=True, padx=16, pady=14)

        # Fila de botones
        btn_frame = tk.Frame(panel, bg=COLORES["bg_panel"])
        btn_frame.pack(fill="x", padx=16, pady=(0, 14))

        self.btn_cargar = self._crear_boton(
            btn_frame,
            texto="⊕  CARGAR FOTO",
            color_bg=COLORES["accent2"],
            color_fg="#FFFFFF",
            comando=self._accion_cargar_imagen,
        )
        self.btn_cargar.pack(side="left", padx=(0, 10))

        self.btn_analizar = self._crear_boton(
            btn_frame,
            texto="◉  ANALIZAR",
            color_bg=COLORES["accent"],
            color_fg=COLORES["bg_dark"],
            comando=self._accion_analizar,
        )
        self.btn_analizar.pack(side="left")
        self.btn_analizar.configure(state="disabled")   # Desactivado hasta cargar imagen

    def _construir_panel_resultados(self, parent):
        """Panel derecho: emoción dominante y barras de porcentaje."""
        panel = tk.Frame(parent, bg=COLORES["bg_panel"], bd=0)
        panel.grid(row=0, column=1, sticky="nsew", pady=4)

        # Título del panel
        header_panel = tk.Frame(panel, bg=COLORES["bg_panel"])
        header_panel.pack(fill="x", padx=16, pady=(14, 0))
        tk.Label(
            header_panel,
            text="▸ RESULTADOS",
            font=FUENTE_LABEL,
            fg=COLORES["accent"],
            bg=COLORES["bg_panel"],
        ).pack(side="left")

        # Emoción dominante (grande, centrada)
        self.lbl_emocion_dominante = tk.Label(
            panel,
            text="—",
            font=FUENTE_EMOCION,
            fg=COLORES["text_muted"],
            bg=COLORES["bg_panel"],
        )
        self.lbl_emocion_dominante.pack(pady=(18, 2))

        tk.Label(
            panel,
            text="Emoción dominante",
            font=FUENTE_VALOR,
            fg=COLORES["text_muted"],
            bg=COLORES["bg_panel"],
        ).pack()

        # Separador horizontal
        tk.Frame(panel, bg=COLORES["border"], height=1).pack(fill="x", padx=16, pady=14)

        # Subtítulo de la sección de barras
        tk.Label(
            panel,
            text="DISTRIBUCIÓN DE EMOCIONES",
            font=("Courier New", 9, "bold"),
            fg=COLORES["text_muted"],
            bg=COLORES["bg_panel"],
        ).pack(anchor="w", padx=18, pady=(0, 10))

        # Contenedor de barras (se rellena dinámicamente al analizar)
        self.frame_barras = tk.Frame(panel, bg=COLORES["bg_panel"])
        self.frame_barras.pack(fill="x", padx=16, pady=(0, 10))

        # Mensaje de estado
        self.lbl_estado = tk.Label(
            panel,
            text="Esperando imagen...",
            font=FUENTE_VALOR,
            fg=COLORES["text_muted"],
            bg=COLORES["bg_panel"],
            wraplength=260,
            justify="center",
        )
        self.lbl_estado.pack(pady=(10, 16))

    def _construir_footer(self):
        """Pie de página con información de versión."""
        footer = tk.Frame(self.root, bg=COLORES["bg_dark"])
        footer.pack(fill="x", padx=30, pady=(0, 10))

        tk.Frame(footer, bg=COLORES["border"], height=1).pack(fill="x", pady=(0, 8))
        tk.Label(
            footer,
            text="EmotiScan v1.0  ·  Powered by DeepFace + OpenCV  ·  © 2025",
            font=("Courier New", 9),
            fg=COLORES["text_muted"],
            bg=COLORES["bg_dark"],
        ).pack()

    # ── Widgets reutilizables ─────────────────────────────────────────────────

    def _crear_boton(
        self,
        parent,
        texto: str,
        color_bg: str,
        color_fg: str,
        comando,
    ) -> tk.Button:
        """Crea y devuelve un botón con el estilo visual de EmotiScan."""
        return tk.Button(
            parent,
            text=texto,
            font=FUENTE_BOTON,
            bg=color_bg,
            fg=color_fg,
            activebackground=color_bg,
            activeforeground=color_fg,
            relief="flat",
            padx=18,
            pady=10,
            cursor="hand2",
            command=comando,
            bd=0,
        )

    # ── Acciones del usuario ──────────────────────────────────────────────────

    def _accion_cargar_imagen(self):
        """Abre el diálogo del sistema de archivos y carga la imagen seleccionada."""
        tipos_archivo = [
            ("Imágenes", "*.jpg *.jpeg *.png *.bmp *.webp *.tiff"),
            ("Todos los archivos", "*.*"),
        ]
        ruta = filedialog.askopenfilename(
            title="Seleccionar imagen",
            filetypes=tipos_archivo,
        )
        if not ruta:
            return  # El usuario canceló

        self.imagen_path = ruta
        self._mostrar_imagen_en_canvas(ruta)
        self.btn_analizar.configure(state="normal")
        self._actualizar_estado(
            "✓ Imagen cargada. Presiona ANALIZAR para detectar emociones.",
            COLORES["success"],
        )
        self._limpiar_resultados()

    def _accion_analizar(self):
        """
        Lanza el análisis en un hilo secundario para no congelar la UI.
        Desactiva los botones mientras el análisis está en curso.
        """
        if not self.imagen_path:
            return

        self.btn_analizar.configure(state="disabled", text="⏳  ANALIZANDO...")
        self.btn_cargar.configure(state="disabled")
        self._actualizar_estado("Procesando... Por favor espera.", COLORES["accent"])

        hilo = threading.Thread(target=self._ejecutar_analisis, daemon=True)
        hilo.start()

    def _ejecutar_analisis(self):
        """
        Se ejecuta en el hilo secundario.
        Llama al analizador y devuelve el resultado al hilo principal con root.after().
        """
        try:
            resultado = self.analyzer.analyze(self.imagen_path)
            # Tkinter no es thread-safe; toda actualización de UI va por root.after()
            self.root.after(0, self._mostrar_resultados, resultado)
        except ValueError as e:
            self.root.after(0, self._mostrar_error, str(e))
        except Exception as e:
            self.root.after(0, self._mostrar_error, f"Error inesperado:\n{str(e)}")
        finally:
            self.root.after(0, self._restaurar_botones)

    # ── Actualización de la UI ────────────────────────────────────────────────

    def _mostrar_resultados(self, resultado: dict):
        """Actualiza imagen, emoción dominante y barras con los datos del análisis."""
        # Imagen con bounding box
        self._mostrar_imagen_en_canvas(resultado["imagen_anotada"], es_pil=True)

        # Nombre de la emoción dominante
        self.lbl_emocion_dominante.configure(
            text=resultado["emocion_dominante"],
            fg=COLORES["accent"],
        )

        # Barras de porcentaje
        self._dibujar_barras(resultado["porcentajes"])

        self._actualizar_estado("✓ Análisis completado exitosamente.", COLORES["success"])

    def _dibujar_barras(self, porcentajes: dict):
        """
        Recrea las barras de progreso para cada emoción detectada.
        Las barras anteriores se eliminan antes de dibujar las nuevas.
        """
        # Eliminar barras del análisis anterior
        for widget in self.frame_barras.winfo_children():
            widget.destroy()

        for i, (emocion, porcentaje) in enumerate(porcentajes.items()):
            fila = tk.Frame(self.frame_barras, bg=COLORES["bg_panel"])
            fila.pack(fill="x", pady=3)

            # Etiqueta con el nombre de la emoción
            tk.Label(
                fila,
                text=emocion,
                font=("Courier New", 9, "bold"),
                fg=COLORES["text_primary"],
                bg=COLORES["bg_panel"],
                width=12,
                anchor="w",
            ).pack(side="left")

            # Pista de la barra (fondo gris oscuro)
            barra_track = tk.Frame(fila, bg=COLORES["bar_bg"], height=10)
            barra_track.pack(side="left", fill="x", expand=True, padx=6)
            barra_track.pack_propagate(False)

            # Relleno de la barra (proporcional al porcentaje)
            color_barra    = COLORES_BARRAS[i % len(COLORES_BARRAS)]
            ancho_relativo = max(0.01, porcentaje / 100)
            barra_fill     = tk.Frame(barra_track, bg=color_barra, height=10)
            barra_fill.place(relx=0, rely=0, relwidth=ancho_relativo, relheight=1)

            # Porcentaje numérico a la derecha
            tk.Label(
                fila,
                text=f"{porcentaje:.1f}%",
                font=("Courier New", 9),
                fg=color_barra,
                bg=COLORES["bg_panel"],
                width=7,
                anchor="e",
            ).pack(side="left")

    def _mostrar_imagen_en_canvas(self, fuente, es_pil: bool = False):
        """
        Muestra la imagen en el área de previsualización, adaptando su tamaño.

        Args:
            fuente: Ruta de archivo (str) o PIL.Image si es_pil=True.
            es_pil: True cuando fuente ya es un objeto PIL.Image.
        """
        img = fuente if es_pil else Image.open(fuente).convert("RGB")

        # Respetar el espacio disponible en el canvas
        self.root.update_idletasks()
        max_w = max(200, self.canvas_imagen.winfo_width()  - 20)
        max_h = max(200, self.canvas_imagen.winfo_height() - 20)
        img.thumbnail((max_w, max_h), Image.LANCZOS)

        # Guardar referencia para evitar que el GC de Python destruya la imagen
        self.imagen_tk = ImageTk.PhotoImage(img)
        self.canvas_imagen.configure(image=self.imagen_tk, text="")

    def _mostrar_error(self, mensaje: str):
        """Muestra un mensaje de error en el panel de estado."""
        self._actualizar_estado(f"⚠ {mensaje}", "#EF5350")
        self._limpiar_resultados()

    def _limpiar_resultados(self):
        """Restablece el panel de resultados a su estado vacío inicial."""
        self.lbl_emocion_dominante.configure(text="—", fg=COLORES["text_muted"])
        for widget in self.frame_barras.winfo_children():
            widget.destroy()

    def _actualizar_estado(self, mensaje: str, color: str = None):
        """Cambia el texto y color del label de estado."""
        self.lbl_estado.configure(text=mensaje, fg=color or COLORES["text_muted"])

    def _restaurar_botones(self):
        """Reactiva los botones una vez terminado el análisis."""
        self.btn_analizar.configure(state="normal", text="◉  ANALIZAR")
        self.btn_cargar.configure(state="normal")


# ══════════════════════════════════════════════════════════════════════════════
#  SECCIÓN 4 — PUNTO DE ENTRADA
# ══════════════════════════════════════════════════════════════════════════════

def main():
    """Inicializa la ventana, conecta el analizador con la UI y arranca el loop."""
    root = tk.Tk()
    root.title("EmotiScan — Detector de Emociones")
    root.resizable(True, True)
    root.minsize(900, 640)

    # Conectar lógica de negocio con la capa de presentación
    analyzer = EmotionAnalyzer()
    app      = EmotiScanUI(root, analyzer)

    # Centrar la ventana en pantalla
    root.update_idletasks()
    w, h = 1100, 720
    x = (root.winfo_screenwidth()  // 2) - (w // 2)
    y = (root.winfo_screenheight() // 2) - (h // 2)
    root.geometry(f"{w}x{h}+{x}+{y}")

    root.mainloop()


if __name__ == "__main__":
    main()