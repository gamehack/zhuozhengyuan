"""Validate project metadata using only the Python standard library."""
from __future__ import annotations

import csv
import json
import math
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASSET_ID = re.compile(r"^ZJY-(BLD|TRE|ROC|WAT|BRG|PTH|OBJ)-[0-9]{3,}$")
VIEW_ID = re.compile(r"^ZJY-VIEW-[0-9]{3,}$")
REF_ID = re.compile(r"^REF-[0-9]{3,}$")
ASSET_TYPES = {"building", "tree", "rock", "water", "bridge", "path", "object"}
AREAS = {"east", "central", "west", "residential", "unknown"}
EVIDENCE = {"A", "B", "C", "D"}
ASSET_STATUSES = {"unresearched", "researched", "blockout", "modeled", "reviewed", "verified"}
VIEW_STATUSES = {"planned", "captured", "calibrated", "approved"}
REFERENCE_HEADERS = {
    "reference_id", "title", "source_type", "publisher", "access_date",
    "url", "permission_status", "related_area", "notes"
}
FEATURE_ID = re.compile(r"^ZJY-FEAT-[0-9]{3,}$")
FEATURE_HEADERS = {"feature_ref", "name_zh", "area", "feature_type", "source_ids", "position_status", "geometry_status", "notes"}


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def is_vector3(value):
    return (
        isinstance(value, list)
        and len(value) == 3
        and all(isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v) for v in value)
    )


def load_reference_ids(path: Path, errors: list[str]) -> set[str]:
    if not path.exists():
        errors.append(f"Missing reference register: {path}")
        return set()
    ids = set()
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        headers = set(reader.fieldnames or [])
        missing = REFERENCE_HEADERS - headers
        if missing:
            errors.append(f"Reference CSV missing headers: {sorted(missing)}")
            return ids
        for line_number, row in enumerate(reader, start=2):
            ref_id = (row.get("reference_id") or "").strip()
            if not REF_ID.fullmatch(ref_id):
                errors.append(f"Reference CSV line {line_number}: invalid reference_id {ref_id!r}")
            if ref_id in ids:
                errors.append(f"Reference CSV line {line_number}: duplicate reference_id {ref_id}")
            ids.add(ref_id)
            url = (row.get("url") or "").strip()
            if not url.startswith(("https://", "http://")):
                errors.append(f"Reference CSV line {line_number}: URL must be http(s)")
            if not (row.get("title") or "").strip():
                errors.append(f"Reference CSV line {line_number}: title is empty")
    return ids


def validate_asset_manifest(path: Path, reference_ids: set[str], errors: list[str]):
    if not path.exists():
        errors.append(f"Missing asset manifest: {path}")
        return
    data = load_json(path)
    if data.get("coordinate_units") != "meters":
        errors.append("Asset manifest coordinate_units must be 'meters'")
    assets = data.get("assets")
    if not isinstance(assets, list):
        errors.append("Asset manifest 'assets' must be an array")
        return
    seen = set()
    for index, asset in enumerate(assets):
        label = f"Asset index {index}"
        asset_id = asset.get("asset_id", "")
        if not ASSET_ID.fullmatch(asset_id):
            errors.append(f"{label}: invalid asset_id {asset_id!r}")
        if asset_id in seen:
            errors.append(f"{label}: duplicate asset_id {asset_id}")
        seen.add(asset_id)
        if asset.get("asset_type") not in ASSET_TYPES:
            errors.append(f"{label} {asset_id}: invalid asset_type")
        if asset.get("area") not in AREAS:
            errors.append(f"{label} {asset_id}: invalid area")
        if not (asset.get("name_zh") or "").strip():
            errors.append(f"{label} {asset_id}: name_zh is required")
        if not is_vector3(asset.get("location_local_m")):
            errors.append(f"{label} {asset_id}: location_local_m must be three finite numbers")
        if not is_vector3(asset.get("rotation_deg")):
            errors.append(f"{label} {asset_id}: rotation_deg must be three finite numbers")
        dimensions = asset.get("dimensions_m")
        if dimensions is not None and (
            not is_vector3(dimensions) or any(value <= 0 for value in dimensions)
        ):
            errors.append(f"{label} {asset_id}: dimensions_m must be null or three positive numbers")
        if asset.get("evidence_level") not in EVIDENCE:
            errors.append(f"{label} {asset_id}: invalid evidence_level")
        if asset.get("modeling_status") not in ASSET_STATUSES:
            errors.append(f"{label} {asset_id}: invalid modeling_status")
        source_ids = asset.get("source_ids")
        if not isinstance(source_ids, list):
            errors.append(f"{label} {asset_id}: source_ids must be an array")
        else:
            for source_id in source_ids:
                if source_id not in reference_ids:
                    errors.append(f"{label} {asset_id}: unknown source_id {source_id}")


