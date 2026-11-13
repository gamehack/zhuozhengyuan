function Get-ZjyUnrealEngineRoot {
    [CmdletBinding()]
    param(
        [string]$RequiredMinorVersion = "5.8"
    )

    $Roots = [System.Collections.Generic.List[string]]::new()

    # Explicit user configuration takes priority.
    foreach ($ConfiguredRoot in @($env:UE_5_8_ROOT, $env:UE_ROOT)) {
        if (-not [string]::IsNullOrWhiteSpace($ConfiguredRoot)) {
            $null = $Roots.Add($ConfiguredRoot)
        }
    }

    # Common Epic Games Launcher installation directories.
    $ProgramFilesRoots = @(
        $env:ProgramFiles,
        [Environment]::GetEnvironmentVariable("ProgramFiles(x86)")
    )
    foreach ($ProgramFilesRoot in $ProgramFilesRoots) {
        if ([string]::IsNullOrWhiteSpace($ProgramFilesRoot)) { continue }
        foreach ($FolderName in @("UE_5.8", "UE_5.8.4")) {
            $null = $Roots.Add((Join-Path $ProgramFilesRoot "Epic Games\$FolderName"))
        }
    }

    # Epic Launcher manifests also reveal custom installation drives and paths.
    $ManifestDirectory = Join-Path $env:ProgramData "Epic\EpicGamesLauncher\Data\Manifests"
    if (Test-Path -LiteralPath $ManifestDirectory) {
        $ManifestFiles = Get-ChildItem -LiteralPath $ManifestDirectory -Filter "*.item" -File -ErrorAction SilentlyContinue
        foreach ($ManifestFile in $ManifestFiles) {
            try {
                $Manifest = Get-Content -LiteralPath $ManifestFile.FullName -Raw -ErrorAction Stop |
                    ConvertFrom-Json -ErrorAction Stop
            } catch {
                continue
            }

            $AppName = [string]$Manifest.AppName
            $DisplayName = [string]$Manifest.DisplayName
            # Epic Launcher may use either UE_5.8 or UE_5.8.4 as AppName.
            # Accept a dot, underscore, or end-of-string after the minor version.
            $IsTargetEngine = (
                $AppName -match '^UE_5\.8(?:\.|$|_)' -or
                $DisplayName -match '(?i)(?:Unreal Engine|UE)[\s_]+5\.8'
            )
            $InstallLocation = [string]$Manifest.InstallLocation
            if ($IsTargetEngine -and -not [string]::IsNullOrWhiteSpace($InstallLocation)) {
                $null = $Roots.Add($InstallLocation)
            }
        }
    }

    $SeenRoots = @{}
    foreach ($Root in $Roots) {
        if ([string]::IsNullOrWhiteSpace($Root)) { continue }

        try {
            $NormalizedRoot = [System.IO.Path]::GetFullPath($Root.TrimEnd('\'))
        } catch {
            continue
        }

        if ($SeenRoots.ContainsKey($NormalizedRoot)) { continue }
        $SeenRoots[$NormalizedRoot] = $true

        $EditorPath = Join-Path $NormalizedRoot "Engine\Binaries\Win64\UnrealEditor.exe"
        if (-not (Test-Path -LiteralPath $EditorPath)) { continue }

        $BuildVersionPath = Join-Path $NormalizedRoot "Engine\Build\Build.version"
        if (Test-Path -LiteralPath $BuildVersionPath) {
            try {
                $BuildVersion = Get-Content -LiteralPath $BuildVersionPath -Raw |
                    ConvertFrom-Json -ErrorAction Stop
                $DetectedMinorVersion = "$($BuildVersion.MajorVersion).$($BuildVersion.MinorVersion)"
                if ($RequiredMinorVersion -and $DetectedMinorVersion -ne $RequiredMinorVersion) {
                    continue
                }
            } catch {
                # An editor executable is still useful to report if version metadata is unreadable.
            }
        }

        return $NormalizedRoot
    }

    return $null
}
