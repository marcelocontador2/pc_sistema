$ErrorActionPreference = "Stop"
$base = "C:\Users\Marcelo Medeiros\pc_sistema"
$ts = Get-Date -Format "yyyyMMdd_HHmmss"
$dest = "$base\backups\backup_$ts"
New-Item -ItemType Directory -Path $dest -Force | Out-Null

Write-Host "=== Iniciando Backup ===" -ForegroundColor Cyan

# pg_dump
$pgDump = $null
$pgRoots = Get-ChildItem "C:\Program Files\PostgreSQL" -Directory -ErrorAction SilentlyContinue | Sort-Object Name -Descending
foreach ($r in $pgRoots) {
    $cand = Join-Path $r.FullName "bin\pg_dump.exe"
    if (Test-Path $cand) { $pgDump = $cand; break }
}
if (-not $pgDump) { Write-Host "pg_dump nao encontrado." -ForegroundColor Red; exit 1 }

$env:PGPASSWORD = "pc_admin_2026"
& $pgDump -h localhost -p 5433 -U postgres -d pc_database -F c -f "$dest\pc_database.dump"
$env:PGPASSWORD = ""
Write-Host "Banco exportado!" -ForegroundColor Green

function Zip-Pasta($origem, $destinoZip) {
    $tmp = Join-Path $env:TEMP ("bkp_" + [guid]::NewGuid().ToString("N"))
    robocopy $origem $tmp /E /XD "__pycache__" ".git" "node_modules" "pc_venv" /NFL /NDL /NJH /NJS /NP | Out-Null
    if (Test-Path $destinoZip) { Remove-Item $destinoZip -Force }
    Compress-Archive -Path "$tmp\*" -DestinationPath $destinoZip -CompressionLevel Optimal -Force
    Remove-Item $tmp -Recurse -Force
}
Zip-Pasta "$base\pc_backend"  "$dest\pc_backend.zip"
Zip-Pasta "$base\pc_frontend" "$dest\pc_frontend.zip"
Zip-Pasta "$base\pc_storage"  "$dest\pc_storage.zip"
Copy-Item "$base\ligar.ps1" -Destination $dest -ErrorAction SilentlyContinue

$readme = @"
BACKUP - $ts
Local: $dest

RESTAURAR:
1) pg_restore -h localhost -p 5433 -U postgres -d pc_database -c --if-exists "$dest\pc_database.dump"
2) Expandir os 3 arquivos zip (pc_backend, pc_frontend, pc_storage).
"@
Set-Content -Path "$dest\RESTORE.txt" -Value $readme -Encoding UTF8

$sizeTotal = [math]::Round(((Get-ChildItem $dest -Recurse | Measure-Object Length -Sum).Sum) / 1MB, 1)
Write-Host "`n=== BACKUP CONCLUIDO: $sizeTotal MB ===" -ForegroundColor Green
Write-Host "Pasta: $dest" -ForegroundColor Green