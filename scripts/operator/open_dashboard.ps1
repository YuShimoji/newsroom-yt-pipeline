param(
    [int]$Port = 8000,
    [switch]$NoBrowser
)

$ErrorActionPreference = "Stop"
$scriptPath = if ($PSCommandPath) { $PSCommandPath } else { $MyInvocation.MyCommand.Path }

function Resolve-RepoRoot {
    param([string]$AnchorPath)

    $scriptDir = Split-Path -Parent $AnchorPath
    if (-not $scriptDir) {
        $scriptDir = (Get-Location).Path
    }

    try {
        $gitRoot = & git -C $scriptDir rev-parse --show-toplevel 2>$null
        if ($LASTEXITCODE -eq 0 -and $gitRoot) {
            return (Resolve-Path -LiteralPath ($gitRoot | Select-Object -First 1)).Path
        }
    } catch {
        # Fall back to the expected scripts/operator location.
    }

    return (Resolve-Path -LiteralPath (Join-Path $scriptDir "..\..")).Path
}

function Test-DocsServer {
    param([string]$Uri)

    try {
        $response = Invoke-WebRequest -Uri $Uri -UseBasicParsing -TimeoutSec 2
        $isHealthyStatus = $response.StatusCode -ge 200 -and $response.StatusCode -lt 500
        $looksLikeDocsView = $response.Content -like "*newsroom-yt-pipeline Local Docs*" -or
            $response.Content -like "*Local Documentation View*"
        return ($isHealthyStatus -and $looksLikeDocsView)
    } catch {
        return $false
    }
}

$repoRoot = Resolve-RepoRoot -AnchorPath $scriptPath
$python = Join-Path $repoRoot ".venv\Scripts\python.exe"
if (-not (Test-Path -LiteralPath $python)) {
    $python = "python"
}

$siteDir = Join-Path $repoRoot ".mkdocs-site"
New-Item -ItemType Directory -Force -Path $siteDir | Out-Null

$uri = "http://127.0.0.1:$Port/"
if (-not (Test-DocsServer -Uri $uri)) {
    $address = "127.0.0.1:$Port"
    $outLog = Join-Path $siteDir "mkdocs-serve-$Port.out.log"
    $errLog = Join-Path $siteDir "mkdocs-serve-$Port.err.log"
    $arguments = @("-m", "mkdocs", "serve", "--dev-addr", $address)

    Start-Process `
        -FilePath $python `
        -ArgumentList $arguments `
        -WorkingDirectory $repoRoot `
        -WindowStyle Hidden `
        -RedirectStandardOutput $outLog `
        -RedirectStandardError $errLog | Out-Null

    for ($i = 0; $i -lt 40; $i++) {
        if (Test-DocsServer -Uri $uri) {
            break
        }
        Start-Sleep -Milliseconds 500
    }
}

if (Test-DocsServer -Uri $uri) {
    Write-Host "Local docs view: $uri"
    Write-Host "Repo root: $repoRoot"
    if (-not $NoBrowser) {
        Start-Process $uri
    }
    exit 0
}

Write-Error "MkDocs did not become available at $uri. Check .mkdocs-site\mkdocs-serve-$Port.err.log from the repository root."
exit 1
