# Data and Coordinate Standard

## Units
- All research measurements are expressed in meters.
- Coordinates are local garden coordinates in meters.
- Angles are degrees.
- Geographic coordinates retain their original CRS and are never silently mixed with local coordinates.
- Unreal import is validated against a 1 m calibration object.

## Local coordinate convention
The planned local convention is X=east, Y=north, Z=up. Rotation is stored in degrees in X, Y, Z order, with the Blender convention documented by each generator.

The local origin is **not yet defined**. It must be selected from a reliable measured plan, survey datum, or control point. Do not use the UNESCO property reference coordinate as a survey origin.

## Stable IDs
| Category | Code | Example |
|---|---|---|
| Building / architecture | BLD | ZJY-BLD-001 |
| Tree / vegetation | TRE | ZJY-TRE-001 |
| Rock / rockery | ROC | ZJY-ROC-001 |
| Water body | WAT | ZJY-WAT-001 |
| Bridge | BRG | ZJY-BRG-001 |
| Path / paving | PTH | ZJY-PTH-001 |
| Other object | OBJ | ZJY-OBJ-001 |
| Fixed viewpoint | VIEW | ZJY-VIEW-001 |
| Source reference | REF | REF-001 |

IDs are immutable. If an object is split or merged, create new IDs and preserve the relationship in notes.

## Evidence grades
| Grade | Meaning | Examples |
|---|---|---|
| A | Direct measurement or authoritative measured drawing | Survey, dimensioned conservation drawing |
| B | Strong visual or documentary evidence | Multiple dated official photographs, detailed archival drawing |
| C | Inference from partial evidence | Estimated dimension from a known scale or several photographs |
| D | Unverified assumption | Visual guess, AI-generated completion, undocumented detail |

Grade D is allowed only for clearly marked placeholders. It cannot pass final accuracy review.

## Asset record requirements
Each asset record must include asset_id, asset_type, area, name_zh, location_local_m, rotation_deg, evidence_level, source_ids, and modeling_status. Dimensions are optional until evidence exists. If present, they must be positive and expressed as length, width, height in meters.

## Source register
Every source receives a REF ID in research/references.csv. Record publisher, URL, access date, source type, permission status, and notes. Asset source_ids must point to existing REF IDs.

## Data quality
- IDs must be unique.
- Coordinates and rotations must contain three finite numbers.
- Source references must exist.
- Do not store secrets, personal data, or restricted material in the public repository.
- Never commit unlicensed full-resolution photos or scanned books. Store a source URL and a short factual note instead.
