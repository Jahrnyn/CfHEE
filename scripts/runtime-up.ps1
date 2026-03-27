Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
if (Get-Variable PSNativeCommandUseErrorActionPreference -ErrorAction SilentlyContinue) {
    $PSNativeCommandUseErrorActionPreference = $false
}

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = Split-Path -Parent $ScriptDir

Push-Location $RepoRoot
try {
    cmd.exe /c "docker compose up --build -d"
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to start the portable runtime. Run 'docker compose logs' to inspect the problem."
    }
}
finally {
    Pop-Location
}
