$ErrorActionPreference = "Continue"
$base = "C:\Users\Marcelo Medeiros\pc_sistema"

Write-Host "=== 1. PostgreSQL ===" -ForegroundColor Cyan
$svc = Get-Service postgresql-x64-18 -ErrorAction SilentlyContinue
if (-not $svc) {
    Write-Host "Servico postgresql-x64-18 nao encontrado." -ForegroundColor Red
    exit 1
}
if ($svc.Status -ne "Running") {
    Write-Host "Iniciando postgresql-x64-18..."
    try { Start-Service postgresql-x64-18 } catch {
        Write-Host "Falha ao iniciar (precisa de Administrador). Rode este script como Admin." -ForegroundColor Red
        exit 1
    }
    Start-Sleep -Seconds 3
}
Write-Host "PostgreSQL: $((Get-Service postgresql-x64-18).Status)" -ForegroundColor Green

Write-Host "=== 2. Detectar porta do PG ===" -ForegroundColor Cyan
$ports = Get-NetTCPConnection -LocalPort 5432,5433 -State Listen -ErrorAction SilentlyContinue | Select-Object -ExpandProperty LocalPort -Unique
if (-not $ports) { Write-Host "PG nao esta escutando em 5432/5433." -ForegroundColor Red; exit 1 }
Write-Host "Portas: $($ports -join ', ')" -ForegroundColor Gray

$portaReal = if ($ports -contains 5433) { 5433 } elseif ($ports -contains 5432) { 5432 } else { 0 }
$match = Select-String -Path "$base\pc_backend\main.py" -Pattern '"port":\s*(\d+)' | Select-Object -First 1
$portaAtual = if ($match) { $match.Matches.Groups[1].Value } else { "" }
if ($portaAtual -and $portaAtual -ne "$portaReal") {
    Write-Host "Ajustando porta no codigo: $portaAtual -> $portaReal" -ForegroundColor Yellow
    (Get-Content "$base\pc_backend\main.py") -replace '"port":\s*\d+', "`"port`": $portaReal" | Set-Content "$base\pc_backend\main.py"
    (Get-Content "$base\pc_backend\app\ingestion\ingestor_unificado.py") -replace '"port":\s*\d+', "`"port`": $portaReal" | Set-Content "$base\pc_backend\app\ingestion\ingestor_unificado.py"
}

Write-Host "=== 3. Liberar porta 8000 ===" -ForegroundColor Cyan
$conn = Get-NetTCPConnection -LocalPort 8000 -State Listen -ErrorAction SilentlyContinue
if ($conn) {
    $procIds = $conn.OwningProcess | Select-Object -Unique
    foreach ($procId in $procIds) {
        Write-Host "Encerrando PID $procId na porta 8000..."
        Stop-Process -Id $procId -Force -ErrorAction SilentlyContinue
    }
    Start-Sleep -Seconds 2
}

Write-Host "=== 4. Iniciar API ===" -ForegroundColor Cyan
Start-Process -FilePath "$base\pc_venv\Scripts\python.exe" -ArgumentList "main.py" -WorkingDirectory "$base\pc_backend"
Start-Sleep -Seconds 5

Write-Host "=== 5. Testar ===" -ForegroundColor Cyan
try {
    $resp = Invoke-WebRequest -Uri "http://localhost:8000/periodos" -UseBasicParsing -TimeoutSec 8
    Write-Host "API OK (HTTP $($resp.StatusCode))" -ForegroundColor Green
    $periodos = $resp.Content | ConvertFrom-Json
    if ($periodos.Count -eq 0) {
        Write-Host "AVISO: /periodos retornou []. Rode o ingestor:" -ForegroundColor Yellow
        Write-Host "  cd '$base\pc_backend\app\ingestion'; ..\..\..\pc_venv\Scripts\python.exe ingestor_unificado.py" -ForegroundColor Yellow
    } else {
        Write-Host "Periodos encontrados: $($periodos.Count)" -ForegroundColor Green
    }
} catch {
    Write-Host "API ainda nao respondeu. Aguarde alguns segundos e teste http://localhost:8000" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "=== SISTEMA LIGADO ===" -ForegroundColor Green
Write-Host "Abra: http://localhost:8000" -ForegroundColor Green