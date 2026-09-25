import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

class PublicContractTests(unittest.TestCase):
    def test_dispatch_contract_is_valid_and_bounded(self):
        data = json.loads((ROOT / "video-runner" / "dispatch-contract.json").read_text())
        self.assertEqual(data.get("schema"), "external-video/v1")
        self.assertIn("job_id", data.get("required", []))
        self.assertIn("manifest_sha256", data.get("required", []))

    def test_renderer_has_duplicate_safe_release_tag(self):
        source = (ROOT / "video-runner" / "render.py").read_text()
        self.assertIn("mina-video-", source)
        self.assertIn("sha256", source.lower())

    def test_workflow_has_duplicate_guard(self):
        source = (ROOT / ".github" / "workflows" / "external-video-render.yml").read_text()
        self.assertIn("duplicate_guard", source)
        self.assertRegex(source, r"steps\.duplicate_guard\.outputs\.exists")
        self.assertIn("gh release create", source)

    def test_no_factory_secret_names_in_public_runner(self):
        public_text = "\n".join(
            p.read_text(errors="ignore")
            for p in [
                ROOT / "video-runner" / "render.py",
                ROOT / ".github" / "workflows" / "external-video-render.yml",
            ]
        )
        forbidden = ["MINA_VIDEO_GITHUB_TOKEN", "GOOGLE_CLIENT_SECRET", "CLIENT_SECRET"]
        for token in forbidden:
            self.assertNotIn(token, public_text)

if __name__ == "__main__":
    unittest.main()
