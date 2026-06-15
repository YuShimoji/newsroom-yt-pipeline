param(
    [string]$Root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path,
    [string]$OutputPath
)

$ErrorActionPreference = "Stop"

$excludeDirectories = @(
    ".claude",
    ".docs-view",
    ".git",
    ".venv",
    "venv",
    "node_modules",
    "dist",
    "build",
    "configs",
    "data",
    "reports",
    "src",
    "tests",
    "tools",
    "__pycache__",
    ".pytest_cache"
)

$categoryOrder = @(
    "Overview",
    "Specs",
    "Runtime State",
    "Development Notes",
    "Artifacts",
    "Prompts",
    "Misc"
)

function Convert-ToRepoPath {
    param([string]$FullName)
    $rootPath = (Resolve-Path -LiteralPath $Root).Path.TrimEnd("\", "/")
    $fullPath = (Resolve-Path -LiteralPath $FullName).Path
    if (-not $fullPath.StartsWith($rootPath, [System.StringComparison]::OrdinalIgnoreCase)) {
        throw "Path is outside root: $FullName"
    }
    $relative = $fullPath.Substring($rootPath.Length).TrimStart("\", "/")
    return ($relative -replace "\\", "/")
}

function Test-IsExcludedPath {
    param([string]$RelativePath)
    $parts = $RelativePath -split "/"
    foreach ($part in $parts) {
        if ($excludeDirectories -contains $part) {
            return $true
        }
    }
    return $false
}

function Get-HeadingTitle {
    param([string]$Path)
    $lines = Get-Content -LiteralPath $Path -Encoding UTF8 -TotalCount 80
    foreach ($line in $lines) {
        if ($line -match "^\s*#\s+(.+?)\s*$") {
            return $Matches[1]
        }
    }
    return [System.IO.Path]::GetFileNameWithoutExtension($Path)
}

function Get-Category {
    param(
        [string]$RelativePath,
        [string]$Title
    )

    switch -Regex ($RelativePath) {
        "^docs/index\.md$" { return "Overview" }
        "^README\.md$" { return "Overview" }
        "^docs/DEVELOPMENT_PRACTICES\.md$" { return "Overview" }
        "^docs/(PROJECT_SPEC|AGENT_BRIEF|NLMYTGEN_BOUNDARY|YMM4_IMPORT_PROOF)\.md$" { return "Specs" }
        "^docs/(HANDOFF|RUNTIME_STATE)\.md$" { return "Runtime State" }
        "^docs/(META_REVIEW_LEDGER)\.md$" { return "Development Notes" }
        "^docs/verification/" { return "Development Notes" }
        "^artifacts/" { return "Artifacts" }
        "^docs/(approved_materializations|channel_memory)/" { return "Artifacts" }
        "^prompts/" { return "Prompts" }
        default { return "Misc" }
    }
}

function Convert-ToDocsViewPath {
    param([string]$RelativePath)

    switch ($RelativePath) {
        "README.md" { return "repository-readme.md" }
        "docs/index.md" { return "index.md" }
        default { return $RelativePath }
    }
}

function Quote-YamlSingle {
    param([string]$Value)
    return "'" + ($Value -replace "'", "''") + "'"
}

$items = Get-ChildItem -LiteralPath $Root -Recurse -File -Filter "*.md" |
    ForEach-Object {
        $relative = Convert-ToRepoPath -FullName $_.FullName
        if (Test-IsExcludedPath -RelativePath $relative) {
            return
        }

        $title = Get-HeadingTitle -Path $_.FullName
        [pscustomobject]@{
            RelativePath = $relative
            ViewPath = Convert-ToDocsViewPath -RelativePath $relative
            Title = $title
            Category = Get-Category -RelativePath $relative -Title $title
        }
    } |
    Sort-Object Category, RelativePath

$lines = [System.Collections.Generic.List[string]]::new()
$lines.Add("# Candidate nav generated from current Markdown placement.")
$lines.Add("# Review categories before copying into mkdocs.yml.")
$lines.Add("nav:")

foreach ($category in $categoryOrder) {
    $categoryItems = @($items | Where-Object { $_.Category -eq $category })
    if ($categoryItems.Count -eq 0) {
        continue
    }

    $lines.Add("  - ${category}:")
    foreach ($item in $categoryItems) {
        $title = Quote-YamlSingle -Value $item.Title
        $path = Quote-YamlSingle -Value $item.ViewPath
        $lines.Add("      - ${title}: ${path}")
    }
}

$output = $lines -join [Environment]::NewLine

if ($OutputPath) {
    Set-Content -LiteralPath $OutputPath -Value $output -Encoding UTF8
} else {
    $output
}
