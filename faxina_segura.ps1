param([switch]$Executar)

$root = "C:\Users\Marcelo Medeiros\pc_sistema"
$dest = Join-Path $root "_backups_arquivo"
$log  = Join-Path $dest "move_log.txt"
$excluir = '\\\.git\\|\\pc_venv\\|\\__pycache__|\\_backups_arquivo\\|\\backup.*\\'

$arquivos = Get-ChildItem $root -Recurse -File -Filter "*.bak*" -ErrorAction SilentlyContinue |
  Where-Object { $_.FullName -notmatch $excluir }

Write-Host "`n📦 Encontrados: $($arquivos.Count) arquivos .bak_*" -ForegroundColor Cyan
if ($arquivos.Count -eq 0) { return }

Write-Host "`n📋 Amostra (primeiros 10):" -ForegroundColor Yellow
$arquivos | Select-Object -First 10 | ForEach-Object {
  Write-Host "   $($_.FullName.Substring($root.Length))"
}

$totalMB = [math]::Round(($arquivos | Measure-Object Length -Sum).Sum / 1MB, 2)
Write-Host "`n💾 Espaço total: $totalMB MB" -ForegroundColor Cyan

if (-not $Executar) {
  Write-Host "`n⚠️  DRY-RUN. Para mover de verdade:  .\faxina_segura.ps1 -Executar" -ForegroundColor Yellow
  return
}

New-Item -ItemType Directory -Force -Path $dest | Out-Null
"# faxina_segura.ps1 — $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" | Out-File $log -Encoding UTF8

$movidos = 0; $erros = 0
foreach ($f in $arquivos) {
  $rel = $f.FullName.Substring($root.Length).TrimStart('\').Replace('\','__')
  $target = Join-Path $dest $rel
  try {
    Move-Item -LiteralPath $f.FullName -Destination $target -Force -ErrorAction Stop
    "OK  $($f.FullName)  ->  $rel" | Out-File $log -Append -Encoding UTF8
    $movidos++
  } catch {
    "ERR $($f.FullName)  ::  $_" | Out-File $log -Append -Encoding UTF8
    $erros++
    Write-Host "   ❌ $($f.Name): $_" -ForegroundColor Red
  }
}
Write-Host "`n✅ Movidos: $movidos   ❌ Erros: $erros" -ForegroundColor Green
Write-Host "📄 Log: $log" -ForegroundColor Cyan
