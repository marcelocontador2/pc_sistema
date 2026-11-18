# ============================================================================
# salvar_tudo.ps1 — commit + push + ZIP + tag
# Uso: .\salvar_tudo.ps1 "mensagem do commit"
# ============================================================================
param(
    [Parameter(Position=0)]
    [string]$Msg = "chore: salva progresso $(Get-Date -Format 'yyyyMMdd_HHmmss')"
)

$ErrorActionPreference = "Stop"
Set-Location "C:\Users\Marcelo Medeiros\pc_sistema"
$ts = Get-Date -Format "yyyyMMdd_HHmmss"

# ----------------------------------------------------------------------------
# [1] Estado atual
# ----------------------------------------------------------------------------
Write-Host "`n[1] git status..." -ForegroundColor Cyan
git status --short

$temMudanca = git status --porcelain
if (-not $temMudanca) {
    Write-Host "  Nada para commitar." -ForegroundColor Yellow
} else {
    # ------------------------------------------------------------------------
    # [2] add + commit
    # ------------------------------------------------------------------------
    Write-Host "`n[2] git add -A..." -ForegroundColor Cyan
    git add -A

    Write-Host "`n[3] git commit..." -ForegroundColor Cyan
    git commit -m $Msg
}

# ----------------------------------------------------------------------------
# [4] push
# ----------------------------------------------------------------------------
Write-Host "`n[4] git push..." -ForegroundColor Cyan
$branch = (git rev-parse --abbrev-ref HEAD).Trim()
$remotes = git remote
if ($remotes) {
    git push origin $branch
} else {
    Write-Host "  [AVISO] Sem remote configurado — commit local apenas." -ForegroundColor Yellow
}

# ----------------------------------------------------------------------------
# [5] ZIP de backup (fora do repo, em ~/pc_sistema_backups/)
# ----------------------------------------------------------------------------
Write-Host "`n[5] Criando ZIP de backup..." -ForegroundColor Cyan
$backupDir = "$env:USERPROFILE\pc_sistema_backups"
New-Item -ItemType Directory -Force -Path $backupDir | Out-Null
$zipNome = "$backupDir\pc_sistema_$ts.zip"

$excluir = @("pc_venv", ".git", "node_modules", "__pycache__", "_tmp", "_backups_zip", "_backups_arquivo", "_arquivo_20261031", "quarentena_20261117_1242", "template_original_1011")
$itens = Get-ChildItem -Path "." -Force | Where-Object {
    $excluir -notcontains $_.Name -and $_.Name -notlike "_backup_*.zip"
}

Compress-Archive -Path $itens.FullName -DestinationPath $zipNome -CompressionLevel Optimal -Force
$tamanhoMB = [math]::Round((Get-Item $zipNome).Length / 1MB, 2)
Write-Host "  [OK] $zipNome ($tamanhoMB MB)" -ForegroundColor Green

# ----------------------------------------------------------------------------
# [6] Tag de release (opcional — descomente se quiser)
# ----------------------------------------------------------------------------
# $tag = "v0.3.0-dvp-$ts"
# Write-Host "`n[6] git tag $tag..." -ForegroundColor Cyan
# git tag -a $tag -m "Release: tabela DVP melhorada + config centralizado"
# git push origin $tag

# ----------------------------------------------------------------------------
# [7] Resumo
# ----------------------------------------------------------------------------
Write-Host "`n============================================================" -ForegroundColor Magenta
Write-Host " RESUMO" -ForegroundColor Magenta
Write-Host "============================================================" -ForegroundColor Magenta
Write-Host " Commit : $Msg" -ForegroundColor White
Write-Host " Branch : $branch" -ForegroundColor White
Write-Host " ZIP    : $zipNome ($tamanhoMB MB)" -ForegroundColor White
Write-Host " Data   : $ts" -ForegroundColor White
Write-Host "============================================================" -ForegroundColor Magenta

Write-Host "`nUltimos 5 commits:" -ForegroundColor Cyan
git log --oneline -5

Write-Host "`nBackups em $backupDir :" -ForegroundColor Cyan
Get-ChildItem $backupDir -Filter "*.zip" | Sort-Object LastWriteTime -Descending | Select-Object -First 5 | Format-Table Name, @{N='MB';E={[math]::Round($_.Length/1MB,2)}}, LastWriteTime
