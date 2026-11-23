"""棱镜宣传片渲染器：Pillow 逐帧画，ffmpeg 编码。

输出：douyin/video/prism_promo.mp4（1080x1920 / 25fps / 无音轨，抖音直接配乐）
"""

import math
import os
import shutil
import subprocess

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
FRAMES = os.path.join(HERE, "_frames")
OUT_DIR = os.path.join(HERE, "video")
W, H, FPS = 1080, 1920, 25

FONTS = r"C:\Windows\Fonts"
BOLD = os.path.join(FONTS, "msyhbd.ttc")
REG = os.path.join(FONTS, "msyh.ttc")
MONO = os.path.join(FONTS, "consola.ttf")

BG = (9, 11, 15)
TEXT = (238, 242, 247)
MUTED = (140, 150, 167)
ACCENT = (79, 209, 197)
WARN = (255, 138, 128)
CARD = (20, 24, 31)


def ft(path, size):
    try:
        return ImageFont.truetype(path, size)
    except OSError:
        return ImageFont.load_default()


def mix(a, b, t):
    t = max(0.0, min(1.0, t))
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def ease(t):
    t = max(0.0, min(1.0, t))
    return 1 - (1 - t) ** 3


def background(tick):
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    for y in range(0, H, 64):
        d.line([(0, y), (W, y)], fill=(14, 17, 22))
    for x in range(0, W, 64):
        d.line([(x, 0), (x, H)], fill=(14, 17, 22))
    y = int((tick * 6) % H)
    d.line([(0, y), (W, y)], fill=(20, 26, 32), width=2)
    d.rectangle([0, 0, W, 6], fill=ACCENT)
    return img, d


def wrap(d, text, font, maxw):
    lines, cur = [], ""
    for ch in text:
        if ch == "\n":
            lines.append(cur)
            cur = ""
            continue
        if d.textlength(cur + ch, font=font) > maxw:
            lines.append(cur)
            cur = ch
        else:
            cur += ch
    if cur:
        lines.append(cur)
    return lines


def put(img, d, text, font, fill, y, x=90, maxw=None, lh=None, alpha=1.0):
    maxw = maxw or (W - 2 * x)
    lh = lh or int(font.size * 1.32)
    for i, ln in enumerate(wrap(d, text, font, maxw)):
        d.text((x, y + i * lh), ln, font=font, fill=mix(BG, fill, alpha))
    return y + len(wrap(d, text, font, maxw)) * lh


def chip(d, x, y, text, alpha=1.0):
    f = ft(BOLD, 30)
    w = int(d.textlength(text, font=f)) + 46
    d.rounded_rectangle([x, y, x + w, y + 60], radius=30, fill=mix(BG, ACCENT, alpha))
    d.text((x + 23, y + 13), text, font=f, fill=mix(BG, (9, 11, 15), 1))
    return y + 60


# ── 场景 ────────────────────────────────────────────────────────────────────

def scene_hook(t):
    img, d = background(t * 60)
    y = 620
    a = ease(t / 0.25)
    y = put(img, d, "DeepSeek Harness · agent preset", ft(REG, 40), ACCENT, y, alpha=a)
    y += 46
    y = put(img, d, "模型还是那个模型", ft(BOLD, 96), TEXT, y, alpha=ease((t - 0.1) / 0.3))
    y += 24
    y = put(img, d, "为什么它不废话了", ft(BOLD, 96), ACCENT, y, alpha=ease((t - 0.45) / 0.35))
    if t > 0.75:
        put(img, d, "一个 preset，把十个安全方向和九条输出纪律一起装进去。",
            ft(REG, 40), MUTED, y + 40, alpha=ease((t - 0.75) / 0.2))
    return img


