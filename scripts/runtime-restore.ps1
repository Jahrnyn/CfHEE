param(
    [Parameter(Mandatory = $true)]
    [string]$BackupPath,

    [string]$ConfirmRestore
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
if (Get-Variable PSNativeCommandUseErrorActionPreference -ErrorAction SilentlyContinue) {
    $PSNativeCommandUseErrorActionPreference = $false
}

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = Split-Path -Parent $ScriptDir

function Get-RunningRuntimeServices {
    $output = cmd.exe /c "docker compose ps --status running --services"
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to inspect the runtime state. Run 'docker compose ps' manually and confirm Docker Compose is available."
    }

    return [string[]]@($output | Where-Object { -not [string]::IsNullOrWhiteSpace($_) })
}

function Assert-RuntimeStopped {
    $runningServices = @(Get-RunningRuntimeServices)
    if ($runningServices.Count -gt 0) {
        $serviceList = $runningServices -join ", "
        throw "The portable runtime must be stopped before restore. Running services: $serviceList. Run '.\scripts\runtime-down.ps1' or 'docker compose down' first."
    }
}

Push-Location $RepoRoot
try {
    Assert-RuntimeStopped

    $resolvedBackupPath = (Resolve-Path -LiteralPath $BackupPath).Path
    $postgresBackup = Join-Path $resolvedBackupPath "postgres"
    $chromaBackup = Join-Path $resolvedBackupPath "chroma"

    if (-not (Test-Path -LiteralPath $postgresBackup -PathType Container)) {
        throw "Backup payload is missing '$postgresBackup'. Restore expects a backup created from the current CfHEE runtime-data layout."
    }

    if (-not (Test-Path -LiteralPath $chromaBackup -PathType Container)) {
        throw "Backup payload is missing '$chromaBackup'. Restore expects a backup created from the current CfHEE runtime-data layout."
    }

    if ([string]::IsNullOrWhiteSpace($ConfirmRestore)) {
        Write-Warning "This restore replaces the current runtime-data/postgres and runtime-data/chroma directories."
        $ConfirmRestore = Read-Host "Type RESTORE to continue"
    }

    if ($ConfirmRestore -ne "RESTORE") {
        throw "Restore cancelled. The exact confirmation phrase 'RESTORE' was not provided."
    }

    $runtimeDataRoot = Join-Path $RepoRoot "runtime-data"
    $postgresTarget = Join-Path $runtimeDataRoot "postgres"
    $chromaTarget = Join-Path $runtimeDataRoot "chroma"
    $stagingRoot = Join-Path $RepoRoot (".restore-staging-" + (Get-Date -Format "yyyyMMdd-HHmmssfff"))

    New-Item -ItemType Directory -Path $runtimeDataRoot -Force | Out-Null
    New-Item -ItemType Directory -Path $stagingRoot | Out-Null

    try {
        Copy-Item -LiteralPath $postgresBackup -Destination $stagingRoot -Recurse -Force
        Copy-Item -LiteralPath $chromaBackup -Destination $stagingRoot -Recurse -Force

        if (Test-Path -LiteralPath $postgresTarget) {
            Remove-Item -LiteralPath $postgresTarget -Recurse -Force
        }

        if (Test-Path -LiteralPath $chromaTarget) {
            Remove-Item -LiteralPath $chromaTarget -Recurse -Force
        }

        Move-Item -LiteralPath (Join-Path $stagingRoot "postgres") -Destination $runtimeDataRoot
        Move-Item -LiteralPath (Join-Path $stagingRoot "chroma") -Destination $runtimeDataRoot
    }
    finally {
        if (Test-Path -LiteralPath $stagingRoot) {
            Remove-Item -LiteralPath $stagingRoot -Recurse -Force
        }
    }

    Write-Host "CfHEE runtime data restored from:"
    Write-Host "  $resolvedBackupPath"
}
finally {
    Pop-Location
}
