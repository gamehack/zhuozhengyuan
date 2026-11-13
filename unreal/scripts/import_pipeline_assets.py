"""Headless UE import + collision verification for the synthetic P0 fixture.

Run through UnrealEditor-Cmd.exe -run=pythonscript. This script is editor-only;
it is not included in or required by the packaged runtime.
"""
from __future__ import annotations

import glob
import json
import os
import traceback

import unreal


REPO_ROOT = os.environ.get("ZJY_REPO_ROOT")
if not REPO_ROOT:
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    REPO_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", ".."))
BUILD_DIR = os.path.join(REPO_ROOT, "build", "pipeline-test")
ASSET_DIR = os.path.join(BUILD_DIR, "assets")
MANIFEST_PATH = os.path.join(ASSET_DIR, "asset-export-manifest.json")
REPORT_PATH = os.path.join(BUILD_DIR, "unreal-import-report.json")
DESTINATION_PATH = "/Game/PipelineTest_Automated"

GROUND_ASSET = "TEST_Ground_10m"
EXPECTED_GROUND_DIMENSIONS_CM = (2000.0, 1600.0, 24.0)
DIMENSION_TOLERANCE_CM = 1.0


def set_if_supported(obj, property_name, value, required=False):
    try:
        obj.set_editor_property(property_name, value)
        return True
    except Exception:
        if required:
            raise
        return False


def vector_components(vector):
    return [float(vector.x), float(vector.y), float(vector.z)]


def close_vector(actual, expected, tolerance):
    return (
        len(actual) == len(expected)
        and all(abs(float(a) - float(b)) <= tolerance for a, b in zip(actual, expected))
    )


def get_collision_count(static_mesh):
    # EditorStaticMeshLibrary is the documented UE 5.8 Python API for this query.
    return int(unreal.EditorStaticMeshLibrary.get_simple_collision_count(static_mesh))


def inspect_box_collision(static_mesh):
    body_setup = static_mesh.get_editor_property("body_setup")
    if not body_setup:
        raise RuntimeError("Static mesh has no BodySetup")

    aggregate_geometry = body_setup.get_editor_property("agg_geom")
    box_elements = list(aggregate_geometry.get_editor_property("box_elems"))
    result = []
    for element in box_elements:
        raw = [
            float(element.get_editor_property("x")),
            float(element.get_editor_property("y")),
            float(element.get_editor_property("z")),
        ]
        # FKBoxElem stores half extents. Also retain raw values in the report
        # so a future engine API change is diagnosable.
        result.append({
            "raw_extents_cm": raw,
            "full_dimensions_cm": [value * 2.0 for value in raw],
            "center_cm": vector_components(element.get_editor_property("center")),
        })
    return result


def import_one_fbx(asset_tools, fbx_path):
    task = unreal.AssetImportTask()
    task.set_editor_property("filename", fbx_path)
    task.set_editor_property("destination_path", DESTINATION_PATH)
    task.set_editor_property("destination_name", os.path.splitext(os.path.basename(fbx_path))[0])
    task.set_editor_property("automated", True)
    task.set_editor_property("replace_existing", True)
    task.set_editor_property("replace_existing_settings", True)
    task.set_editor_property("save", True)

    options = unreal.FbxImportUI()
    set_if_supported(options, "import_mesh", True, required=True)
    set_if_supported(options, "import_as_skeletal", False, required=True)
    set_if_supported(options, "import_materials", True)
    set_if_supported(options, "import_textures", False)
    set_if_supported(options, "import_animations", False)
    set_if_supported(options, "import_collision", True)

    static_data = options.get_editor_property("static_mesh_import_data")
    set_if_supported(static_data, "combine_meshes", False, required=True)
    set_if_supported(static_data, "auto_generate_collision", False)
    set_if_supported(static_data, "import_uniform_scale", 1.0)
    set_if_supported(static_data, "import_rotation", unreal.Rotator(0.0, 0.0, 0.0))
    set_if_supported(static_data, "import_translation", unreal.Vector(0.0, 0.0, 0.0))
    options.set_editor_property("static_mesh_import_data", static_data)
    task.set_editor_property("options", options)

    asset_tools.import_asset_tasks([task])
    imported_paths = list(task.get_editor_property("imported_object_paths"))
    if not imported_paths:
        raise RuntimeError(f"No assets were imported from {os.path.basename(fbx_path)}")

    imported = []
    for object_path in imported_paths:
        asset = unreal.EditorAssetLibrary.load_asset(object_path)
        if isinstance(asset, unreal.StaticMesh):
            imported.append(asset)
    if len(imported) != 1:
        raise RuntimeError(
            f"{os.path.basename(fbx_path)} should produce one StaticMesh, "
            f"got {len(imported)}: {imported_paths}"
        )
    return imported[0], imported_paths


