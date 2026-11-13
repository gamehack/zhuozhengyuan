# Unreal Engine Project

## P0 target
Unreal Engine 5.8.4, Windows, Blueprint-first first-person walkthrough.

The local Blueprint project has been created with UE 5.8.4. It was initially created outside the repository and must be copied into unreal/Zhuozhengyuan before repository-based development continues.

Do not commit generated Binaries, Intermediate, Saved, DerivedDataCache, or local IDE files.

## Initial project settings
For the HP EliteBook 865 G9 (Radeon 680M integrated graphics, 16 GB RAM):
- Start with a small scene and Low/Medium scalability.
- Disable hardware ray tracing and Lumen for the first import test.
- Do not depend on Nanite.
- Use a simple skylight/directional-light setup.
- Keep texture sizes and foliage counts low.
- Test the FBX calibration cube before importing garden-scale geometry.

## FBX import acceptance
1. Import the pipeline-test FBX.
2. Confirm the calibration cube measures 100 Unreal units on each side (1 meter).
3. Confirm the X/Y calibration bars point along the intended project axes.
4. Inspect normals, material assignments, and object transforms.
5. Add simple collision to the ground and test first-person movement.
6. Record the exact editor version and import settings in the P0 issue.

## Packaging
Use scripts/package.ps1 only after a valid .uproject exists and the editor has successfully opened it. Packaging is not expected to work before local engine installation and project creation.


## Verified local engine installation

The Windows environment validator detected the user's installed engine on 2026-11-13:

- Engine root: `C:\\Program Files\\Epic Games\\UE_5.8\\UE_5.8`
- Version: **5.8.4**
- Changelist: **58902052**
- Editor executable: `Engine/Binaries/Win64/UnrealEditor.exe`

The next local action is to create the Blueprint project from the editor wizard. Do not create a C++ project or compile engine source for P0.

## Exact project creation procedure

1. Launch `UnrealEditor.exe` from Epic Games Launcher, or run the detected executable.
2. In the Project Browser select **Games** → **Blank**.
3. Select **Blueprint** (not C++).
4. Target platform: **Desktop**.
5. Quality preset: **Scalable** (not Maximum Quality).
6. Starter Content: **Off**.
7. Project name: `Zhuozhengyuan`.
8. Project location: the repository's `unreal` directory.
9. Create the project. The expected project file is:
   `unreal/Zhuozhengyuan/Zhuozhengyuan.uproject`.

If the wizard asks whether to enable ray tracing, leave it disabled. Do not add optional plugins yet.

After creation, open the project once, wait for shader compilation and initial asset discovery to finish, save, then close the editor. Keep the editor on Low scalability for the first test. Avoid opening Blender and other memory-heavy applications simultaneously on the 16 GB machine.

## First local verification

From the repository root:

```powershell
$Project = ".\\unreal\\Zhuozhengyuan\\Zhuozhengyuan.uproject"
Test-Path $Project
Get-Content $Project
```

Expected: `Test-Path` returns `True`. Do not run the packaging script yet; FBX import and first-person walkthrough are still pending.

## Migrate the existing local project into this repository

Do not create a second project. Close Unreal Editor, pull the latest repository, and run the migration helper from the repository root:

```powershell
git pull origin main
.\scripts\migrate-unreal-project.ps1 -SourceProjectDirectory 'PATH_TO_THE_EXISTING_ZHUOZHENGYUAN_PROJECT_FOLDER'
```

The script searches the supplied folder for Zhuozhengyuan.uproject, copies the project into unreal/Zhuozhengyuan, and excludes generated folders (Binaries, DerivedDataCache, Intermediate, Saved, and .vs). It refuses to overwrite an existing destination and never deletes the original project.

After copying:

```powershell
$Project = ".\unreal\Zhuozhengyuan\Zhuozhengyuan.uproject"
Test-Path $Project
git status --short
```

Open the copied project at the repository path once. Confirm it opens, then close the editor. Keep the original Documents copy until the repository copy has been verified and committed.
