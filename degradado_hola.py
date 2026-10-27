import argparse
import os
from PIL import Image, ImageDraw, ImageFont, ImageOps


def find_font(font_size: int) -> ImageFont.FreeTypeFont:
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "C:\\Windows\\Fonts\\arialbd.ttf",
        "C:\\Windows\\Fonts\\arial.ttf",
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/Library/Fonts/Arial Bold.ttf",
        "/Library/Fonts/Arial.ttf",
        "DejaVuSansCondensed-Bold.ttf",
        "DejaVuSans-Bold.ttf",
        "DejaVuSans.ttf",
        "arialbd.ttf",
        "arial.ttf",
    ]

    for path in candidates:
        try:
            if os.path.exists(path) or (":" not in path and "/" not in path):
                return ImageFont.truetype(path, font_size)
        except Exception:
            pass

    return ImageFont.load_default()




def _parse_rgb(s: str) -> tuple[int, int, int]:
    parts = [p.strip() for p in str(s).split(",")]
    if len(parts) != 3:
        raise ValueError('El color debe ser "R,G,B" (ej: 24,68,117)')
    r, g, b = (int(p) for p in parts)
    return (max(0, min(255, r)), max(0, min(255, g)), max(0, min(255, b)))


def _parse_size(s: str) -> tuple[int, int]:
    """
    Lee tamaños tipo '1080x1350' o '1638x2048'.
    Si viene vacío, devuelve (0, 0).
    """
    s = (s or "").lower().replace(" ", "")
    if not s:
        return (0, 0)
    if "x" not in s:
        raise ValueError('Usa --out-size como "1080x1350" o "1638x2048"')
    a, b = s.split("x", 1)
    w, h = int(a), int(b)
    if w < 10 or h < 10:
        raise ValueError("El tamaño es demasiado pequeño.")
    return (w, h)


def resize_cover(img: Image.Image, out_w: int, out_h: int, crop_x: float = 0.5, crop_y: float = 0.5) -> Image.Image:
    """
    Redimensiona y recorta para llenar EXACTO el tamaño (cover), manteniendo proporción.
    Útil para pasar de horizontal a vertical tipo 4:5.
    crop_x/crop_y controlan el centro del recorte (0..1).
    """
    if out_w <= 0 or out_h <= 0:
        return img

    crop_x = 0.0 if crop_x < 0.0 else (1.0 if crop_x > 1.0 else crop_x)
    crop_y = 0.0 if crop_y < 0.0 else (1.0 if crop_y > 1.0 else crop_y)

    try:
        method = Image.Resampling.LANCZOS
    except Exception:
        method = Image.LANCZOS

    return ImageOps.fit(img, (out_w, out_h), method=method, centering=(crop_x, crop_y))


def _smoothstep(t: float) -> float:
    """Suaviza una transición 0..1 (ease-in-out)."""
    t = 0.0 if t < 0.0 else (1.0 if t > 1.0 else t)
    return t * t * (3.0 - 2.0 * t)


def make_gradient_column_rgba(
    height: int,
    fade_start: float,
    solid_start: float,
    max_alpha: int,
    gamma: float,
    fade_rgb: tuple[int, int, int],
    top_rgb: tuple[int, int, int],
    mid_rgb: tuple[int, int, int],
    bottom_rgb: tuple[int, int, int],
    mid_pos: float,
) -> Image.Image:
    """
    Columna (1px) RGBA con:
    - Zona arriba: transparente
    - Zona de transición larga y suave (fade_start..solid_start)
    - Banda sólida abajo con gradiente de color (top->mid->bottom)
    """
    height = max(2, int(height))

    fade_start = max(0.0, min(1.0, float(fade_start)))
    solid_start = max(0.0, min(1.0, float(solid_start)))
    if solid_start <= fade_start:
        solid_start = min(1.0, fade_start + 0.05)

    max_alpha = max(0, min(255, int(max_alpha)))
    gamma = max(0.01, float(gamma))
    mid_pos = max(0.05, min(0.95, float(mid_pos)))

    y_fade = int(height * fade_start)
    y_solid = int(height * solid_start)

    y_fade = min(y_fade, height - 2)
    y_solid = min(max(y_solid, y_fade + 1), height - 1)

    fade_span = max(1, y_solid - y_fade)
    band_span = max(1, (height - 1) - y_solid)
    y_mid = y_solid + int(band_span * mid_pos)
    y_mid = max(y_solid + 1, min(height - 2, y_mid))

    data = bytearray(height * 4)

    for y in range(height):
        if y < y_fade:
            a = 0
            r, g, b = fade_rgb
        elif y < y_solid:
            t = (y - y_fade) / float(fade_span)  # 0..1
            t = _smoothstep(t)
            t = t ** gamma
            a = int(t * max_alpha)

            r = int(fade_rgb[0] * (1 - t) + top_rgb[0] * t)
            g = int(fade_rgb[1] * (1 - t) + top_rgb[1] * t)
            b = int(fade_rgb[2] * (1 - t) + top_rgb[2] * t)
        else:
            a = max_alpha
            if y <= y_mid:
                tt = (y - y_solid) / float(max(1, y_mid - y_solid))
                tt = _smoothstep(tt)
                r = int(top_rgb[0] * (1 - tt) + mid_rgb[0] * tt)
                g = int(top_rgb[1] * (1 - tt) + mid_rgb[1] * tt)
                b = int(top_rgb[2] * (1 - tt) + mid_rgb[2] * tt)
            else:
                tt = (y - y_mid) / float(max(1, (height - 1) - y_mid))
                tt = _smoothstep(tt)
                r = int(mid_rgb[0] * (1 - tt) + bottom_rgb[0] * tt)
                g = int(mid_rgb[1] * (1 - tt) + bottom_rgb[1] * tt)
                b = int(mid_rgb[2] * (1 - tt) + bottom_rgb[2] * tt)

        i = y * 4
        data[i + 0] = max(0, min(255, r))
        data[i + 1] = max(0, min(255, g))
        data[i + 2] = max(0, min(255, b))
        data[i + 3] = max(0, min(255, a))

    return Image.frombytes("RGBA", (1, height), bytes(data))


