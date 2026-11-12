# Technical Architecture

## Locked P0 stack

| Layer | Technology | Responsibility |
|---|---|---|
| Source asset authoring | Blender 5.2.4 LTS | Meshes, materials, scene organization, procedural modeling |
| Asset automation | Blender Python API | Deterministic generation, validation, export |
| Real-time runtime | Unreal Engine 5.8.4 | Scene assembly, lighting, collision, navigation, Windows runtime |
| Primary interchange | FBX | Blender-to-Unreal static mesh transfer |
| Preview interchange | GLB | Lightweight inspection and cross-tool preview only |
| Project automation | Python + PowerShell | Data validation, build, export, packaging |
| Version control | GitHub | Code, documentation, schemas, small fixtures, manifests |

Engine and tool versions are pinned for P0 reproducibility. Upgrade only through a documented change and a successful pipeline regression test.

## Production pipeline
1. Research sources and capture evidence.
2. Convert trusted measurements into structured site and asset data.
3. Validate metadata, IDs, references, units, and evidence grades.
4. Generate or refine source assets in Blender.
5. Validate Blender scene structure and object metadata.
6. Export FBX using the project's single export profile.
7. Import into Unreal and verify scale, axes, normals, UVs, materials, collision, and LOD.
8. Assemble the runtime scene and compare fixed viewpoints.
9. Package a Windows build after editor validation.

## Coordinate and unit policy
- Research measurements are stored in meters.
- Blender scenes use Metric units with scale length 1.0 (one Blender unit represents one meter).
- Unreal Engine uses centimeters internally.
- The FBX interchange profile is expected to perform unit conversion; verify with a 1 m calibration object on every new engine/export profile.
- Project-local axes are provisionally X=east, Y=north, Z=up. This is a project convention, not a claim about source-map orientation.
- Preserve source coordinate reference systems and georeferencing metadata.
- Do not derive the local origin from the UNESCO reference point. A surveyed or traceable site-plan datum must be selected first.
- FBX axis conversion is centralized in the export script. Do not manually rotate or mirror individual assets to compensate for import settings.

## Unreal rendering strategy

### P0 profile for the current HP EliteBook 865 G9
The current machine has a Ryzen 7 PRO 6850HS, Radeon 680M integrated graphics, 16 GB DDR5-4800, and Windows 11. Use a small test scene and conservative scalability settings. Keep hardware ray tracing and Lumen disabled for the initial pipeline proof. Do not depend on Nanite for the P0 test.

### Later quality profile
Evaluate Lumen, Nanite, Virtual Shadow Maps, foliage instancing, and higher-quality water only after the target GPU and memory budget are known. Use Nanite selectively; dense foliage generally requires instancing and LOD strategy rather than blindly converting every plant to Nanite.

## Scene organization
Use stable collections/folders and asset IDs. Keep reference objects, terrain, water, architecture, rocks, vegetation, paths, lighting, and export sets separate. Export only the intended collection or tagged objects.

## Runtime architecture
The first Unreal deliverable is a small first-person walkthrough used to verify asset import and runtime behavior. Garden-wide streaming, World Partition, advanced water, seasonal states, audio, and optimization are later decisions based on measured scene scale and target hardware.

## CI boundary
GitHub Actions validates source-controlled JSON, CSV, and Python tests. It does not run Blender rendering or Unreal Editor/BuildCookRun in P0. Those are Windows-local tasks because the required software, assets, and GPU environment are not available in the hosted CI runner.
