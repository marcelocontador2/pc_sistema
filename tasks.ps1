# ============================================================================
# tasks.ps1 - Ponto unico de entrada para operacoes do pc_sistema
#
# Uso:
#   .\tasks.ps1 test              # roda pytest
#   .\tasks.ps1 test -v           # pytest verboso
#   .\tasks.ps1 import            # smoke test dos routers
#   .\tasks.ps1 backup            # ZIP de backup
#   .\tasks.ps1 commit "msg"      # commit + push + ZIP
#   .\tasks.ps1 run               # sobe uvicorn (porta 8010)
#   .\tasks.ps1 clean             # limpa caches
#   .\tasks.ps1 check             # verifica lixo antes de commitar
#   .\tasks.ps1 status            # git status + ultimos commits
#   .\tasks.ps1 install           # pip install requirements
# ============================================================================
param(
    [Parameter(Position=0)]
    [ValidateSet("test","import","backup","commit","run","clean","check","status","install","help")]
    [string]$Cmd = "help",

    [Parameter(Position=1)]
    [string]$Arg = "",

    [switch]$v
)

$ErrorActionPreference = "Stop"
Set-Location "C:\Users\Marcelo Medeiros\pc_sistema"
$pyExe = "pc_venv\Scripts\python.exe"
$pipExe = "pc_venv\Scripts\pip.exe"

function Write-Header($msg) {
    Write-Host "`n=== $msg ===" -ForegroundColor Cyan
}

function Write-OK($msg) {
    Write-Host "[OK] $msg" -ForegroundColor Green
}

function Write-Err($msg) {
    Write-Host "[ERRO] $msg" -ForegroundColor Red
}

