# -*- coding: utf-8 -*-
"""
《我还没死，你们急什么》番茄小说封面生成
600x800 / jpg+png / 夜景少年剪影风
2倍超采样渲染后降采样，保证边缘平滑
"""
import random
import math
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

S = 2  # 超采样倍数
W, H = 600 * S, 800 * S
random.seed(42)

OUT_DIR = os.path.dirname(os.path.abspath(__file__))

# ---------------- 工具 ----------------

def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def multi_gradient(h, stops):
    """stops: [(t, (r,g,b)), ...] 竖向多段渐变，宽度1"""
    img = Image.new("RGB", (1, h))
    px = img.load()
    for y in range(h):
        t = y / (h - 1)
        for i in range(len(stops) - 1):
            t0, c0 = stops[i]
            t1, c1 = stops[i + 1]
            if t0 <= t <= t1:
                px[0, y] = lerp(c0, c1, (t - t0) / (t1 - t0))
                break
        else:
            px[0, y] = stops[-1][1]
    return img


def paste_glow(base, cx, cy, rx, ry, color, alpha, blur):
    """贴一团模糊辉光"""
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=color + (alpha,))
    layer = layer.filter(ImageFilter.GaussianBlur(blur))
    base.paste(layer, (0, 0), layer)


# ---------------- 1. 夜空渐变 ----------------
sky = multi_gradient(H, [
    (0.00, (5, 7, 24)),
    (0.35, (13, 17, 48)),
    (0.62, (34, 26, 66)),
    (0.78, (72, 44, 66)),
    (0.92, (26, 20, 40)),
    (1.00, (10, 9, 20)),
]).resize((W, H))
img = sky.convert("RGB")

# ---------------- 2. 星空 ----------------
stars = Image.new("RGBA", (W, H), (0, 0, 0, 0))
ds = ImageDraw.Draw(stars)
for _ in range(300):
    x = random.randint(0, W)
    y = random.randint(20, int(H * 0.55))
    b = random.randint(60, 220)
    r = random.choice([1, 1, 1, 2, 2, 3])
    ds.ellipse([x - r, y - r, x + r, y + r],
               fill=(b, b, min(255, b + 20), random.randint(90, 200)))
stars = stars.filter(ImageFilter.GaussianBlur(0.6))
img.paste(stars, (0, 0), stars)

# ---------------- 3. 天穹裂缝（界渊意象） ----------------
crack_path = [(830, 480), (800, 560), (848, 640), (796, 720), (852, 800),
              (812, 880), (860, 960), (828, 1060)]
crack = Image.new("RGBA", (W, H), (0, 0, 0, 0))
dc = ImageDraw.Draw(crack)
# 外层辉光
dc.line(crack_path, fill=(255, 190, 80, 160), width=13 * S, joint="curve")
for br in [[(800, 560), (744, 616)], [(852, 800), (916, 852)]]:
    dc.line(br, fill=(255, 190, 80, 130), width=6 * S, joint="curve")
crack = crack.filter(ImageFilter.GaussianBlur(14 * S))
img.paste(crack, (0, 0), crack)
# 中层
crack2 = Image.new("RGBA", (W, H), (0, 0, 0, 0))
dc2 = ImageDraw.Draw(crack2)
dc2.line(crack_path, fill=(255, 226, 150, 220), width=5 * S, joint="curve")
for br in [[(612, 660), (556, 712)], [(660, 890), (724, 942)]]:
    dc2.line(br, fill=(255, 226, 150, 190), width=3 * S, joint="curve")
crack2 = crack2.filter(ImageFilter.GaussianBlur(4 * S))
img.paste(crack2, (0, 0), crack2)
# 核心亮线
crack3 = Image.new("RGBA", (W, H), (0, 0, 0, 0))
dc3 = ImageDraw.Draw(crack3)
dc3.line(crack_path, fill=(255, 250, 226, 255), width=2 * S, joint="curve")
img.paste(crack3, (0, 0), crack3)

# 裂缝垂落的光柱
beam = Image.new("RGBA", (W, H), (0, 0, 0, 0))
db = ImageDraw.Draw(beam)
db.polygon([(600, 1080), (700, 1080), (760, 1260), (540, 1260)],
           fill=(255, 200, 110, 46))
beam = beam.filter(ImageFilter.GaussianBlur(30 * S))
img.paste(beam, (0, 0), beam)

# ---------------- 4. 城市地平线辉光 ----------------
paste_glow(img, 620, 1180, 500, 220, (255, 150, 80), 70, 40 * S)
paste_glow(img, 300, 1150, 300, 150, (90, 200, 255), 50, 30 * S)

# ---------------- 5. 城市剪影（远/近两层 + 霓虹窗） ----------------
win_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))   # 窗灯单独一层，最后模糊发光
dw = ImageDraw.Draw(win_layer)
WIN_COLORS = [(120, 230, 255), (255, 120, 210), (255, 200, 120), (150, 255, 190)]

city = Image.new("RGBA", (W, H), (0, 0, 0, 0))
dct = ImageDraw.Draw(city)

