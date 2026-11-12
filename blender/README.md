# Blender Asset Pipeline

## Version
P0 targets Blender 5.2.4 LTS, matching the currently reported local installation.

## Responsibilities
- Generate source meshes and materials through Blender Python.
- Organize scene objects into stable collections.
- Attach asset IDs and evidence metadata to real garden assets.
- Validate scene units and object metadata.
- Export only the intended collection to FBX.

## P0 test
Run from the repository root:

~~~powershell
.\scripts\build.ps1
~~~

The generator creates a synthetic pavilion/wall/pond/path/tree test fixture. It is tagged PIPELINE_TEST_ONLY and is not a model of any real feature in the garden.

Generated files are written under build/pipeline-test and are ignored by Git.

## Real asset policy
Do not create a real garden asset until the relevant source reference and evidence grade are recorded in the asset manifest. Use parametric geometry where dimensions are known; use a separate evidence-backed refinement task for complex historic geometry.
