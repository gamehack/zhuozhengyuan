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

$EngineRoots = @()
if ($env:UE_5_8_ROOT) { $EngineRoots += $env:UE_5_8_ROOT }
if ($env:UE_ROOT) { $EngineRoots += $env:UE_ROOT }
$EngineRoots += "$env:ProgramFiles\Epic Games\UE_5.8"

$RunUAT = $null
foreach ($Root in $EngineRoots) {
    $Candidate = Join-Path $Root "Engine\Build\BatchFiles\RunUAT.bat"
    if (Test-Path $Candidate) { $RunUAT = $Candidate; break }
}
if (-not $RunUAT) {
    throw "RunUAT.bat not found. Install UE 5.8.x or set UE_5_8_ROOT to the engine directory."
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
