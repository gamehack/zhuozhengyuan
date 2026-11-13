[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$SourceProjectDirectory
)

$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent $PSScriptRoot
$Destination = Join-Path $RepoRoot "unreal\Zhuozhengyuan"

if (-not (Test-Path -LiteralPath $SourceProjectDirectory -PathType Container)) {
    throw "Source directory does not exist: $SourceProjectDirectory"
}

$RunningEditor = Get-Process -Name "UnrealEditor" -ErrorAction SilentlyContinue
if ($RunningEditor) {
    throw "UnrealEditor is running. Close the editor before migrating the project."
}

$ProjectFile = Get-ChildItem -LiteralPath $SourceProjectDirectory -Filter "Zhuozhengyuan.uproject" -File -Recurse -ErrorAction Stop | Select-Object -First 1
if (-not $ProjectFile) {
    throw "Zhuozhengyuan.uproject was not found under: $SourceProjectDirectory"
}

$SourceRoot = $ProjectFile.Directory.FullName
$ResolvedSource = [System.IO.Path]::GetFullPath($SourceRoot).TrimEnd('\')
$ResolvedDestination = [System.IO.Path]::GetFullPath($Destination).TrimEnd('\')

if ($ResolvedSource -eq $ResolvedDestination) {
    Write-Host "Project is already in the repository: $ResolvedDestination" -ForegroundColor Green
    exit 0
}

if (Test-Path -LiteralPath $Destination) {
    throw "Destination already exists; refusing to overwrite or merge: $Destination"
}

Write-Host "Source project:      $ResolvedSource"
Write-Host "Destination project: $ResolvedDestination"
Write-Host "The original project will be kept unchanged as a backup."
Write-Host "Copying project files (excluding generated caches and build outputs)..."

New-Item -ItemType Directory -Force -Path (Split-Path -Parent $Destination) | Out-Null
& robocopy $ResolvedSource $Destination /E /COPY:DAT /DCOPY:DAT /R:2 /W:2 /XD "Binaries" "DerivedDataCache" "Intermediate" "Saved" ".vs" /XF "*.sln" "*.slnx"

$RobocopyExitCode = $LASTEXITCODE
if ($RobocopyExitCode -ge 8) {
    throw "Project copy failed; robocopy exit code: $RobocopyExitCode"
}

$DestinationProject = Join-Path $Destination "Zhuozhengyuan.uproject"
if (-not (Test-Path -LiteralPath $DestinationProject -PathType Leaf)) {
    throw "Copy completed but the destination .uproject file is missing: $DestinationProject"
}

Write-Host ""
Write-Host "Project copied successfully." -ForegroundColor Green
Write-Host "Project file: $DestinationProject"
Write-Host "Original source was not deleted."
Write-Host "Next: open the destination project, verify it, then run git status."
