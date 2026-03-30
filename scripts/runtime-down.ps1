# runtime-down.ps1
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
if (Get-Variable PSNativeCommandUseErrorActionPreference -ErrorAction SilentlyContinue) {
    $PSNativeCommandUseErrorActionPreference = $false
}

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = Split-Path -Parent $ScriptDir

Push-Location $RepoRoot
try {
    $output = cmd.exe /c "docker compose down 2>&1"
    Write-Host $output

    # A 'down' akkor sikeres, ha nincs futó konténer utána
    $running = cmd.exe /c "docker compose ps --services --filter status=running 2>&1"
    if ($running.Trim() -ne "") {
        throw "Failed to stop the portable runtime. Run 'docker compose ps' and 'docker compose logs' to inspect the current state."
    }
    Write-Host "[OK] Runtime stopped."
}
finally {
    Pop-Location
}