def apply_gradient_band(
    img: Image.Image,
    fade_start: float,
    solid_start: float,
    max_alpha: int,
    gamma: float,
    fade_rgb: tuple[int, int, int],
    top_rgb: tuple[int, int, int],
    mid_rgb: tuple[int, int, int],
    bottom_rgb: tuple[int, int, int],
    mid_pos: float,
) -> Image.Image:
    img = img.convert("RGBA")
    w, h = img.size
    col = make_gradient_column_rgba(
        height=h,
        fade_start=fade_start,
        solid_start=solid_start,
        max_alpha=max_alpha,
        gamma=gamma,
        fade_rgb=fade_rgb,
        top_rgb=top_rgb,
        mid_rgb=mid_rgb,
        bottom_rgb=bottom_rgb,
        mid_pos=mid_pos,
    )
    overlay = col.resize((w, h), resample=Image.BILINEAR)
    return Image.alpha_composite(img, overlay)


def _measure_line_raw(draw: ImageDraw.ImageDraw, line: str, font: ImageFont.FreeTypeFont, tracking: int) -> tuple[int, int, list[int]]:
    char_widths = []
    total = 0
    max_h = 0
    for ch in line:
        bbox = draw.textbbox((0, 0), ch, font=font)
        cw = bbox[2] - bbox[0]
        ch_h = bbox[3] - bbox[1]
        char_widths.append(cw)
        total += cw
        if ch_h > max_h:
            max_h = ch_h
    if len(line) > 1:
        total += tracking * (len(line) - 1)
    line_h = max(max_h, int(font.size * 1.05))
    return max(1, int(total)), max(1, int(line_h)), char_widths


def _wrap_text_to_width(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont, tracking: int, max_width_px: int) -> list[str]:
    if "\n" in text:
        return [ln.strip() for ln in text.splitlines() if ln.strip()]

    words = [w for w in text.split(" ") if w]
    if not words:
        return [""]

    lines = []
    current = words[0]
    for w in words[1:]:
        candidate = f"{current} {w}"
        raw_w, _, _ = _measure_line_raw(draw, candidate, font, tracking)
        if raw_w <= max_width_px:
            current = candidate
        else:
            lines.append(current)
            current = w
    lines.append(current)
    return lines


