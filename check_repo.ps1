$lixo = git status --short | Select-String "_backup_|\.bak_|_ver_|_fix_|\.dump|\.db$|temp_downloads|\.env"
if ($lixo) {
    Write-Host "[ATENCAO] Lixo detectado no staging:" -ForegroundColor Yellow
    $lixo | ForEach-Object { Write-Host "  $_" -ForegroundColor Red }
    Write-Host "`nRode 'git reset' e ajuste o .gitignore." -ForegroundColor Yellow
    exit 1
}
Write-Host "[OK] Repo limpo - pode commitar" -ForegroundColor Green
