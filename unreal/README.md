# Unreal Engine Project

## P0 target
Unreal Engine 5.8.4, Windows, Blueprint-first first-person walkthrough.

Create the project locally from Games > Blank using the Desktop target, Maximum Quality disabled, Starter Content optional, and Blueprint. Name the project Zhuozhengyuan and place the resulting project under this directory.

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
