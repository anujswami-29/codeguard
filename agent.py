# ============================================================
# CODEGUARD — Main Agent
# The primary agent. Receives instructions → parses intent →
# validates policy → executes (or blocks).
# Can spawn delegate agents with bounded scope.
# ============================================================

from intent_model import Intent
from intent_parser import parse_intent
from policy_engine import PolicyEngine, PolicyDecision
from executor import Executor
from delegate_agent import DelegateAgent
from logger import get_logger, print_decision, print_banner

logger = get_logger("CodeGuardAgent")


class CodeGuardAgent:
    """
    Main CodeGuard agent.
    
    Flow:
    1. Receive instruction (natural language)
    2. Parse → structured Intent (reasoning layer)
    3. Evaluate → PolicyDecision (enforcement layer)
    4. Execute only if allowed (execution layer)
    5. Log everything
    """

    def __init__(self):
        self.policy_engine = PolicyEngine(is_delegate=False)
        self.executor = Executor()
        self.delegates: dict[str, DelegateAgent] = {}
        logger.info("CodeGuard main agent initialized")

    def handle(self, instruction: str) -> str:
        """Process a natural language instruction end-to-end."""
        print_banner(f"INSTRUCTION: {instruction}")

        # ── Step 1: REASONING — Parse to structured intent
        print("  📋 Step 1: Parsing instruction into structured intent...")
        intent = parse_intent(instruction)
        print(f"  → {intent}\n")

        # ── Step 2: ENFORCEMENT — Evaluate against policies
        print("  🔒 Step 2: Evaluating against policy rules...")
        decision = self.policy_engine.evaluate(intent)
        print_decision(decision.allowed, decision.reason)
        print()

        # ── Step 3: EXECUTION — Only if allowed
        if decision.allowed:
            print("  ⚙️  Step 3: Executing approved action...")
            result = self.executor.run(intent)
            print(f"  → {result}\n")
            return result
        else:
            msg = f"Action blocked by policy: {decision.reason}"
            print(f"  🚫 Execution prevented. {msg}\n")
            return msg

    def spawn_delegate(self, delegate_id: str, scope: str) -> DelegateAgent:
        """
        Create a sub-agent with bounded delegation.
        The delegate gets FEWER permissions than the main agent.
        """
        print_banner(f"SPAWNING DELEGATE AGENT: {delegate_id}", color="YELLOW")
        agent = DelegateAgent(delegate_id=delegate_id, granted_scope=scope)
        self.delegates[delegate_id] = agent
        print(f"  Delegate '{delegate_id}' created with restricted scope: {scope}\n")
        return agent

    def delegate_instruction(self, delegate_id: str, instruction: str) -> str:
        """
        Send an instruction to an existing delegate agent.
        The delegate has its own (stricter) policy engine.
        """
        if delegate_id not in self.delegates:
            return f"No delegate found with id: {delegate_id}"

        print_banner(f"DELEGATE '{delegate_id}' INSTRUCTION: {instruction}", color="YELLOW")

        # Parse intent — marked as delegated
        intent = parse_intent(instruction, delegated=True, delegate_id=delegate_id)
        print(f"  → {intent}\n")

        delegate = self.delegates[delegate_id]
        decision, result = delegate.handle(intent)

        if result:
            return result
        else:
            return f"Delegate action blocked: {decision.reason}"
