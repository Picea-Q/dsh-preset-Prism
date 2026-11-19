#!/usr/bin/env python3
"""把「棱镜 · 安全研究模式」装进 DeepSeek Harness（macOS / Linux / Windows 通用）。

做三件事：
  1. 读 preset/agent.cordis.yml
  2. 把 customSkillDirs 的相对路径换成绝对路径（只保留真实存在的目录）
  3. 往 <dsh>/profiles/<profile>/cordis.patch.yml 写一段 - insert: 声明（先备份、可重复执行）
"""

import os
import shutil
import sys
import time
from pathlib import Path

BEGIN = "# ---- dsh-prism preset begin（install 脚本生成，勿手改）----"
END = "# ---- dsh-prism preset end ----"

DESC = ("安全研究总控：Web/API 安全测试、代码审计、二进制分析、样本免杀研究、应急溯源、"
        "云与容器、CTF、资产映射等十个方向一体，十本 playbook 全量挂载，统一输出纪律，"
        "用于授权范围内的安全测试与风险验证。")


def find_profile(profiles_dir: Path) -> str:
    if (profiles_dir / "desktop").is_dir():
        return "desktop"
    for p in sorted(profiles_dir.iterdir()):
        if p.is_dir():
            return p.name
    raise SystemExit(f"{profiles_dir} 是空的，先用 DSH 跑一次再装")


def main() -> int:
    root = Path(__file__).resolve().parent.parent
    src = root / "preset" / "agent.cordis.yml"
    if not src.is_file():
        raise SystemExit(f"找不到 {src}")

    dsh_home = Path(os.environ.get("DSH_HOME", Path.home() / ".dsh")).expanduser()
    profiles = dsh_home / "profiles"
    if not profiles.is_dir():
        raise SystemExit(f"找不到 {profiles} —— 这台机器上似乎没有装 DSH")

    profile = sys.argv[1] if len(sys.argv) > 1 else find_profile(profiles)
    patch = profiles / profile / "cordis.patch.yml"
    if not patch.is_file():
        raise SystemExit(f"找不到 {patch}")

    print(f"DSH_HOME : {dsh_home}")
    print(f"profile  : {profile}")
    print(f"patch    : {patch}")

    body, kept, skipped = [], 0, 0
    for line in src.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        # 注释行原样保留：文件头注释里也写着 new URL('../<mode>/skills/', baseUrl)
        if stripped.startswith("#"):
            body.append(line)
            continue
        if stripped.startswith("dshHome:"):
            continue
        if stripped.startswith("text: |-"):
            body.append(line.replace("text:", "prefix:", 1))
            continue

        indent = line[: len(line) - len(line.lstrip())] if stripped.startswith("- !!js") else ""

        if "new URL('skills/', baseUrl)" in line:
            target = dsh_home / ".agent-presets" / "prism" / "skills"
            if target.is_dir():
                body.append(f'{indent}- "{target.as_posix()}"')
                kept += 1
            else:
                skipped += 1
            continue

        if "../" in line and "/skills/" in line and "baseUrl" in line:
            seg = line.split("new URL('../", 1)[1].split("/skills/", 1)[0]
            target = dsh_home / ".agent-presets" / seg / "skills"
            if target.is_dir():
                body.append(f'{indent}- "{target.as_posix()}"')
                kept += 1
            else:
                skipped += 1
            continue

        if "shared/skills" in line:
            continue

        body.append(line)

    print(f"技能目录: 挂上 {kept} 个，跳过 {skipped} 个不存在的")
    if kept == 0:
        print("警告: 一个技能目录都没找到，先装 @dsh-external/dsh-redteam-model 那套 bundle")

    decl = [
        BEGIN,
        "- insert:",
        "    - id: preset-prism",
        "      name: '@deepseek-ai/dsh-agent-preset'",
        "      config:",
        "        id: prism",
        "        name: 棱镜 · 安全研究模式",
        f"        description: '{DESC}'",
        "        order: 95",
        "        plugins:",
    ]
    for line in body:
        decl.append("            " + line if line.strip() else "")
    decl.append(END)
    block = "\n".join(decl)

    shutil.copy2(patch, patch.with_suffix(f".yml.bak-prism-{time.strftime('%Y%m%d-%H%M%S')}"))

    text = patch.read_text(encoding="utf-8")
    if BEGIN in text:
        head = text[: text.index(BEGIN)]
        tail = text[text.index(END) + len(END):]
        text = head + block + tail
        print("已替换旧的声明块")
    else:
        text = text.rstrip() + "\n\n" + block + "\n"
        print("已追加声明块")

    patch.write_text(text, encoding="utf-8")
    print("\n装好了。下一步：")
    print("  1) 完全退出 DeepSeek Harness 再打开")
    print("  2) 新建会话 -> 人格选择器选「棱镜 · 安全研究模式」")
    print("  3) 说一句「在吗」，应该回：棱镜已校准。报目标。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
