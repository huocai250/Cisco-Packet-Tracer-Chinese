# Cisco Packet Tracer 简体中文汉化包 - 一键安装（Windows）
# 用法：右键“使用 PowerShell 运行”，或：
#   powershell -ExecutionPolicy Bypass -File .\scripts\install.ps1
$ErrorActionPreference = 'Stop'

# --- 需要管理员权限（要写入 Program Files） ---
$identity  = [Security.Principal.WindowsIdentity]::GetCurrent()
$isAdmin   = (New-Object Security.Principal.WindowsPrincipal($identity)).IsInRole(
                [Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host '需要管理员权限，正在重新启动…' -ForegroundColor Yellow
    Start-Process -FilePath 'powershell.exe' -Verb RunAs -ArgumentList @(
        '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', "`"$PSCommandPath`""
    )
    exit
}

# --- 定位 dist 目录（脚本所在目录的上一级） ---
$repoRoot = Split-Path -Parent (Split-Path -Parent $PSCommandPath)
$distDir  = Join-Path $repoRoot 'dist'
if (-not (Test-Path -LiteralPath (Join-Path $distDir 'Chinese_chi.ptl'))) {
    throw "找不到 $distDir\Chinese_chi.ptl，请确认脚本位于仓库的 scripts\ 目录下。"
}

# --- 定位 Packet Tracer 的 languages 目录 ---
$candidates = @(
    'D:\Program Files\Cisco Packet Tracer 9.0.1\languages',
    'C:\Program Files\Cisco Packet Tracer 9.0.1\languages',
    'D:\Program Files\Cisco Packet Tracer 9.0.0\languages',
    'C:\Program Files\Cisco Packet Tracer 9.0.0\languages'
)
$targetDir = $candidates | Where-Object { Test-Path -LiteralPath $_ } | Select-Object -First 1

if (-not $targetDir) {
    Write-Host '没有自动找到 Packet Tracer 的 languages 目录。' -ForegroundColor Yellow
    $input_path = Read-Host '请粘贴完整路径（例如 D:\Program Files\Cisco Packet Tracer 9.0.1\languages）'
    $targetDir = $input_path.Trim('"')
}
if (-not (Test-Path -LiteralPath $targetDir)) { throw "目录不存在：$targetDir" }

Write-Host "语言包来源：$distDir"
Write-Host "安装目标  ：$targetDir" -ForegroundColor Cyan

foreach ($name in @('Chinese_chi.ptl', 'Chinese_chi.ts')) {
    $src = Join-Path $distDir $name
    if (Test-Path -LiteralPath $src) {
        Copy-Item -LiteralPath $src -Destination (Join-Path $targetDir $name) -Force
        Write-Host "  已复制 $name" -ForegroundColor Green
    }
}

Write-Host ''
Write-Host '安装完成。接下来：' -ForegroundColor Cyan
Write-Host '  1. 完全退出并重新启动 Packet Tracer'
Write-Host '  2. Options -> Preferences -> Interface -> Language 选择 Chinese'
Write-Host '  3. 再次重启 Packet Tracer 生效'
Write-Host ''
Write-Host '提示：languages 目录里请只保留一个中文 .ptl，多余的条目会让语言列表出现重复项。'
Write-Host ''
Write-Host '按任意键退出…'
$null = $Host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown')