def validate_viewpoints(path: Path, reference_ids: set[str], errors: list[str]):
    if not path.exists():
        errors.append(f"Missing viewpoints file: {path}")
        return
    data = load_json(path)
    if data.get("coordinate_units") != "meters":
        errors.append("Viewpoints coordinate_units must be 'meters'")
    viewpoints = data.get("viewpoints")
    if not isinstance(viewpoints, list):
        errors.append("Viewpoints 'viewpoints' must be an array")
        return
    seen = set()
    for index, view in enumerate(viewpoints):
        label = f"Viewpoint index {index}"
        view_id = view.get("viewpoint_id", "")
        if not VIEW_ID.fullmatch(view_id):
            errors.append(f"{label}: invalid viewpoint_id {view_id!r}")
        if view_id in seen:
            errors.append(f"{label}: duplicate viewpoint_id {view_id}")
        seen.add(view_id)
        if view.get("area") not in {"east", "central", "west", "residential"}:
            errors.append(f"{label} {view_id}: invalid area")
        if not is_vector3(view.get("camera_position_local_m")):
            errors.append(f"{label} {view_id}: invalid camera_position_local_m")
        if not is_vector3(view.get("look_at_local_m")):
            errors.append(f"{label} {view_id}: invalid look_at_local_m")
        if view.get("status") not in VIEW_STATUSES:
            errors.append(f"{label} {view_id}: invalid status")
        source_ids = view.get("source_ids")
        if not isinstance(source_ids, list) or not source_ids:
            errors.append(f"{label} {view_id}: source_ids must be a non-empty array")
        else:
            for source_id in source_ids:
                if source_id not in reference_ids:
                    errors.append(f"{label} {view_id}: unknown source_id {source_id}")


def validate_feature_register(path: Path, reference_ids: set[str], errors: list[str]):
    if not path.exists():
        errors.append(f"Missing feature register: {path}")
        return
    seen = set()
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        missing = FEATURE_HEADERS - set(reader.fieldnames or [])
        if missing:
            errors.append(f"Feature register missing headers: {sorted(missing)}")
            return
        for line_number, row in enumerate(reader, start=2):
            feature_id = (row.get("feature_ref") or "").strip()
            if not FEATURE_ID.fullmatch(feature_id):
                errors.append(f"Feature register line {line_number}: invalid feature_ref {feature_id!r}")
            if feature_id in seen:
                errors.append(f"Feature register line {line_number}: duplicate feature_ref {feature_id}")
            seen.add(feature_id)
            if not (row.get("name_zh") or "").strip():
                errors.append(f"Feature register line {line_number}: name_zh is empty")
            if (row.get("area") or "").strip() not in {"east", "central", "west", "residential"}:
                errors.append(f"Feature register line {line_number}: invalid area")
            if not (row.get("feature_type") or "").strip():
                errors.append(f"Feature register line {line_number}: feature_type is empty")
            source_ids = [value.strip() for value in (row.get("source_ids") or "").split(";") if value.strip()]
            if not source_ids:
                errors.append(f"Feature register line {line_number}: source_ids is empty")
            for source_id in source_ids:
                if source_id not in reference_ids:
                    errors.append(f"Feature register line {line_number}: unknown source_id {source_id}")


def validate_baseline(path: Path, reference_ids: set[str], errors: list[str]):
    if not path.exists():
        errors.append(f"Missing site baseline: {path}")
        return
    data = load_json(path)
    area = data.get("area_m2")
    if not isinstance(area, (int, float)) or isinstance(area, bool) or area <= 0:
        errors.append("Site baseline area_m2 must be a positive number")
    point = data.get("geographic_reference_point", {})
    lat, lon = point.get("latitude"), point.get("longitude")
    if not isinstance(lat, (int, float)) or not -90 <= lat <= 90:
        errors.append("Site baseline latitude is invalid")
    if not isinstance(lon, (int, float)) or not -180 <= lon <= 180:
        errors.append("Site baseline longitude is invalid")
    for source_id in data.get("area_source_ids", []):
        if source_id not in reference_ids:
            errors.append(f"Site baseline: unknown area source_id {source_id}")
    point_source = point.get("source_id")
    if point_source and point_source not in reference_ids:
        errors.append(f"Site baseline: unknown geographic point source_id {point_source}")
    local = data.get("local_coordinate_system", {})
    if local.get("status") == "not_established" and local.get("origin_definition") is not None:
        errors.append("Local origin must remain null until a reliable datum is selected")


def validate_all(root: Path = ROOT) -> list[str]:
    errors: list[str] = []
    reference_ids = load_reference_ids(root / "research" / "references.csv", errors)
    validate_asset_manifest(root / "data" / "asset-manifest" / "assets.json", reference_ids, errors)
    validate_feature_register(root / "data" / "asset-manifest" / "feature-register.csv", reference_ids, errors)
    validate_viewpoints(root / "data" / "scene-layout" / "viewpoints.json", reference_ids, errors)
    validate_baseline(root / "data" / "site-baseline.json", reference_ids, errors)
    return errors


def main() -> int:
    errors = validate_all()
    if errors:
        print("DATA VALIDATION FAILED")
        for error in errors:
            print(f"- {error}")
        return 1
    print("DATA VALIDATION PASSED")
    print("References, site baseline, asset manifest, and viewpoints are structurally valid.")
    print("Structural validity does not certify source accuracy or licensing.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
