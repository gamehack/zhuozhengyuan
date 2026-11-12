"""Export the synthetic pipeline-test collection to FBX."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import bpy


def parse_args():
    argv = sys.argv
    argv = argv[argv.index("--") + 1:] if "--" in argv else []
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    parser.add_argument("--collection", default="90_EXPORT_PIPELINE_TEST")
    return parser.parse_args(argv)


def collection_objects(collection):
    objects = list(collection.objects)
    for child in collection.children:
        objects.extend(collection_objects(child))
    return objects


def main():
    args = parse_args()
    output_path = Path(args.output).resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)

    collection = bpy.data.collections.get(args.collection)
    if collection is None:
        raise RuntimeError(f"Export collection not found: {args.collection}")

    objects = [
        obj for obj in collection_objects(collection)
        if obj.type == "MESH" and obj.get("zjy_export", False)
    ]
    if not objects:
        raise RuntimeError("No tagged mesh objects found in export collection")

    bpy.ops.object.select_all(action="DESELECT")
    for obj in objects:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = objects[0]

    if not hasattr(bpy.ops.export_scene, "fbx"):
        raise RuntimeError(
            "FBX exporter is unavailable. In Blender 5.2, open Edit > Preferences > Get Extensions, "
            "search for 'FBX format', install/enable it, then rerun the export."
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
        "use_custom_props": True
    }
    supported = bpy.ops.export_scene.fbx.get_rna_type().properties.keys()
    kwargs = {key: value for key, value in requested.items() if key in supported}
    result = bpy.ops.export_scene.fbx(**kwargs)
    if "FINISHED" not in result or not output_path.exists():
        raise RuntimeError(f"FBX export failed: {result}")

    print(f"Exported {len(objects)} mesh objects to {output_path}")


if __name__ == "__main__":
    main()
