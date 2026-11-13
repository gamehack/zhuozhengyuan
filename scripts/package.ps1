[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][string]$ProjectFile,
    [string]$OutputDirectory = ".\build\windows",
    [ValidateSet("Development", "Shipping")][string]$Configuration = "Development"
)

$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent $PSScriptRoot
if (-not [System.IO.Path]::IsPathRooted($ProjectFile)) {
    $ProjectFile = Join-Path $RepoRoot $ProjectFile
}
if (-not (Test-Path $ProjectFile)) {
    throw "Unreal project file not found: $ProjectFile. Create and validate the UE 5.8.4 project first."
}

. (Join-Path $PSScriptRoot "resolve-unreal.ps1")
$UnrealRoot = Get-ZjyUnrealEngineRoot -RequiredMinorVersion "5.8"
if (-not $UnrealRoot) {
    throw "Unreal Engine 5.8 was not found in configured paths or Epic Games Launcher install manifests."
}
$RunUAT = Join-Path $UnrealRoot "Engine\Build\BatchFiles\RunUAT.bat"
if (-not (Test-Path -LiteralPath $RunUAT)) {
    throw "Unreal Engine was detected at '$UnrealRoot' but RunUAT.bat is missing."
}

if (-not [System.IO.Path]::IsPathRooted($OutputDirectory)) {
    $OutputDirectory = Join-Path $RepoRoot $OutputDirectory
}
New-Item -ItemType Directory -Force -Path $OutputDirectory | Out-Null

$Arguments = @(
    "BuildCookRun",
    "-project=$ProjectFile",
    "-noP4",
    "-platform=Win64",
    "-clientconfig=$Configuration",
    "-build",
    "-cook",
    "-stage",
    "-pak",
    "-archive",
    "-archivedirectory=$OutputDirectory"
)
Write-Host "Packaging Unreal project for Windows..."
& $RunUAT @Arguments
if ($LASTEXITCODE -ne 0) { throw "Unreal BuildCookRun failed with exit code $LASTEXITCODE." }
Write-Host "Windows package created under $OutputDirectory" -ForegroundColor Green
