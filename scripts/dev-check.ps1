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
$OllamaBaseUrl = if ($env:OLLAMA_BASE_URL) { $env:OLLAMA_BASE_URL.TrimEnd("/") } else { "http://127.0.0.1:11434" }
$EmbeddingOllamaBaseUrl = if ($env:EMBEDDING_OLLAMA_BASE_URL) { $env:EMBEDDING_OLLAMA_BASE_URL.TrimEnd("/") } else { $OllamaBaseUrl }
$OllamaTagsUrl = "$OllamaBaseUrl/api/tags"
$EmbeddingOllamaTagsUrl = "$EmbeddingOllamaBaseUrl/api/tags"
$OllamaModel = if ($env:OLLAMA_MODEL) { $env:OLLAMA_MODEL } else { "qwen2.5:7b" }
$EmbeddingModel = if ($env:EMBEDDING_MODEL) { $env:EMBEDDING_MODEL } else { "bge-m3" }
$AnswerProviderSelection = if ($env:ANSWER_PROVIDER) { $env:ANSWER_PROVIDER } else { "auto" }
$EmbeddingProviderSelection = if ($env:EMBEDDING_PROVIDER) { $env:EMBEDDING_PROVIDER } else { "ollama" }
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

function Write-Warn {
    param([string]$Message)
    Write-Host "[WARN] $Message" -ForegroundColor Yellow
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

function Invoke-OllamaTags {
    param([string]$Url)

    try {
        return Invoke-RestMethod -Uri $Url -Method Get -TimeoutSec 5
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

Write-Step "Checking Ollama reachability"
$ollamaTags = Invoke-OllamaTags -Url $OllamaTagsUrl
if ($null -eq $ollamaTags) {
    Write-Warn "Ollama is not reachable at $OllamaBaseUrl. The backend should fall back to the deterministic provider."
}
else {
    Write-Ok "Ollama responded from $OllamaBaseUrl."

    $modelNames = @($ollamaTags.models | ForEach-Object { $_.name })
    if ($modelNames -contains $OllamaModel) {
        Write-Ok "Configured Ollama model '$OllamaModel' is available locally."
    }
    else {
        Write-Warn "Configured Ollama model '$OllamaModel' is not available locally. Run 'ollama pull $OllamaModel' if you want Ollama-backed answers."
    }
}

Write-Step "Checking embedding-provider readiness"
$embeddingOllamaTags = $null
if ($EmbeddingProviderSelection -eq "hash") {
    Write-Ok "EMBEDDING_PROVIDER is set to hash. Retrieval will use the explicit placeholder fallback mode."
}
elseif ($EmbeddingProviderSelection -ne "ollama") {
    Write-Fail "Unknown EMBEDDING_PROVIDER '$EmbeddingProviderSelection'. Supported values are 'ollama' and 'hash'."
}
else {
    $embeddingOllamaTags = if ($EmbeddingOllamaBaseUrl -eq $OllamaBaseUrl) { $ollamaTags } else { Invoke-OllamaTags -Url $EmbeddingOllamaTagsUrl }
    if ($null -eq $embeddingOllamaTags) {
        Write-Fail "EMBEDDING_PROVIDER is ollama but Ollama is not reachable at $EmbeddingOllamaBaseUrl. Ingest and retrieval will fail until Ollama is reachable."
    }
    else {
        Write-Ok "Embedding Ollama endpoint responded from $EmbeddingOllamaBaseUrl."
        $embeddingModelNames = @($embeddingOllamaTags.models | ForEach-Object { $_.name })
        if ($embeddingModelNames -contains $EmbeddingModel) {
            Write-Ok "Configured embedding model '$EmbeddingModel' is available locally."
        }
        else {
            Write-Fail "Configured embedding model '$EmbeddingModel' is not available locally. Run 'ollama pull $EmbeddingModel' or switch EMBEDDING_PROVIDER to hash explicitly."
        }
    }
}

Write-Step "Checking answer-provider readiness"
if ($AnswerProviderSelection -eq "deterministic") {
    Write-Ok "ANSWER_PROVIDER is set to deterministic. Grounded answers should use the deterministic fallback."
}
elseif ($null -ne $ollamaTags -and (@($ollamaTags.models | ForEach-Object { $_.name }) -contains $OllamaModel)) {
    Write-Ok "Ollama-backed answers appear ready for model '$OllamaModel'."
}
else {
    Write-Warn "Ollama-backed answers are not fully ready. The backend should continue using the deterministic fallback."
}

Write-Host ""
if ($hasFailures) {
    Write-Host "One or more local checks failed." -ForegroundColor Red
    exit 1
}

Write-Host "All local development checks passed." -ForegroundColor Green
