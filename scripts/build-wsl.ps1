# ==============================================================================
# CODER-OS Local WSL Builder (Windows PowerShell)
# ==============================================================================

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "   CODER-OS 1.0 • Сборщик ISO через WSL                    " -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

# Check if WSL is available
$wslDistros = wsl --list --quiet 2>$null
if (-not $wslDistros) {
    Write-Host "[!] WSL не установлен или нет активных дистрибутивов." -ForegroundColor Yellow
    Write-Host "[i] Для установки Arch Linux в WSL выполните:" -ForegroundColor Yellow
    Write-Host "    wsl --install" -ForegroundColor White
    Write-Host "    или используйте GitHub Actions для автоматической сборки в облаке." -ForegroundColor White
    exit 1
}

$currentDir = Get-Location
$wslPath = "/mnt/" + $currentDir.Path.Substring(0, 1).ToLower() + $currentDir.Path.Substring(2).Replace('\', '/')

Write-Host "[✓] Путь в WSL: $wslPath" -ForegroundColor Green
Write-Host "[*] Запуск процесса сборки в WSL..." -ForegroundColor Cyan

wsl sudo bash -c "cd '$wslPath' && pacman -Syu --noconfirm archiso && bash ./scripts/build-iso.sh"

Write-Host "[✓] Процесс завершен! Проверьте папку out/" -ForegroundColor Green
