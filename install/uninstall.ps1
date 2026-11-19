<#
.SYNOPSIS
  从 DeepSeek Harness 里卸载「十面安全研究模式」（只删自己那一段声明）。
#>
param([string]$Profile = "")

$ErrorActionPreference = "Stop"

$DshHome = if ($env:DSH_HOME) { $env:DSH_HOME } else { Join-Path $env:USERPROFILE ".dsh" }
$ProfilesDir = Join-Path $DshHome "profiles"
if (-not (Test-Path $ProfilesDir)) { throw "找不到 $ProfilesDir" }

if (-not $Profile) {
    if (Test-Path (Join-Path $ProfilesDir "desktop")) { $Profile = "desktop" }
    else {
        $first = Get-ChildItem $ProfilesDir -Directory | Select-Object -First 1
        if (-not $first) { throw "profiles 目录是空的" }
        $Profile = $first.Name
    }
}

$Patch = Join-Path $ProfilesDir "$Profile\cordis.patch.yml"
if (-not (Test-Path $Patch)) { throw "找不到 $Patch" }

$Begin = "# ---- shi-mian preset begin（install 脚本生成，勿手改）----"
$End = "# ---- shi-mian preset end ----"

$text = [IO.File]::ReadAllText($Patch, [Text.Encoding]::UTF8)
if (-not $text.Contains($Begin)) {
    Write-Host "patch 里没有十面的声明块，无需卸载"
    exit 0
}

$stamp = Get-Date -Format "yyyyMMdd-HHmmss"
Copy-Item $Patch "$Patch.bak-shimian-uninstall-$stamp" -Force

$i = $text.IndexOf($Begin)
$j = $text.IndexOf($End, $i)
if ($j -lt 0) { throw "有 begin 没 end，手工修一下" }
$j += $End.Length

$text = ($text.Substring(0, $i).TrimEnd() + "`n" + $text.Substring($j).TrimStart())
[IO.File]::WriteAllText($Patch, $text, (New-Object Text.UTF8Encoding($false)))

Write-Host "已移除十面声明块（备份 $Patch.bak-shimian-uninstall-$stamp）" -ForegroundColor Green
Write-Host "完全退出 DSH 再打开，选择器里就没有它了"
