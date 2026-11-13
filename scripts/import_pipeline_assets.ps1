[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent $PSScriptRoot
$Project = Join-Path $RepoRoot "unreal\Zhuozhengyuan\Zhuozhengyuan.uproject"
$Script = Join-Path $RepoRoot "unreal\scripts\import_pipeline_assets.py"
$BuildDir = Join-Path $RepoRoot "build\pipeline-test"
$Manifest = Join-Path $BuildDir "assets\asset-export-manifest.json"
$Report = Join-Path $BuildDir "unreal-import-report.json"
$Log = Join-Path $BuildDir "unreal-import.log"

if (-not (Test-Path -LiteralPath $Project)) {
    throw "Unreal project not found: $Project"
}
if (-not (Test-Path -LiteralPath $Manifest)) {
    throw "Asset export manifest not found. Run .\scripts\build.ps1 first."
}
if (-not (Test-Path -LiteralPath $Script)) {
    throw "Unreal import script not found: $Script"
}

$RunningEditor = Get-Process -Name "UnrealEditor" -ErrorAction SilentlyContinue
if ($RunningEditor) {
    throw "Close Unreal Editor before running the headless import. This avoids project file locks and unsaved editor state."
}

. (Join-Path $PSScriptRoot "resolve-unreal.ps1")
$UnrealRoot = Get-ZjyUnrealEngineRoot -RequiredMinorVersion "5.8"
if (-not $UnrealRoot) {
    throw "Unreal Engine 5.8 was not found. Set UE_5_8_ROOT or UE_ROOT."
}

$UnrealCmd = Join-Path $UnrealRoot "Engine\Binaries\Win64\UnrealEditor-Cmd.exe"
if (-not (Test-Path -LiteralPath $UnrealCmd)) {
    throw "Unreal command-line editor not found: $UnrealCmd"
}

New-Item -ItemType Directory -Force -Path $BuildDir | Out-Null
Remove-Item -LiteralPath $Report -Force -ErrorAction SilentlyContinue
Remove-Item -LiteralPath $Log -Force -ErrorAction SilentlyContinue

Write-Host "Running unattended Unreal FBX import and collision verification..." -ForegroundColor Cyan
$Arguments = @(
    $Project,
    "-run=pythonscript",
    "-script=$Script",
    "-unattended",
    "-nop4",
    "-nosplash",
    "-log=$Log"
)
& $UnrealCmd @Arguments
$ExitCode = $LASTEXITCODE
if ($ExitCode -ne 0) {
    throw "Unreal automated import failed with exit code $ExitCode. Inspect: $Log"
}
if (-not (Test-Path -LiteralPath $Report)) {
    throw "Unreal did not produce the expected verification report: $Report"
}

$Result = Get-Content -LiteralPath $Report -Raw | ConvertFrom-Json
if ($Result.status -ne "PASS") {
    throw "Unreal collision verification did not pass. Inspect: $Report"
}

Write-Host ""
Write-Host "UNREAL IMPORT AND COLLISION VALIDATION PASSED" -ForegroundColor Green
Write-Host "Imported Static Meshes: $($Result.imported_static_mesh_count)"
Write-Host "Ground collision primitives: $($Result.ground_validation.collision_count)"
Write-Host "Ground bounds: $($Result.ground_validation.mesh_bounds_dimensions_cm -join ' x ') cm"
Write-Host "Report: $Report"