def scene_ten(t):
    img, d = background(t * 60)
    y = 480
    y = put(img, d, "一个身份", ft(BOLD, 92), TEXT, y, alpha=ease(t / 0.2))
    y = put(img, d, "十个方向", ft(BOLD, 92), ACCENT, y + 8, alpha=ease((t - 0.15) / 0.25))

    items = ["渗透", "攻防", "代码审计", "二进制", "免杀",
             "应急", "云安全", "CTF", "资产测绘", "路由"]
    y0 = y + 80
    for i, name in enumerate(items):
        start = 0.28 + i * 0.055
        a = ease((t - start) / 0.18)
        if a <= 0:
            continue
        col, row = i % 2, i // 2
        x = 90 + col * 460
        yy = y0 + row * 92
        d.rounded_rectangle([x, yy, x + 420, yy + 72], radius=14,
                            fill=mix(BG, CARD, a), outline=mix(BG, (46, 54, 66), a))
        d.ellipse([x + 20, yy + 31, x + 30, yy + 41], fill=mix(BG, ACCENT, a))
        d.text((x + 46, yy + 16), name, font=ft(REG, 34), fill=mix(BG, TEXT, a))

    if t > 0.78:
        put(img, d, "十本 playbook 同时挂载 · 主方向由任务决定 · 不切模式",
            ft(REG, 34), MUTED, H - 330, alpha=ease((t - 0.78) / 0.2))
    return img


def scene_discipline(t):
    img, d = background(t * 60)
    y = 470
    y = put(img, d, "九条输出纪律", ft(BOLD, 90), TEXT, y, alpha=ease(t / 0.2))
    y = put(img, d, "写进人格，不写在文档里", ft(REG, 40), MUTED, y + 16, alpha=ease((t - 0.1) / 0.2))

    rules = ["首行不铺垫，直接给结论", "中段不撤回，不补免责", "不送替代品，要么给要么说不"]
    yy = y + 110
    for i, r in enumerate(rules):
        a = ease((t - 0.3 - i * 0.16) / 0.2)
        if a <= 0:
            continue
        d.rounded_rectangle([90, yy, W - 90, yy + 108], radius=16,
                            fill=mix(BG, CARD, a), outline=mix(BG, (46, 54, 66), a))
        d.text((122, yy + 30), f"0{i+1}", font=ft(BOLD, 36), fill=mix(BG, ACCENT, a))
        d.text((200, yy + 32), r, font=ft(REG, 36), fill=mix(BG, TEXT, a))
        yy += 128

    a = ease((t - 0.82) / 0.18)
    if a > 0:
        put(img, d, "高危操作只出计划，不自动执行", ft(BOLD, 44), WARN, yy + 30, alpha=a)
    return img


def typewriter(d, text, font, x, y, progress, fill):
    n = int(len(text) * max(0.0, min(1.0, progress)))
    d.text((x, y), text[:n], font=font, fill=fill)
    if n < len(text) and int(progress * 12) % 2 == 0:
        w = d.textlength(text[:n], font=font)
        d.rectangle([x + w + 4, y + 6, x + w + 16, y + font.size + 4], fill=ACCENT)


def scene_traps(t):
    img, d = background(t * 60)
    y = 420
    y = put(img, d, "踩过的坑", ft(BOLD, 92), TEXT, y, alpha=ease(t / 0.18))
    y = put(img, d, "三条都写进 README 的「已知坑」", ft(REG, 38), MUTED, y + 12,
            alpha=ease((t - 0.08) / 0.2))

    # 坑 1：红框 + 打字机
    a = ease((t - 0.25) / 0.2)
    if a > 0:
        d.rounded_rectangle([90, y + 60, W - 90, y + 300], radius=18,
                            fill=mix(BG, CARD, a), outline=mix(BG, WARN, a), width=2)
        d.text((122, y + 88), "坑 1 · 路径塞进求值标签", font=ft(BOLD, 34), fill=mix(BG, MUTED, a))
        typewriter(d, "Invalid regular expression flags", ft(MONO, 38), 122, y + 156,
                   (t - 0.35) / 0.3, mix(BG, WARN, a))
        d.text((122, y + 232), "Windows 路径被当成「正则 + 非法标志」", font=ft(REG, 32),
               fill=mix(BG, MUTED, a))

    yy = y + 340
    for i, r in enumerate(["坑 2 · .ps1 没存 BOM，PowerShell 按 GBK 读中文",
                           "坑 3 · github 直连 TCP 通、HTTPS 不通"]):
        a2 = ease((t - 0.6 - i * 0.12) / 0.2)
        if a2 <= 0:
            continue
        put(img, d, r, ft(REG, 34), TEXT, yy + i * 76, alpha=a2)
    return img


