[CmdletBinding()]
param([string]$BlenderExe)

$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent $PSScriptRoot

$RunningEditor = Get-Process -Name "UnrealEditor" -ErrorAction SilentlyContinue
if ($RunningEditor) {
    throw "Close Unreal Editor first. Do not save the manually edited TEST_Ground_10m collision asset; this pipeline creates a clean automated import in /Game/PipelineTest_Automated."
}

Write-Host "=== Zhuozhengyuan P0 automated asset pipeline ===" -ForegroundColor Cyan
$BuildScript = Join-Path $PSScriptRoot "build.ps1"
$ImportScript = Join-Path $PSScriptRoot "import_pipeline_assets.ps1"

if ($BlenderExe) {
    & $BuildScript -BlenderExe $BlenderExe
} else {
    & $BuildScript
}
if ($LASTEXITCODE -ne 0) {
    throw "Blender build/export stage failed."
}

& $ImportScript
if ($LASTEXITCODE -ne 0) {
    throw "Unreal import/verification stage failed."
}

Write-Host ""
Write-Host "P0 AUTOMATED ASSET PIPELINE PASSED" -ForegroundColor Green
Write-Host "Review build\pipeline-test\unreal-import-report.json"