def draw_buildings(baseline, color, h_min, h_max, win_density, win_alpha):
    x = -20
    while x < W + 20:
        bw = random.randint(20 * S, 55 * S)
        bh = random.randint(h_min, h_max)
        top = baseline - bh
        dct.rectangle([x, top, x + bw, baseline + 40], fill=color)
        # 楼顶天线
        if random.random() < 0.25:
            ax = x + bw // 2
            dct.line([(ax, top), (ax, top - random.randint(8 * S, 20 * S))],
                     fill=color, width=2 * S)
        # 窗
        for wy in range(top + 6 * S, baseline - 4 * S, 9 * S):
            for wx in range(x + 3 * S, x + bw - 3 * S, 7 * S):
                if random.random() < win_density:
                    c = random.choice(WIN_COLORS)
                    dw.rectangle([wx, wy, wx + 2 * S, wy + 3 * S],
                                 fill=c + (random.randint(win_alpha // 2, win_alpha),))
        x += bw + random.randint(2 * S, 8 * S)

draw_buildings(1180, (26, 30, 58), 30 * S, 130 * S, 0.05, 110)   # 远景
draw_buildings(1270, (12, 14, 30), 50 * S, 190 * S, 0.08, 170)   # 近景
img.paste(city, (0, 0), city)
win_glow = win_layer.filter(ImageFilter.GaussianBlur(2 * S))
img.paste(win_glow, (0, 0), win_glow)
img.paste(win_layer, (0, 0), win_layer)

# ---------------- 6. 前景天台 ----------------
slab = Image.new("RGBA", (W, H), (0, 0, 0, 0))
dsl = ImageDraw.Draw(slab)
dsl.polygon([(0, 1285), (W, 1255), (W, H), (0, H)], fill=(6, 7, 14, 255))
# 左侧矮墙/设备箱
dsl.rectangle([60, 1242, 185, 1284], fill=(8, 9, 18, 255))
# 右侧天线
dsl.line([(1050, 1256), (1050, 1130)], fill=(8, 9, 18, 255), width=3 * S)
dsl.line([(1036, 1180), (1064, 1180)], fill=(8, 9, 18, 255), width=2 * S)
img.paste(slab, (0, 0), slab)
# 天台边缘冷光
edge = Image.new("RGBA", (W, H), (0, 0, 0, 0))
de = ImageDraw.Draw(edge)
de.line([(0, 1285), (W, 1255)], fill=(90, 150, 220, 140), width=2 * S)
edge = edge.filter(ImageFilter.GaussianBlur(3 * S))
img.paste(edge, (0, 0), edge)
# 天线红色警示灯
paste_glow(img, 1050, 1128, 8, 8, (255, 60, 60), 220, 4 * S)

# ---------------- 7. 少年剪影（背影，风衣） ----------------
fig = Image.new("RGBA", (W, H), (0, 0, 0, 0))
df = ImageDraw.Draw(fig)
INK = (4, 5, 12, 255)
cx = 600

# 腿
df.polygon([(570, 1220), (594, 1220), (592, 1264), (572, 1264)], fill=INK)
df.polygon([(606, 1220), (630, 1220), (628, 1264), (608, 1264)], fill=INK)
# 鞋
df.polygon([(566, 1258), (598, 1258), (600, 1272), (564, 1272)], fill=INK)
df.polygon([(602, 1258), (634, 1258), (636, 1272), (600, 1272)], fill=INK)
# 立领
df.polygon([(566, 1004), (634, 1004), (622, 978), (600, 988), (578, 978)], fill=INK)
# 风衣躯干（右摆被风吹起）
df.polygon([
    (546, 1000), (654, 1000),          # 肩
    (648, 1060), (640, 1105),          # 右侧收腰
    (668, 1195), (716, 1168), (684, 1236),  # 风摆
    (660, 1230), (638, 1218), (624, 1238),
    (604, 1220), (590, 1240), (570, 1220),
    (552, 1234), (536, 1198),          # 左摆
    (560, 1105), (552, 1060),
], fill=INK)
# 头
df.ellipse([564, 898, 636, 970], fill=INK)
# 碎发
df.polygon([(566, 930), (560, 904), (574, 912), (570, 888), (588, 904),
            (590, 882), (602, 898), (614, 882), (616, 904), (632, 888),
            (626, 912), (640, 904), (634, 930)], fill=INK)

# 轮廓光：右侧金色（裂缝方向）、左侧冷蓝
alpha = fig.split()[3]
rim_gold = Image.new("RGBA", (W, H), (0, 0, 0, 0))
rim_gold.putalpha(alpha.transform((W, H), Image.AFFINE,
                                  (1, 0, -6 * S, 0, 1, 2 * S)).point(lambda v: int(v * 0.9)))
gold = Image.new("RGBA", (W, H), (255, 196, 96, 255))
gold.putalpha(rim_gold.split()[3].filter(ImageFilter.GaussianBlur(3 * S)))
img.paste(gold, (0, 0), gold)

rim_blue = Image.new("RGBA", (W, H), (0, 0, 0, 0))
rim_blue.putalpha(alpha.transform((W, H), Image.AFFINE,
                                  (1, 0, 4 * S, 0, 1, 0)).point(lambda v: int(v * 0.55)))
blue = Image.new("RGBA", (W, H), (110, 170, 255, 255))
blue.putalpha(rim_blue.split()[3].filter(ImageFilter.GaussianBlur(3 * S)))
img.paste(blue, (0, 0), blue)

img.paste(fig, (0, 0), fig)

# ---------------- 8. 暗角 ----------------
vs = 200
vig = Image.new("L", (vs, vs))
pv = vig.load()
for yy in range(vs):
    for xx in range(vs):
        d = math.hypot((xx - vs / 2) / (vs / 2), (yy - vs / 2) / (vs / 2))
        pv[xx, yy] = int(max(0, min(255, (d - 0.62) * 300)))
vig = vig.resize((W, H), Image.BICUBIC).filter(ImageFilter.GaussianBlur(15 * S))
dark = Image.new("RGB", (W, H), (2, 3, 8))
img = Image.composite(dark, img, vig.point(lambda v: v // 2))

# ---------------- 9. 书名（华文行楷 + 金色渐变 + 描边 + 辉光） ----------------
F_TITLE = "C:/Windows/Fonts/STXINGKA.TTF"
F_YAHEI = "C:/Windows/Fonts/msyh.ttc"

def draw_title(base, cy_top, text, font_size, tracking,
               c_top=(255, 246, 216), c_bot=(232, 156, 52)):
    font = ImageFont.truetype(F_TITLE, font_size)
    widths = [font.getlength(ch) for ch in text]
    total = sum(widths) + tracking * (len(text) - 1)
    xs = []
    x = (W - total) / 2
    for wd in widths:
        xs.append(x)
        x += wd + tracking
    # 文字蒙版
    mask = Image.new("L", (W, H), 0)
    dm = ImageDraw.Draw(mask)
    for ch, xx in zip(text, xs):
        dm.text((xx, cy_top), ch, font=font, fill=255)
    # 辉光
    glow_alpha = mask.filter(ImageFilter.GaussianBlur(9 * S)).point(lambda v: int(v * 0.55))
    glow = Image.new("RGBA", (W, H), (255, 208, 110, 255))
    glow.putalpha(glow_alpha)
    base.paste(glow, (0, 0), glow)
    # 深色描边（蒙版膨胀）
    stroke = mask.filter(ImageFilter.MaxFilter(5 * S + 1))
    outline = Image.new("RGBA", (W, H), (46, 26, 6, 255))
    outline.putalpha(stroke)
    base.paste(outline, (0, 0), outline)
    # 竖向金色渐变填充
    band = multi_gradient(H, [(0.0, c_top), (1.0, c_bot)]).resize((W, H))
    # 让渐变只作用于文字区域高度
    grad = Image.new("RGB", (W, H))
    top_c, bot_c = c_top, c_bot
    gp = grad.load()
    y0, y1 = cy_top, cy_top + int(font_size * 1.25)
    for yy in range(y0, min(y1, H)):
        t = (yy - y0) / max(1, (y1 - y0))
        row = lerp(top_c, bot_c, t)
        for xx in range(W):
            gp[xx, yy] = row
    base.paste(grad, (0, 0), mask)

draw_title(img, 120, "我还没死，", 150, 8)
draw_title(img, 350, "你们急什么", 172, 10)

# ---------------- 10. 笔名 + 印章 ----------------
f_author = ImageFont.truetype(F_YAHEI, 19 * S)
name = "明心如是"
tracking = 6 * S
widths = [f_author.getlength(ch) for ch in name]
name_w = sum(widths) + tracking * (len(name) - 1)
seal = 24 * S
gap = 10 * S
group_w = name_w + gap + seal
start_x = (W - group_w) / 2
ay = 714 * S

dA = ImageDraw.Draw(img)
x = start_x
for ch, wd in zip(name, widths):
    dA.text((x, ay), ch, font=f_author, fill=(214, 220, 238))
    x += wd + tracking
# 印章
sx0 = start_x + name_w + gap
sy0 = ay - 2 * S
dA.rounded_rectangle([sx0, sy0, sx0 + seal, sy0 + seal],
                     radius=3 * S, fill=(176, 32, 38))
f_seal = ImageFont.truetype(F_YAHEI, 15 * S)
tw = f_seal.getlength("著")
dA.text((sx0 + (seal - tw) / 2, sy0 + (seal - 15 * S) / 2 - 1 * S),
        "著", font=f_seal, fill=(255, 244, 235))

# ---------------- 11. 降采样输出 ----------------
final = img.resize((600, 800), Image.LANCZOS)
jpg_path = os.path.join(OUT_DIR, "封面_v1.jpg")
png_path = os.path.join(OUT_DIR, "封面_v1.png")
final.save(jpg_path, quality=93)
final.save(png_path)
print("JPG:", jpg_path, os.path.getsize(jpg_path) // 1024, "KB")
print("PNG:", png_path, os.path.getsize(png_path) // 1024, "KB")
