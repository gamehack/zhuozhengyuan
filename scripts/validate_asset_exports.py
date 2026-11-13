"""Validate Blender's per-asset FBX export manifest."""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path


EXPECTED_RENDER_COUNT = 19
EXPECTED_GROUND = "TEST_Ground_10m"
EXPECTED_COLLISION = "UBX_TEST_Ground_10m_00"
EXPECTED_DIMENSIONS_M = (20.0, 16.0, 0.24)
TOLERANCE = 1e-4


def close_vector(actual, expected):
    return (
        isinstance(actual, list)
        and len(actual) == len(expected)
        and all(
            isinstance(value, (int, float))
            and math.isfinite(value)
            and abs(float(value) - float(target)) <= TOLERANCE
            for value, target in zip(actual, expected)
        )
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True)
    args = parser.parse_args()

    manifest_path = Path(args.manifest).resolve()
    if not manifest_path.is_file():
        raise SystemExit(f"Manifest not found: {manifest_path}")

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    errors = []
    assets = manifest.get("assets")
    if not isinstance(assets, list):
        raise SystemExit("Manifest assets must be an array")

    if manifest.get("pipeline") != "ONE_RENDER_MESH_PER_FBX":
        errors.append("Unexpected export pipeline identifier")
    if manifest.get("render_mesh_count") != EXPECTED_RENDER_COUNT:
        errors.append(
            f"Expected {EXPECTED_RENDER_COUNT} render meshes, "
            f"got {manifest.get('render_mesh_count')}"
        )
    if len(assets) != EXPECTED_RENDER_COUNT:
        errors.append(f"Expected {EXPECTED_RENDER_COUNT} asset FBXs, got {len(assets)}")

    seen = set()
    ground = None
    for asset in assets:
        name = asset.get("render_mesh")
        if name in seen:
            errors.append(f"Duplicate render mesh in manifest: {name}")
        seen.add(name)

        fbx_name = asset.get("fbx_file", "")
        fbx_path = manifest_path.parent / fbx_name
        if not fbx_path.is_file() or fbx_path.stat().st_size <= 0:
            errors.append(f"Missing or empty FBX file: {fbx_name}")

        if name == EXPECTED_GROUND:
            ground = asset

    if ground is None:
        errors.append(f"Missing ground asset {EXPECTED_GROUND}")
    else:
        collisions = ground.get("collision_objects", [])
        if len(collisions) != 1:
            errors.append(f"Ground must have exactly 1 collision mesh, got {len(collisions)}")
        else:
            collision = collisions[0]
            if collision.get("name") != EXPECTED_COLLISION:
                errors.append(
                    f"Ground collision name mismatch: {collision.get('name')!r}"
                )
            if collision.get("shape") != "box":
                errors.append(f"Ground collision shape must be box, got {collision.get('shape')!r}")
            if not close_vector(collision.get("dimensions_m"), EXPECTED_DIMENSIONS_M):
                errors.append(
                    "Ground collision dimensions mismatch: "
                    f"{collision.get('dimensions_m')!r}, "
                    f"expected {EXPECTED_DIMENSIONS_M}"
                )

    if manifest.get("collision_mesh_count") != 1:
        errors.append(
            f"Expected 1 collision mesh in fixture, got {manifest.get('collision_mesh_count')}"
        )

    if errors:
        print("ASSET EXPORT VALIDATION FAILED")
        for error in errors:
            print(f"- {error}")
        return 1

    print("ASSET EXPORT VALIDATION PASSED")
    print(f"Render assets: {len(assets)} separate FBX files")
    print(f"Ground collision: {EXPECTED_COLLISION}")
    print(f"Ground dimensions: {EXPECTED_DIMENSIONS_M} m")
    print("Each FBX contains one render mesh and only its matching collision meshes.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
