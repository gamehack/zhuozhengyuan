# Working Workflow

## Roles
- ChatGPT: project planning, source synthesis, data/schema design, Blender Python and PowerShell authoring, code review, and visual QA.
- User: local Windows execution when required, review of outputs, access to field observations or licensed source material, and decisions on visual priorities.
- Blender: deterministic asset authoring and interchange preparation.
- Unreal Engine: scene assembly, real-time review, and Windows packaging.
- GitHub: source of truth for project code, standards, manifests, and task tracking.

## Task lifecycle
1. Define one bounded task and its acceptance criteria.
2. Identify source evidence and record its REF IDs.
3. Create or update structured data before modeling.
4. Implement a deterministic script or documented manual operation.
5. Run data and scene validation.
6. Generate a preview and/or export.
7. Compare against evidence and record defects.
8. Commit code and metadata; keep large generated artifacts out of Git unless explicitly approved.
9. Mark a task complete only after its acceptance criteria pass.

## Change protocol
- Keep changes small and reversible.
- Do not change the coordinate convention, engine version, asset ID scheme, or FBX profile without documenting the migration.
- Do not overwrite source references or original captures.
- Separate measured data, estimates, and synthetic pipeline fixtures.
- Every synthetic fixture must be named and tagged as a test asset.

## Local Windows commands
From the repository root:

~~~powershell
python .\scripts\validate_data.py
.\scripts\validate.ps1
.\scripts\build.ps1
~~~

The build script creates a synthetic Blender pipeline test scene and exports an FBX. It does not create a model of any real pavilion in the garden.

## Review loop
A modeling task is not accepted from a single attractive render. Review top-down placement, at least two ground-level views, dimensions and scale, source alignment, silhouette and occlusion, material response, import result in Unreal, and runtime behavior where relevant.
