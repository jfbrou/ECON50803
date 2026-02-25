"""Generate newspaper logo PNGs for the headlines slide template."""

from PIL import Image, ImageDraw, ImageFont
import os

OUTDIR = os.path.dirname(os.path.abspath(__file__))
SIZE = 400
R = 30  # corner radius
FONTS = "/System/Library/Fonts/Supplemental/"


def new_logo(bg):
    """Create a 400x400 RGBA image with a rounded-rectangle background."""
    img = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle([0, 0, SIZE - 1, SIZE - 1], radius=R, fill=bg)
    return img, draw


def center_text(draw, text, font, y, color=(255, 255, 255)):
    """Draw text horizontally centered at vertical position y."""
    bbox = draw.textbbox((0, 0), text, font=font)
    w = bbox[2] - bbox[0]
    x = (SIZE - w) // 2
    draw.text((x, y), text, font=font, fill=color)


def save(img, name):
    path = os.path.join(OUTDIR, f"{name}.png")
    img.save(path)
    print(f"  Created {name}.png")


# ── The Economist ──────────────────────────────────────────────────────────
# Red background, large white serif "E"
def make_economist():
    img, draw = new_logo((227, 18, 11))  # #E3120B
    font = ImageFont.truetype(FONTS + "Georgia.ttf", 280)
    center_text(draw, "E", font, 30)
    save(img, "economist")


# ── Financial Times ────────────────────────────────────────────────────────
# Beige/salmon background, black serif "FT"
def make_ft():
    img, draw = new_logo((255, 241, 224))  # #FFF1E0 FT salmon
    font = ImageFont.truetype(FONTS + "Georgia Bold.ttf", 200)
    center_text(draw, "FT", font, 70, color=(26, 26, 46))  # #1A1A2E dark
    save(img, "ft")


# ── La Presse ──────────────────────────────────────────────────────────────
# Red background, white Helvetica Neue Condensed Black "LA PRESSE" left-aligned
def make_lapresse():
    img, draw = new_logo((211, 53, 49))  # #D33531
    font = ImageFont.truetype(
        "/System/Library/Fonts/HelveticaNeue.ttc", 110, index=9  # Condensed Black
    )
    pad = 22
    draw.text((pad, 50), "LA", font=font, fill=(255, 255, 255))
    draw.text((pad, 180), "PRESSE", font=font, fill=(255, 255, 255))
    save(img, "lapresse")


# ── Bloomberg ─────────────────────────────────────────────────────────────
# Black background, large white sans-serif "B"
def make_bloomberg():
    img, draw = new_logo((0, 0, 0))  # black
    font = ImageFont.truetype(FONTS + "Arial Bold.ttf", 280)
    center_text(draw, "B", font, 30)
    save(img, "bloomberg")


# ── The Globe and Mail ────────────────────────────────────────────────────
# Red background, white serif stacked left-aligned, with maple leaf
def make_globeandmail():
    img, draw = new_logo((196, 40, 37))  # dark red
    font = ImageFont.truetype(FONTS + "Georgia Bold.ttf", 95)
    white = (255, 255, 255)
    pad = 15
    draw.text((pad, 10), "THE", font=font, fill=white)
    draw.text((pad, 100), "GLOBE", font=font, fill=white)
    draw.text((pad, 190), "AND", font=font, fill=white)
    draw.text((pad, 280), "MAIL", font=font, fill=white)
    save(img, "globeandmail")


# ── The Wall Street Journal ──────────────────────────────────────────────
# White background, black serif "WSJ"
def make_wsj():
    img, draw = new_logo((235, 235, 235))  # pale gray
    font = ImageFont.truetype(FONTS + "Times New Roman Bold.ttf", 160)
    center_text(draw, "WSJ", font, 90, color=(0, 0, 0))
    save(img, "wsj")


# ── Le Devoir ────────────────────────────────────────────────────────────
# Light background, black serif stacked
def make_ledevoir():
    img, draw = new_logo((235, 235, 235))  # pale gray
    font = ImageFont.truetype(FONTS + "Georgia Bold.ttf", 82)
    black = (0, 0, 0)
    pad = 18
    draw.text((pad, 95), "LE", font=font, fill=black)
    draw.text((pad, 195), "DEVOIR", font=font, fill=black)
    save(img, "ledevoir")


