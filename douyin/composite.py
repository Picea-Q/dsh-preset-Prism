"""把 Sora 生成的画面 + 本地渲染的文字层合成一条成片。

用法:
    python composite.py --video sora.mp4
    python composite.py --video sora.mp4 --text video\\prism_promo.mp4 --out out.mp4

原理：文字层是「纯黑底 + 亮字」，用 blend=screen 叠加时黑色不贡献任何亮度，
等于自动透明，不依赖 alpha 通道，也不用绿幕。

参数可选：
    --crop-fit   素材比例不是 9:16 时，按 cover 裁切（默认）
    --fit-pad    改为留黑边（contain）
    --dim 0.25   把素材整体压暗 25%，保证白字可读
"""

import argparse
import os
import shutil
import subprocess
import sys

W, H = 1080, 1920


def find_ffmpeg():
    p = shutil.which("ffmpeg")
    if p:
        return p, shutil.which("ffprobe") or p.replace("ffmpeg", "ffprobe")
    base = os.path.expandvars(
        r"%LOCALAPPDATA%\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-9.0.2-full_build\bin"
    )
    return os.path.join(base, "ffmpeg.exe"), os.path.join(base, "ffprobe.exe")


def probe(path, ffprobe):
    out = subprocess.run(
        [ffprobe, "-v", "error", "-select_streams", "v:0",
         "-show_entries", "stream=width,height,r_frame_rate,duration",
         "-of", "default=nw=1", path],
        capture_output=True, text=True,
    ).stdout
    info = {}
    for line in out.splitlines():
        if "=" in line:
            k, v = line.split("=", 1)
            info[k] = v
    return info


def build_filter(dim, fit):
    scale = (
        f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H}"
        if fit == "crop" else
        f"scale={W}:{H}:force_original_aspect_ratio=decrease,pad={W}:{H}:(ow-iw)/2:(oh-ih)/2:black"
    )
    chain = f"[0:v]{scale},setsar=1,fps=25"
    if dim > 0:
        chain += f",colorlevels=rimax={1-dim:.2f}:gimax={1-dim:.2f}:bimax={1-dim:.2f}"
    chain += ",setsar=1[bg];[bg][1:v]blend=all_mode=screen:shortest=1[out]"
    return chain


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--video", required=True, help="Sora 生成的画面")
    ap.add_argument("--text", default=os.path.join("video", "prism_promo.mp4"),
                    help="文字层（黑底亮字），默认用本地渲染那版")
    ap.add_argument("--out", default=os.path.join("video", "prism_final.mp4"))
    ap.add_argument("--dim", type=float, default=0.20, help="素材压暗比例 0~0.6")
    ap.add_argument("--fit", choices=["crop", "pad"], default="crop")
    args = ap.parse_args()

    ffmpeg, ffprobe = find_ffmpeg()
    for p in (args.video, args.text):
        if not os.path.isfile(p):
            sys.exit(f"找不到文件: {p}")

    bg = probe(args.video, ffprobe)
    tx = probe(args.text, ffprobe)
    print(f"画面: {bg.get('width')}x{bg.get('height')} {bg.get('duration','?')}s")
    print(f"文字层: {tx.get('width')}x{tx.get('height')} {tx.get('duration','?')}s")

    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    cmd = [
        ffmpeg, "-y",
        "-i", args.video,
        "-i", args.text,
        "-filter_complex", build_filter(args.dim, args.fit),
        "-map", "[out]",
        "-c:v", "libx264", "-preset", "medium", "-crf", "19",
        "-pix_fmt", "yuv420p", "-movflags", "+faststart",
        "-an",
        args.out,
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stderr[-1800:])
        sys.exit("ffmpeg 失败")
    print(f"输出: {args.out}  {os.path.getsize(args.out)/1024/1024:.1f} MB")


if __name__ == "__main__":
    main()
