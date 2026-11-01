$ErrorActionPreference = 'Stop'
$dir = Split-Path -Parent $MyInvocation.MyCommand.Path
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

Write-Host ""
Write-Host "  ============================================" -ForegroundColor Cyan
Write-Host "   解阵求解器 · 剪贴板模式" -ForegroundColor White
Write-Host "  ============================================" -ForegroundColor Cyan

# ---- 读剪贴板图片 ----
$clip = $null
try { $clip = [System.Windows.Forms.Clipboard]::GetImage() } catch { $clip = $null }

if (-not $clip) {
    Write-Host ""
    Write-Host "  [X] 剪贴板里没有图片" -ForegroundColor Red
    Write-Host "      先按 Win+Shift+S 框选截图，再双击这个" -ForegroundColor DarkGray
    Write-Host ""
    Read-Host "按回车退出"
    exit 1
}

# 顺手清理三天前的临时图
Get-ChildItem $env:TEMP -Filter 'jx3_*.png' -ErrorAction SilentlyContinue |
    Where-Object { $_.LastWriteTime -lt (Get-Date).AddDays(-3) } |
    Remove-Item -Force -ErrorAction SilentlyContinue

$tmp = Join-Path $env:TEMP ("jx3_" + (Get-Date -Format 'yyyyMMdd_HHmmss') + ".png")
$clip.Save($tmp, [System.Drawing.Imaging.ImageFormat]::Png)
$cw = $clip.Width; $ch = $clip.Height
$clip.Dispose()
Write-Host "  已读取剪贴板图片：$cw x $ch" -ForegroundColor Gray
Write-Host ""

# ---- 找 Python ----
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
    Write-Host "  [X] 没找到 Python" -ForegroundColor Red
    Read-Host "按回车退出"
    exit 1
}

$env:PYTHONUTF8 = '1'
$env:PYTHONIOENCODING = 'utf-8'

& $py (Join-Path $dir 'auto_solve.py') $tmp
$code = $LASTEXITCODE

Write-Host ""
if ($code -eq 0) {
    $outFile = $tmp -replace '\.png$', '_answer.png'
    if (Test-Path -LiteralPath $outFile) {
        Write-Host "  答案图已生成，正在打开…" -ForegroundColor Green
        Start-Sleep -Milliseconds 200
        Start-Process -FilePath $outFile
        Start-Sleep -Milliseconds 600
        exit 0
    }
}

Write-Host "  没识别成功" -ForegroundColor Yellow
Write-Host "  可能是截图没框全棋盘，或者棋盘被 UI 挡住了" -ForegroundColor DarkGray
Write-Host ""
Read-Host "按回车退出"
exit 1