def _render_line_image(line: str, font: ImageFont.FreeTypeFont, tracking: int, stroke: int) -> Image.Image:
    dummy = Image.new("RGBA", (10, 10))
    d = ImageDraw.Draw(dummy)
    raw_w, line_h, char_widths = _measure_line_raw(d, line, font, tracking)

    layer = Image.new("RGBA", (raw_w + stroke * 4, line_h + stroke * 4), (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)

    x = stroke * 2
    y = stroke * 2

    cx = x
    for i, ch in enumerate(line):
        draw.text(
            (cx, y),
            ch,
            font=font,
            fill=(255, 255, 255, 255),
            stroke_width=stroke,
            stroke_fill=(0, 0, 0, 255),
        )
        cx += char_widths[i] + (tracking if i < len(line) - 1 else 0)

    return layer



def _fit_title_lines(draw, text, font, tracking, stroke, x_scale,
                     line_spacing, max_width, max_height):
    """Keep the font size; shorten overflowing titles at word boundaries."""
    # Reserve the transparent padding and stroke used by _render_line_image.
    wrap_width = max(1, int(max_width / x_scale) - stroke * 4)

    def layout(candidate):
        lines = _wrap_text_to_width(draw, candidate, font, tracking, wrap_width)
        lines = [line for line in lines if line.strip()]
        if not lines:
            return None
        sizes = [_measure_line_raw(draw, line, font, tracking)[:2] for line in lines]
        heights = [height + stroke * 4 for _, height in sizes]
        step = int(heights[0] * line_spacing)
        height = max(i * step + h for i, h in enumerate(heights))
        width = max(max(1, int((w + stroke * 4) * x_scale)) for w, _ in sizes)
        return lines if width <= max_width and height <= max_height else None

    full = layout(text)
    if full is not None:
        return full

    best = layout('...')
    if best is None:
        raise ValueError('El area del titular es demasiado pequena para los puntos suspensivos.')
    prefix = []
    for word in text.split():
        prefix.append(word)
        candidate = ' '.join(prefix).rstrip('.,;:!?') + '...'
        fitted = layout(candidate)
        if fitted is None:
            break
        best = fitted
    return best


def draw_center_text(
    img: Image.Image,
    text: str,
    *,
    max_width_ratio: float = 0.94,
    top_ratio: float = 0.44,
    bottom_ratio: float = 0.98,
    x_scale: float = 0.65,
    tracking_ratio: float = -0.015,
    stroke: int = 3,
    line_spacing: float = 0.88,
    start_font_ratio: float = 0.09,
    min_font_size: int = 14,
) -> Image.Image:
    img = img.convert("RGBA")
    w, h = img.size

    text = (text or "").replace("\\n", "\n").strip()
    if not text:
        return img

    text = text.upper()

    max_width_ratio = max(0.2, min(0.98, float(max_width_ratio)))
    top_ratio = max(0.0, min(0.95, float(top_ratio)))
    bottom_ratio = max(top_ratio + 0.05, min(1.0, float(bottom_ratio)))
    x_scale = max(0.4, min(1.0, float(x_scale)))
    line_spacing = max(0.6, min(1.6, float(line_spacing)))
    stroke = max(0, int(stroke))

    max_block_w = int(w * max_width_ratio)
    block_top = int(h * top_ratio)
    block_bottom = int(h * bottom_ratio)
    max_block_h = max(10, block_bottom - block_top)

    font_size = int(h * start_font_ratio)
    font_size = max(min_font_size, font_size)

    dummy = Image.new("RGBA", (10, 10))
    d = ImageDraw.Draw(dummy)

    font = find_font(font_size)
    tracking = int(font_size * float(tracking_ratio))
    lines = _fit_title_lines(
        d, text, font, tracking, stroke, x_scale, line_spacing,
        max_block_w, max_block_h,
    )
    line_imgs = []
    for line in lines:
        layer = _render_line_image(line, font, tracking, stroke)
        layer = layer.resize(
            (max(1, int(layer.width * x_scale)), layer.height),
            resample=Image.BICUBIC,
        )
        line_imgs.append(layer)
    line_step = int(line_imgs[0].height * line_spacing)
    total_h = max(i * line_step + layer.height for i, layer in enumerate(line_imgs))
    start_y = block_top + int((max_block_h - total_h) / 2)

    out = img.copy()
    y = start_y

    for ln_img in line_imgs:
        x = int((w - ln_img.width) / 2)
        out.alpha_composite(ln_img, (x, y))
        y += line_step

    return out


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input", help="Imagen de entrada (jpg/png/webp, etc.)")
    parser.add_argument("output", help="Imagen de salida (recomendado .png)")
    parser.add_argument("--text", default="hola mundo", help='Texto (default: "hola mundo")')

    # --- SALIDA 4:5 por defecto (para que se parezca a tu imagen 2 en proporción/tamaño) ---
    parser.add_argument(
        "--out-size",
        default="1080x1350",
        help='Tamaño final "ANCHOxALTO" (default: 1080x1350, formato 4:5).',
    )
    parser.add_argument(
        "--no-resize",
        action="store_true",
        help="No cambia el tamaño/recorte: respeta el tamaño original de la imagen.",
    )
    parser.add_argument("--crop-x", type=float, default=0.50, help="Centro horizontal del recorte (0..1). Default 0.50")
    parser.add_argument("--crop-y", type=float, default=0.50, help="Centro vertical del recorte (0..1). Default 0.50")

    # Degradado
    parser.add_argument("--blue", default="20,60,105", help='(Compat) Azul base RGB "R,G,B". Si lo pasas, sobre-escribe --mid-color. Default 20,60,105')
    parser.add_argument("--fade-start", type=float, default=0.47, help="Altura donde el degradado empieza desde transparente (0..1). Default 0.47")
    parser.add_argument("--solid-start", type=float, default=0.65, help="Altura donde la banda ya es sólida (0..1). Default 0.65")
    parser.add_argument("--max-alpha", type=int, default=255, help="Opacidad máxima del overlay (0..255). Default 255")
    parser.add_argument("--gamma", type=float, default=1.0, help="Curva adicional (>=0.01). 1.0 = natural. >1 = más suave/lento. Default 1.0")

    parser.add_argument("--fade-color", default="0,0,0", help='Color hacia donde se oscurece al volverse transparente (default: 0,0,0)')
    parser.add_argument("--top-color", default="8,20,45", help='Color en la parte alta de la banda ("2") (default: 8,20,45)')
    parser.add_argument("--mid-color", default="20,60,105", help='Color en el medio de la banda ("1.2") (default: 20,60,105)')
    parser.add_argument("--bottom-color", default="70,115,175", help='Color en la parte baja de la banda ("1") (default: 70,115,175)')
    parser.add_argument("--mid-pos", type=float, default=0.45, help='Posición relativa (0..1) del punto medio "1.2" dentro de la banda sólida. Default 0.45')

    # Texto estilo titular
    parser.add_argument("--text-max-width", type=float, default=0.94, help="Ancho máximo del bloque de texto (0..1). Default 0.94")
    parser.add_argument("--text-top", type=float, default=0.44, help="Inicio vertical del área del texto (0..1). Default 0.44")
    parser.add_argument("--text-bottom", type=float, default=0.98, help="Fin vertical del área del texto (0..1). Default 0.98")
    parser.add_argument("--text-x-scale", type=float, default=0.65, help="Compresión horizontal del texto (0.4..1). Default 0.65")
    parser.add_argument("--text-tracking", type=float, default=-0.015, help="Tracking relativo al tamaño de fuente. Default -0.015")
    parser.add_argument("--text-stroke", type=int, default=3, help="Grosor del borde negro. Default 3")
    parser.add_argument("--text-line-spacing", type=float, default=0.88, help="Espaciado entre líneas. <1 más pegado. Default 0.88")
    parser.add_argument("--text-start-font", type=float, default=0.09, help="Tamano fijo relativo a la altura; si no cabe, acorta con ... Default 0.09")
    parser.add_argument("--text-min-font", type=int, default=14, help="Tamaño mínimo de fuente. Default 14")

    args = parser.parse_args()

    # Colores
    blue_rgb = _parse_rgb(args.blue)
    fade_rgb = _parse_rgb(args.fade_color)
    top_rgb = _parse_rgb(args.top_color)
    mid_rgb = _parse_rgb(args.mid_color)
    bottom_rgb = _parse_rgb(args.bottom_color)

    # Compat: --blue manda sobre mid_rgb
    mid_rgb = blue_rgb

    img = Image.open(args.input)
    img = ImageOps.exif_transpose(img)

    # --- Recorte/resize tipo cover (4:5 por defecto) ---
    if not args.no_resize:
        out_w, out_h = _parse_size(args.out_size)
        if out_w and out_h:
            img = resize_cover(img, out_w, out_h, crop_x=args.crop_x, crop_y=args.crop_y)

    out = apply_gradient_band(
        img,
        fade_start=args.fade_start,
        solid_start=args.solid_start,
        max_alpha=args.max_alpha,
        gamma=args.gamma,
        fade_rgb=fade_rgb,
        top_rgb=top_rgb,
        mid_rgb=mid_rgb,
        bottom_rgb=bottom_rgb,
        mid_pos=args.mid_pos,
    )

    out = draw_center_text(
        out,
        args.text,
        max_width_ratio=args.text_max_width,
        top_ratio=args.text_top,
        bottom_ratio=args.text_bottom,
        x_scale=args.text_x_scale,
        tracking_ratio=args.text_tracking,
        stroke=args.text_stroke,
        line_spacing=args.text_line_spacing,
        start_font_ratio=args.text_start_font,
        min_font_size=args.text_min_font,
    )

    ext = os.path.splitext(args.output.lower())[1]
    if ext in [".jpg", ".jpeg"]:
        out = out.convert("RGB")

    out.save(args.output)
    print(f"✅ Listo: {args.output}")


if __name__ == "__main__":
    main()
