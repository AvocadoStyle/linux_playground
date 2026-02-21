# Ollama Setup Script for Windows
# Run: powershell -ExecutionPolicy Bypass -File setup_ollama_windows.ps1

param(
    [string]$Model = "llama3.2"
)

Write-Host "=============================" -ForegroundColor Cyan
Write-Host "  Ollama Setup - Windows" -ForegroundColor Cyan
Write-Host "=============================" -ForegroundColor Cyan

# Step 1: Check if Ollama is installed
Write-Host "`n[1/4] Checking if Ollama is installed..." -ForegroundColor Yellow
$ollamaPath = "$env:LOCALAPPDATA\Programs\Ollama\ollama.exe"
$ollamaInPath = Get-Command ollama -ErrorAction SilentlyContinue

if ($ollamaInPath) {
    $ollamaExe = "ollama"
    Write-Host "  Ollama found in PATH" -ForegroundColor Green
} elseif (Test-Path $ollamaPath) {
    $ollamaExe = $ollamaPath
    Write-Host "  Ollama found at: $ollamaPath" -ForegroundColor Green
} else {
    Write-Host "  Ollama not found. Installing via winget..." -ForegroundColor Yellow
    winget install Ollama.Ollama --accept-package-agreements --accept-source-agreements
    if ($LASTEXITCODE -ne 0) {
        Write-Host "  ERROR: winget install failed. Download manually from https://ollama.com/download" -ForegroundColor Red
        exit 1
    }
    $ollamaExe = $ollamaPath
    Write-Host "  Ollama installed successfully" -ForegroundColor Green
}

# Step 2: Check if Ollama server is running
Write-Host "`n[2/4] Checking Ollama server..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:11434" -TimeoutSec 3 -ErrorAction Stop
    Write-Host "  Ollama server is running" -ForegroundColor Green
} catch {
    Write-Host "  Starting Ollama server..." -ForegroundColor Yellow
    Start-Process -FilePath $ollamaExe -ArgumentList "serve" -WindowStyle Hidden
    Start-Sleep -Seconds 3
    Write-Host "  Ollama server started" -ForegroundColor Green
}

# Step 3: Pull model
Write-Host "`n[3/4] Pulling model: $Model ..." -ForegroundColor Yellow
& $ollamaExe pull $Model
if ($LASTEXITCODE -eq 0) {
    Write-Host "  Model '$Model' ready" -ForegroundColor Green
} else {
    Write-Host "  ERROR: Failed to pull model '$Model'" -ForegroundColor Red
    exit 1
}

# Step 4: Install Python client
Write-Host "`n[4/4] Installing Python ollama client..." -ForegroundColor Yellow
$projectRoot = (Get-Item $PSScriptRoot).Parent.Parent.Parent.FullName
Push-Location $projectRoot
if (Test-Path "pyproject.toml") {
    poetry add ollama 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  Python ollama client installed via poetry" -ForegroundColor Green
    } else {
        pip install ollama 2>$null
        Write-Host "  Python ollama client installed via pip" -ForegroundColor Green
    }
} else {
    pip install ollama
    Write-Host "  Python ollama client installed via pip" -ForegroundColor Green
}
Pop-Location

# Done
Write-Host "`n=============================" -ForegroundColor Cyan
Write-Host "  Setup Complete!" -ForegroundColor Green
Write-Host "  Model: $Model" -ForegroundColor White
Write-Host "  Server: http://localhost:11434" -ForegroundColor White
Write-Host "=============================" -ForegroundColor Cyan
