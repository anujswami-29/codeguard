# ============================================================
# CODEGUARD — Delegate Agent
# A sub-agent with BOUNDED DELEGATION.
# It has FEWER permissions than the main agent.
# Main agent can spawn it, but cannot grant it MORE than it has.
# ============================================================

from intent_model import Intent
from policy_engine import PolicyEngine, PolicyDecision
from executor import Executor
from logger import get_logger, print_decision

logger = get_logger("DelegateAgent")


class DelegateAgent:
    """
    A sub-agent spawned by the main CodeGuard agent.
    
    Delegation constraints (from policy_config.py):
    - Can only access: workspace/src/utils (NOT helpers)
    - Can only perform: read, add_docstring (NOT edit, create, fix_style)
    
    This demonstrates BOUNDED DELEGATION:
    The main agent cannot grant the delegate more than it owns.
    """

    def __init__(self, delegate_id: str, granted_scope: str):
        self.delegate_id = delegate_id
        self.granted_scope = granted_scope
        self.policy_engine = PolicyEngine(is_delegate=True)
        self.executor = Executor()
        logger.info(
            f"Delegate agent '{delegate_id}' spawned with scope: {granted_scope}"
        )

    def handle(self, intent: Intent) -> tuple[PolicyDecision, str | None]:
        """
        Process an intent through the delegate's restricted policy engine.
        Returns (decision, result).
        """
        # Mark this intent as delegated
        intent.delegated = True
        intent.delegate_id = self.delegate_id

        logger.info(f"Delegate '{self.delegate_id}' received: {intent}")

        # Evaluate against DELEGATE policies (stricter)
        decision = self.policy_engine.evaluate(intent)
        print_decision(decision.allowed, str(decision))

        if decision.allowed:
            result = self.executor.run(intent)
            return decision, result
        else:
            return decision, None
