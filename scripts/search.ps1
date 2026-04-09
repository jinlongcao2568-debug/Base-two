param(
    [Parameter(Mandatory = $true, Position = 0)]
    [string]$Pattern,

    [Parameter(Position = 1)]
    [string]$Path = ".",

    [ValidateSet("Auto", "Ripgrep", "SelectString")]
    [string]$Backend = "Auto",

    [switch]$Regex,

    [switch]$CaseInsensitive
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
[Console]::InputEncoding = [System.Text.Encoding]::UTF8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$defaultExcludedDirectories = @(
    ".git",
    "__pycache__",
    ".pytest_cache",
    ".ruff_cache",
    ".mypy_cache",
    ".venv",
    "venv",
    "node_modules"
)

function Get-DisplayPath {
    param(
        [Parameter(Mandatory = $true)]
        [string]$FullPath
    )

    $absolutePath = [System.IO.Path]::GetFullPath($FullPath)
    $currentDirectory = [System.IO.Path]::GetFullPath((Get-Location).Path)
    $comparison = [System.StringComparison]::OrdinalIgnoreCase
    if ($absolutePath.StartsWith($currentDirectory, $comparison)) {
        $relativePath = $absolutePath.Substring($currentDirectory.Length).TrimStart("\", "/")
        if ([string]::IsNullOrWhiteSpace($relativePath)) {
            return "."
        }

        return $relativePath -replace "\\", "/"
    }

    return $absolutePath -replace "\\", "/"
}

function Test-RunnableExecutable {
    param(
        [Parameter(Mandatory = $true)]
        [string]$ExecutablePath
    )

    try {
        & $ExecutablePath "--version" *> $null
        return $true
    }
    catch {
        return $false
    }
}

function Get-RipgrepCommandInfo {
    $command = Get-Command "rg" -ErrorAction SilentlyContinue
    if ($null -eq $command) {
        return $null
    }

    return $command.Source
}

function Get-RunnableRipgrepPath {
    $discoveredPath = Get-RipgrepCommandInfo
    if ($null -eq $discoveredPath) {
        return $null
    }

    if (Test-RunnableExecutable -ExecutablePath $discoveredPath) {
        return $discoveredPath
    }

    try {
        $cacheDirectory = Join-Path ([System.IO.Path]::GetTempPath()) "ax9-tools"
        $cachePath = Join-Path $cacheDirectory "rg.exe"
        if (-not (Test-Path -LiteralPath $cacheDirectory)) {
            $null = New-Item -ItemType Directory -Path $cacheDirectory -Force
        }

        Copy-Item -LiteralPath $discoveredPath -Destination $cachePath -Force
        if (Test-RunnableExecutable -ExecutablePath $cachePath) {
            return $cachePath
        }
    }
    catch {
        return $null
    }

    return $null
}

function Get-SearchFiles {
    param(
        [Parameter(Mandatory = $true)]
        [string]$TargetPath
    )

    if (-not (Test-Path -LiteralPath $TargetPath)) {
        throw "Search path not found: $TargetPath"
    }

    $item = Get-Item -LiteralPath $TargetPath
    if (-not $item.PSIsContainer) {
        return @($item.FullName)
    }

    $rootPath = [System.IO.Path]::GetFullPath($item.FullName)
    $separator = [System.IO.Path]::DirectorySeparatorChar
    $files = Get-ChildItem -LiteralPath $rootPath -Recurse -File -Force
    $searchFiles = foreach ($file in $files) {
        $relativePath = $file.FullName.Substring($rootPath.Length).TrimStart($separator, [System.IO.Path]::AltDirectorySeparatorChar)
        $pathSegments = $relativePath.Split(@($separator, [System.IO.Path]::AltDirectorySeparatorChar), [System.StringSplitOptions]::RemoveEmptyEntries)
        $isExcluded = $false
        foreach ($segment in $pathSegments) {
            if ($defaultExcludedDirectories -contains $segment) {
                $isExcluded = $true
                break
            }
        }

        if (-not $isExcluded) {
            $file.FullName
        }
    }

    return @($searchFiles)
}

function Invoke-RipgrepSearch {
    param(
        [Parameter(Mandatory = $true)]
        [string]$ExecutablePath,

        [Parameter(Mandatory = $true)]
        [string]$SearchPattern,

        [Parameter(Mandatory = $true)]
        [string]$SearchPath,

        [Parameter(Mandatory = $true)]
        [bool]$UseRegex,

        [Parameter(Mandatory = $true)]
        [bool]$UseCaseInsensitive
    )

    $arguments = @(
        "--line-number",
        "--with-filename",
        "--color",
        "never",
        "--glob",
        "!.git/**",
        "--glob",
        "!**/__pycache__/**",
        "--glob",
        "!**/.pytest_cache/**",
        "--glob",
        "!**/.ruff_cache/**",
        "--glob",
        "!**/.mypy_cache/**",
        "--glob",
        "!**/.venv/**",
        "--glob",
        "!**/venv/**",
        "--glob",
        "!**/node_modules/**"
    )

    if (-not $UseRegex) {
        $arguments += "-F"
    }

    if ($UseCaseInsensitive) {
        $arguments += "-i"
    }

    $arguments += @($SearchPattern, $SearchPath)

    $outputLines = @(& $ExecutablePath @arguments)
    return @{
        ExitCode = $LASTEXITCODE
        Output   = $outputLines
    }
}

function Invoke-SelectStringSearch {
    param(
        [Parameter(Mandatory = $true)]
        [string]$SearchPattern,

        [Parameter(Mandatory = $true)]
        [string]$SearchPath,

        [Parameter(Mandatory = $true)]
        [bool]$UseRegex,

        [Parameter(Mandatory = $true)]
        [bool]$UseCaseInsensitive
    )

    $files = @(Get-SearchFiles -TargetPath $SearchPath)
    if ($files.Count -eq 0) {
        return 1
    }

    $selectStringParameters = @{
        Path         = $files
        Pattern      = $SearchPattern
        Encoding     = "utf8"
        ErrorAction  = "SilentlyContinue"
    }

    if (-not $UseRegex) {
        $selectStringParameters["SimpleMatch"] = $true
    }

    if (-not $UseCaseInsensitive) {
        $selectStringParameters["CaseSensitive"] = $true
    }

    $results = @(Select-String @selectStringParameters)
    $matchCount = 0
    $outputLines = @()
    foreach ($result in $results) {
        $matchCount += 1
        $displayPath = Get-DisplayPath -FullPath $result.Path
        $lineText = $result.Line.TrimEnd()
        $outputLines += ("{0}:{1}:{2}" -f $displayPath, $result.LineNumber, $lineText)
    }

    if ($matchCount -gt 0) {
        return @{
            ExitCode = 0
            Output   = $outputLines
        }
    }

    return @{
        ExitCode = 1
        Output   = @()
    }
}

try {
    $selectedBackend = $Backend
    $ripgrepPath = $null
    if ($selectedBackend -ne "SelectString") {
        $ripgrepPath = Get-RunnableRipgrepPath
    }

    if ($selectedBackend -eq "Auto") {
        if ($null -ne $ripgrepPath) {
            $selectedBackend = "Ripgrep"
        }
        else {
            $selectedBackend = "SelectString"
        }
    }

    if ($selectedBackend -eq "Ripgrep") {
        if ($null -eq $ripgrepPath) {
            throw "rg is discoverable but not executable in the current agent environment. Use Backend SelectString or repair the runnable ripgrep path."
        }

        $result = Invoke-RipgrepSearch `
            -ExecutablePath $ripgrepPath `
            -SearchPattern $Pattern `
            -SearchPath $Path `
            -UseRegex:$Regex.IsPresent `
            -UseCaseInsensitive:$CaseInsensitive.IsPresent
        foreach ($line in $result.Output) {
            Write-Output $line
        }

        exit $result.ExitCode
    }

    $result = Invoke-SelectStringSearch `
        -SearchPattern $Pattern `
        -SearchPath $Path `
        -UseRegex:$Regex.IsPresent `
        -UseCaseInsensitive:$CaseInsensitive.IsPresent
    foreach ($line in $result.Output) {
        Write-Output $line
    }

    exit $result.ExitCode
}
catch {
    Write-Error $_
    exit 2
}
