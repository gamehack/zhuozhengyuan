# P0 Implementation Plan

## Objective
Prove a repeatable local pipeline from structured data and Blender Python to FBX, Unreal Engine 5.8.4, and a minimal Windows walkthrough. P0 is infrastructure validation and does not reconstruct any real garden feature.

## Work packages

### P0-1 — Local environment and hardware validation
- [x] Record current hardware baseline.
- [ ] Confirm Blender executable and version from PowerShell.
- [ ] Install or confirm Unreal Engine 5.8.4.
- [ ] Confirm available disk space and editor launch.
- [ ] Keep initial editor settings conservative for Radeon 680M / 16 GB RAM.

### P0-2 — Repository foundation
- [x] Establish project charter and technical direction.
- [x] Establish data, evidence, and coordinate standards.
- [x] Establish art direction and quality gates.
- [x] Add CI for data validation.
- [ ] Review repository structure after the first local run.

### P0-3 — Research register and baseline metadata
- [x] Register initial official and UNESCO sources.
- [x] Record published site area and reference location as metadata only.
- [x] Record that no survey datum or site boundary geometry has been established.
- [ ] Obtain a reliable current site plan or authorized measured drawing.
- [ ] Build the source-backed asset inventory.
- [ ] Capture and register fixed viewpoints.

### P0-4 — Blender automation
- [x] Add a synthetic pipeline-test scene generator.
- [x] Add a collection-scoped FBX export script.
- [ ] Run scripts locally with Blender 5.2.4.
- [ ] Confirm generated BLEND, FBX, and report.
- [ ] Verify repeatability and object naming.

### P0-5 — Unreal import and walkthrough
- [ ] Create the UE 5.8.4 project locally from the official template.
- [ ] Import the calibration FBX.
- [ ] Verify 1 m scale, axis orientation, normals, materials, and collision.
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
