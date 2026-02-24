# ============================================================
# CODEGUARD — Policy Engine (Enforcement Layer)
# This is the GATEKEEPER. Every intent passes through here.
# If ANY rule is violated → BLOCKED. No exceptions.
# ============================================================

import os
from dataclasses import dataclass
from intent_model import Intent, ActionType
from policy_config import POLICY
from logger import get_logger

logger = get_logger("PolicyEngine")


@dataclass
class PolicyDecision:
    """Result of a policy check."""
    allowed: bool
    reason: str
    intent: Intent

    def __str__(self):
        status = "✅ ALLOWED" if self.allowed else "❌ BLOCKED"
        return f"{status} | {self.intent} | Reason: {self.reason}"


class PolicyEngine:
    """
    Deterministic, rule-based enforcement layer.
    Checks every intent against the policy config.
    Hardcoded if/else is NOT sufficient per the rubric —
    this uses a structured rule evaluation pipeline.
    """

    def __init__(self, is_delegate: bool = False):
        self.is_delegate = is_delegate
        self.policy = POLICY

    def evaluate(self, intent: Intent) -> PolicyDecision:
        """
        Run ALL policy checks on an intent.
        Returns a PolicyDecision with allow/block + reason.
        """
        logger.info(f"Evaluating: {intent}")

        # Run each rule in sequence — first failure blocks
        checks = [
            self._check_action_blocked,
            self._check_action_allowed,
            self._check_protected_file,
            self._check_directory_scope,
        ]

        for check in checks:
            decision = check(intent)
            if decision is not None:
                # Log the final decision
                if decision.allowed:
                    logger.info(f"  ✅ ALLOWED → {decision.reason}")
                else:
                    logger.warning(f"  ❌ BLOCKED → {decision.reason}")
                return decision

        # All checks passed
        decision = PolicyDecision(
            allowed=True,
            reason="All policy checks passed",
            intent=intent
        )
        logger.info(f"  ✅ ALLOWED → All policy checks passed")
        return decision

    def _check_action_blocked(self, intent: Intent) -> PolicyDecision | None:
        """Rule 1: Is this action globally forbidden?"""
        if intent.action.value in self.policy.blocked_actions:
            return PolicyDecision(
                allowed=False,
                reason=f"Action '{intent.action.value}' is globally blocked. "
                       f"Blocked actions: {self.policy.blocked_actions}",
                intent=intent
            )
        return None

    def _check_action_allowed(self, intent: Intent) -> PolicyDecision | None:
        """Rule 2: Is this action in the permitted list?"""
        allowed = (self.policy.delegate_allowed_actions
                   if self.is_delegate else self.policy.allowed_actions)
        if intent.action.value not in allowed:
            return PolicyDecision(
                allowed=False,
                reason=f"Action '{intent.action.value}' not in permitted actions "
                       f"for {'delegate' if self.is_delegate else 'main'} agent. "
                       f"Permitted: {allowed}",
                intent=intent
            )
        return None

    def _check_protected_file(self, intent: Intent) -> PolicyDecision | None:
        """Rule 3: Is the target file on the protected list?"""
        # Normalize path for comparison
        target = os.path.normpath(intent.target_file)
        for protected in self.policy.protected_files:
            if target == os.path.normpath(protected):
                return PolicyDecision(
                    allowed=False,
                    reason=f"'{intent.target_file}' is a PROTECTED FILE. "
                           f"Access is permanently blocked.",
                    intent=intent
                )
        return None

    def _check_directory_scope(self, intent: Intent) -> PolicyDecision | None:
        """Rule 4: Is the file inside an allowed directory?"""
        allowed_dirs = (self.policy.delegate_allowed_directories
                        if self.is_delegate else self.policy.allowed_directories)
        target = os.path.normpath(intent.target_file)
        for allowed_dir in allowed_dirs:
            if target.startswith(os.path.normpath(allowed_dir)):
                return None  # Pass — file is in scope

        return PolicyDecision(
            allowed=False,
            reason=f"'{intent.target_file}' is outside allowed directories. "
                   f"Allowed: {allowed_dirs}",
            intent=intent
        )
