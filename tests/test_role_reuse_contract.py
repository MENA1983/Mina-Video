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

    def test_open_ended_expiry_is_rejected(self):
        for expiry in ("permanent", "never", "indefinite", "no-expiry", "none"):
            self.assertFalse(
                validate_assignment(
                    TemporaryExecutionAssignment(
                        task=ExecutionTask.PROVIDER_EXPERIMENT,
                        scope="provider-experiment",
                        expires_when=expiry,
                    )
                )
            )

    def test_embedded_protected_scope_tokens_are_rejected(self):
        for scope in ("grant billing access", "rotate credentials now", "ownership:admin", "final-live-activation-now"):
            self.assertFalse(
                validate_assignment(
                    TemporaryExecutionAssignment(
                        task=ExecutionTask.PROVIDER_EXPERIMENT,
                        scope=scope,
                        expires_when="later",
                    )
                )
            )

    def test_evidence_is_required(self):
        self.assertFalse(
            validate_assignment(
                TemporaryExecutionAssignment(
                    task=ExecutionTask.RENDER_DIAGNOSTICS,
                    scope="diagnostics",
                    expires_when="later",
                    evidence_required=False,
                )
            )
        )

    def test_invalid_task_type_is_rejected(self):
        self.assertFalse(
            validate_assignment(
                TemporaryExecutionAssignment(
                    task="not-a-real-task",
                    scope="diagnostics",
                    expires_when="later",
                )
            )
        )


if __name__ == "__main__":
    unittest.main()
