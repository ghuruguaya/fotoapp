"""
fotoapp.py - Módulo de la App para editar y compartir fotos en redes sociales.

Proyecto 2 - Programación Python Avanzada (UPSO, 2026)

Funciones del módulo:
    1. redimensionar_para_red(ruta, red_social)  -> abre la foto y la adapta a la red social
    2. ecualizar_histograma(imagen)               -> mejora el contraste usando el histograma
    3. aplicar_filtro(imagen, nombre_filtro)      -> aplica uno de los 9 filtros de Pillow
    4. boceto(imagen)                             -> resalta bordes como un dibujo de líneas
    5. menu()                                     -> menú interactivo para usar todo lo anterior

"""

import os
from io import BytesIO

import cv2
import numpy as np
import matplotlib.pyplot as plt
import requests
from PIL import Image, ImageOps, ImageFilter


# ---------------------------------------------------------------------------
# Constantes (datos fijos que usa todo el módulo)
# ---------------------------------------------------------------------------

# Carpeta donde se guardan todas las figuras e imágenes generadas
CARPETA_RESULTADOS = "resultados"

# Tamaños recomendados (ancho, alto) en píxeles para cada red social
TAMANIOS_REDES = {
    "youtube": (1280, 720),     # miniatura de video, 16:9
    "instagram": (1080, 1080),  # publicación cuadrada, 1:1
    "twitter": (1600, 900),     # imagen en un posteo de X/Twitter, 16:9
    "facebook": (1200, 630),    # imagen horizontal / link, 1.91:1
}

# Los 9 filtros de Pillow que pide la consigna: nombre -> filtro
FILTROS = {
    "BLUR": ImageFilter.BLUR,
    "CONTOUR": ImageFilter.CONTOUR,
    "DETAIL": ImageFilter.DETAIL,
    "EDGE_ENHANCE": ImageFilter.EDGE_ENHANCE,
    "EDGE_ENHANCE_MORE": ImageFilter.EDGE_ENHANCE_MORE,
    "EMBOSS": ImageFilter.EMBOSS,
    "FIND_EDGES": ImageFilter.FIND_EDGES,
    "SHARPEN": ImageFilter.SHARPEN,
    "SMOOTH": ImageFilter.SMOOTH,
}

# Lista con los nombres, para poder elegir un filtro por número (1 a 9)
LISTA_FILTROS = list(FILTROS.keys())


# ---------------------------------------------------------------------------
# Excepción propia y funciones auxiliares
# ---------------------------------------------------------------------------

class ImagenNoCargadaError(Exception):
    """Se lanza cuando se intenta editar una foto sin haberla cargado antes (opción 1)."""
    pass


def verificar_imagen(imagen):
    """Controla que haya una imagen de Pillow cargada. Si no, lanza una excepción."""
    if imagen is None:
        raise ImagenNoCargadaError(
            "Todavía no cargaste ninguna imagen. Primero usá la opción 1 del menú."
        )
    if not isinstance(imagen, Image.Image):
        raise TypeError("La imagen tiene que ser un objeto Image de Pillow.")


def guardar_figura(nombre_archivo):
    """Guarda la figura de matplotlib que se está armando dentro de la carpeta de resultados."""
    os.makedirs(CARPETA_RESULTADOS, exist_ok=True)       # crea la carpeta si no existe
    ruta = os.path.join(CARPETA_RESULTADOS, nombre_archivo)
    plt.savefig(ruta, dpi=100, bbox_inches="tight")   # dpi = resolución
    print("Figura guardada en:", ruta)
    return ruta


def abrir_imagen(ruta):
    """Abre una imagen desde una URL (http/https) o desde una ruta de la compu / Drive."""
    if ruta.startswith("http://") or ruta.startswith("https://"):
        respuesta = requests.get(ruta, timeout=15)         # descargamos la foto
        respuesta.raise_for_status()                        # da error si la página falló (ej. 404)
        imagen = Image.open(BytesIO(respuesta.content))     # BytesIO: "archivo" en memoria
    else:
        if not os.path.exists(ruta):
            raise FileNotFoundError(f"No se encontró el archivo: {ruta}")
        imagen = Image.open(ruta)
    return imagen.convert("RGB")      # siempre trabajamos en RGB (3 canales)


# ---------------------------------------------------------------------------
# Función 1: abrir y redimensionar para una red social
# ---------------------------------------------------------------------------

