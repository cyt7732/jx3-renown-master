param([string]$Image)

$ErrorActionPreference = 'Stop'
$dir = Split-Path -Parent $MyInvocation.MyCommand.Path
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

# 没指定图片时，自动挑目录里最新的一张截图（排除结果图）
if (-not $Image) {
    $pick = Get-ChildItem -LiteralPath $dir -Filter '*.png' -ErrorAction SilentlyContinue |
        Where-Object { $_.Name -notmatch '_answer\.png$' } |
        Sort-Object LastWriteTime -Descending |
        Select-Object -First 1
    if ($pick) { $Image = $pick.FullName }
}

if (-not $Image -or -not (Test-Path -LiteralPath $Image)) {
    Write-Host ""
    Write-Host "  [X] 这个文件夹里没找到截图" -ForegroundColor Red
    Write-Host "      把游戏截图存到这里，或者直接拖到 一键求解.bat 上" -ForegroundColor DarkGray
    Write-Host ""
    Read-Host "按回车退出"
    exit 1
}

# 找一个能用的 Python
$py = $null
$cands = @()
$cmd = Get-Command python -ErrorAction SilentlyContinue
if ($cmd) { $cands += $cmd.Source }
$cands += "$env:LOCALAPPDATA\Programs\Python\Python314\python.exe"
$cands += "$env:USERPROFILE\.dsh\dsh-runtimes\dsh-primary-runtime\dependencies\python\python.exe"
foreach ($c in $cands) {
    if ($c -and (Test-Path -LiteralPath $c)) { $py = $c; break }
}

if (-not $py) {
    Write-Host ""
    Write-Host "  [X] 没找到 Python，可以直接双击 index.html 用网页版" -ForegroundColor Red
    Write-Host ""
    Read-Host "按回车退出"
    exit 1
}

$env:PYTHONUTF8 = '1'
$env:PYTHONIOENCODING = 'utf-8'

Write-Host ""
Write-Host "  ============================================" -ForegroundColor Cyan
Write-Host "   解阵求解器" -ForegroundColor White
Write-Host "  ============================================" -ForegroundColor Cyan
Write-Host "   正在识别：$(Split-Path -Leaf $Image)" -ForegroundColor Gray
Write-Host ""

& $py (Join-Path $dir 'auto_solve.py') $Image
$code = $LASTEXITCODE

Write-Host ""
if ($code -eq 0) {
    Write-Host "   结果图已保存在图片旁边（文件名带 _answer）" -ForegroundColor Green
} else {
    Write-Host "   没识别成功，可以改用 index.html 网页版手动点" -ForegroundColor Yellow
}
Write-Host ""
Read-Host "按回车退出"