switch ($Cmd) {

    "test" {
        Write-Header "Rodando pytest"
        if ($v) {
            & $pyExe -m pytest pc_backend/tests/ -v
        } else {
            & $pyExe -m pytest pc_backend/tests/
        }
        if ($LASTEXITCODE -eq 0) { Write-OK "Todos os testes passaram" }
    }

    "import" {
        Write-Header "Smoke test dos routers"
        & $pyExe -c @"
routers = ['analise_financeira', 'analise_orcamentaria', 'bp', 'dfc', 'dmpl', 'integridade', 'dvp', 'despesas', 'receitas']
falhas = 0
for r in routers:
    try:
        mod = __import__(f'pc_backend.app.routers.{r}', fromlist=['router'])
        n = len(mod.router.routes)
        print(f'[OK] {r}: {n} rotas')
    except Exception as e:
        print(f'[ERRO] {r}: {e}')
        falhas += 1
if falhas == 0:
    print(f'\n[OK] {len(routers)} routers importados')
else:
    print(f'\n[ERRO] {falhas} falhas')
    exit(1)
"@
    }

    "backup" {
        Write-Header "Criando ZIP de backup"
        $ts = Get-Date -Format "yyyyMMdd_HHmmss"
        $backupDir = "$env:USERPROFILE\pc_sistema_backups"
        New-Item -ItemType Directory -Force -Path $backupDir | Out-Null
        $zipNome = "$backupDir\pc_sistema_$ts.zip"

        $excluir = @("pc_venv", ".git", "node_modules", "__pycache__", "_tmp", "_backups_zip", "_backups_arquivo", "_arquivo_20261031", "quarentena_20261117_1242", "template_original_1011", ".pytest_cache")
        $itens = Get-ChildItem -Path "." -Force | Where-Object {
            $excluir -notcontains $_.Name -and $_.Name -notlike "_backup_*.zip" -and $_.Name -notlike "_teste_*"
        }

        Compress-Archive -Path $itens.FullName -DestinationPath $zipNome -CompressionLevel Optimal -Force
        $tamanhoMB = [math]::Round((Get-Item $zipNome).Length / 1MB, 2)
        Write-OK "$zipNome ($tamanhoMB MB)"
    }

    "commit" {
        if (-not $Arg) {
            Write-Err "Uso: .\tasks.ps1 commit 'sua mensagem'"
            exit 1
        }
        Write-Header "Commit + push + backup"
        $ts = Get-Date -Format "yyyyMMdd_HHmmss"
        $msg = "$Arg ($ts)"

        $temMudanca = git status --porcelain
        if (-not $temMudanca) {
            Write-Host "  Nada para commitar." -ForegroundColor Yellow
        } else {
            git add -A
            git commit -m $msg
            if ($LASTEXITCODE -ne 0) {
                Write-Err "Commit falhou"
                exit 1
            }
            Write-OK "Commit criado: $msg"
        }

        $branch = (git rev-parse --abbrev-ref HEAD).Trim()
        $remotes = git remote
        if ($remotes) {
            git push origin $branch
            Write-OK "Push para origin/$branch"
        } else {
            Write-Host "  [AVISO] Sem remote configurado." -ForegroundColor Yellow
        }

        & $PSCommandPath backup
        Write-Header "Resumo"
        git log --oneline -3
    }

    "run" {
        Write-Header "Subindo uvicorn na porta 8010"
        & $pyExe -m uvicorn pc_backend.main:app --port 8010 --reload
    }

    "clean" {
        Write-Header "Limpando caches"
        Get-ChildItem -Recurse -Directory -Filter "__pycache__" -ErrorAction SilentlyContinue | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
        Get-ChildItem -Recurse -Directory -Filter ".pytest_cache" -ErrorAction SilentlyContinue | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
        Get-ChildItem -Recurse -Filter "*.pyc" -ErrorAction SilentlyContinue | Remove-Item -Force -ErrorAction SilentlyContinue
        Get-ChildItem -Recurse -Filter "*.pyo" -ErrorAction SilentlyContinue | Remove-Item -Force -ErrorAction SilentlyContinue
        Write-OK "Caches limpos"
    }

    "check" {
        Write-Header "Verificando lixo no staging"
        $lixo = git status --short | Select-String "_backup_|\.bak_|_ver_|_fix_|\.dump|\.db$|temp_downloads|\.env$|_teste_"
        if ($lixo) {
            Write-Err "Lixo detectado:"
            $lixo | ForEach-Object { Write-Host "  $_" -ForegroundColor Red }
            Write-Host "`nRode 'git reset' e ajuste o .gitignore." -ForegroundColor Yellow
            exit 1
        } else {
            Write-OK "Staging limpo - pode commitar"
        }
    }

    "status" {
        Write-Header "Git status"
        git status --short
        Write-Header "Ultimos 5 commits"
        git log --oneline -5
        Write-Header "Arquivos versionados"
        (git ls-files | Measure-Object -Line).Lines
    }

    "install" {
        Write-Header "Instalando dependencias"
        if (Test-Path "requirements.txt") {
            & $pipExe install -r requirements.txt
            Write-OK "Dependencias instaladas"
        } else {
            Write-Err "requirements.txt nao encontrado"
        }
    }

    "help" {
        Write-Host ""
        Write-Host "  tasks.ps1 - Ponto unico de entrada" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "  Uso: .\tasks.ps1 <comando> [argumento] [-v]" -ForegroundColor White
        Write-Host ""
        Write-Host "  Comandos:" -ForegroundColor Yellow
        Write-Host "    test            Roda pytest (adicione -v para verboso)" -ForegroundColor White
        Write-Host "    import          Smoke test dos routers" -ForegroundColor White
        Write-Host "    backup          Cria ZIP de backup" -ForegroundColor White
        Write-Host "    commit 'msg'    Commit + push + backup" -ForegroundColor White
        Write-Host "    run             Sobe uvicorn (porta 8010)" -ForegroundColor White
        Write-Host "    clean           Limpa __pycache__ / .pytest_cache" -ForegroundColor White
        Write-Host "    check           Verifica lixo no staging" -ForegroundColor White
        Write-Host "    status          git status + commits + contagem" -ForegroundColor White
        Write-Host "    install         pip install -r requirements.txt" -ForegroundColor White
        Write-Host "    help            Mostra esta ajuda" -ForegroundColor White
        Write-Host ""
        Write-Host "  Exemplos:" -ForegroundColor Yellow
        Write-Host "    .\tasks.ps1 test -v" -ForegroundColor Gray
        Write-Host "    .\tasks.ps1 commit 'feat: nova funcionalidade'" -ForegroundColor Gray
        Write-Host "    .\tasks.ps1 run" -ForegroundColor Gray
        Write-Host ""
    }
}