# P0-05 — FBX import and calibration checklist

This is a pipeline fixture, not a reconstruction of Zhuozhengyuan. Do not use its shapes as real garden geometry.

## 1. Generate the source FBX

From the repository root in PowerShell:

```powershell
.\scripts\build.ps1
```

Expected outputs (ignored by Git):

- `build/pipeline-test/pipeline-test.blend`
- `build/pipeline-test/pipeline-test.fbx` (geometry-only aggregate smoke-test FBX)
- `build/pipeline-test/report.json`
- `build/pipeline-test/assets/*.fbx` (one render mesh per FBX; matching collision meshes included)
- `build/pipeline-test/assets/asset-export-manifest.json`

The build also runs `scripts/validate_asset_exports.py`. It checks that the ground collision is named `UBX_TEST_Ground_10m_00` and measures 20 × 16 × 0.24 m before Unreal is involved.

The report should identify `PIPELINE_TEST_ONLY`, Blender 5.2.4 LTS, metric units, X=east, Y=north, Z=up, and 19 exported mesh objects. Do not add these generated files to Git.

## 2. Import into Unreal (automated)

The normal path is unattended; do not manually import the fixture FBX files one by one.

1. Close Unreal Editor.
2. From the repository root run:

```powershell
.\scripts\import_pipeline_assets.ps1
```

3. The commandlet imports the per-asset FBXs into `/Game/PipelineTest_Automated`.
4. The script writes `build/pipeline-test/unreal-import-report.json` and exits non-zero if import or collision validation fails.

The aggregate `pipeline-test.fbx` remains available as a geometry-only smoke-test artifact. It is not the collision-validation import source.

## 3. Expected calibration geometry

The fixture uses Blender metric units with a 1.0 scene scale and exports with FBX global scale 1.0 and unit scale applied.

| Object | Expected UE dimensions | Purpose |
|---|---:|---|
| `TEST_Calibration_Cube_1m` | 100 × 100 × 100 cm | Unit scale |
| `TEST_Calibration_X_2m` | 200 × 8 × 8 cm | X-axis direction |
| `TEST_Calibration_Y_1m` | 8 × 100 × 8 cm | Y-axis direction |

The X bar is timber-brown and the Y bar is foliage-green in the source fixture. Use object names and dimensions as the primary evidence if the FBX material importer changes colors.

Unreal's viewport axis gizmo uses X=red, Y=green, Z=blue. Confirm that the long dimension of the X bar is parallel to world X and the long dimension of the Y bar is parallel to world Y. The vertical axis must remain Z. No mirrored or unexpected 90-degree rotation is acceptable.

The ground fixture is 2000 × 1600 × 24 cm. Its origin and the other objects' positions are not site survey data.

## 4. Inspect and record

For the cube and both bars:

- Open each Static Mesh asset and inspect its Details / Bounds dimensions.
- Confirm no unexpected negative scale or rotation is introduced.
- Inspect the viewport for inverted faces, missing faces, or severe shading artifacts.
- Confirm the expected material slots exist and note whether materials were auto-created or need rebuilding.
- Do not assume collision exists merely because a mesh is visible.

Take screenshots of:
- FBX import options before import.
- Content/PipelineTest showing the imported assets.
- Calibration cube dimensions in the Static Mesh Editor.
- X/Y bars aligned against the viewport axis gizmo.

## 5. Automated collision import (no Static Mesh Editor hand-editing)

Collision geometry is authored in Blender Python and imported with its render mesh.

- Ground render mesh: `TEST_Ground_10m`
- Ground box collision mesh: `UBX_TEST_Ground_10m_00`
- Expected dimensions: 20 × 16 × 0.24 m (2000 × 1600 × 24 cm)
- The `UBX_` prefix tells the Unreal FBX importer to treat the object as a box collision primitive.
- Each render mesh is exported to its own FBX together with only its matching collision mesh. This is deliberate: Epic's FBX pipeline documentation states that when multiple render meshes with custom collision are in one FBX, only the first mesh's collision is imported.

Run the unattended import and verification from the repository root:

```powershell
# Close Unreal Editor first so the commandlet can open the project without file locks.
.\scripts\import_pipeline_assets.ps1
```

The script uses Unreal Engine 5.8.4's command-line editor and Python Editor Script Plugin. It imports the per-asset FBXs into `/Game/PipelineTest_Automated`, then checks:

- Exactly one simple collision primitive on the ground mesh.
- Exactly one imported box element.
- Box dimensions match 2000 × 1600 × 24 cm within 1 cm.
- Render-mesh bounds match the same expected dimensions within 1 cm.

The machine-readable result is written to `build/pipeline-test/unreal-import-report.json`. The command exits non-zero unless every ground check passes. Do not manually edit collision in the Static Mesh Editor to compensate for a failed automated check; fix the Blender source or import pipeline and rerun.

First-person movement testing remains a separate P0 walkthrough acceptance item.

## 6. Failure policy

If scale or orientation is wrong:

- Stop before importing real garden assets.
- Record the observed dimensions/orientation and the import settings.
- Correct the shared Blender FBX export or Unreal import convention once.
- Rebuild and re-import the fixture into a clean test folder.
- Never compensate by manually rotating or scaling individual garden assets.
