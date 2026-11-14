"""Create a synthetic Blender scene to test the ZJY asset pipeline.

Infrastructure test geometry only. It is NOT a reconstruction of the garden.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import bpy
from mathutils import Vector

TEST_TAG = "PIPELINE_TEST_ONLY"


def parse_args():
    argv = sys.argv
    argv = argv[argv.index("--") + 1:] if "--" in argv else []
    parser = argparse.ArgumentParser()
    parser.add_argument("--blend-output", required=True)
    parser.add_argument("--report-output", required=True)
    return parser.parse_args(argv)


def ensure_collection(name):
    collection = bpy.data.collections.get(name)
    if collection is None:
        collection = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(collection)
    return collection


def move_to_collection(obj, collection):
    for old_collection in list(obj.users_collection):
        old_collection.objects.unlink(obj)
    collection.objects.link(obj)


def make_material(name, color, roughness=0.7):
    material = bpy.data.materials.get(name)
    if material is None:
        material = bpy.data.materials.new(name=name)
    material.diffuse_color = (*color, 1.0)
    material.use_nodes = True
    bsdf = material.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = (*color, 1.0)
        bsdf.inputs["Roughness"].default_value = roughness
    return material


def tag_object(obj, label, collection, material=None):
    move_to_collection(obj, collection)
    if material:
        obj.data.materials.clear()
        obj.data.materials.append(material)
    obj["zjy_test_tag"] = TEST_TAG
    obj["zjy_test_label"] = label
    obj["zjy_export"] = True
    obj.name = f"TEST_{label}"
    return obj


def add_cube(label, location, dimensions, collection, material):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=location)
    obj = bpy.context.object
    obj.dimensions = dimensions
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    return tag_object(obj, label, collection, material)


def add_cylinder(label, location, radius, depth, collection, material):
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=16, radius=radius, depth=depth, location=location
    )
    return tag_object(bpy.context.object, label, collection, material)


def add_uv_sphere(label, location, scale, collection, material):
    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=16, ring_count=8, radius=1.0, location=location
    )
    obj = bpy.context.object
    obj.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    return tag_object(obj, label, collection, material)



def add_box_collision(render_obj, collection):
    """Create a UE-compatible UBX box matching the render mesh local bounds."""
    corners = [Vector(corner) for corner in render_obj.bound_box]
    minimum = Vector((
        min(point.x for point in corners),
        min(point.y for point in corners),
        min(point.z for point in corners),
    ))
    maximum = Vector((
        max(point.x for point in corners),
        max(point.y for point in corners),
        max(point.z for point in corners),
    ))
    half = (maximum - minimum) * 0.5
    center = (maximum + minimum) * 0.5

    vertices = [
        (center.x - half.x, center.y - half.y, center.z - half.z),
        (center.x + half.x, center.y - half.y, center.z - half.z),
        (center.x + half.x, center.y + half.y, center.z - half.z),
        (center.x - half.x, center.y + half.y, center.z - half.z),
        (center.x - half.x, center.y - half.y, center.z + half.z),
        (center.x + half.x, center.y - half.y, center.z + half.z),
        (center.x + half.x, center.y + half.y, center.z + half.z),
        (center.x - half.x, center.y + half.y, center.z + half.z),
    ]
    faces = [
        (0, 3, 2, 1), (4, 5, 6, 7),
        (0, 1, 5, 4), (1, 2, 6, 5),
        (2, 3, 7, 6), (3, 0, 4, 7),
    ]

    mesh = bpy.data.meshes.new(f"UBX_{render_obj.name}_00_Mesh")
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    collision = bpy.data.objects.new(
        f"UBX_{render_obj.name}_00", mesh
    )
    collection.objects.link(collision)
    collision.matrix_world = render_obj.matrix_world.copy()
    bpy.context.view_layer.update()
    collision.display_type = "WIRE"
    collision.hide_render = True
    collision["zjy_test_tag"] = TEST_TAG
    collision["zjy_collision_for"] = render_obj.name
    collision["zjy_collision_shape"] = "box"
    collision["zjy_collision_dimensions_m"] = [
        round(maximum.x - minimum.x, 6),
        round(maximum.y - minimum.y, 6),
        round(maximum.z - minimum.z, 6),
    ]
    return collision


def main():
    args = parse_args()
    blend_output = Path(args.blend_output).resolve()
    report_output = Path(args.report_output).resolve()
    blend_output.parent.mkdir(parents=True, exist_ok=True)
    report_output.parent.mkdir(parents=True, exist_ok=True)

    # Safe rerun: remove only objects generated by this fixture.
    for obj in list(bpy.data.objects):
        if obj.get("zjy_test_tag") == TEST_TAG:
            bpy.data.objects.remove(obj, do_unlink=True)

    scene = bpy.context.scene
    scene.unit_settings.system = "METRIC"
    scene.unit_settings.length_unit = "METERS"
    scene.unit_settings.scale_length = 1.0
    # Blender's render-engine identifiers vary across releases. This fixture
    # does not render an image, but choose an installed engine so the saved
    # .blend opens cleanly across Blender 4.x/5.x builds.
    available_engines = scene.render.bl_rna.properties["engine"].enum_items.keys()
    preferred_engines = (
        "BLENDER_EEVEE_NEXT",
        "BLENDER_EEVEE",
        "BLENDER_WORKBENCH",
        "CYCLES",
    )
    selected_engine = next(
        (engine for engine in preferred_engines if engine in available_engines),
        None,
    )
    if selected_engine is None:
        raise RuntimeError(
            f"No supported render engine found. Available: {list(available_engines)}"
        )
    scene.render.engine = selected_engine
    print(f"Pipeline fixture render engine: {selected_engine}")
    scene.render.resolution_x = 1280
    scene.render.resolution_y = 720
    scene.render.resolution_percentage = 60

    export_collection = ensure_collection("90_EXPORT_PIPELINE_TEST")
    ensure_collection("00_REFERENCE")
    ensure_collection("01_TERRAIN")
    ensure_collection("02_WATER")
    ensure_collection("03_ARCHITECTURE")
    ensure_collection("04_ROCKS")
    ensure_collection("05_VEGETATION")
    ensure_collection("06_PATHS")
    lighting_collection = ensure_collection("07_LIGHTS_CAMERAS")

    plaster = make_material("TEST_MAT_Plaster", (0.78, 0.76, 0.69), 0.88)
    roof = make_material("TEST_MAT_Roof", (0.10, 0.12, 0.13), 0.82)
    timber = make_material("TEST_MAT_Timber", (0.24, 0.12, 0.06), 0.72)
    stone = make_material("TEST_MAT_Stone", (0.34, 0.35, 0.32), 0.92)
    water = make_material("TEST_MAT_Water", (0.08, 0.20, 0.22), 0.22)
    foliage = make_material("TEST_MAT_Foliage", (0.12, 0.22, 0.10), 0.9)

    ground = add_cube("Ground_10m", (0, 0, -0.12), (20, 16, 0.24), export_collection, stone)
    ground_collision = add_box_collision(ground, export_collection)
    add_cube("Pond_6x4m", (5.0, 2.0, 0.02), (6.0, 4.0, 0.04), export_collection, water)
    add_cube("White_Wall", (-4.0, 0.0, 1.6), (0.25, 8.0, 3.2), export_collection, plaster)
    add_cube("Window_Trim_Top", (-3.82, 0.0, 2.2), (0.12, 2.0, 0.12), export_collection, timber)
    add_cube("Window_Trim_Bottom", (-3.82, 0.0, 1.2), (0.12, 2.0, 0.12), export_collection, timber)
    add_cube("Window_Trim_Left", (-3.82, -0.94, 1.7), (0.12, 0.12, 1.0), export_collection, timber)
    add_cube("Window_Trim_Right", (-3.82, 0.94, 1.7), (0.12, 0.12, 1.0), export_collection, timber)

    for x in (-1.2, 1.2):
        for y in (-1.2, 1.2):
            add_cylinder("Pavilion_Test_Column", (x, y, 1.35), 0.12, 2.7, export_collection, timber)

    add_cube("Pavilion_Test_Roof_Base", (0, 0, 2.85), (3.2, 3.2, 0.22), export_collection, roof)
    add_cube("Pavilion_Test_Roof_Ridge", (0, 0, 3.05), (3.4, 0.18, 0.16), export_collection, timber)
    add_cube("Stone_Path_Test", (1.0, -4.0, 0.03), (8.0, 1.4, 0.12), export_collection, stone)

    add_cylinder("Tree_Trunk_Test", (7.5, -3.0, 1.1), 0.16, 2.2, export_collection, timber)
    add_uv_sphere("Tree_Canopy_Test", (7.5, -3.0, 2.8), (1.2, 1.0, 1.4), export_collection, foliage)

    # Asymmetric calibration geometry: 1 m cube plus X/Y bars.
    add_cube("Calibration_Cube_1m", (-7.0, -5.0, 0.5), (1.0, 1.0, 1.0), export_collection, plaster)
    add_cube("Calibration_X_2m", (-5.0, -5.0, 0.05), (2.0, 0.08, 0.08), export_collection, timber)
    add_cube("Calibration_Y_1m", (-5.0, -5.0, 0.55), (0.08, 1.0, 0.08), export_collection, foliage)

    bpy.ops.object.light_add(type="AREA", location=(1.0, -4.0, 9.0))
    light = bpy.context.object
    light.name = "TEST_Key_Light"
    light.data.energy = 1800
    light.data.shape = "DISK"
    light.data.size = 8.0
    move_to_collection(light, lighting_collection)

    bpy.ops.object.camera_add(location=(13.0, -18.0, 12.0))
    camera = bpy.context.object
    camera.name = "TEST_Camera"
    camera.rotation_euler = (Vector((0.0, 0.0, 1.0)) - camera.location).to_track_quat("-Z", "Y").to_euler()
    move_to_collection(camera, lighting_collection)
    scene.camera = camera

    scene.render.filepath = str(blend_output.parent / "pipeline-test-preview.png")
    bpy.ops.wm.save_as_mainfile(filepath=str(blend_output))

    report = {
        "fixture": TEST_TAG,
        "blender_version": bpy.app.version_string,
        "blend_file": str(blend_output),
        "export_collection": export_collection.name,
        "export_object_count": len([obj for obj in export_collection.objects if obj.get("zjy_export", False)]),
        "collision_object_count": 1,
        "collision_objects": [{
            "name": ground_collision.name,
            "render_mesh": ground.name,
            "shape": ground_collision["zjy_collision_shape"],
            "dimensions_m": [float(value) for value in ground_collision["zjy_collision_dimensions_m"]],
            "expected_dimensions_m": [20.0, 16.0, 0.24],
        }],
        "units": "meters",
        "local_axes": {"x": "east", "y": "north", "z": "up"},
        "real_garden_geometry": False,
        "calibration_object": "Calibration_Cube_1m"
    }
    report_output.write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