def scene_install(t):
    img, d = background(t * 60)
    y = 640
    y = put(img, d, "一条命令装好", ft(BOLD, 92), TEXT, y, alpha=ease(t / 0.2))
    y += 60

    a = ease((t - 0.2) / 0.2)
    d.rounded_rectangle([90, y, W - 90, y + 220], radius=18,
                        fill=mix(BG, CARD, a), outline=mix(BG, ACCENT, a), width=2)
    typewriter(d, "powershell -File install\\install.ps1", ft(MONO, 34), 122, y + 40,
               (t - 0.3) / 0.3, mix(BG, ACCENT, a))
    typewriter(d, "python3 install/install.py   # macOS / Linux", ft(MONO, 28), 122, y + 118,
               (t - 0.55) / 0.25, mix(BG, MUTED, a))

    a2 = ease((t - 0.8) / 0.2)
    if a2 > 0:
        put(img, d, "装完完全退出重开，新建会话选「棱镜 · 安全研究模式」",
            ft(REG, 34), MUTED, y + 268, alpha=a2)
    return img


def scene_cta(t):
    img, d = background(t * 60)
    y = 620
    y = put(img, d, "棱镜 · Prism", ft(BOLD, 104), TEXT, y, alpha=ease(t / 0.25))
    y = put(img, d, "十个安全方向 · 九条输出纪律 · 不关审批", ft(REG, 38), ACCENT, y + 20,
            alpha=ease((t - 0.2) / 0.25))

    a = ease((t - 0.4) / 0.25)
    if a > 0:
        d.rounded_rectangle([90, y + 90, W - 90, y + 190], radius=16,
                            fill=mix(BG, CARD, a), outline=mix(BG, (46, 54, 66), a))
        d.text((122, y + 122), "github.com/Picea-Q/dsh-preset-Prism", font=ft(REG, 34),
               fill=mix(BG, TEXT, a))

    a2 = ease((t - 0.65) / 0.25)
    if a2 > 0:
        put(img, d, "MIT · 删一段就完全回滚", ft(REG, 32), MUTED, y + 240, alpha=a2)
    return img


SCENES = [
    (scene_hook, 5.0),
    (scene_ten, 7.5),
    (scene_discipline, 7.0),
    (scene_traps, 8.0),
    (scene_install, 5.5),
    (scene_cta, 5.0),
]


def render_frames():
    if os.path.isdir(FRAMES):
        shutil.rmtree(FRAMES)
    os.makedirs(FRAMES)
    idx = 0
    for fn, dur in SCENES:
        n = int(dur * FPS)
        for i in range(n):
            img = fn(i / max(1, n - 1))
            img.save(os.path.join(FRAMES, f"{idx:05d}.png"))
            idx += 1
    print(f"frames: {idx} 张")
    return idx


def encode(ffmpeg):
    os.makedirs(OUT_DIR, exist_ok=True)
    out = os.path.join(OUT_DIR, "prism_promo.mp4")
    if os.path.exists(out):
        os.remove(out)
    cmd = [
        ffmpeg, "-y", "-framerate", str(FPS), "-i", os.path.join(FRAMES, "%05d.png"),
        "-c:v", "libx264", "-preset", "medium", "-crf", "20",
        "-pix_fmt", "yuv420p", "-movflags", "+faststart", out,
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stderr[-1500:])
        raise SystemExit("ffmpeg 失败")
    print("输出:", out, f"{os.path.getsize(out)/1024/1024:.1f} MB")
    return out


if __name__ == "__main__":
    ffmpeg = os.environ.get("FFMPEG") or shutil.which("ffmpeg")
    if not ffmpeg:
        ffmpeg = os.path.expandvars(
            r"%LOCALAPPDATA%\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-9.0.2-full_build\bin\ffmpeg.exe"
        )
    render_frames()
    encode(ffmpeg)
    shutil.rmtree(FRAMES, ignore_errors=True)
