param(
    [int]$BackendPort = 8000,
    [int]$FrontendPort = 4200
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
if (Get-Variable PSNativeCommandUseErrorActionPreference -ErrorAction SilentlyContinue) {
    $PSNativeCommandUseErrorActionPreference = $false
}

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = Split-Path -Parent $ScriptDir
$PostgresContainerName = "cfhee-postgres"
$BackendUrl = "http://127.0.0.1:$BackendPort/health"
$FrontendUrl = "http://127.0.0.1:$FrontendPort"
$hasFailures = $false

function Write-Step {
    param([string]$Message)
    Write-Host ""
    Write-Host "==> $Message" -ForegroundColor Cyan
}

function Write-Ok {
    param([string]$Message)
    Write-Host "[OK] $Message" -ForegroundColor Green
}

function Write-Fail {
    param([string]$Message)
    Write-Host "[FAIL] $Message" -ForegroundColor Red
    $script:hasFailures = $true
}

function Test-CommandAvailable {
    param([string]$Name)
    return $null -ne (Get-Command $Name -ErrorAction SilentlyContinue)
}

function Invoke-EndpointCheck {
    param([string]$Url)

    try {
        return Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec 5
    }
    catch {
        return $null
    }
}

Write-Step "Checking Postgres container"
Push-Location $RepoRoot
try {
    if (-not (Test-CommandAvailable "docker")) {
        Write-Fail "Docker CLI is not available on PATH."
    }
    else {
        $status = (cmd.exe /c "docker inspect -f ""{{.State.Status}}"" $PostgresContainerName 2>nul" | Out-String).Trim()
        if ($LASTEXITCODE -eq 0 -and $status -eq "running") {
            Write-Ok "Postgres container '$PostgresContainerName' is running."
        }
        elseif ($LASTEXITCODE -eq 0) {
            Write-Fail "Postgres container '$PostgresContainerName' exists but is '$status'. Run 'docker compose up -d postgres'."
        }
        else {
            Write-Fail "Postgres container '$PostgresContainerName' was not found. Run 'docker compose up -d postgres'."
        }
    }
}
finally {
    Pop-Location
}

Write-Step "Checking backend health"
$backendResponse = Invoke-EndpointCheck -Url $BackendUrl
if ($null -ne $backendResponse -and $backendResponse.StatusCode -ge 200 -and $backendResponse.StatusCode -lt 300) {
    Write-Ok "Backend responded from $BackendUrl with HTTP $($backendResponse.StatusCode)."
}
else {
    Write-Fail "Backend did not respond successfully at $BackendUrl. Start it with '.\\scripts\\dev-up.ps1' or inspect the backend PowerShell window."
}

Write-Step "Checking frontend HTTP response"
$frontendResponse = Invoke-EndpointCheck -Url $FrontendUrl
if ($null -ne $frontendResponse) {
    Write-Ok "Frontend responded from $FrontendUrl with HTTP $($frontendResponse.StatusCode)."
}
else {
    Write-Fail "Frontend did not respond successfully at $FrontendUrl. Start it with '.\\scripts\\dev-up.ps1' or inspect the frontend PowerShell window."
}

Write-Host ""
if ($hasFailures) {
    Write-Host "One or more local checks failed." -ForegroundColor Red
    exit 1
}

Write-Host "All local development checks passed." -ForegroundColor Green
