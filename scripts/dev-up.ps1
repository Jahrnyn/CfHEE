param(
    [int]$BackendPort = 8000,
    [int]$FrontendPort = 4200,
    [int]$PostgresPort = 5432
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
if (Get-Variable PSNativeCommandUseErrorActionPreference -ErrorAction SilentlyContinue) {
    $PSNativeCommandUseErrorActionPreference = $false
}

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = Split-Path -Parent $ScriptDir
$BackendDir = Join-Path $RepoRoot "apps/backend"
$FrontendDir = Join-Path $RepoRoot "apps/frontend"
$BackendVenvDir = Join-Path $BackendDir ".venv"
$BackendPython = Join-Path $BackendVenvDir "Scripts/python.exe"
$BackendPyproject = Join-Path $BackendDir "pyproject.toml"
$BackendDepsMarker = Join-Path $BackendVenvDir ".deps-installed"
$FrontendPackageJson = Join-Path $FrontendDir "package.json"
$FrontendLockFile = Join-Path $FrontendDir "package-lock.json"
$FrontendNodeModules = Join-Path $FrontendDir "node_modules"
$FrontendDepsMarker = Join-Path $FrontendNodeModules ".deps-installed"
$PostgresContainerName = "cfhee-postgres"

function Get-OllamaModelName {
    if ($env:OLLAMA_MODEL) {
        return $env:OLLAMA_MODEL
    }

    return "qwen2.5:7b"
}

function Get-OllamaBaseUrl {
    if ($env:OLLAMA_BASE_URL) {
        return $env:OLLAMA_BASE_URL.TrimEnd("/")
    }

    return "http://127.0.0.1:11434"
}

$OllamaBaseUrl = Get-OllamaBaseUrl
$OllamaTagsUrl = "$OllamaBaseUrl/api/tags"
$OllamaModel = Get-OllamaModelName
$EmbeddingProvider = if ($env:EMBEDDING_PROVIDER) { $env:EMBEDDING_PROVIDER } else { "ollama" }
$EmbeddingOllamaBaseUrl = if ($env:EMBEDDING_OLLAMA_BASE_URL) { $env:EMBEDDING_OLLAMA_BASE_URL.TrimEnd("/") } else { $OllamaBaseUrl }
$EmbeddingOllamaTagsUrl = "$EmbeddingOllamaBaseUrl/api/tags"
$EmbeddingModel = if ($env:EMBEDDING_MODEL) { $env:EMBEDDING_MODEL } else { "bge-m3" }

function Write-Step {
    param([string]$Message)
    Write-Host ""
    Write-Host "==> $Message" -ForegroundColor Cyan
}

function Fail {
    param([string]$Message)
    Write-Error $Message
    exit 1
}

function Test-CommandAvailable {
    param([string]$Name)
    return $null -ne (Get-Command $Name -ErrorAction SilentlyContinue)
}

function Get-PythonLauncher {
    if (Test-CommandAvailable "py") {
        return @{
            Path = (Get-Command "py").Source
            Args = @("-3.12")
        }
    }

    if (Test-CommandAvailable "python") {
        return @{
            Path = (Get-Command "python").Source
            Args = @()
        }
    }

    Fail "Python was not found. Install Python 3.12+ and make sure 'py' or 'python' is on PATH."
}

function Update-InstallMarker {
    param([string]$Path)
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Set-Content -Path $Path -Value $timestamp
}

function Test-BackendDependenciesInstalled {
    if (-not (Test-Path $BackendPython) -or -not (Test-Path $BackendDepsMarker)) {
        return $false
    }

    return (Get-Item $BackendDepsMarker).LastWriteTimeUtc -ge (Get-Item $BackendPyproject).LastWriteTimeUtc
}

function Test-FrontendDependenciesInstalled {
    if (-not (Test-Path $FrontendNodeModules) -or -not (Test-Path $FrontendDepsMarker)) {
        return $false
    }

    $markerTime = (Get-Item $FrontendDepsMarker).LastWriteTimeUtc
    if ($markerTime -lt (Get-Item $FrontendPackageJson).LastWriteTimeUtc) {
        return $false
    }

    if (Test-Path $FrontendLockFile) {
        return $markerTime -ge (Get-Item $FrontendLockFile).LastWriteTimeUtc
    }

    return $true
}

function Test-HttpEndpoint {
    param([string]$Url)

    try {
        $response = Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec 3
        return $response.StatusCode -ge 200 -and $response.StatusCode -lt 500
    }
    catch {
        return $false
    }
}

function Invoke-OllamaJson {
    param(
        [string]$Url,
        [int]$TimeoutSeconds = 3
    )

    try {
        return Invoke-RestMethod -Uri $Url -Method Get -TimeoutSec $TimeoutSeconds
    }
    catch {
        return $null
    }
}

function Wait-ForContainerRunning {
    param(
        [string]$ContainerName,
        [int]$TimeoutSeconds = 20
    )

    $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
    while ((Get-Date) -lt $deadline) {
        $status = (cmd.exe /c "docker inspect -f ""{{.State.Status}}"" $ContainerName 2>nul" | Out-String).Trim()
        if ($LASTEXITCODE -eq 0 -and $status -eq "running") {
            return $true
        }

        Start-Sleep -Seconds 1
    }

    return $false
}

function Start-DevWindow {
    param(
        [string]$Title,
        [string]$WorkingDirectory,
        [string]$Command
    )

    $windowCommand = "`$Host.UI.RawUI.WindowTitle = '$Title'; Set-Location '$WorkingDirectory'; $Command"
    Start-Process -FilePath "powershell.exe" -WorkingDirectory $WorkingDirectory -ArgumentList @("-NoExit", "-Command", $windowCommand) | Out-Null
}

function Wait-ForHttpEndpoint {
    param(
        [string]$Url,
        [int]$TimeoutSeconds = 20
    )

    $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
    while ((Get-Date) -lt $deadline) {
        if (Test-HttpEndpoint -Url $Url) {
            return $true
        }

        Start-Sleep -Seconds 2
    }

    return $false
}

function Start-DockerDesktop {
    $dockerDesktopPath = @(
        "$env:ProgramFiles\Docker\Docker\Docker Desktop.exe",
        "$env:LOCALAPPDATA\Programs\Docker\Docker\Docker Desktop.exe"
    ) | Where-Object { Test-Path $_ } | Select-Object -First 1

    if (-not $dockerDesktopPath) {
        Fail "Docker Desktop executable not found. Make sure Docker Desktop is installed."
    }

    Write-Host "Starting Docker Desktop..." -ForegroundColor Yellow
    Start-Process -FilePath $dockerDesktopPath

    $deadline = (Get-Date).AddSeconds(60)
    while ((Get-Date) -lt $deadline) {
        Start-Sleep -Seconds 3
        cmd.exe /c "docker info >nul 2>&1"
        if ($LASTEXITCODE -eq 0) {
            Write-Host "Docker Desktop is ready." -ForegroundColor Green
            return
        }
        Write-Host "  Still waiting for Docker Desktop..." -ForegroundColor DarkGray
    }

    Fail "Docker Desktop did not become available within 60 seconds. Try starting it manually."
}

Write-Step "Checking required tools"
if (-not (Test-CommandAvailable "docker")) {
    Fail "Docker CLI was not found. Install Docker Desktop and reopen PowerShell."
}

if (-not (Test-CommandAvailable "npm.cmd") -and -not (Test-CommandAvailable "npm")) {
    Fail "npm was not found. Install Node.js and reopen PowerShell."
}

$pythonLauncher = Get-PythonLauncher

Write-Step "Checking Docker Desktop status"
cmd.exe /c "docker info >nul 2>&1"
if ($LASTEXITCODE -ne 0) {
    Start-DockerDesktop
}
else {
    Write-Host "Docker Desktop is already running." -ForegroundColor DarkGreen
}

Write-Step "Starting Postgres with docker compose"
Push-Location $RepoRoot
try {
    cmd.exe /c "docker compose up -d postgres"
    if ($LASTEXITCODE -ne 0) {
        Fail "Failed to start Postgres with docker compose. Run 'docker compose up -d postgres' manually to inspect the error."
    }
}
finally {
    Pop-Location
}

Write-Step "Verifying Postgres container status"
if (-not (Wait-ForContainerRunning -ContainerName $PostgresContainerName)) {
    Fail "Postgres container '$PostgresContainerName' did not reach 'running' state. Check 'docker compose logs postgres' for details."
}
Write-Host "Postgres is running in container '$PostgresContainerName' on localhost:$PostgresPort." -ForegroundColor Green

Write-Step "Preparing backend virtual environment"
if (-not (Test-Path $BackendPython)) {
    & $pythonLauncher.Path @($pythonLauncher.Args + @("-m", "venv", $BackendVenvDir))
    if ($LASTEXITCODE -ne 0 -or -not (Test-Path $BackendPython)) {
        Fail "Failed to create backend virtual environment at '$BackendVenvDir'."
    }
    Write-Host "Created backend virtual environment." -ForegroundColor Green
}
else {
    Write-Host "Backend virtual environment already exists." -ForegroundColor DarkGreen
}

Write-Step "Ensuring backend dependencies are installed"
if (-not (Test-BackendDependenciesInstalled)) {
    Push-Location $BackendDir
    try {
        & $BackendPython -m pip install -e .
        if ($LASTEXITCODE -ne 0) {
            Fail "Backend dependency installation failed. Try '$BackendPython -m pip install -e .' inside '$BackendDir'."
        }
        Update-InstallMarker -Path $BackendDepsMarker
    }
    finally {
        Pop-Location
    }
    Write-Host "Backend dependencies installed." -ForegroundColor Green
}
else {
    Write-Host "Backend dependencies look current; skipping install." -ForegroundColor DarkGreen
}

Write-Step "Ensuring frontend dependencies are installed"
if (-not (Test-FrontendDependenciesInstalled)) {
    Push-Location $FrontendDir
    try {
        & npm.cmd install
        if ($LASTEXITCODE -ne 0) {
            Fail "Frontend dependency installation failed. Try 'npm install' inside '$FrontendDir'."
        }
        if (-not (Test-Path $FrontendNodeModules)) {
            Fail "npm reported success but '$FrontendNodeModules' was not created."
        }
        Update-InstallMarker -Path $FrontendDepsMarker
    }
    finally {
        Pop-Location
    }
    Write-Host "Frontend dependencies installed." -ForegroundColor Green
}
else {
    Write-Host "Frontend dependencies look current; skipping install." -ForegroundColor DarkGreen
}

Write-Step "Checking Ollama availability"
if (-not (Test-CommandAvailable "ollama")) {
    if ($EmbeddingProvider -eq "ollama") {
        Write-Host "Ollama CLI was not found. EMBEDDING_PROVIDER=ollama is the current default, so ingest and retrieval will fail until Ollama is installed and running or EMBEDDING_PROVIDER is set to hash explicitly." -ForegroundColor Yellow
    }
    else {
        Write-Host "Ollama CLI was not found. The backend can still run because EMBEDDING_PROVIDER is set to hash explicitly and answers can fall back to the deterministic provider." -ForegroundColor Yellow
    }
}
else {
    $ollamaTags = Invoke-OllamaJson -Url $OllamaTagsUrl
    if ($null -eq $ollamaTags) {
        Write-Host "Ollama server is not reachable at $OllamaBaseUrl. Trying to start it in a new PowerShell window..." -ForegroundColor Yellow
        Start-DevWindow -Title "CFHEE Ollama" -WorkingDirectory $RepoRoot -Command "ollama serve"

        if (Wait-ForHttpEndpoint -Url $OllamaTagsUrl -TimeoutSeconds 20) {
            Write-Host "Ollama server is reachable." -ForegroundColor Green
            $ollamaTags = Invoke-OllamaJson -Url $OllamaTagsUrl
        }
        else {
            Write-Host "Ollama did not become reachable automatically. Start it manually with 'ollama serve' or the Ollama desktop app. Answers will fall back to the deterministic provider." -ForegroundColor Yellow
        }
    }
    else {
        Write-Host "Ollama server is reachable." -ForegroundColor DarkGreen
    }

    if ($null -ne $ollamaTags) {
        $modelNames = @($ollamaTags.models | ForEach-Object { $_.name })
        if ($modelNames -contains $OllamaModel) {
            Write-Host "Configured Ollama model '$OllamaModel' is available locally." -ForegroundColor Green
        }
        else {
            Write-Host "Configured Ollama model '$OllamaModel' is missing locally. Run 'ollama pull $OllamaModel' to enable Ollama-backed answers. Deterministic fallback remains available." -ForegroundColor Yellow
        }

        if ($EmbeddingProvider -eq "ollama") {
            $embeddingTags = if ($EmbeddingOllamaBaseUrl -eq $OllamaBaseUrl) { $ollamaTags } else { Invoke-OllamaJson -Url $EmbeddingOllamaTagsUrl }
            if ($null -eq $embeddingTags) {
                Write-Host "Embedding runtime is configured for Ollama at $EmbeddingOllamaBaseUrl but is not reachable. Ingest and retrieval will fail until it is reachable." -ForegroundColor Yellow
            }
            else {
                $embeddingModelNames = @($embeddingTags.models | ForEach-Object { $_.name })
                if ($embeddingModelNames -contains $EmbeddingModel) {
                    Write-Host "Configured embedding model '$EmbeddingModel' is available locally." -ForegroundColor Green
                }
                else {
                    Write-Host "Configured embedding model '$EmbeddingModel' is missing locally. Run 'ollama pull $EmbeddingModel' or set EMBEDDING_PROVIDER=hash explicitly if you need the placeholder fallback." -ForegroundColor Yellow
                }
            }
        }
    }
}

Write-Step "Starting backend and frontend processes"
$backendUrl = "http://127.0.0.1:$BackendPort"
$frontendUrl = "http://127.0.0.1:$FrontendPort"
$healthUrl = "$backendUrl/health"
$answerUrl = "$backendUrl/answer/query"

if (Test-HttpEndpoint -Url $healthUrl) {
    Write-Host "Backend is already responding at $healthUrl; not starting a second process." -ForegroundColor Yellow
}
else {
    $backendCommand = "& '$BackendPython' -m uvicorn cfhee_backend.main:app --host 127.0.0.1 --port $BackendPort --reload"
    Start-DevWindow -Title "CFHEE Backend" -WorkingDirectory $BackendDir -Command $backendCommand
    Write-Host "Started backend in a new PowerShell window." -ForegroundColor Green
}

if (Test-HttpEndpoint -Url $frontendUrl) {
    Write-Host "Frontend is already responding at $frontendUrl; not starting a second process." -ForegroundColor Yellow
}
else {
    $frontendCommand = "npm.cmd start -- --host 127.0.0.1 --port $FrontendPort"
    Start-DevWindow -Title "CFHEE Frontend" -WorkingDirectory $FrontendDir -Command $frontendCommand
    Write-Host "Started frontend in a new PowerShell window." -ForegroundColor Green
}

Write-Step "Local development URLs"
Write-Host "Frontend:  $frontendUrl" -ForegroundColor White
Write-Host "Backend:   $backendUrl" -ForegroundColor White
Write-Host "API docs:  $backendUrl/docs" -ForegroundColor White
Write-Host "Health:    $healthUrl" -ForegroundColor White
Write-Host "Answer:    $answerUrl" -ForegroundColor White
Write-Host "Ollama:    $OllamaBaseUrl" -ForegroundColor White
Write-Host ""
Write-Host "Run '.\scripts\dev-check.ps1' in the repo root to verify everything after startup." -ForegroundColor Cyan