def write_report(report):
    os.makedirs(BUILD_DIR, exist_ok=True)
    with open(REPORT_PATH, "w", encoding="utf-8") as handle:
        json.dump(report, handle, ensure_ascii=False, indent=2)


def main():
    if not os.path.isfile(MANIFEST_PATH):
        raise RuntimeError(
            f"Asset export manifest missing: {MANIFEST_PATH}. Run scripts/build.ps1 first."
        )

    with open(MANIFEST_PATH, "r", encoding="utf-8") as handle:
        manifest = json.load(handle)

    fbx_files = sorted(glob.glob(os.path.join(ASSET_DIR, "*.fbx")))
    if len(fbx_files) != int(manifest.get("render_mesh_count", -1)):
        raise RuntimeError(
            f"FBX count mismatch: found {len(fbx_files)}, "
            f"manifest expects {manifest.get('render_mesh_count')}"
        )

    asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
    imported_assets = []
    ground_result = None

    for fbx_path in fbx_files:
        static_mesh, imported_paths = import_one_fbx(asset_tools, fbx_path)
        asset_name = os.path.splitext(os.path.basename(fbx_path))[0]
        collision_count = get_collision_count(static_mesh)
        item = {
            "source_fbx": os.path.basename(fbx_path),
            "asset_path": static_mesh.get_path_name(),
            "collision_count": collision_count,
            "imported_object_paths": imported_paths,
        }

        if asset_name == GROUND_ASSET:
            box_collisions = inspect_box_collision(static_mesh)
            bounds = static_mesh.get_bounds()
            mesh_dimensions = [
                float(bounds.box_extent.x) * 2.0,
                float(bounds.box_extent.y) * 2.0,
                float(bounds.box_extent.z) * 2.0,
            ]
            item["mesh_bounds_dimensions_cm"] = mesh_dimensions
            item["box_collisions"] = box_collisions

            collision_dimensions_ok = (
                len(box_collisions) == 1
                and close_vector(
                    box_collisions[0]["full_dimensions_cm"],
                    EXPECTED_GROUND_DIMENSIONS_CM,
                    DIMENSION_TOLERANCE_CM,
                )
            )
            mesh_dimensions_ok = close_vector(
                mesh_dimensions,
                EXPECTED_GROUND_DIMENSIONS_CM,
                DIMENSION_TOLERANCE_CM,
            )
            item["checks"] = {
                "one_simple_collision": collision_count == 1,
                "one_box_element": len(box_collisions) == 1,
                "collision_dimensions_match": collision_dimensions_ok,
                "render_mesh_dimensions_match": mesh_dimensions_ok,
            }
            item["status"] = (
                "PASS" if all(item["checks"].values()) else "FAIL"
            )
            ground_result = item

        unreal.EditorAssetLibrary.save_loaded_asset(static_mesh)
        imported_assets.append(item)
        unreal.log(
            f"[ZJY PIPELINE] Imported {asset_name}: "
            f"simple_collision_count={collision_count}"
        )

    if ground_result is None:
        raise RuntimeError(f"Imported assets do not contain {GROUND_ASSET}")

    failures = [
        item for item in imported_assets
        if item.get("status") == "FAIL"
    ]
    report = {
        "status": "PASS" if not failures else "FAIL",
        "engine_version": unreal.SystemLibrary.get_engine_version(),
        "destination_path": DESTINATION_PATH,
        "imported_static_mesh_count": len(imported_assets),
        "ground_validation": ground_result,
        "assets": imported_assets,
    }
    write_report(report)
    unreal.log(f"[ZJY PIPELINE] Report written: {REPORT_PATH}")

    if failures:
        raise RuntimeError(
            "Ground collision validation failed. See unreal-import-report.json."
        )


try:
    main()
except Exception as exc:
    failure_report = {
        "status": "FAIL",
        "error": str(exc),
        "traceback": traceback.format_exc(),
    }
    write_report(failure_report)
    unreal.log_error(f"[ZJY PIPELINE] {exc}")
    raise
