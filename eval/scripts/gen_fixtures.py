"""Generate synthetic film-still fixtures for storyboard-generator evals.

Three 16:9 stills sharing one look: cool teal/cyan shadows, warm orange
highlights, high contrast, low-key lighting, film grain. Still 2 contains a
distinctive red sphere on a table -- a salient object the style prefix must
NOT mention.
"""
from PIL import Image, ImageDraw, ImageFilter
import random
from pathlib import Path

W, H = 1024, 576
OUT = Path(__file__).resolve().parent.parent / "fixtures"


def gradient(top, bottom):
    """Vertical RGB gradient, fast: 1-px strip then bilinear resize."""
    strip = Image.new("RGB", (1, H))
    for y in range(H):
        t = y / (H - 1)
        strip.putpixel((0, y), tuple(int(a + (b - a) * t) for a, b in zip(top, bottom)))
    return strip.resize((W, H), Image.BILINEAR)


def grain(img, strength=14, alpha=0.10):
    noise = Image.effect_noise((W, H), strength).convert("L").convert("RGB")
    return Image.blend(img, noise, alpha)


def vignette(img, alpha=0.30):
    mask = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(mask)
    d.ellipse([-W * 0.30, -H * 0.45, W * 1.30, H * 1.45], fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(160))
    dark = mask.point(lambda v: int((255 - v) * alpha))  # edges darker, centre untouched
    black = Image.new("RGB", (W, H), (0, 0, 0))
    return Image.composite(black, img, dark)


def save(img, name):
    img.save(f"{OUT}/{name}")
    print("wrote", name)


random.seed(7)

# --- Still 1: night street, teal shadows, sodium-orange lit windows ---
img = gradient((26, 62, 94), (6, 15, 24))
d = ImageDraw.Draw(img, "RGBA")
buildings = []
for i, bw in enumerate([170, 210, 150, 190, 230]):
    x0 = 40 + i * 200
    hgt = random.randint(200, 420)
    buildings.append((x0, bw))
    d.rectangle([x0, H - 60 - hgt, x0 + bw, H - 60], fill=(10, 22, 34, 255))
glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
gd = ImageDraw.Draw(glow)
for x0, bw in buildings:
    for _ in range(random.randint(4, 8)):
        wx = x0 + random.randint(10, bw - 26)
        wy = H - 60 - random.randint(30, 380)
        w = random.choice([(255, 176, 92, 255), (255, 196, 120, 255), (255, 150, 70, 255)])
        d.rectangle([wx, wy, wx + 16, wy + 20], fill=w)
        gd.ellipse([wx - 18, wy - 18, wx + 34, wy + 38], fill=(255, 150, 60, 90))
glow = glow.filter(ImageFilter.GaussianBlur(18))
img = Image.alpha_composite(img.convert("RGBA"), glow).convert("RGB")
# warm sodium pool on the pavement from a streetlight
pool = Image.new("RGBA", (W, H), (0, 0, 0, 0))
pd = ImageDraw.Draw(pool)
pd.ellipse([W // 2 - 260, H - 190, W // 2 + 260, H - 30], fill=(255, 150, 60, 70))
pool = pool.filter(ImageFilter.GaussianBlur(60))
img = Image.alpha_composite(img.convert("RGBA"), pool).convert("RGB")
save(grain(vignette(img)), "still-1.png")

# --- Still 2: interior, warm key light from frame-left, red sphere on table ---
img = gradient((16, 42, 64), (6, 14, 24))
d = ImageDraw.Draw(img, "RGBA")
d.rectangle([0, int(H * 0.62), W, H], fill=(12, 24, 38, 255))  # table band
key = Image.new("RGBA", (W, H), (0, 0, 0, 0))
kd = ImageDraw.Draw(key)
kd.ellipse([-140, -120, 480, 420], fill=(255, 170, 90, 120))
key = key.filter(ImageFilter.GaussianBlur(90))
img = Image.alpha_composite(img.convert("RGBA"), key).convert("RGB")
d = ImageDraw.Draw(img, "RGBA")
cx, cy, r = int(W * 0.62), int(H * 0.62), 64
d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(196, 44, 44, 255))
d.ellipse([cx - r + 16, cy - r + 14, cx - r + 46, cy - r + 44], fill=(238, 120, 110, 200))
d.ellipse([cx - r + 6, cy + r - 12, cx + r - 6, cy + r + 26], fill=(0, 0, 0, 160))
save(grain(vignette(img)), "still-2.png")

# --- Still 3: night waterfront, warm light streaks on dark water ---
img = gradient((12, 44, 70), (4, 10, 18))
d = ImageDraw.Draw(img, "RGBA")
horizon = int(H * 0.58)
d.rectangle([0, horizon - 90, 240, horizon], fill=(8, 20, 32, 255))
d.rectangle([560, horizon - 60, 780, horizon], fill=(8, 20, 32, 255))
d.rectangle([860, horizon - 120, 1024, horizon], fill=(8, 20, 32, 255))
streaks = Image.new("RGBA", (W, H), (0, 0, 0, 0))
sd = ImageDraw.Draw(streaks)
random.seed(11)
for _ in range(26):
    x = random.randint(30, W - 30)
    y = horizon + random.randint(10, 200)
    w = random.randint(30, 130)
    h = random.randint(2, 5)
    sd.rectangle([x, y, x + w, y + h], fill=(255, 160, 70, random.randint(90, 200)))
streaks = streaks.filter(ImageFilter.GaussianBlur(3))
img = Image.alpha_composite(img.convert("RGBA"), streaks).convert("RGB")
save(grain(vignette(img)), "still-3.png")

print("done")
