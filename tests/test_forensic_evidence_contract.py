import unittest

from backend.forensic_evidence_contract import (
    EvidenceAssignment,
    EvidenceScope,
    validate_evidence_assignment,
)


class ForensicEvidenceContractTests(unittest.TestCase):
    def test_media_evidence_assignment_is_allowed(self):
        self.assertTrue(
            validate_evidence_assignment(
                EvidenceAssignment(
                    scope=EvidenceScope.MEDIA_QUALITY,
                    case_id="case-001",
                    expires_when="case closed",
                )
            )
        )

    def test_evidence_assignment_requires_case_and_expiry(self):
        self.assertFalse(
            validate_evidence_assignment(
                EvidenceAssignment(
                    scope=EvidenceScope.PROVENANCE,
                    case_id="",
                    expires_when="",
                )
            )
        )


if __name__ == "__main__":
    unittest.main()
