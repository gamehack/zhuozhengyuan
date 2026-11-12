import json
import unittest

from scripts.validate_data import ROOT, validate_all


class ProjectDataValidationTests(unittest.TestCase):
    def test_committed_project_data_is_valid(self):
        errors = validate_all(ROOT)
        self.assertEqual(errors, [], "\n".join(errors))

    def test_asset_manifest_starts_empty_until_evidence_exists(self):
        path = ROOT / "data" / "asset-manifest" / "assets.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(data["assets"], [])

    def test_site_origin_is_not_fabricated(self):
        path = ROOT / "data" / "site-baseline.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(data["local_coordinate_system"]["status"], "not_established")
        self.assertIsNone(data["local_coordinate_system"]["origin_definition"])


if __name__ == "__main__":
    unittest.main()
