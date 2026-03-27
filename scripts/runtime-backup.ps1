param(
    [string]$DestinationRoot
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
if (Get-Variable PSNativeCommandUseErrorActionPreference -ErrorAction SilentlyContinue) {
    $PSNativeCommandUseErrorActionPreference = $false
}

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = Split-Path -Parent $ScriptDir

if ([string]::IsNullOrWhiteSpace($DestinationRoot)) {
    $DestinationRoot = Join-Path $RepoRoot "backups"
}

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
        throw "The portable runtime must be stopped before backup. Running services: $serviceList. Run '.\scripts\runtime-down.ps1' or 'docker compose down' first."
    }
}

function Assert-DirectoryExists {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Path,

        [Parameter(Mandatory = $true)]
        [string]$Description
    )

    if (-not (Test-Path -LiteralPath $Path -PathType Container)) {
        throw "$Description not found at '$Path'. Backup expects the current runtime-data layout to exist."
    }
}

Push-Location $RepoRoot
try {
    Assert-RuntimeStopped

    $postgresSource = Join-Path $RepoRoot "runtime-data\postgres"
    $chromaSource = Join-Path $RepoRoot "runtime-data\chroma"

    Assert-DirectoryExists -Path $postgresSource -Description "Postgres runtime data directory"
    Assert-DirectoryExists -Path $chromaSource -Description "Chroma runtime data directory"

    New-Item -ItemType Directory -Path $DestinationRoot -Force | Out-Null

    $timestamp = Get-Date -Format "yyyyMMdd-HHmmssfff"
    $backupRoot = Join-Path $DestinationRoot ("cfhee-backup-" + $timestamp)
    New-Item -ItemType Directory -Path $backupRoot | Out-Null

    Copy-Item -LiteralPath $postgresSource -Destination $backupRoot -Recurse -Force
    Copy-Item -LiteralPath $chromaSource -Destination $backupRoot -Recurse -Force

    $manifest = [ordered]@{
        backup_format_version = 1
        created_at_utc = (Get-Date).ToUniversalTime().ToString("o")
        runtime_must_be_stopped = $true
        postgres_source = "runtime-data/postgres"
        chroma_source = "runtime-data/chroma"
    }

    $manifestPath = Join-Path $backupRoot "manifest.json"
    $manifest | ConvertTo-Json | Set-Content -LiteralPath $manifestPath -Encoding utf8

    Write-Host "CfHEE runtime backup created:"
    Write-Host "  $backupRoot"
}
finally {
    Pop-Location
}
