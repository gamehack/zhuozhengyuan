# P0-05 — FBX import and calibration checklist

This is a pipeline fixture, not a reconstruction of Zhuozhengyuan. Do not use its shapes as real garden geometry.

## 1. Generate the source FBX

From the repository root in PowerShell:

```powershell
.\scripts\build.ps1
```

Expected outputs (ignored by Git):

- `build/pipeline-test/pipeline-test.blend`
- `build/pipeline-test/pipeline-test.fbx`
- `build/pipeline-test/report.json`

The report should identify `PIPELINE_TEST_ONLY`, Blender 5.2.4 LTS, metric units, X=east, Y=north, Z=up, and 19 exported mesh objects. Do not add these generated files to Git.

## 2. Import into Unreal

1. Open `unreal/Zhuozhengyuan/Zhuozhengyuan.uproject` with Unreal Engine 5.8.4.
2. In the Content Drawer, create `Content/PipelineTest`.
3. Open that folder and use **Import** to select `build/pipeline-test/pipeline-test.fbx`.
4. Import as Static Mesh assets; do not import as a Level/Scene.
5. Keep **Combine Meshes** disabled so the 19 test objects remain separate.
6. Keep **Import Uniform Scale = 1.0** and import translation/rotation at zero.
7. Keep **Force Front X Axis** disabled. Do not apply per-mesh rotations or scale corrections.
8. Enable **Import Materials** for this first material smoke test. There are no image textures in the fixture.
9. Use **Import Normals and Tangents** if the FBX import dialog exposes the normal import method.
10. Keep Nanite disabled and do not generate collision during this first geometry inspection. Confirm the exact options shown by UE 5.8.4 if labels differ.

If an option is not present in the UE 5.8.4 dialog, leave its equivalent at the engine default and record that fact rather than guessing.

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

## 5. Collision is a separate sub-step

After scale and axes pass, add simple collision to the ground mesh in the Static Mesh Editor (for example, a box collision fitted to the ground). Save the asset and verify collision visualization. First-person collision testing is completed in the later walkthrough task; do not mark the walkthrough complete here.

## 6. Failure policy

If scale or orientation is wrong:

- Stop before importing real garden assets.
- Record the observed dimensions/orientation and the import settings.
- Correct the shared Blender FBX export or Unreal import convention once.
- Rebuild and re-import the fixture into a clean test folder.
- Never compensate by manually rotating or scaling individual garden assets.
