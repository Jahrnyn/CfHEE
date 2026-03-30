Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
if (Get-Variable PSNativeCommandUseErrorActionPreference -ErrorAction SilentlyContinue) {
    $PSNativeCommandUseErrorActionPreference = $false
}

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = Split-Path -Parent $ScriptDir

Push-Location $RepoRoot
try {
    $embeddingModel = if ($env:CFHEE_EMBEDDING_MODEL) { $env:CFHEE_EMBEDDING_MODEL } else { "bge-m3" }
    cmd.exe /c "docker compose up --build -d"
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to start the portable runtime. Run 'docker compose logs' to inspect the problem."
    }

    Write-Host "Portable runtime start requested." -ForegroundColor Green
    Write-Host "If this is the first runtime start on this data directory, runtime-local Ollama may still be pulling '$embeddingModel'." -ForegroundColor Yellow
    Write-Host "Inspect readiness with 'docker compose ps', 'docker compose logs ollama-model-init', and 'docker compose logs ollama'." -ForegroundColor Yellow
}
finally {
    Pop-Location
}
