"""Export each render mesh as its own FBX, including only its named collision meshes.

One render mesh per FBX avoids the Unreal FBX importer's documented limitation
where only the first mesh's custom collision is imported from a multi-mesh file.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import bpy


COLLISION_PREFIXES = ("UBX_", "UCP_", "USP_", "UCX_")


def parse_args():
    argv = sys.argv
    argv = argv[argv.index("--") + 1:] if "--" in argv else []
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--collection", default="90_EXPORT_PIPELINE_TEST")
    return parser.parse_args(argv)


def collection_objects(collection):
    objects = list(collection.objects)
    for child in collection.children:
        objects.extend(collection_objects(child))
    return objects


def export_selected_fbx(output_path: Path):
    if not hasattr(bpy.ops.export_scene, "fbx"):
        raise RuntimeError(
            "FBX exporter is unavailable. Install/enable the 'FBX format' extension "
            "in Blender 5.2, then rerun the export."
        )

    requested = {
        "filepath": str(output_path),
        "use_selection": True,
        "object_types": {"MESH"},
        "global_scale": 1.0,
        "apply_unit_scale": True,
        "apply_scale_options": "FBX_SCALE_ALL",
        "axis_forward": "-Y",
        "axis_up": "Z",
        "use_mesh_modifiers": True,
        "bake_anim": False,
        "add_leaf_bones": False,
        "use_custom_props": True,
    }
    supported = bpy.ops.export_scene.fbx.get_rna_type().properties.keys()
    kwargs = {key: value for key, value in requested.items() if key in supported}
    result = bpy.ops.export_scene.fbx(**kwargs)
    if "FINISHED" not in result or not output_path.exists():
        raise RuntimeError(f"FBX export failed for {output_path.name}: {result}")


def dimensions_close(a, b, tolerance=0.001):
    return all(abs(float(x) - float(y)) <= tolerance for x, y in zip(a, b))


def main():
    args = parse_args()
    output_dir = Path(args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    collection = bpy.data.collections.get(args.collection)
    if collection is None:
        raise RuntimeError(f"Export collection not found: {args.collection}")

    all_objects = list(bpy.data.objects)
    render_objects = [
        obj for obj in collection_objects(collection)
        if obj.type == "MESH" and obj.get("zjy_export", False)
    ]
    if not render_objects:
        raise RuntimeError("No tagged render meshes found")

    referenced_collisions = set()
    manifest_assets = []

    for render_obj in sorted(render_objects, key=lambda item: item.name):
        collisions = [
            obj for obj in all_objects
            if obj.type == "MESH"
            and obj.get("zjy_collision_for") == render_obj.name
        ]

        selected_objects = [render_obj] + collisions
        for collision in collisions:
            if not collision.name.startswith(COLLISION_PREFIXES):
                raise RuntimeError(
                    f"Collision object {collision.name} has no supported Unreal prefix"
                )
            if not dimensions_close(collision.dimensions, render_obj.dimensions):
                raise RuntimeError(
                    f"Collision bounds mismatch for {render_obj.name}: "
                    f"render={tuple(render_obj.dimensions)}, "
                    f"collision={tuple(collision.dimensions)}"
                )
            referenced_collisions.add(collision.name)

        bpy.ops.object.select_all(action="DESELECT")
        for obj in selected_objects:
            obj.select_set(True)
        bpy.context.view_layer.objects.active = render_obj

        output_path = output_dir / f"{render_obj.name}.fbx"
        if output_path.exists():
            output_path.unlink()
        export_selected_fbx(output_path)

        manifest_assets.append({
            "render_mesh": render_obj.name,
            "fbx_file": output_path.name,
            "fbx_size_bytes": output_path.stat().st_size,
            "collision_objects": [
                {
                    "name": collision.name,
                    "shape": collision.get("zjy_collision_shape", "unknown"),
                    "dimensions_m": [
                        round(float(value), 6) for value in collision.dimensions
                    ],
                }
                for collision in collisions
            ],
        })
        print(
            f"Exported {render_obj.name}: "
            f"{len(collisions)} collision mesh(es) -> {output_path}"
        )

    orphan_collisions = [
        obj.name for obj in all_objects
        if obj.type == "MESH"
        and obj.get("zjy_collision_for")
        and obj.name not in referenced_collisions
    ]
    if orphan_collisions:
        raise RuntimeError(f"Orphan collision meshes: {orphan_collisions}")

    manifest = {
        "schema_version": 1,
        "pipeline": "ONE_RENDER_MESH_PER_FBX",
        "blender_version": bpy.app.version_string,
        "render_mesh_count": len(render_objects),
        "collision_mesh_count": len(referenced_collisions),
        "assets": manifest_assets,
    }
    manifest_path = output_dir / "asset-export-manifest.json"
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(json.dumps(manifest, ensure_ascii=False, indent=2))
    print(f"Asset export manifest: {manifest_path}")


if __name__ == "__main__":
    main()
