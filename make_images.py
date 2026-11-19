"""生成 README 用的三张图：banner / 十方向网格 / 输出对比。"""

import os

from PIL import Image, ImageDraw, ImageFont

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
os.makedirs(OUT, exist_ok=True)

FONTS = r"C:\Windows\Fonts"
BOLD = os.path.join(FONTS, "msyhbd.ttc")
REG = os.path.join(FONTS, "msyh.ttc")
MONO = os.path.join(FONTS, "consola.ttf")

BG = (10, 12, 16)
PANEL = (18, 21, 27)
LINE = (34, 39, 48)
TEXT = (232, 236, 242)
MUTED = (138, 148, 166)
ACCENT = (79, 209, 197)
WARN = (255, 138, 128)


def f(path, size):
    try:
        return ImageFont.truetype(path, size)
    except OSError:
        return ImageFont.load_default()


def grid_bg(img, step=40, color=(20, 24, 31)):
    d = ImageDraw.Draw(img)
    w, h = img.size
    for x in range(0, w, step):
        d.line([(x, 0), (x, h)], fill=color, width=1)
    for y in range(0, h, step):
        d.line([(0, y), (w, y)], fill=color, width=1)


def center(d, box, text, font, fill):
    x0, y0, x1, y1 = box
    bb = d.textbbox((0, 0), text, font=font)
    w, h = bb[2] - bb[0], bb[3] - bb[1]
    d.text((x0 + (x1 - x0 - w) / 2 - bb[0], y0 + (y1 - y0 - h) / 2 - bb[1]), text, font=font, fill=fill)


def banner():
    W, H = 1280, 460
    img = Image.new("RGB", (W, H), BG)
    grid_bg(img)
    d = ImageDraw.Draw(img)

    d.rectangle([0, 0, W, 4], fill=ACCENT)

    title_font = f(BOLD, 150)
    d.text((72, 52), "棱镜", font=title_font, fill=TEXT)
    tb = d.textbbox((72, 52), "棱镜", font=title_font)
    line_y = tb[3] + 12
    d.line([(78, line_y), (300, line_y)], fill=ACCENT, width=3)
    d.text((78, line_y + 14), "PRISM", font=f(BOLD, 32), fill=ACCENT)
    d.text((78, line_y + 58), "Ten-Discipline Security Research Preset", font=f(REG, 23), fill=MUTED)

    items = ["渗透", "攻防", "代码审计", "二进制", "免杀", "应急", "云安全", "CTF", "资产测绘", "路由"]
    x0, y0 = 720, 96
    for i, name in enumerate(items):
        col, row = i % 2, i // 2
        x, y = x0 + col * 250, y0 + row * 56
        d.ellipse([x, y + 8, x + 8, y + 16], fill=ACCENT)
        d.text((x + 20, y), name, font=f(REG, 26), fill=TEXT)

    d.text((72, H - 44), "DSH agent preset   ·   one identity   ·   ten directions   ·   zero mode-switching",
           font=f(MONO, 18), fill=(96, 105, 120))

    img.save(os.path.join(OUT, "banner.png"))
    print("banner.png", img.size)


def grid():
    W, H = 1240, 660
    img = Image.new("RGB", (W, H), BG)
    grid_bg(img, 40, (18, 22, 28))
    d = ImageDraw.Draw(img)

    d.text((56, 46), "十个方向，一本 playbook 各一册", font=f(BOLD, 34), fill=TEXT)
    d.text((56, 96), "全部挂进同一个 preset —— 不需要在模式之间来回切", font=f(REG, 22), fill=MUTED)

    cells = [
        ("渗透", "pentest-playbook"), ("攻防", "ad-playbook"),
        ("代码审计", "audit-playbook"), ("二进制", "re-playbook"),
        ("免杀", "av-playbook"), ("应急", "ir-playbook"),
        ("云安全", "cloud-playbook"), ("CTF", "ctf-playbook"),
        ("资产测绘", "asset-mapping-playbook"), ("路由", "router-playbook"),
    ]

    pad, gap = 56, 20
    cols = 5
    cw = (W - pad * 2 - gap * (cols - 1)) // cols
    ch = 190
    top = 168

    for i, (zh, en) in enumerate(cells):
        r, c = divmod(i, cols)
        x = pad + c * (cw + gap)
        y = top + r * (ch + gap)
        d.rounded_rectangle([x, y, x + cw, y + ch], radius=14, fill=PANEL, outline=LINE, width=1)
        d.rectangle([x, y, x + 3, y + ch], fill=ACCENT)
        d.text((x + 22, y + 26), zh, font=f(BOLD, 30), fill=TEXT)
        d.text((x + 22, y + 96), en, font=f(MONO, 15), fill=MUTED)
        d.text((x + 22, y + 138), "loaded", font=f(MONO, 15), fill=ACCENT)

    img.save(os.path.join(OUT, "grid.png"))
    print("grid.png", img.size)


def output():
    W, H = 1240, 630
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)

    d.text((56, 44), "同一个问题，两种回答", font=f(BOLD, 34), fill=TEXT)
    d.text((56, 94), "差别不在能力，在输出纪律 —— 这就是这个 preset 真正想解决的问题", font=f(REG, 22), fill=MUTED)

    box_w, box_h, top = 556, 400, 156
    left_x, right_x = 56, 628

    d.rounded_rectangle([left_x, top, left_x + box_w, top + box_h], radius=14, fill=PANEL, outline=LINE)
    d.rounded_rectangle([right_x, top, right_x + box_w, top + box_h], radius=14, fill=PANEL, outline=ACCENT, width=1)

    d.text((left_x + 24, top + 20), "默认人格", font=f(BOLD, 22), fill=WARN)
    d.text((right_x + 24, top + 20), "棱镜", font=f(BOLD, 22), fill=ACCENT)

    q = "问：「帮我看看这个目标」"
    d.text((left_x + 24, top + 62), q, font=f(REG, 18), fill=MUTED)
    d.text((right_x + 24, top + 62), q, font=f(REG, 18), fill=MUTED)

    left_lines = ["好的呀，师傅先看看这个目标的", "授权情况哦", "", "这个问题比较复杂，我们需要从",
                  "几个角度来分析……", "", "希望能帮到你！"]
    right_lines = ["目标。先给授权范围，", "再出入口面清单。", "", "三件事要定：入口面、凭据、出网。",
                   "按顺序来。", "", ""]

    for i, t in enumerate(left_lines):
        d.text((left_x + 24, top + 104 + i * 34), t, font=f(REG, 20), fill=(200, 205, 214))
    for i, t in enumerate(right_lines):
        d.text((right_x + 24, top + 104 + i * 34), t, font=f(REG, 20), fill=TEXT)

    d.text((56, H - 44), "九条输出纪律：首行净化 · 不中途撤回 · 不送替代品 · 无据不改口 · 不预告 …",
           font=f(REG, 17), fill=(96, 105, 120))

    img.save(os.path.join(OUT, "output.png"))
    print("output.png", img.size)


if __name__ == "__main__":
    banner()
    grid()
    output()
