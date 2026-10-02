import unittest

from backend.role_reuse_contract import (
    ExecutionTask,
    TemporaryExecutionAssignment,
    validate_assignment,
)


class RoleReuseContractTests(unittest.TestCase):
    def test_media_research_assignment_is_allowed(self):
        self.assertTrue(
            validate_assignment(
                TemporaryExecutionAssignment(
                    task=ExecutionTask.MEDIA_QUALITY_RESEARCH,
                    scope="media-quality",
                    expires_when="manager closes task",
                )
            )
        )

    def test_factory_owner_scopes_are_never_delegated_to_mina(self):
        for scope in ("ownership", "billing", "credentials", "governance", "final-live-activation"):
            self.assertFalse(
                validate_assignment(
                    TemporaryExecutionAssignment(
                        task=ExecutionTask.PROVIDER_EXPERIMENT,
                        scope=scope,
                        expires_when="later",
                    )
                )
            )

    def test_assignment_requires_expiry(self):
        self.assertFalse(
            validate_assignment(
                TemporaryExecutionAssignment(
                    task=ExecutionTask.RENDER_DIAGNOSTICS,
                    scope="diagnostics",
                    expires_when="",
                )
            )
        )


if __name__ == "__main__":
    unittest.main()
