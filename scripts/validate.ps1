[CmdletBinding()]
param(
    [switch]$SkipData,
    [switch]$SkipToolDetection
)

$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent $PSScriptRoot
Write-Host "=== Zhuozhengyuan local environment validation ===" -ForegroundColor Cyan

if (-not $SkipData) {
    $Python = Get-Command python -ErrorAction SilentlyContinue
    if (-not $Python) { throw "Python was not found on PATH. Install Python 3.10+ or add it to PATH." }
    & $Python.Source (Join-Path $RepoRoot "scripts\validate_data.py")
    if ($LASTEXITCODE -ne 0) { throw "Project data validation failed." }
}

if (-not $SkipToolDetection) {
    $BlenderCandidates = @()
    if ($env:BLENDER_EXE) { $BlenderCandidates += $env:BLENDER_EXE }
    $BlenderCandidates += "C:\Program Files\Blender Foundation\Blender 5.2\blender.exe"
    $BlenderCommand = Get-Command blender -ErrorAction SilentlyContinue
    if ($BlenderCommand) { $BlenderCandidates += $BlenderCommand.Source }
    $BlenderExe = $BlenderCandidates | Where-Object { $_ -and (Test-Path $_) } | Select-Object -First 1

    if ($BlenderExe) {
        Write-Host "Blender: $BlenderExe" -ForegroundColor Green
        & $BlenderExe --version
        if ($LASTEXITCODE -ne 0) { Write-Warning "Blender version command returned a non-zero exit code." }
    } else {
        Write-Warning "Blender executable not found. Set BLENDER_EXE or install Blender 5.2.x."
    }

    . (Join-Path $PSScriptRoot "resolve-unreal.ps1")
    $UnrealRoot = Get-ZjyUnrealEngineRoot -RequiredMinorVersion "5.8"
    if ($UnrealRoot) {
        $UnrealEditor = Join-Path $UnrealRoot "Engine\Binaries\Win64\UnrealEditor.exe"
        Write-Host "Unreal Editor: $UnrealEditor" -ForegroundColor Green

        $BuildVersionPath = Join-Path $UnrealRoot "Engine\Build\Build.version"
        if (Test-Path -LiteralPath $BuildVersionPath) {
            $BuildVersion = Get-Content -LiteralPath $BuildVersionPath -Raw | ConvertFrom-Json
            $VersionText = "{0}.{1}.{2}" -f $BuildVersion.MajorVersion, $BuildVersion.MinorVersion, $BuildVersion.PatchVersion
            Write-Host "Unreal Engine version: $VersionText"
            if ($VersionText -ne "5.8.4") {
                Write-Warning "Detected UE $VersionText. Project baseline is UE 5.8.4; confirm compatibility before creating the project."
            }
        } else {
            Write-Warning "Unreal Engine Build.version metadata was not found; editor executable exists but exact version is unverified."
        }
    } else {
        Write-Warning "Unreal Engine 5.8 was not found in configured paths or Epic Games Launcher install manifests."
    }

    $Computer = Get-CimInstance Win32_ComputerSystem
    $Os = Get-CimInstance Win32_OperatingSystem
    $FreeC = (Get-Volume -DriveLetter C -ErrorAction SilentlyContinue).SizeRemaining
    Write-Host ("RAM: {0:N1} GB" -f ($Computer.TotalPhysicalMemory / 1GB))
    Write-Host "OS: $($Os.Caption) $($Os.Version)"
    if ($FreeC) { Write-Host ("C: free space: {0:N1} GB" -f ($FreeC / 1GB)) }
}

Write-Host "Environment check complete. Warnings are informational unless a required command failed." -ForegroundColor Cyan
