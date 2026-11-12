[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][string]$BlendFile,
    [Parameter(Mandatory = $true)][string]$OutputFile,
    [string]$BlenderExe
)

$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent $PSScriptRoot
if (-not (Test-Path $BlendFile)) { throw "BLEND file not found: $BlendFile" }

if (-not $BlenderExe) {
    if ($env:BLENDER_EXE) { $BlenderExe = $env:BLENDER_EXE }
    elseif (Test-Path "C:\Program Files\Blender Foundation\Blender 5.2\blender.exe") {
        $BlenderExe = "C:\Program Files\Blender Foundation\Blender 5.2\blender.exe"
    } else {
        $Command = Get-Command blender -ErrorAction SilentlyContinue
        if ($Command) { $BlenderExe = $Command.Source }
    }
}
if (-not $BlenderExe -or -not (Test-Path $BlenderExe)) { throw "Blender executable not found." }

$OutputParent = Split-Path -Parent $OutputFile
New-Item -ItemType Directory -Force -Path $OutputParent | Out-Null
$Exporter = Join-Path $RepoRoot "blender\scripts\export_fbx.py"

& $BlenderExe --background $BlendFile --python $Exporter -- --output $OutputFile
if ($LASTEXITCODE -ne 0) { throw "Blender FBX exporter failed with exit code $LASTEXITCODE." }
if (-not (Test-Path $OutputFile)) { throw "Expected FBX output was not created: $OutputFile" }
Write-Host "FBX exported: $OutputFile" -ForegroundColor Green
