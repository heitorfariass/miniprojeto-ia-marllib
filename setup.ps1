# Instala o ambiente do miniprojeto no Windows (PowerShell).
# Uso, na raiz do repositório:  powershell -ExecutionPolicy Bypass -File setup.ps1
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

function Run($exe, [string[]]$argv) {
    & $exe @argv
    if ($LASTEXITCODE -ne 0) { throw "falhou: $exe $($argv -join ' ')" }
}

if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
    Write-Host ">> Instalando uv (gerenciador de Python)..."
    powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
    $env:Path = "$env:USERPROFILE\.local\bin;$env:Path"
}

if (-not (Test-Path "MARLlib\requirements.txt")) {
    Write-Host ">> Baixando o código da MARLlib (submódulo)..."
    Run git @("submodule", "update", "--init")
}

Write-Host ">> Python 3.8 e ambiente virtual .venv"
Run uv @("python", "install", "3.8")
Run uv @("venv", ".venv", "--python", "3.8", "--seed", "--clear")
$py = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"

Write-Host ">> Dependências (leva ~10-15 min na primeira vez; baixa ~1 GB)"
Run $py @("-m", "pip", "install", "-q", "pip==21", "setuptools==65.5.0", "wheel==0.38.0")
Run $py @("-m", "pip", "install", "-q", "--no-build-isolation", "-r", "MARLlib\requirements.txt")
Run $py @("-m", "pip", "install", "-q", "pillow==9.5.0")
Run $py @("-m", "pip", "install", "-q", "--no-deps", "-e", "MARLlib")
Run $py @("experiments\apply_patch.py")

Write-Host ""
Write-Host "Pronto. Ative o ambiente com:  .\.venv\Scripts\Activate.ps1"
Write-Host "Depois rode:                  python experiments\smoke_test.py"