# ── The New York Times ───────────────────────────────────────────────────
# Black background, white gothic "T" (from reference image nyt_source.png)
# The iconic NYT logo cannot be reproduced with system fonts.
# To regenerate: place a black-on-white source image of the gothic T at
# Figures/logos/nyt_source.png, then run make_nyt().
def make_nyt():
    import glob
    from PIL import ImageOps
    # Try to load source image; skip if not found
    sources = glob.glob(os.path.join(OUTDIR, "nyt_source*"))
    if not sources:
        print("  SKIP nyt.png (no nyt_source image found)")
        return
    src = Image.open(sources[0]).convert("RGBA")
    img, draw = new_logo((0, 0, 0))  # black
    # Resize source to fit with padding
    pad = 30
    target = SIZE - 2 * pad
    src_w, src_h = src.size
    scale = min(target / src_w, target / src_h)
    new_w, new_h = int(src_w * scale), int(src_h * scale)
    src_resized = src.resize((new_w, new_h), Image.LANCZOS)
    # Invert: black T on white → white T on transparent
    gray = src_resized.convert("L")
    alpha = ImageOps.invert(gray)
    white_layer = Image.new("RGBA", (new_w, new_h), (255, 255, 255, 255))
    white_layer.putalpha(alpha)
    # Center on rounded rect
    x_off = (SIZE - new_w) // 2
    y_off = (SIZE - new_h) // 2
    img.paste(white_layer, (x_off, y_off), white_layer)
    save(img, "nyt")


# ── Les Echos ────────────────────────────────────────────────────────────
# Blue background, white serif "les Echos" (from source image lesechos_source.png)
# To regenerate: place a black-on-white logo at logos/lesechos_source.png.
def make_lesechos():
    from PIL import ImageOps
    import numpy as np
    src_path = os.path.join(OUTDIR, "lesechos_source.png")
    if not os.path.exists(src_path):
        print("  SKIP lesechos.png (no lesechos_source.png found)")
        return
    src = Image.open(src_path).convert("RGBA")
    white_bg = Image.new("RGBA", src.size, (255, 255, 255, 255))
    white_bg.paste(src, (0, 0), src)
    gray = white_bg.convert("L")
    alpha = ImageOps.invert(gray)
    # Trim to content
    arr = np.array(alpha)
    rows = np.any(arr > 30, axis=1)
    cols = np.any(arr > 30, axis=0)
    rmin, rmax = np.where(rows)[0][[0, -1]]
    cmin, cmax = np.where(cols)[0][[0, -1]]
    alpha_crop = alpha.crop((cmin, rmin, cmax + 1, rmax + 1))
    # Blue rounded rect
    img, draw = new_logo((0, 83, 160))  # #0053A0
    pad = 35
    target = SIZE - 2 * pad
    tw, th = alpha_crop.size
    scale = min(target / tw, target / th)
    new_w, new_h = int(tw * scale), int(th * scale)
    alpha_resized = alpha_crop.resize((new_w, new_h), Image.LANCZOS)
    white_layer = Image.new("RGBA", (new_w, new_h), (255, 255, 255, 255))
    white_layer.putalpha(alpha_resized)
    x_off = (SIZE - new_w) // 2
    y_off = (SIZE - new_h) // 2
    img.paste(white_layer, (x_off, y_off), white_layer)
    save(img, "lesechos")


# ── Reuters ──────────────────────────────────────────────────────────────
# Orange background, white dot-circle icon (from source image reuters_source.png)
# To regenerate: place a full Reuters logo PNG at logos/reuters_source.png.
def make_reuters():
    from PIL import ImageOps
    import numpy as np
    src_path = os.path.join(OUTDIR, "reuters_source.png")
    if not os.path.exists(src_path):
        print("  SKIP reuters.png (no reuters_source.png found)")
        return
    src = Image.open(src_path).convert("RGBA")
    arr = np.array(src)
    r, g, b, a = arr[:,:,0], arr[:,:,1], arr[:,:,2], arr[:,:,3]
    # Detect non-white, non-transparent content pixels
    is_content = (a > 128) & ~((r > 240) & (g > 240) & (b > 240))
    # Find gap between dot circle and text
    col_has = np.any(is_content, axis=0)
    prev_had = False
    gap_col = src.width
    for c in range(src.width):
        if col_has[c]:
            prev_had = True
        elif prev_had:
            gap_col = c
            break
    # Trim to dot circle bounding box
    row_has = np.any(is_content[:, :gap_col], axis=1)
    rows = np.where(row_has)[0]
    cols = np.where(col_has[:gap_col])[0]
    top, bottom = rows[0], rows[-1] + 1
    left = cols[0]
    dot_crop = src.crop((left, top, gap_col, bottom))
    # Flatten onto white, threshold for clean binary alpha
    white_bg = Image.new("RGBA", dot_crop.size, (255, 255, 255, 255))
    white_bg.paste(dot_crop, (0, 0), dot_crop)
    gray = white_bg.convert("L")
    binary = gray.point(lambda x: 255 if x < 200 else 0)
    # Orange rounded rect
    img, draw = new_logo((255, 130, 0))  # #FF8200
    pad = 40
    target = SIZE - 2 * pad
    dw, dh = binary.size
    scale = min(target / dw, target / dh)
    new_w, new_h = int(dw * scale), int(dh * scale)
    alpha_resized = binary.resize((new_w, new_h), Image.LANCZOS)
    white_layer = Image.new("RGBA", (new_w, new_h), (255, 255, 255, 255))
    white_layer.putalpha(alpha_resized)
    x_off = (SIZE - new_w) // 2
    y_off = (SIZE - new_h) // 2
    img.paste(white_layer, (x_off, y_off), white_layer)
    save(img, "reuters")


