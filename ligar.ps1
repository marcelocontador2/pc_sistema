$ErrorActionPreference = "Continue"
$base = "C:\Users\Marcelo Medeiros\pc_sistema"

Write-Host "=== 1. PostgreSQL ===" -ForegroundColor Cyan
$svc = Get-Service postgresql-x64-18 -ErrorAction SilentlyContinue
if (-not $svc) { Write-Host "Servico postgresql-x64-18 nao encontrado." -ForegroundColor Red; exit 1 }
if ($svc.Status -ne "Running") {
    Write-Host "Iniciando postgresql-x64-18..."
    try { Start-Service postgresql-x64-18 } catch { Write-Host "Falha ao iniciar (precisa de Admin)." -ForegroundColor Red; exit 1 }
    Start-Sleep -Seconds 3
}
Write-Host "PostgreSQL: $((Get-Service postgresql-x64-18).Status)" -ForegroundColor Green

Write-Host "=== 2. Detectar porta do PG (via netstat) ===" -ForegroundColor Cyan
$linha5433 = netstat -ano | findstr ":5433" | findstr "LISTENING"
$linha5432 = netstat -ano | findstr ":5432" | findstr "LISTENING"
if (-not $linha5433 -and -not $linha5432) { Write-Host "PG nao esta escutando em 5432/5433." -ForegroundColor Red; exit 1 }
if ($linha5433) { Write-Host "PG escutando na 5433" -ForegroundColor Gray } else { Write-Host "PG escutando na 5432" -ForegroundColor Gray }

Write-Host "=== 3. Liberar porta 9994 ===" -ForegroundColor Cyan
$conns = Get-NetTCPConnection -LocalPort 9994 -ErrorAction SilentlyContinue | Where-Object { $_.OwningProcess -gt 0 } | Select-Object -ExpandProperty OwningProcess -Unique
foreach ($procId in $conns) {
    Write-Host "Encerrando PID $procId na porta 9994..."
    Stop-Process -Id $procId -Force -ErrorAction SilentlyContinue
}
Start-Sleep -Seconds 2

Write-Host "=== 4. Iniciar API ===" -ForegroundColor Cyan
Start-Process -FilePath "$base\pc_venv\Scripts\python.exe" -ArgumentList "-m","uvicorn","main:app","--host","0.0.0.0","--port","9994" -WorkingDirectory "$base\pc_backend"
Start-Sleep -Seconds 5

Write-Host "=== 5. Testar ===" -ForegroundColor Cyan
try {
    $resp = Invoke-WebRequest -Uri "http://localhost:9994/periodos" -UseBasicParsing -TimeoutSec 10
    Write-Host "API OK (HTTP $($resp.StatusCode))" -ForegroundColor Green
    $periodos = $resp.Content | ConvertFrom-Json
    if ($periodos.Count -eq 0) {
        Write-Host "AVISO: /periodos retornou []." -ForegroundColor Yellow
    } else {
        Write-Host "Periodos encontrados: $($periodos.Count)" -ForegroundColor Green
    }
} catch {
    Write-Host "API ainda nao respondeu. Aguarde e teste http://localhost:9994" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "=== SISTEMA LIGADO ===" -ForegroundColor Green
Write-Host "Abra: http://localhost:9994" -ForegroundColor Green

