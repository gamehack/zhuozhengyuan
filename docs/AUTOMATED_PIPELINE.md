# Automated Blender → Unreal Asset Pipeline

**Status:** implementation on branch `automation/p0-asset-collision-pipeline`; local UE 5.8.4 execution is still required.

## Production principle

AI and deterministic scripts should author and validate assets. The user should not be asked to repeat editor operations that can be expressed as source data or an editor API call. Human involvement is reserved for visual/source-evidence review, decisions, and local execution when access to the user's Windows machine is required.

## Collision authoring

The P0 ground fixture is defined in Blender in meters:

- Render mesh: `TEST_Ground_10m`
- Render dimensions: 20 × 16 × 0.24 m
- Collision object: `UBX_TEST_Ground_10m_00`
- Collision shape: axis-aligned box
- Collision dimensions: 20 × 16 × 0.24 m

Unreal's FBX pipeline recognizes custom collision objects by name. `UBX_[RenderMeshName]_##` is the box convention. The render mesh name must match exactly.

Epic's FBX pipeline documentation also records an important constraint: when multiple render meshes with custom collision are placed in one FBX, only the first mesh's collision is imported. Therefore the pipeline exports one render mesh per FBX, with its own collision objects alongside it.

References:
- [FBX Static Mesh Pipeline — custom collision naming and caveats](https://dev.epicgames.com/documentation/unreal-engine/fbx-static-mesh-pipeline-in-unreal-engine?lang=en-US)
- [Unreal Engine 5.8 — scripting the Editor using Python](https://dev.epicgames.com/documentation/unreal-engine/scripting-the-unreal-editor-using-python?lang=en-US)
- [Unreal Engine 5.8 — collision setup with Blueprints and Python](https://dev.epicgames.com/documentation/unreal-engine/setting-up-collisions-with-static-meshes-in-blueprints-and-python-in-unreal-engine?lang=en-US)

## Commands

Run from the repository root in PowerShell.

1. Close Unreal Editor. Do not save the previous manually edited ground collision test asset; the automated import uses a clean destination folder.
2. Run one command:

```powershell
.\scripts\run_pipeline.ps1
```

The runner performs:

1. Blender Python scene generation.
2. Combined geometry-only fixture export.
3. One-FBX-per-render-mesh export with matching collision objects.
4. Standard-library validation of the asset export manifest.
5. Headless Unreal Editor Python import into `/Game/PipelineTest_Automated`.
6. Verification of ground render bounds, simple collision count, box element count, and box dimensions.

## Acceptance report

The machine-readable report is written to:

```text
build/pipeline-test/unreal-import-report.json
```

The pipeline passes only when:

- The expected 19 fixture render meshes import as Static Mesh assets.
- Ground render bounds equal 2000 × 1600 × 24 cm within 1 cm.
- Ground has exactly one simple collision primitive.
- That primitive is exactly one box element.
- The imported box dimensions equal 2000 × 1600 × 24 cm within 1 cm.

A failed check produces a non-zero process exit and a `FAIL` report. Do not compensate for a failed check by manually scaling collision in Unreal. Correct the Blender source, export or import script and rerun.

## Important scope boundary

This pipeline currently automates a synthetic P0 fixture. It proves infrastructure only; it does not reconstruct any real garden feature. Real asset collision types will be selected from asset semantics and geometry (box, capsule, convex decomposition, or no collision), then stored in structured asset metadata. The same pipeline will consume those definitions at scale.
