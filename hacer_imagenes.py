#!/usr/bin/env python3
"""Diseño estilo 'Un Café con Jesús': letra manuscrita (Caveat), globo de diálogo blanco,
versículo en bandas de marcador de colores (amarillo, lavanda, menta), corazones y estrellas.
Formatos: 4:5 (1080x1350) para Instagram/X y 9:16 (1080x1920) para TikTok."""
from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont
import math
import os

BASE = os.path.dirname(os.path.abspath(__file__))
ORIG = os.path.join(BASE, "imagenes", "originales")
FINAL = os.path.join(BASE, "imagenes", "final")             # 4:5 Instagram/X
FINAL_TT = os.path.join(BASE, "imagenes", "final-tiktok")   # 9:16 TikTok
LOGO = os.path.join(BASE, "logo.png")
FUENTES = os.path.join(BASE, "fuentes")
CAVEAT = os.path.join(FUENTES, "Caveat.ttf")
PATRICK = os.path.join(FUENTES, "PatrickHand.ttf")
MARCA = "De regreso a casa · Impacto de Fe"
FLECHA_TXT = "dale a la otra"

AZUL = (20, 48, 74, 255)
TINTA = (32, 32, 32, 255)
VERDE = (0, 165, 100, 255)
MARCADORES = [(255, 232, 120, 175), (205, 185, 255, 175), (165, 230, 195, 175)]

REFLEXIONES = [
    {
        "problema_img": "problema-regreso.png",
        "respuesta_img": "respuesta-regreso.png",
        "problema_titulo": "¿Te alejaste de Dios?",
        "problema_texto": "Y ahora sientes que ya es tarde para volver...",
        "respuesta_titulo": "Nunca es tarde para volver",
        "respuesta_texto": "El Padre no te está esperando para juzgarte. Te está esperando para abrazarte.",
        "versiculo_partes": [
            "Y cuando aún estaba lejos,",
            "lo vio su padre, y fue movido a misericordia",
            "— Lucas 15:20",
        ],
    },
    {
        "problema_img": "problema-puerta.png",
        "respuesta_img": "respuesta-puerta.png",
        "problema_titulo": "¿Sientes que la puerta se cerró?",
        "problema_texto": "Tu pasado te dice que ya no hay perdón para ti...",
        "respuesta_titulo": "La puerta sigue abierta",
        "respuesta_texto": "Jesús no vino a cerrar puertas. Vino a abrir la que nadie podía abrir.",
        "versiculo_partes": [
            "Yo soy la puerta;",
            "el que por mí entrare, será salvo",
            "— Juan 10:9",
        ],
    },
    {
        "problema_img": "problema-camino.png",
        "respuesta_img": "respuesta-camino.png",
        "problema_titulo": "¿El camino se hizo oscuro?",
        "problema_texto": "No sabes hacia dónde ir y cada paso pesa más...",
        "respuesta_titulo": "No caminas solo",
        "respuesta_texto": "Su Palabra es la lámpara que alumbra tu camino, paso a paso.",
        "versiculo_partes": [
            "Lámpara es a mis pies tu palabra,",
            "y lumbrera a mi camino",
            "— Salmo 119:105",
        ],
    },
    {
        "problema_img": "problema-culpa.png",
        "respuesta_img": "respuesta-culpa.png",
        "problema_titulo": "¿La culpa no te deja avanzar?",
        "problema_texto": "Cargas un peso que te hace sentir indigno de volver...",
        "respuesta_titulo": "Ven tal como estás",
        "respuesta_texto": "No tienes que limpiarte primero. Él te limpia cuando llegas.",
        "versiculo_partes": [
            "Si vuestros pecados fueren como la grana,",
            "como la nieve serán blanqueados",
            "— Isaías 1:18",
        ],
    },
]


def caveat(tam, peso=700):
    try:
        f = ImageFont.truetype(CAVEAT, tam)
        f.set_variation_by_axes([peso])
        return f
    except Exception:
        return ImageFont.truetype(PATRICK, tam)


def montserrat(tam):
    ruta = os.path.join(FUENTES, "Montserrat-ExtraBold.ttf")
    if os.path.exists(ruta):
        return ImageFont.truetype(ruta, tam)
    return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", tam)


def envolver(draw, texto, fuente, ancho_max):
    lineas, actual = [], ""
    for palabra in texto.split():
        prueba = (actual + " " + palabra).strip()
        if draw.textlength(prueba, font=fuente) <= ancho_max:
            actual = prueba
        else:
            if actual:
                lineas.append(actual)
            actual = palabra
    if actual:
        lineas.append(actual)
    return lineas


def abrir(nombre):
    return Image.open(os.path.join(ORIG, nombre)).convert("RGB")


