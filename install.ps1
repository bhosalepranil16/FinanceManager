# One-click installer: creates FinaceManager/.env with random secrets (only if missing),
# builds the images, starts the stack, and waits for the app to respond.
# Safe to re-run (e.g. after `git pull`); it never overwrites FinaceManager/.env or data.
$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot

# Compose only auto-reads a root-level .env, so this file is passed explicitly.
$envFile = 'FinaceManager/.env'
$envExample = 'FinaceManager/.env.example'

function New-Secret([int]$Length) {
    $chars = (48..57) + (65..90) + (97..122) | ForEach-Object { [char]$_ }
    -join (1..$Length | ForEach-Object { $chars | Get-Random })
}

function Get-EnvValue([string]$Name) {
    $match = Select-String -Path $envFile -Pattern "^$Name=(.*)$" | Select-Object -First 1
    if (-not $match) { Write-Error "$Name is missing in $envFile" }
    $match.Matches[0].Groups[1].Value.Trim()
}

if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Error "Docker not found. Install it with: winget install Docker.DockerDesktop"
}
docker compose version *> $null
if ($LASTEXITCODE -ne 0) { Write-Error "The 'docker compose' plugin was not found. Update Docker Desktop." }
docker info *> $null
if ($LASTEXITCODE -ne 0) { Write-Error "Docker is not running. Start Docker Desktop and re-run." }

if (-not (Test-Path $envFile)) {
    Write-Host "No $envFile found - generating one with random secrets..."
    $content = Get-Content $envExample -Raw
    $content = $content -replace '(?m)^SECRET_KEY=.*$', "SECRET_KEY=$(New-Secret 64)"
    $content = $content -replace '(?m)^DATABASE_PASSWORD=.*$', "DATABASE_PASSWORD=$(New-Secret 32)"
    $content = $content -replace '(?m)^DATABASE_ROOT_PASSWORD=.*$', "DATABASE_ROOT_PASSWORD=$(New-Secret 32)"
    [IO.File]::WriteAllText((Join-Path $PSScriptRoot $envFile), $content, (New-Object Text.UTF8Encoding $false))
}

Write-Host "Building images and starting the stack (first run can take a few minutes)..."
docker compose --env-file $envFile up -d --build
if ($LASTEXITCODE -ne 0) { Write-Error "docker compose up failed." }

$port = Get-EnvValue 'HOST_PORT'

Write-Host "Waiting for the app to come online..."
$ready = $false
for ($i = 0; $i -lt 120; $i++) {
    try {
        Invoke-WebRequest "http://localhost:$port/" -UseBasicParsing -TimeoutSec 3 | Out-Null
        $ready = $true; break
    } catch { Start-Sleep -Seconds 1 }
}
if (-not $ready) {
    Write-Error "The app did not respond within 120s. Check logs with: docker compose --env-file $envFile logs"
}

Write-Host "Ready: http://localhost:$port  (restarts automatically with Docker Desktop)"