def redimensionar_para_red(ruta, red_social):
    """
    Abre la foto indicada en `ruta` (archivo o URL) y la redimensiona al tamaño
    recomendado para `red_social` ("Youtube", "Instagram", "Twitter" o "Facebook").

    Usa ImageOps.fit, que respeta la proporción: achica/agranda la foto y recorta
    lo que sobra desde el centro, en lugar de estirarla. Así la foto NO se deforma.
    """
    if not isinstance(ruta, str) or not isinstance(red_social, str):
        raise TypeError("La ruta y la red social tienen que ser textos (str).")

    clave = red_social.strip().lower()          # " Instagram " -> "instagram"
    if clave not in TAMANIOS_REDES:
        raise ValueError(
            f"Red social '{red_social}' no válida. Opciones: Youtube, Instagram, Twitter, Facebook."
        )

    imagen = abrir_imagen(ruta)
    tamanio = TAMANIOS_REDES[clave]
    imagen_redimensionada = ImageOps.fit(imagen, tamanio)

    print(f"Original: {imagen.size} -> {red_social}: {imagen_redimensionada.size}")
    return imagen_redimensionada


# ---------------------------------------------------------------------------
# Función 2: ajustar el contraste con el histograma (ecualización)
# ---------------------------------------------------------------------------

def ecualizar_histograma(imagen, nombre_archivo="ecualizada.png"):
    """
    Mejora el contraste de la foto ecualizando su histograma.

    Para no arruinar los colores, se pasa la foto a HSV y se ecualiza solo el
    canal V (el brillo). Muestra en una misma figura la original y la ecualizada
    con sus histogramas, guarda la figura y devuelve la imagen ecualizada.
    """
    verificar_imagen(imagen)

    arreglo = np.array(imagen)                             # Pillow -> NumPy (RGB)
    hsv = cv2.cvtColor(arreglo, cv2.COLOR_RGB2HSV)         # RGB -> HSV
    brillo_original = hsv[:, :, 2].copy()                  # canal V antes de ecualizar
    hsv[:, :, 2] = cv2.equalizeHist(hsv[:, :, 2])          # ecualizamos solo el brillo
    ecualizada = cv2.cvtColor(hsv, cv2.COLOR_HSV2RGB)      # HSV -> RGB

    # Figura de 2x2: arriba las fotos, abajo sus histogramas
    plt.figure(figsize=(12, 8))

    plt.subplot(2, 2, 1)
    plt.imshow(arreglo)
    plt.title("Original")
    plt.axis("off")

    plt.subplot(2, 2, 2)
    plt.imshow(ecualizada)
    plt.title("Ecualizada")
    plt.axis("off")

    plt.subplot(2, 2, 3)
    plt.hist(brillo_original.ravel(), bins=256, range=(0, 256), color="gray")
    plt.title("Histograma original (brillo)")

    plt.subplot(2, 2, 4)
    plt.hist(hsv[:, :, 2].ravel(), bins=256, range=(0, 256), color="gray")
    plt.title("Histograma ecualizado (brillo)")

    guardar_figura(nombre_archivo)
    plt.show()

    return Image.fromarray(ecualizada)                     # NumPy -> Pillow


# ---------------------------------------------------------------------------
# Función 3: aplicar uno de los 9 filtros de Pillow
# ---------------------------------------------------------------------------

def aplicar_filtro(imagen, nombre_filtro, nombre_archivo=None):
    """
    Aplica a la imagen el filtro de Pillow indicado por su nombre
    (Blur, Contour, Detail, Edge Enhance, Edge Enhance More, Emboss,
    Find Edges, Sharpen o Smooth).

    Muestra la original y la filtrada una al lado de la otra, guarda la figura
    y devuelve la imagen filtrada.
    """
    verificar_imagen(imagen)

    clave = nombre_filtro.strip().upper().replace(" ", "_")   # "Edge Enhance" -> "EDGE_ENHANCE"
    if clave not in FILTROS:
        raise ValueError(f"Filtro '{nombre_filtro}' no válido. Opciones: {', '.join(LISTA_FILTROS)}")

    filtrada = imagen.filter(FILTROS[clave])

    plt.figure(figsize=(12, 5))

    plt.subplot(1, 2, 1)
    plt.imshow(imagen)
    plt.title("Original")
    plt.axis("off")

    plt.subplot(1, 2, 2)
    plt.imshow(filtrada)
    plt.title(clave)                                       # el nombre del filtro como título
    plt.axis("off")

    if nombre_archivo is None:
        nombre_archivo = f"filtro_{clave.lower()}.png"
    guardar_figura(nombre_archivo)
    plt.show()

    return filtrada


# ---------------------------------------------------------------------------
# Función 4: boceto (resaltar bordes y contornos)
# ---------------------------------------------------------------------------

