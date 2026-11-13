# P0 Implementation Plan

## Objective
Prove a repeatable local pipeline from structured data and Blender Python to FBX, Unreal Engine 5.8.4, and a minimal Windows walkthrough. P0 is infrastructure validation and does not reconstruct any real garden feature.

## Work packages

### P0-1 — Local environment and hardware validation
- [x] Record current hardware baseline.
- [x] Confirm Blender executable and version from the prior Windows validation (Blender 5.2.4 LTS).
- [x] Confirm Unreal Engine 5.8.4 installation (Build.version: 5.8.4, changelist 58902052; Windows validation passed 2026-11-13).
- [x] Confirm C: free space (117.1 GB on 2026-11-13).
- [x] Create the UE 5.8.4 Blank Blueprint project locally (initially under Documents, 2026-11-13).
- [x] Copy the existing project into the repository at unreal/Zhuozhengyuan (project file exists; 2026-11-13).
- [x] Open the repository copy successfully and set viewport scalability to Low (2026-11-13).
- [x] Save the initial level as Content/Maps/L_Main.umap (confirmed in local Git status, 2026-11-13).
- [x] Set initial viewport scalability to Low for Radeon 680M / 16 GB RAM.

### P0-2 — Repository foundation
- [x] Establish project charter and technical direction.
- [x] Establish data, evidence, and coordinate standards.
- [x] Establish art direction and quality gates.
- [x] Add CI for data validation.
- [x] Review repository structure after the first local run; only the project descriptor, four config files, and initial map are untracked (2026-11-13).

### P0-3 — Research register and baseline metadata
- [x] Register initial official and UNESCO sources.
- [x] Record published site area and reference location as metadata only.
- [x] Record that no survey datum or site boundary geometry has been established.
- [x] Seed an official named-feature register without inventing positions or dimensions.
- [x] Document the historical-survey and present-day measurement gap.
- [ ] Obtain a reliable current site plan or authorized measured drawing.
- [ ] Build the source-backed asset inventory.
- [ ] Capture and register fixed viewpoints.

### P0-4 — Blender automation
- [x] Add a synthetic pipeline-test scene generator.
- [x] Add a collection-scoped FBX export script.
- [x] Run scripts locally with Blender 5.2.4 (Windows, 2026-11-13).
- [x] Confirm generated BLEND, FBX, and report (19 mesh objects exported, 2026-11-13).
- [x] Verify repeatability with a second clean run and stable export count (19 meshes on both runs).

### P0-5 — Unreal import and walkthrough
- [x] Create the UE 5.8.4 Blank Blueprint project locally and place its copy under unreal/Zhuozhengyuan.
- [x] Commit and push the initial UE project baseline (07c8201, 2026-11-13).
- [ ] Import the calibration FBX from build/pipeline-test/pipeline-test.fbx into Content/PipelineTest.
- [x] Verify the 1 m calibration cube imports at 100 × 100 × 100 cm in UE 5.8.4 (user screenshot, 2026-11-13).
- [x] Verify X/Y calibration bar bounds and principal orientation: X bar 200×8×7 cm (minor-axis display discrepancy pending exact bounds); Y bar 8×100×8 cm, aligned with world Y (2026-11-13).
- [ ] Inspect normals/shading, confirm material assignments, and resolve X-bar 7 cm display discrepancy with exact bounds.
- [x] Replace oversized test-column collision with one tightly fitting capsule simplified collision (visual inspection, 2026-11-13; asset save pending).
- [ ] Add and test simple ground collision.
- [ ] Create a minimal first-person walkthrough.
- [ ] Record editor performance and memory usage.

### P0-6 — Windows packaging and acceptance
- [x] Add a guarded packaging entry point.
- [ ] Package a Windows development build.
- [ ] Run outside the editor.
- [ ] Record exact engine version and build configuration.
- [ ] Mark P0 complete only when all acceptance criteria pass.

## Local hardware baseline
- HP EliteBook 865 16-inch G9.
- AMD Ryzen 7 PRO 6850HS.
- AMD Radeon 680M integrated graphics.
- 16 GB DDR5-4800 (2 × 8 GB Micron).
- Windows 11 Home, build 10.0.26300.
- C: free space reported as 151.5 GB at initial inspection.

This machine is the P0 authoring and pipeline-validation machine, not the assumed final high-fidelity runtime target.

## P0 rendering profile
Use a small test scene, conservative scalability, no hardware ray tracing or Lumen for initial validation, no Nanite dependency, simple lighting, and low-resolution previews. Revisit quality only after the target GPU and memory budget are known.

## Exit criteria
See docs/QUALITY_STANDARDS.md. The critical end-to-end test is Blender Python → BLEND → FBX → UE import → 1 m calibration → Windows walkthrough → packaged executable.


## GitHub task tracking

- [P0-01 — Validate local Windows toolchain](https://github.com/gamehack/zhuozhengyuan/issues/1)
- [P0-02 — Obtain authoritative current site plan and survey material](https://github.com/gamehack/zhuozhengyuan/issues/2)
- [P0-03 — Run Blender fixture and export FBX](https://github.com/gamehack/zhuozhengyuan/issues/3)
- [P0-04 — Install/confirm UE 5.8.4 and create project](https://github.com/gamehack/zhuozhengyuan/issues/4)
- [P0-05 — Verify FBX scale, axes, and materials in Unreal](https://github.com/gamehack/zhuozhengyuan/issues/5)
- [P0-06 — Complete Windows walkthrough and package acceptance](https://github.com/gamehack/zhuozhengyuan/issues/6)


## P0 automation correction — 2026-11-14

The manual Static Mesh Editor collision workflow has been stopped. The replacement implementation is documented in [AUTOMATED_PIPELINE.md](AUTOMATED_PIPELINE.md) and is on branch `automation/p0-asset-collision-pipeline`.

Implemented in source:
- Blender-authored `UBX_TEST_Ground_10m_00` collision box generated from render-mesh bounds.
- One render mesh per FBX, with matching collision objects included.
- Per-asset FBX manifest and standard-library validation.
- Headless Unreal Python importer and machine-readable collision verification.
- Single-command runner: `.\scripts\run_pipeline.ps1`.

Still pending: execute the new pipeline on the local Windows / UE 5.8.4 installation and obtain a PASS report. Do not mark P0 collision or walkthrough acceptance complete until that local run passes.
