# Quality and Acceptance Standards

## Evidence gate
- Every real garden asset has an asset ID and at least one source reference.
- Evidence grade and modeling status are explicit.
- Unverified dimensions are omitted, not guessed.
- Conflicting evidence is documented.
- Source-use permission is reviewed before redistributing source material.

## Spatial gate
- Local coordinate datum and axes are documented.
- Units are consistent.
- Asset location and orientation are traceable to source evidence.
- Site boundary, water edge, and path geometry are not inferred from a single perspective photograph.
- Survey accuracy and source scale are recorded when known.

## Geometry gate
- Silhouette matches the available references.
- Dimensions and proportions are checked independently.
- Normals, non-manifold geometry, transforms, and mesh density are reviewed.
- Important architectural elements are not replaced by generic primitives in final assets.
- Test primitives are clearly labeled as pipeline fixtures.

## Material and lighting gate
- Materials use physically plausible parameters.
- Surface variation is subtle and evidence-based.
- Lighting comparison uses a recorded capture condition.
- Water appearance is evaluated from several viewpoints.
- No material or post-process effect is used to conceal geometry errors.

## Runtime gate
- FBX scale and axis calibration passes.
- Collision is appropriate for walkthrough.
- Player movement does not pass through walls, railings, or terrain.
- Frame time and memory use are recorded on the target machine.
- Quality settings are selected for the actual GPU, not assumed hardware.

## Fixed viewpoints
The project intends to build at least 20 fixed reference viewpoints. They are not pre-filled with invented camera positions. Each must be captured or derived from a reliable plan and recorded with source photo, date, camera direction, and related assets.

## P0 acceptance
P0 passes only when data validation and unit tests pass; Blender generates a repeatable synthetic test scene; a BLEND and FBX are produced; FBX imports into UE 5.8.4; a 1 m calibration object has the correct size in UE; a minimal Windows walkthrough runs; and build steps are repeatable.