def boceto(imagen, umbral_bajo=50, umbral_alto=150, nombre_archivo="boceto.png"):
    """
    Convierte la foto en un "dibujo de líneas" (líneas negras sobre fondo blanco)
    probando tres técnicas y mostrándolas lado a lado:

        - Canny: el detector de bordes más usado (umbral_bajo y umbral_alto se pueden ajustar).
        - Sobel: mide cuánto cambia la intensidad (el gradiente) en X y en Y.
        - Umbral adaptativo: binariza la imagen calculando un umbral distinto por zona.

    Devuelve el boceto de Canny como imagen de Pillow.
    """
    verificar_imagen(imagen)

    gris = np.array(imagen.convert("L"))                  # escala de grises
    suave = cv2.GaussianBlur(gris, (5, 5), 0)             # sacamos ruido (evita bordes falsos)

    # Técnica 1: Canny (bordes = 255 sobre fondo 0) -> invertimos para fondo blanco
    bordes_canny = cv2.Canny(suave, umbral_bajo, umbral_alto)
    boceto_canny = 255 - bordes_canny

    # Técnica 2: Sobel (gradiente en X y en Y, combinados con Pitágoras)
    sobel_x = cv2.Sobel(suave, cv2.CV_64F, 1, 0, ksize=3)
    sobel_y = cv2.Sobel(suave, cv2.CV_64F, 0, 1, ksize=3)
    magnitud = np.sqrt(sobel_x**2 + sobel_y**2)
    magnitud = cv2.normalize(magnitud, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
    boceto_sobel = 255 - magnitud

    # Técnica 3: umbral adaptativo (cada zona tiene su propio umbral)
    boceto_umbral = cv2.adaptiveThreshold(suave, 255, cv2.ADAPTIVE_THRESH_MEAN_C,
                                          cv2.THRESH_BINARY, 9, 5)

    imagenes = [gris, boceto_canny, boceto_sobel, boceto_umbral]
    titulos = ["Original (gris)", f"Canny ({umbral_bajo}, {umbral_alto})",
               "Sobel", "Umbral adaptativo"]

    plt.figure(figsize=(16, 5))
    for i in range(4):
        plt.subplot(1, 4, i + 1)
        plt.imshow(imagenes[i], cmap="gray", vmin=0, vmax=255)
        plt.title(titulos[i])
        plt.axis("off")

    guardar_figura(nombre_archivo)
    plt.show()

    return Image.fromarray(boceto_canny)


# ---------------------------------------------------------------------------
# Función 5: menú de opciones
# ---------------------------------------------------------------------------

def mostrar_imagen(imagen, titulo=""):
    """Muestra una sola imagen con matplotlib."""
    plt.figure(figsize=(8, 6))
    plt.imshow(imagen)
    plt.title(titulo)
    plt.axis("off")
    plt.show()


def menu():
    """Menú interactivo. Obliga a cargar una imagen (opción 1) antes de editarla."""
    imagen = None        # todavía no hay ninguna imagen cargada

    while True:
        print("\n========== FOTOAPP ==========")
        print("1. Cargar y redimensionar una imagen para una red social")
        print("2. Ajustar el contraste (ecualizar histograma)")
        print("3. Aplicar un filtro")
        print("4. Crear un boceto (resaltar bordes)")
        print("0. Salir")
        opcion = input("Elegí una opción: ").strip()

        try:
            if opcion == "1":
                ruta = input("Ruta o URL de la imagen: ").strip()
                red = input("Red social (Youtube, Instagram, Twitter, Facebook): ").strip()
                imagen = redimensionar_para_red(ruta, red)
                os.makedirs(CARPETA_RESULTADOS, exist_ok=True)
                ruta_salida = os.path.join(CARPETA_RESULTADOS, f"redimensionada_{red.lower()}.jpg")
                imagen.save(ruta_salida)
                print("Imagen guardada en:", ruta_salida)
                mostrar_imagen(imagen, f"Imagen para {red}")

            elif opcion == "2":
                verificar_imagen(imagen)
                ecualizar_histograma(imagen)

            elif opcion == "3":
                verificar_imagen(imagen)
                for numero, nombre in enumerate(LISTA_FILTROS, start=1):
                    print(f"  {numero}. {nombre}")
                texto = input("Número de filtro (1 a 9): ").strip()
                if not texto.isdigit():                          # isdigit: ¿son todos dígitos?
                    raise ValueError("Tenés que escribir un número.")
                numero = int(texto)
                if numero < 1 or numero > 9:
                    raise ValueError("El número de filtro tiene que estar entre 1 y 9.")
                aplicar_filtro(imagen, LISTA_FILTROS[numero - 1])

            elif opcion == "4":
                verificar_imagen(imagen)
                boceto(imagen)

            elif opcion == "0":
                print("¡Hasta luego!")
                break

            else:
                print("Opción no válida. Elegí 0, 1, 2, 3 o 4.")

        except ImagenNoCargadaError as error:
            print("ATENCIÓN:", error)
        except (FileNotFoundError, ValueError, TypeError) as error:
            print("Error:", error)
        except requests.exceptions.RequestException as error:
            print("No se pudo descargar la imagen de la URL:", error)
        except Exception as error:
            print("Ocurrió un error inesperado:", error)


# Este bloque solo se ejecuta si corremos "python fotoapp.py".
# Si hacemos "import fotoapp" desde el notebook, NO se ejecuta el menú.
if __name__ == "__main__":
    menu()