def lienzo(W, H, img):
    """Lienzo WxH: fondo difuminado + ilustración centrada a ancho completo."""
    fondo = img.resize((W, H)).filter(ImageFilter.GaussianBlur(40))
    fondo = Image.blend(fondo, Image.new("RGB", (W, H), (9, 13, 20)), 0.3)
    escala = W / img.width
    nh = round(img.height * escala)
    if nh > H:
        escala = H / img.height
        nw = round(img.width * escala)
        principal = img.resize((nw, nh), Image.LANCZOS)
        x = (W - nw) // 2
    else:
        principal = img.resize((W, nh), Image.LANCZOS)
        x = 0
    y = (H - nh) // 2
    fondo.paste(principal, (x, y))
    return fondo


def cargar_logo(ancho):
    """Carga el logo y vuelve transparente el fondo negro (efecto pantalla)."""
    logo = Image.open(LOGO).convert("RGBA")
    r, g, b, _ = logo.split()
    mx = ImageChops.lighter(ImageChops.lighter(r, g), b)
    logo.putalpha(mx.point(lambda v: min(255, int(v * 1.1))))
    alto = round(logo.height * ancho / logo.width)
    return logo.resize((ancho, alto), Image.LANCZOS)


def texto_sombra(d, xy, texto, fuente, color=AZUL):
    d.text((xy[0] + 2, xy[1] + 2), texto, font=fuente, fill=(255, 255, 255, 170))
    d.text(xy, texto, font=fuente, fill=color)


def burbuja(d, x, y, w, h, radio, cola):
    d.rounded_rectangle([x, y, x + w, y + h], radius=radio, fill=(255, 255, 255, 242))
    d.polygon([(x + w * 0.22, y + h - 3), (x + w * 0.42, y + h - 3), cola], fill=(255, 255, 255, 242))


def corazon(d, cx, cy, s, color):
    d.ellipse([cx - s, cy - s, cx, cy], fill=color)
    d.ellipse([cx, cy - s, cx + s, cy], fill=color)
    d.polygon([(cx - s, cy - s * 0.35), (cx + s, cy - s * 0.35), (cx, cy + s)], fill=color)


def estrella(d, cx, cy, r, color):
    pts = []
    for i in range(10):
        ang = -math.pi / 2 + i * math.pi / 5
        rad = r if i % 2 == 0 else r * 0.45
        pts.append((cx + rad * math.cos(ang), cy + rad * math.sin(ang)))
    d.polygon(pts, fill=color)


