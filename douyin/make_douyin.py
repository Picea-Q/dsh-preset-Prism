"""抖音图文生成器：三套方案，竖屏 1080x1440。

A 痛点型 · B 成品型 · C 故事型
每套输出到 douyin/<方案>/NN.png，并拼一张 preview_<方案>.png 供对比。
"""

import os

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
OUT = HERE
W, H = 1080, 1440

FONTS = r"C:\Windows\Fonts"
BOLD = os.path.join(FONTS, "msyhbd.ttc")
REG = os.path.join(FONTS, "msyh.ttc")
MONO = os.path.join(FONTS, "consola.ttf")

BG = (9, 11, 15)
CARD = (20, 24, 31)
LINE = (38, 44, 54)
TEXT = (238, 242, 247)
MUTED = (140, 150, 167)
ACCENT = (79, 209, 197)
WARN = (255, 138, 128)


def ft(path, size):
    try:
        return ImageFont.truetype(path, size)
    except OSError:
        return ImageFont.load_default()


def base():
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    return layer, ImageDraw.Draw(layer)


def compose(layer, foot=""):
    bg = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(bg)
    for y in range(0, H, 60):
        d.line([(0, y), (W, y)], fill=(15, 18, 23))
    d.rectangle([0, 0, W, 6], fill=ACCENT)
    bbox = layer.getbbox()
    offset = 0
    if bbox:
        top, bottom = bbox[1], bbox[3]
        offset = max(70, (H - (bottom - top)) // 2 - top)
    bg.paste(layer, (0, offset), layer)
    if foot:
        d.text((90, H - 114), foot, font=ft(REG, 26), fill=(102, 111, 126))
        d.rectangle([90, H - 172, 210, H - 166], fill=ACCENT)
    return bg


def fit_font(d, text, path, size, maxw, min_size=62):
    s = size
    while s > min_size:
        f = ft(path, s)
        longest = max(d.textlength(l, font=f) for l in text.split("\n"))
        if longest <= maxw:
            return f
        s -= 6
    return ft(path, min_size)


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


def draw_lines(d, lines, x, y, font, fill, lh):
    for i, ln in enumerate(lines):
        d.text((x, y + i * lh), ln, font=font, fill=fill)
    return y + len(lines) * lh


def chip(d, x, y, text, fill=ACCENT, fg=(9, 11, 15)):
    f = ft(BOLD, 30)
    w = d.textlength(text, font=f) + 44
    d.rounded_rectangle([x, y, x + w, y + 58], radius=29, fill=fill)
    d.text((x + 22, y + 12), text, font=f, fill=fg)
    return y + 58


def slide_cover(kicker, big, sub, foot=""):
    img, d = base()
    y = 190
    if kicker:
        y = chip(d, 90, y, kicker) + 70
    f_big = fit_font(d, big, BOLD, 108, W - 180)
    lines = wrap(d, big, f_big, W - 180)
    y = draw_lines(d, lines, 90, y, f_big, TEXT, 132) + 40
    f_sub = ft(REG, 46)
    y = draw_lines(d, wrap(d, sub, f_sub, W - 180), 90, y, f_sub, MUTED, 66)
    return compose(img, foot)


def slide_lines(title, lines, kicker=""):
    img, d = base()
    y = 170
    if kicker:
        y = chip(d, 90, y, kicker) + 60
    f_t = fit_font(d, title, BOLD, 74, W - 180)
    y = draw_lines(d, wrap(d, title, f_t, W - 180), 90, y, f_t, TEXT, 96) + 60

    f_b = ft(REG, 42)
    for ln in lines:
        if ln == "":
            y += 30
            continue
        d.ellipse([92, y + 20, 104, y + 32], fill=ACCENT)
        h = draw_lines(d, wrap(d, ln, f_b, W - 260), 132, y, f_b, (206, 212, 222), 60)
        y = h + 26
    return compose(img)


def slide_quote(quote, note, bad=True):
    img, d = base()
    y = 260
    d.text((90, y), "“", font=ft(BOLD, 200), fill=(60, 68, 80) if bad else ACCENT)
    y += 200
    f_q = ft(REG, 54)
    y = draw_lines(d, wrap(d, quote, f_q, W - 200), 110, y, f_q, TEXT, 82) + 50
    d.line([(110, y + 10), (110 + 140, y + 10)], fill=WARN if bad else ACCENT, width=5)
    f_n = ft(BOLD, 40)
    draw_lines(d, wrap(d, note, f_n, W - 200), 110, y + 46, f_n, WARN if bad else ACCENT, 58)
    return compose(img)


def slide_bullets(title, items, kicker=""):
    img, d = base()
    y = 180
    if kicker:
        y = chip(d, 90, y, kicker) + 56
    f_t = fit_font(d, title, BOLD, 78, W - 180)
    y = draw_lines(d, wrap(d, title, f_t, W - 180), 90, y, f_t, TEXT, 100) + 64

    f_i = ft(REG, 40)
    for num, txt in items:
        d.rounded_rectangle([90, y, W - 90, y + 132], radius=18, fill=CARD, outline=LINE)
        d.text((118, y + 42), num, font=ft(BOLD, 40), fill=ACCENT)
        d.text((190, y + 44), txt, font=f_i, fill=TEXT)
        y += 152
    return compose(img)


def slide_image(path, caption, kicker=""):
    img, d = base()
    y = 150
    if kicker:
        y = chip(d, 90, y, kicker) + 50
    src = Image.open(path)
    target_w = W - 100
    ratio = target_w / src.width
    src = src.resize((target_w, int(src.height * ratio)), Image.LANCZOS)
    img.paste(src, (60, y))
    y += src.height + 50
    f_c = ft(REG, 42)
    draw_lines(d, wrap(d, caption, f_c, W - 180), 90, y, f_c, MUTED, 60)
    return compose(img)



def slide_error(title, code, note, kicker=""):
    layer, d = base()
    y = 220
    if kicker:
        y = chip(d, 90, y, kicker) + 60
    f_t = fit_font(d, title, BOLD, 74, W - 180)
    y = draw_lines(d, wrap(d, title, f_t, W - 180), 90, y, f_t, TEXT, 96) + 60

    f_c = ft(MONO, 40)
    lines = wrap(d, code, f_c, W - 260)
    box_h = len(lines) * 60 + 76
    d.rounded_rectangle([90, y, W - 90, y + box_h], radius=18, fill=CARD, outline=WARN, width=2)
    yy = y + 38
    for ln in lines:
        d.text((120, yy), ln, font=f_c, fill=WARN)
        yy += 60
    y += box_h + 46

    f_n = ft(REG, 40)
    draw_lines(d, wrap(d, note, f_n, W - 180), 90, y, f_n, MUTED, 58)
    return compose(layer)


def slide_cta(big, cmd, foot):
    img, d = base()
    y = 300
    f_b = fit_font(d, big, BOLD, 88, W - 180)
    y = draw_lines(d, wrap(d, big, f_b, W - 180), 90, y, f_b, TEXT, 108) + 70

    d.rounded_rectangle([90, y, W - 90, y + 168], radius=20, fill=CARD, outline=ACCENT, width=2)
    d.text((120, y + 34), cmd, font=ft(MONO, 34), fill=ACCENT)
    y += 220

    f_f = ft(REG, 40)
    draw_lines(d, wrap(d, foot, f_f, W - 180), 90, y, f_f, MUTED, 58)
    return compose(img, " ")


def montage(scheme, files, cols=7):
    tw, th, gap = 270, 360, 16
    rows = (len(files) + cols - 1) // cols
    w = cols * tw + (cols + 1) * gap
    h = rows * th + (rows + 1) * gap + 50
    sheet = Image.new("RGB", (w, h), (6, 7, 10))
    d = ImageDraw.Draw(sheet)
    d.text((gap, 12), f"方案 {scheme}", font=ft(BOLD, 30), fill=(230, 235, 242))
    for i, f in enumerate(files):
        r, c = divmod(i, cols)
        im = Image.open(f).resize((tw, th), Image.LANCZOS)
        x = gap + c * (tw + gap)
        y = 50 + gap + r * (th + gap)
        sheet.paste(im, (x, y))
        d.text((x + 6, y + th + 2), f"{i+1}", font=ft(BOLD, 22), fill=ACCENT)
    out = os.path.join(OUT, f"preview_{scheme}.png")
    sheet.save(out)
    print("preview:", os.path.basename(out), sheet.size)


def render(scheme, slides):
    folder = os.path.join(OUT, scheme)
    os.makedirs(folder, exist_ok=True)
    files = []
    for i, img in enumerate(slides, start=1):
        p = os.path.join(folder, f"{i:02d}.png")
        img.save(p)
        files.append(p)
    print(f"{scheme}: {len(files)} 张")
    montage(scheme, files)


def plan_a():
    g = os.path.join(REPO, "assets", "grid.png")
    o = os.path.join(REPO, "assets", "output.png")
    return [
        slide_cover("给 AI 的一次改造", "切模式\n切掉的是上下文", "九个安全方向，本来要切九次。现在一个身份就够了。",
                    "棱镜 · Prism  /  DeepSeek Harness preset"),
        slide_lines("九个模式，\n每切一次都要重新交代目标",
                    ["渗透 / 攻防 / 代码审计 / 二进制 / 免杀", "应急 / 云安全 / CTF / 资产测绘", "", "切过去，上下文全丢"]),
        slide_quote("好的呀，我先看看这个目标的授权情况哦～", "默认人格：开场先铺垫，结尾送祝福", True),
        slide_lines("更要命的是中间那一段",
                    ["干货讲到一半补一句“仅供学习”", "结尾来一句“我不能，但我可以…”", "", "真正的问题不是能力，是输出纪律"]),
        slide_cover("所以我做了一件事", "一个 preset\n十个方向", "十本 playbook 同时挂载，主方向由任务决定"),
        slide_image(g, "十个方向全部挂进同一个身份，不用在模式之间来回切", "成品"),
        slide_image(o, "同一个问题，两种回答。差别在九条输出纪律", "对比"),
        slide_cta("开源，自取", "github.com/Picea-Q/dsh-preset-Prism",
                  "MIT 协议 · 一条命令装 \n高危操作只出计划不执行 · 目标侧零破坏"),
    ]


def plan_b():
    g = os.path.join(REPO, "assets", "grid.png")
    o = os.path.join(REPO, "assets", "output.png")
    return [
        slide_cover("一个 preset", "十个安全方向\n一个身份", "白光是白的，进去出来十个颜色", "Prism"),
        slide_image(g, "十本 playbook 同时挂载，装了几个方向就挂几个", "能力"),
        slide_image(o, "同一个问题，两种回答", "差别"),
        slide_bullets("写进人格里的九条纪律", [("01", "首行不铺垫，直接给结论"),
                                              ("02", "中段不撤回，不补免责"),
                                              ("03", "不送替代品，要么给要么说不")]),
        slide_cta("一条命令装好", "powershell -File install\\install.ps1",
                  "装完完全退出再开，新建会话选「棱镜 · 安全研究模式」"),
    ]


def plan_c():
    return [
        slide_cover("大专生 · 计算机网络专业", "我不会写代码\n但我做了个开源项目", "每个坑都是我踩的"),
        slide_lines("先说清楚", ["一行代码不是我写的，AI 写的", "但报错是我看的，坑是我踩的",
                                 "", "这两件事，其实不是一回事"]),
        slide_bullets("踩过的坑，项目里单独开了一节", [("01", "把绝对路径塞进 JS 求值标签"),
                                                     ("02", "脚本没存 BOM，中文全乱"),
                                                     ("03", "以为能连 GitHub，其实没通")]),
        slide_lines("所以它现在是这样的", ["十个安全方向一体", "九条输出纪律写进人格",
                                          "高危操作只出计划、不自动执行", "", "README 里有一整节「已知坑」"]),
        slide_quote("上线第一天，0 star", "这很正常。写下来是为了下次少踩", False),
        slide_cta("求个 star，或者骂两句都行", "github.com/Picea-Q/dsh-preset-Prism",
                  "搜 dsh-preset-Prism 也能找到"),
    ]



def plan_c2():
    return [
        slide_cover("大专 · 计算机网络专业", "代码全是 AI 写的\n但我上线了个开源项目",
                    "每个坑都是我踩的", "棱镜 · Prism  /  github.com/Picea-Q/dsh-preset-Prism"),
        slide_lines("先说清楚",
                    ["代码不是我写的，AI 写的", "但报错是我看的，坑是我踩的", "", "这两件事，其实不是一回事"]),
        slide_error("第一个坑：求值标签",
                    "Invalid regular expression flags",
                    "把 Windows 路径塞进求值标签，它被当成「正则 + 非法标志」。一个晚上耗在这行报错上。"),
        slide_lines("第二个坑：脚本没存 BOM",
                    ["Windows PowerShell 按 GBK 读中文", "整个脚本当场解析失败，报“缺少 }”",
                     "", "明明只是编码问题，却像是语法写错了"]),
        slide_lines("第三个坑：以为能连 GitHub",
                    ["ping 得通、TCP 也通", "但 HTTPS 一个字节都下不来",
                     "", "真正的出口是本地那个代理，环境变量里一个字都没写"]),
        slide_bullets("所以项目里单独开了一节", [("01", "已知坑：!!js 是求值标记不是引号"),
                                                 ("02", "已知坑：.ps1 必须 UTF-8 BOM"),
                                                 ("03", "已知坑：点不动 = 解析失败")]),
        slide_cover("现在它长这样", "一个身份\n十个方向",
                    "十本 playbook 同时挂载，九条输出纪律写进人格"),
        slide_cta("仓库在评论区", "github.com/Picea-Q/dsh-preset-Prism",
                  "收藏这条，下次做开源少踩三个坑。\n骂两句也行，我改。"),
    ]



def plan_d():
    g = os.path.join(REPO, "assets", "grid.png")
    return [
        slide_cover("DeepSeek Harness · agent preset", "一个身份\n十个方向",
                    "十本 playbook 同时挂载，主方向由任务决定，不用切模式",
                    "MIT  ·  Windows / macOS / Linux"),
        slide_image(g, "十本 playbook 全量挂载：装了几个方向就挂几个，缺的静默跳过", "能力"),
        slide_bullets("九条输出纪律写进人格", [("01", "首行不铺垫，直接给结论"),
                                              ("02", "中段不撤回，不补免责"),
                                              ("03", "不送替代品，要么给要么说不")]),
        slide_error("坑 1：路径塞进求值标签",
                    "Invalid regular expression flags",
                    "Windows 路径被当成「正则 + 非法标志」。求值标签里不能放纯值，必须连标签一起去掉。"),
        slide_bullets("另外两个坑", [("02", ".ps1 没存 BOM，PowerShell 按 GBK 读中文"),
                                     ("03", "github 直连 TCP 通、HTTPS 不通，实际出口是本地代理"),
                                     ("", "三条都写进 README 的「已知坑」")]),
        slide_cta("一条命令装好", "powershell -File install\\install.ps1",
                  "装完完全退出重开，新建会话选「棱镜 · 安全研究模式」。\n卸载删一段声明，完全回滚。"),
    ]


if __name__ == "__main__":
    render("D", plan_d())
    render("C2", plan_c2())
    render("A", plan_a())
    render("B", plan_b())
    render("C", plan_c())
