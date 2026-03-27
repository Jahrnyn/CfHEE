Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
if (Get-Variable PSNativeCommandUseErrorActionPreference -ErrorAction SilentlyContinue) {
    $PSNativeCommandUseErrorActionPreference = $false
}

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = Split-Path -Parent $ScriptDir

Push-Location $RepoRoot
try {
    cmd.exe /c "docker compose down"
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to stop the portable runtime. Run 'docker compose ps' and 'docker compose logs' to inspect the current state."
    }
}
finally {
    Pop-Location
}