def pastilla_flecha(d, w, h, margen, f_flecha, relleno_x, relleno_y):
    """Pastilla verde 'dale a la otra' con chevron dibujado, esquina inferior derecha."""
    tw = d.textlength(FLECHA_TXT, font=f_flecha)
    th = d.textbbox((0, 0), FLECHA_TXT, font=f_flecha)[3]
    chev = int(w * 0.02)
    pw = tw + 2 * relleno_x + chev
    ph = th + 2 * relleno_y
    x1 = w - margen - int(w * 0.02) - pw
    y1 = h - margen - int(w * 0.02) - ph
    d.rounded_rectangle([x1, y1, x1 + pw, y1 + ph], radius=ph // 2, fill=(0, 214, 143, 255))
    d.text((x1 + relleno_x, y1 + relleno_y - int(w * 0.004)), FLECHA_TXT, font=f_flecha, fill=(9, 13, 20, 255))
    cx = x1 + relleno_x + tw + chev * 0.3
    cy = y1 + ph / 2
    s = ph * 0.22
    d.line([(cx, cy - s), (cx + s, cy), (cx, cy + s)], fill=(9, 13, 20, 255), width=max(2, int(ph * 0.09)))
    return ph


def procesar_problema(r, W, H, img, carpeta):
    base = lienzo(W, H, img)
    capa = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(capa)
    margen = int(W * 0.055)
    f_titulo = caveat(int(W * 0.06), 700)
    f_texto = caveat(int(W * 0.048), 600)
    f_flecha = montserrat(int(W * 0.032))
    # título manuscrito arriba a la izquierda
    y = margen
    for l in envolver(d, r["problema_titulo"], f_titulo, W - 2 * margen):
        texto_sombra(d, (margen, y), l, f_titulo)
        y += d.textbbox((0, 0), l, font=f_titulo)[3] + int(W * 0.008)
    y += int(W * 0.02)
    # globo de diálogo blanco
    ancho_b = int(W * 0.64)
    lineas_b = envolver(d, r["problema_texto"], f_texto, ancho_b - int(W * 0.05))
    inter = int(W * 0.008)
    h_b = sum(d.textbbox((0, 0), l, font=f_texto)[3] for l in lineas_b) + inter * (len(lineas_b) - 1) + int(W * 0.045)
    burbuja(d, margen, y, ancho_b, h_b, int(W * 0.035), (margen + int(W * 0.10), y + h_b + int(W * 0.05)))
    ty = y + int(W * 0.022)
    for l in lineas_b:
        d.text((margen + int(W * 0.025), ty), l, font=f_texto, fill=TINTA)
        ty += d.textbbox((0, 0), l, font=f_texto)[3] + inter
    # decoraciones
    corazon(d, W - margen - int(W * 0.06), margen + int(W * 0.10), int(W * 0.018), (255, 110, 140, 220))
    estrella(d, W - margen - int(W * 0.15), margen + int(W * 0.04), int(W * 0.016), (255, 200, 80, 220))
    corazon(d, margen + int(W * 0.04), y + h_b + int(W * 0.11), int(W * 0.014), (255, 150, 170, 200))
    # flecha
    pastilla_flecha(d, W, H, margen, f_flecha, int(W * 0.03), int(W * 0.018))
    salida = os.path.join(carpeta, r["problema_img"].rsplit(".", 1)[0] + ".jpg")
    Image.alpha_composite(base.convert("RGBA"), capa).convert("RGB").save(salida, "JPEG", quality=88)
    print("OK", salida)


def procesar_respuesta(r, W, H, img, carpeta):
    base = lienzo(W, H, img)
    capa = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(capa)
    margen = int(W * 0.055)
    f_titulo = caveat(int(W * 0.06), 700)
    f_texto = caveat(int(W * 0.048), 600)
    f_versiculo = caveat(int(W * 0.046), 600)
    f_marca = caveat(int(W * 0.038), 600)
    logo = cargar_logo(int(W * 0.18)) if os.path.exists(LOGO) else None
    x_der = (W - margen - logo.width - int(W * 0.02)) if logo else (W - margen)
    # título manuscrito arriba a la izquierda
    y = margen
    for l in envolver(d, r["respuesta_titulo"], f_titulo, x_der - margen):
        texto_sombra(d, (margen, y), l, f_titulo)
        y += d.textbbox((0, 0), l, font=f_titulo)[3] + int(W * 0.008)
    y += int(W * 0.02)
    # globo con la respuesta
    ancho_b = int(W * 0.68)
    lineas_b = envolver(d, r["respuesta_texto"], f_texto, ancho_b - int(W * 0.05))
    inter = int(W * 0.008)
    h_b = sum(d.textbbox((0, 0), l, font=f_texto)[3] for l in lineas_b) + inter * (len(lineas_b) - 1) + int(W * 0.045)
    burbuja(d, margen, y, ancho_b, h_b, int(W * 0.035), (margen + int(W * 0.10), y + h_b + int(W * 0.05)))
    ty = y + int(W * 0.022)
    for l in lineas_b:
        d.text((margen + int(W * 0.025), ty), l, font=f_texto, fill=TINTA)
        ty += d.textbbox((0, 0), l, font=f_texto)[3] + inter
    y = y + h_b + int(W * 0.04)
    # versículo en bandas de marcador de colores
    for i, parte in enumerate(r["versiculo_partes"]):
        for l in envolver(d, parte, f_versiculo, W - 2 * margen - int(W * 0.06)):
            tw = d.textlength(l, font=f_versiculo)
            th = d.textbbox((0, 0), l, font=f_versiculo)[3]
            pad_x = int(W * 0.025)
            pad_y = int(W * 0.012)
            bw = tw + 2 * pad_x
            bh = th + 2 * pad_y
            bx = (W - bw) // 2
            d.rounded_rectangle([bx, y, bx + bw, y + bh], radius=int(bh * 0.4), fill=MARCADORES[i % len(MARCADORES)])
            d.text((bx + pad_x, y + pad_y - int(W * 0.004)), l, font=f_versiculo, fill=AZUL)
            y += bh + int(W * 0.014)
    # marca abajo
    y += int(W * 0.01)
    texto_sombra(d, (margen, y), MARCA, f_marca, color=VERDE)
    # decoraciones
    corazon(d, W - margen - int(W * 0.06), margen + int(W * 0.10), int(W * 0.018), (255, 110, 140, 220))
    estrella(d, W - margen - int(W * 0.15), margen + int(W * 0.04), int(W * 0.016), (255, 200, 80, 220))
    final = Image.alpha_composite(base.convert("RGBA"), capa).convert("RGB")
    if logo:
        final.paste(logo, (W - margen - logo.width, margen), logo)
    salida = os.path.join(carpeta, r["respuesta_img"].rsplit(".", 1)[0] + ".jpg")
    final.save(salida, "JPEG", quality=88)
    print("OK", salida)


if __name__ == "__main__":
    FORMATOS = [(1080, 1350, FINAL), (1080, 1920, FINAL_TT)]
    for r in REFLEXIONES:
        img_p = abrir(r["problema_img"])
        img_r = abrir(r["respuesta_img"])
        for W, H, carpeta in FORMATOS:
            os.makedirs(carpeta, exist_ok=True)
            procesar_problema(r, W, H, img_p, carpeta)
            procesar_respuesta(r, W, H, img_r, carpeta)
