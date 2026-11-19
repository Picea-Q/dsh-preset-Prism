<#
.SYNOPSIS
  把「棱镜 · 安全研究模式」装进 DeepSeek Harness（写入 profile 的 preset 声明行）。

.DESCRIPTION
  做三件事：
    1. 读 preset/agent.cordis.yml
    2. 把 customSkillDirs 里的相对路径换成你机器上的绝对路径（只保留真实存在的目录）
    3. 往 ~/.dsh/profiles/<profile>/cordis.patch.yml 写一段 - insert: 声明（先备份、可重复执行）

.PARAMETER Profile
  profile 名。默认自动挑 desktop，否则取 profiles/ 下第一个。
#>
param([string]$Profile = "")

$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $PSScriptRoot
$SrcYml = Join-Path $Root "preset\agent.cordis.yml"
if (-not (Test-Path $SrcYml)) { throw "找不到 $SrcYml（请在仓库根目录里跑本脚本）" }

$DshHome = if ($env:DSH_HOME) { $env:DSH_HOME } else { Join-Path $env:USERPROFILE ".dsh" }
$ProfilesDir = Join-Path $DshHome "profiles"
if (-not (Test-Path $ProfilesDir)) { throw "找不到 $ProfilesDir —— 这台机器上似乎没有装 DSH" }

if (-not $Profile) {
    if (Test-Path (Join-Path $ProfilesDir "desktop")) { $Profile = "desktop" }
    else {
        $first = Get-ChildItem $ProfilesDir -Directory | Select-Object -First 1
        if (-not $first) { throw "profiles 目录是空的，先用 DSH 跑一次再装" }
        $Profile = $first.Name
    }
}

$Patch = Join-Path $ProfilesDir "$Profile\cordis.patch.yml"
if (-not (Test-Path $Patch)) { throw "找不到 $Patch —— profile '$Profile' 没有 patch 层" }

Write-Host "DSH_HOME : $DshHome"
Write-Host "profile  : $Profile"
Write-Host "patch    : $Patch"
Write-Host ""

$Begin = "# ---- dsh-prism preset begin（install 脚本生成，勿手改）----"
$End = "# ---- dsh-prism preset end ----"

$lines = [IO.File]::ReadAllLines($SrcYml, [Text.Encoding]::UTF8)
$body = New-Object 'System.Collections.Generic.List[string]'
$kept = 0
$skipped = 0

foreach ($line in $lines) {
    # 注释行原样保留：文件头注释里也写着 new URL('../<mode>/skills/', baseUrl)，
    # 不跳过就会被当成真配置处理，$Matches 抓到 "<mode>" 这种非法路径
    if ($line.TrimStart().StartsWith('#')) { $body.Add($line); continue }

    if ($line -match '^\s*dshHome:') { continue }

    if ($line -match '^\s*text: \|-') {
        $body.Add(($line -replace 'text:', 'prefix:'))
        continue
    }

    $indent = ""
    if ($line -match '^(\s*)-\s+!!js') { $indent = $Matches[1] }

    if ($line.Contains("new URL('skills/', baseUrl)")) {
        $abs = Join-Path $DshHome ".agent-presets\prism\skills"
        if (Test-Path $abs) { $body.Add($indent + '- "' + ($abs -replace '\\', '/') + '"'); $kept++ } else { $skipped++ }
        continue
    }

    if ($line -match "new URL\('\.\./([^/']+)/skills/', baseUrl\)") {
        $mode = $Matches[1]
        $abs = Join-Path $DshHome ".agent-presets\$mode\skills"
        if (Test-Path $abs) { $body.Add($indent + '- "' + ($abs -replace '\\', '/') + '"'); $kept++ } else { $skipped++ }
        continue
    }

    if ($line.Contains("shared/skills")) { continue }

    $body.Add($line)
}

Write-Host ("技能目录: 挂上 {0} 个，跳过 {1} 个不存在的" -f $kept, $skipped)
if ($kept -eq 0) {
    Write-Warning "一个技能目录都没找到 —— 先装 @dsh-external/dsh-redteam-model 那套 bundle，否则十本 playbook 全是空的"
}

$Description = '安全研究总控：Web/API 安全测试、代码审计、二进制分析、样本免杀研究、应急溯源、云与容器、CTF、资产映射等十个方向一体，十本 playbook 全量挂载，统一输出纪律，用于授权范围内的安全测试与风险验证。'

$decl = New-Object 'System.Collections.Generic.List[string]'
$decl.Add($Begin)
$decl.Add("- insert:")
$decl.Add("    - id: preset-prism")
$decl.Add("      name: '@deepseek-ai/dsh-agent-preset'")
$decl.Add("      config:")
$decl.Add("        id: prism")
$decl.Add("        name: 棱镜 · 安全研究模式")
$decl.Add("        description: '$Description'")
$decl.Add("        order: 95")
$decl.Add("        plugins:")
foreach ($l in $body) {
    if ($l.Trim().Length -eq 0) { $decl.Add("") } else { $decl.Add("            " + $l) }
}
$decl.Add($End)

$stamp = Get-Date -Format "yyyyMMdd-HHmmss"
Copy-Item $Patch "$Patch.bak-prism-$stamp" -Force
Write-Host "已备份 patch -> $Patch.bak-prism-$stamp"

$text = [IO.File]::ReadAllText($Patch, [Text.Encoding]::UTF8)
$block = ($decl -join "`n")

if ($text.Contains($Begin)) {
    $i = $text.IndexOf($Begin)
    $j = $text.IndexOf($End, $i)
    if ($j -lt 0) { throw "patch 里有 begin 标记但找不到 end 标记，先手工修一下" }
    $j += $End.Length
    $text = $text.Substring(0, $i) + $block + $text.Substring($j)
    Write-Host "已替换旧的声明块"
} else {
    $text = $text.TrimEnd() + "`n`n" + $block + "`n"
    Write-Host "已追加声明块"
}

[IO.File]::WriteAllText($Patch, $text, (New-Object Text.UTF8Encoding($false)))

Write-Host ""
Write-Host "装好了。下一步：" -ForegroundColor Green
Write-Host "  1) 完全退出 DeepSeek Harness（托盘也退出）再打开"
Write-Host "  2) 新建会话 -> 人格选择器选「棱镜 · 安全研究模式」"
Write-Host "  3) 说一句「在吗」，应该回：棱镜已校准。报目标。"
Write-Host ""
Write-Host "卸载：powershell -ExecutionPolicy Bypass -File install\uninstall.ps1"
