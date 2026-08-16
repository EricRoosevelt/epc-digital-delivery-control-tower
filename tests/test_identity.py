import unittest

from src.identity import (
    IDENTITY_NAMESPACE,
    build_finding_key,
    build_requirement_key,
    canonical_json,
)


class IdentityTests(unittest.TestCase):
    def test_canonical_json_preserves_order_and_unicode(self):
        self.assertEqual(
            canonical_json(["R-005A", "配电"]),
            '["R-005A","配电"]',
        )

    def test_requirement_key_matches_golden_uuid(self):
        self.assertEqual(
            str(IDENTITY_NAMESPACE),
            "7611c2a0-c29a-50fa-b00d-5058d25a41d3",
        )
        self.assertEqual(
            build_requirement_key(
                "R-005A",
                "EPC_Delivery.AssetTag",
            ),
            "842a37c7-3183-5fce-ab45-b93c37ec7a08",
        )

    def test_finding_key_matches_golden_uuid(self):
        requirement_key = build_requirement_key(
            "R-005A",
            "EPC_Delivery.AssetTag",
        )

        self.assertEqual(
            build_finding_key(
                "ids-v0.1-8706ef58303bfd11",
                "hvac",
                requirement_key,
                "hvac::38WbwIGD90nB_3T2BTU5Ed",
            ),
            "031430a9-4a49-58cb-9ce1-13619e4b0a3d",
        )

    def test_empty_element_key_is_canonical_for_na(self):
        requirement_key = build_requirement_key(
            "R-003",
            "Pset_BeamCommon.LoadBearing",
        )

        self.assertEqual(
            build_finding_key(
                "ids-v0.1-8706ef58303bfd11",
                "architecture",
                requirement_key,
                None,
            ),
            "935997f4-e041-5fa1-a0dc-c729e8a87613",
        )


if __name__ == "__main__":
    unittest.main()
