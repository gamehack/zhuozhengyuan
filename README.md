# Digital Reconstruction of the Humble Administrator's Garden

**Project:** Zhuozhengyuan / 拙政园数字复原  
**Baseline:** The garden as it exists today  
**Target:** High-fidelity, real-time Windows PC walkthrough  
**Status:** P0 — foundations and pipeline validation

This project aims to build an evidence-led, dimensionally coherent digital reconstruction of the present-day Humble Administrator's Garden in Suzhou. It is not a garden-inspired game scene. Geometry, placement, materials, vegetation, water, and viewpoints must be traceable to documented evidence or explicitly marked as estimates.

## Locked technical direction

- **Blender 5.2.4 LTS** — source asset creation and Python-driven procedural modeling.
- **Unreal Engine 5.8.4** — target real-time rendering and Windows runtime.
- **Python** — data validation, Blender automation, asset manifests, and build orchestration.
- **PowerShell** — Windows-local build, export, validation, and packaging commands.
- **FBX** — primary Blender-to-Unreal asset interchange; GLB is for lightweight preview only.
- **GitHub** — source code, project standards, structured metadata, and small test fixtures.

The current development machine is an HP EliteBook 865 G9 with Ryzen 7 PRO 6850HS, Radeon 680M integrated graphics, 16 GB (2 × 8 GB) DDR5-4800, and approximately 151 GB free on C: at the time of the initial assessment. It is suitable for P0, data work, procedural modeling, and small UE validation scenes. It is not the target machine for final high-fidelity rendering.

## P0 objective

Prove a repeatable local pipeline:

1. Validate project data and local tools.
2. Generate a clearly labeled, synthetic pipeline-test scene in Blender.
3. Save a `.blend` source file.
4. Export a calibration FBX.
5. Import the FBX into UE 5.8.4 and verify units, axes, materials, and collision.
6. Run a minimal Windows walkthrough and package a test build.

The synthetic test scene is infrastructure validation only. It must never be presented as a measured part of the real garden.

## Repository map

- `docs/` — project charter, architecture, evidence, workflow, quality, and P0 plan.
- `research/` — source register and research notes; do not commit unlicensed source imagery.
- `data/` — site baseline, asset manifest, viewpoints, and JSON schemas.
- `blender/` — Blender Python automation and test-scene generation.
- `unreal/` — Unreal project setup notes and configuration guidance.
- `scripts/` — Windows PowerShell entry points and portable data validation.
- `tests/` — automated tests for project data.

## First commands

From the repository root in PowerShell:

```powershell
python .\scripts\validate_data.py
.\scripts\validate.ps1
.\scripts\build.ps1
```

`build.ps1` requires Blender 5.2.x. UE project creation and packaging remain explicit local steps until the engine is installed and validated.

## Evidence and accuracy rules

- Do not invent dimensions, coordinates, tree species, or construction details.
- Every modeled real-world asset must have a stable asset ID, source references, evidence grade, and modeling status.
- Keep source coordinates and coordinate reference systems; do not treat an approximate map point as a survey datum.
- Resolve conflicting published measurements by recording the conflict, not by silently choosing one.
- Publicly accessible images and plans are not automatically licensed for redistribution. The source register tracks permission status.

## Current status

See [P0_PLAN.md](docs/P0_PLAN.md) and [WORKFLOW.md](docs/WORKFLOW.md). No measured garden geometry has been committed yet.


## Research status — important constraint

The repository now contains an official named-feature register and a source-backed research status note. However, a verified comprehensive **present-day measured site plan** has not yet been obtained. Historical drawings and the 1986 aerial-photo study are valuable references, but they must not be presented as current survey data.

- [Research status and source strategy](research/RESEARCH_STATUS.md)
- [Official named-feature register](data/asset-manifest/feature-register.csv)
- [Source register](research/references.csv)

The project intentionally has no local coordinate origin, site boundary geometry, or fabricated object coordinates yet.