# ── The Washington Post ──────────────────────────────────────────────────
# Black background, white gothic "WP" (from source image washpost_source.png)
# The iconic WP gothic monogram cannot be reproduced with system fonts.
# To regenerate: place a black-on-transparent source at logos/washpost_source.png.
def make_washpost():
    from PIL import ImageOps
    src_path = os.path.join(OUTDIR, "washpost_source.png")
    if not os.path.exists(src_path):
        print("  SKIP washpost.png (no washpost_source.png found)")
        return
    src = Image.open(src_path).convert("RGBA")
    img, draw = new_logo((0, 0, 0))  # black
    # Flatten onto white to get clean black-on-white
    white_bg = Image.new("RGBA", src.size, (255, 255, 255, 255))
    white_bg.paste(src, (0, 0), src)
    gray = white_bg.convert("L")
    alpha = ImageOps.invert(gray)
    # Resize to fit with padding
    pad = 50
    target = SIZE - 2 * pad
    src_w, src_h = alpha.size
    scale = min(target / src_w, target / src_h)
    new_w, new_h = int(src_w * scale), int(src_h * scale)
    alpha_resized = alpha.resize((new_w, new_h), Image.LANCZOS)
    white_layer = Image.new("RGBA", (new_w, new_h), (255, 255, 255, 255))
    white_layer.putalpha(alpha_resized)
    x_off = (SIZE - new_w) // 2
    y_off = (SIZE - new_h) // 2
    img.paste(white_layer, (x_off, y_off), white_layer)
    save(img, "washpost")


# ── Radio-Canada ─────────────────────────────────────────────────────────
# Light gray background, red CBC gem logo (from source image radiocanada_source.png)
def make_radiocanada():
    from PIL import ImageOps
    import numpy as np
    src_path = os.path.join(OUTDIR, "radiocanada_source.png")
    if not os.path.exists(src_path):
        print("  SKIP radiocanada.png (no radiocanada_source.png found)")
        return
    src = Image.open(src_path).convert("RGBA")
    # White rounded rect background
    img, draw = new_logo((255, 255, 255))  # white
    # Flatten source onto white to isolate the red logo
    white_bg = Image.new("RGBA", src.size, (255, 255, 255, 255))
    white_bg.paste(src, (0, 0), src)
    arr = np.array(white_bg)
    r, g, b = arr[:,:,0], arr[:,:,1], arr[:,:,2]
    # Detect red-ish pixels (the logo) — ignore gray/white background
    is_content = (r > 150) & (g < 100) & (b < 100)
    # Trim to bounding box
    rows = np.any(is_content, axis=1)
    cols = np.any(is_content, axis=0)
    if not rows.any():
        print("  SKIP radiocanada.png (no content detected)")
        return
    rmin, rmax = np.where(rows)[0][[0, -1]]
    cmin, cmax = np.where(cols)[0][[0, -1]]
    cropped = white_bg.crop((cmin, rmin, cmax + 1, rmax + 1))
    # Resize to fit with padding
    pad = 30
    target = SIZE - 2 * pad
    cw, ch = cropped.size
    scale = min(target / cw, target / ch)
    new_w, new_h = int(cw * scale), int(ch * scale)
    resized = cropped.resize((new_w, new_h), Image.LANCZOS)
    # Create mask: non-gray/white pixels are opaque
    res_arr = np.array(resized)
    rr, gg, bb = res_arr[:,:,0], res_arr[:,:,1], res_arr[:,:,2]
    mask_arr = ((rr > 150) & (gg < 120) & (bb < 120)).astype(np.uint8) * 255
    mask = Image.fromarray(mask_arr, mode='L')
    resized.putalpha(mask)
    # Center on background
    x_off = (SIZE - new_w) // 2
    y_off = (SIZE - new_h) // 2
    img.paste(resized, (x_off, y_off), resized)
    save(img, "radiocanada")


# ── National Post ────────────────────────────────────────────────────────
# Gold/yellow background, dark serif "NP"
def make_nationalpost():
    img, draw = new_logo((243, 199, 43))  # #F3C72B gold yellow
    font = ImageFont.truetype(FONTS + "Times New Roman Bold.ttf", 220)
    center_text(draw, "NP", font, 65, color=(40, 40, 40))  # near-black
    save(img, "nationalpost")


if __name__ == "__main__":
    print("Generating logos...")
    make_economist()
    make_ft()
    make_lapresse()
    make_bloomberg()
    make_globeandmail()
    make_wsj()
    make_ledevoir()
    make_nyt()
    make_lesechos()
    make_reuters()
    make_washpost()
    make_radiocanada()
    make_nationalpost()
    print("Done.")
