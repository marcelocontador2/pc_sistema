$p = 'ligar.ps1'
with open(p, 'r', encoding='utf-8') as f:
    s = f.read()

old_block = '''Write-Host "=== 1. PostgreSQL ===" -ForegroundColor Cyan
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
if ($linha5433) { Write-Host "PG escutando na 5433" -ForegroundColor Gray } else { Write-Host "PG escutando na 5432" -ForegroundColor Gray }'''

new_block = '''Write-Host "=== 1. PostgreSQL ===" -ForegroundColor Cyan
# Verifica primeiro se a porta ja esta ativa (pode ter sido iniciado via pg_ctl)
$p = netstat -ano | findstr ":5433" | findstr "LISTENING"
if ($p) {
    Write-Host "PostgreSQL ja esta rodando na porta 5433." -ForegroundColor Green
} else {
    Write-Host "PG nao detectado. Tentando iniciar via Servico..."
    try { 
        Start-Service postgresql-x64-18 -ErrorAction Stop
        Start-Sleep -Seconds 3
    } catch { 
        Write-Host "Sem permissao de Admin. Tentando iniciar via pg_ctl..."
        & "C:\Program Files\PostgreSQL\18\bin\pg_ctl.exe" -D "C:\Program Files\PostgreSQL\18\data" -l "C:\temp\pg_auto.log" start
        Start-Sleep -Seconds 3
    }
}

Write-Host "=== 2. Detectar porta do PG (via netstat) ===" -ForegroundColor Cyan
$linha5433 = netstat -ano | findstr ":5433" | findstr "LISTENING"
$linha5432 = netstat -ano | findstr ":5432" | findstr "LISTENING"
if (-not $linha5433 -and -not $linha5432) { Write-Host "PG nao esta escutando em 5432/5433." -ForegroundColor Red; exit 1 }
if ($linha5433) { Write-Host "PG escutando na 5433" -ForegroundColor Gray } else { Write-Host "PG escutando na 5432" -ForegroundColor Gray }'''

if old_block not in s:
    print('ERRO: bloco antigo nao encontrado no ligar.ps1')
    raise SystemExit(1)

s = s.replace(old_block, new_block)
with open(p, 'w', encoding='utf-8') as f:
    f.write(s)
print('OK: ligar.ps1 reescrito com logica inteligente de PG')
