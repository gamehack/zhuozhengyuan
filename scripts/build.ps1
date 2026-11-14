[CmdletBinding()]
param([string]$BlenderExe)

$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent $PSScriptRoot
$BuildDir = Join-Path $RepoRoot "build\pipeline-test"
$BlendFile = Join-Path $BuildDir "pipeline-test.blend"
$ReportFile = Join-Path $BuildDir "report.json"
$FbxFile = Join-Path $BuildDir "pipeline-test.fbx"
$AssetDir = Join-Path $BuildDir "assets"
$AssetManifest = Join-Path $AssetDir "asset-export-manifest.json"

if (-not $BlenderExe) {
    if ($env:BLENDER_EXE) { $BlenderExe = $env:BLENDER_EXE }
    elseif (Test-Path "C:\Program Files\Blender Foundation\Blender 5.2\blender.exe") {
        $BlenderExe = "C:\Program Files\Blender Foundation\Blender 5.2\blender.exe"
    } else {
        $Command = Get-Command blender -ErrorAction SilentlyContinue
        if ($Command) { $BlenderExe = $Command.Source }
    }
}
if (-not $BlenderExe -or -not (Test-Path $BlenderExe)) {
    throw "Blender 5.2.x not found. Set BLENDER_EXE or pass -BlenderExe."
}

New-Item -ItemType Directory -Force -Path $BuildDir | Out-Null
$Generator = Join-Path $RepoRoot "blender\scripts\create_pipeline_test_scene.py"

# Remove stale outputs so a failed run can never be mistaken for a fresh build.
Remove-Item -LiteralPath $BlendFile, $ReportFile, $FbxFile -Force -ErrorAction SilentlyContinue
if (Test-Path -LiteralPath $AssetDir) { Remove-Item -LiteralPath $AssetDir -Recurse -Force }

Write-Host "Generating synthetic pipeline-test scene..."
& $BlenderExe --background --factory-startup --python $Generator -- --blend-output $BlendFile --report-output $ReportFile
$BlenderExitCode = $LASTEXITCODE
if ($BlenderExitCode -ne 0) {
    throw "Blender scene generation failed with exit code $BlenderExitCode. FBX export was not started."
}
if (-not (Test-Path -LiteralPath $BlendFile)) {
    throw "Blender exited successfully but did not create the expected BLEND file: $BlendFile"
}
if (-not (Test-Path -LiteralPath $ReportFile)) {
    throw "Blender exited successfully but did not create the expected report: $ReportFile"
}

Write-Host "Exporting pipeline-test FBX..."
& (Join-Path $PSScriptRoot "export.ps1") -BlendFile $BlendFile -OutputFile $FbxFile -BlenderExe $BlenderExe
if ($LASTEXITCODE -ne 0) {
    throw "FBX export stage failed with exit code $LASTEXITCODE."
}
if (-not (Test-Path -LiteralPath $FbxFile)) {
    throw "Expected FBX output was not created: $FbxFile"
}

Write-Host "Exporting collision-aware per-asset FBX files..."
$AssetExporter = Join-Path $RepoRoot "blender\scripts\export_assets.py"
& $BlenderExe --background $BlendFile --python $AssetExporter -- --output-dir $AssetDir
$AssetExportExitCode = $LASTEXITCODE
if ($AssetExportExitCode -ne 0) {
    throw "Per-asset FBX export failed with exit code $AssetExportExitCode."
}
if (-not (Test-Path -LiteralPath $AssetManifest)) {
    throw "Per-asset export manifest was not created: $AssetManifest"
}

Write-Host "Validating collision-aware exports..."
$AssetValidator = Join-Path $RepoRoot "scripts\validate_asset_exports.py"
& python $AssetValidator --manifest $AssetManifest
if ($LASTEXITCODE -ne 0) {
    throw "Per-asset FBX validation failed."
}

Write-Host ""
Write-Host "P0 Blender pipeline fixture generated:" -ForegroundColor Green
Write-Host "BLEND:  $BlendFile"
Write-Host "FBX:    $FbxFile"
Write-Host "Report: $ReportFile"
Write-Host "Per-asset FBX: $AssetDir"
Write-Host "Asset manifest: $AssetManifest"
Write-Host "Reminder: this is synthetic test geometry, not a reconstruction of the real garden."
