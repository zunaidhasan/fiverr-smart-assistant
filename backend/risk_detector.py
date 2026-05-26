from typing import List, Optional, Dict
from models import SardarProject, RiskDetectorResponse
from similarity_search import ProjectAnalyzer
import numpy as np


class RiskDetector:
    """Detect risks and red flags in buyer messages."""

    def __init__(self, projects: List[SardarProject]):
        self.projects = projects
        self.analyzer = ProjectAnalyzer(projects)

    def analyze(
        self,
        buyer_message: str,
        budget: Optional[float] = None,
        category: Optional[str] = None,
    ) -> RiskDetectorResponse:
        """Analyze a buyer message for risks and red flags."""
        message_lower = buyer_message.lower()
        red_flags = []

        # --- Check for red flags ---

        # 1. Vague requirements
        vague_score = self._check_vagueness(buyer_message)
        is_vague = vague_score > 0.5

        if is_vague:
            red_flags.append({
                "type": "vague_requirements",
                "severity": "high" if vague_score > 0.7 else "medium",
                "description": "Requirements are very vague. This often leads to scope creep.",
                "details": "Consider asking for specific deliverables, wireframes, or reference examples.",
            })

        # 2. Urgency signals
        urgency_keywords = {
            "urgent": 0.8,
            "asap": 0.9,
            "immediately": 0.9,
            "right away": 0.8,
            "emergency": 0.7,
            "critical": 0.6,
            "broken": 0.5,
            "as soon as possible": 0.7,
            "yesterday": 0.6,
            "fast": 0.3,
            "quick": 0.3,
        }

        urgency_score = 0.0
        for kw, weight in urgency_keywords.items():
            if kw in message_lower:
                urgency_score = max(urgency_score, weight)

        has_urgency = urgency_score > 0.4

        if has_urgency:
            red_flags.append({
                "type": "urgency_pressure",
                "severity": "high" if urgency_score > 0.7 else "medium",
                "description": "Client is applying time pressure.",
                "details": "Set clear boundaries on what can be delivered in the timeframe. Charge a premium for urgency.",
            })

        # 3. Budget mismatch check
        budget_mismatch = None
        if budget and budget > 0 and category:
            budget_info = self.analyzer.get_budget_range(category, buyer_message)
            avg = budget_info["average"]
            if avg > 0:
                ratio = budget / avg
                if ratio < 0.3:
                    budget_mismatch = {
                        "client_budget": budget,
                        "category_average": round(avg, 2),
                        "ratio": round(ratio, 2),
                        "severity": "high",
                        "description": f"Budget (${budget}) is significantly below typical range for this category.",
                    }
                    red_flags.append({
                        "type": "budget_mismatch",
                        "severity": "high",
                        "description": budget_mismatch["description"],
                        "details": "Consider negotiating or offering a scaled-down scope.",
                    })
                elif ratio > 3.0:
                    budget_mismatch = {
                        "client_budget": budget,
                        "category_average": round(avg, 2),
                        "ratio": round(ratio, 2),
                        "severity": "medium",
                        "description": f"Budget is well above average — verify requirements match the investment.",
                    }
                    red_flags.append({
                        "type": "budget_mismatch",
                        "severity": "medium",
                        "description": budget_mismatch["description"],
                        "details": "High budgets are great, but ensure scope justifies the investment.",
                    })

        # 4. Scope creep signals
        scope_keywords = {
            "also": 0.3,
            "and also": 0.4,
            "one more thing": 0.6,
            "by the way": 0.5,
            "while you're at it": 0.7,
            "add": 0.3,
            "include": 0.2,
            "would be great if": 0.5,
            "if possible": 0.3,
            "might need": 0.4,
            "could also": 0.4,
            "unlimited": 0.8,
            "as many as needed": 0.7,
            "until i'm satisfied": 0.8,
        }

        scope_creep_score = 0.0
        for kw, weight in scope_keywords.items():
            if kw in message_lower:
                scope_creep_score = max(scope_creep_score, weight)

        if scope_creep_score > 0.3:
            red_flags.append({
                "type": "scope_creep",
                "severity": "high" if scope_creep_score > 0.6 else "low",
                "description": "Message contains language suggesting potential scope creep.",
                "details": "Clearly define deliverables and revision limits in your proposal.",
            })

        # 5. Check for unrealistic expectations
        if "complex" in message_lower and budget and budget < 200:
            red_flags.append({
                "type": "complexity_mismatch",
                "severity": "medium",
                "description": "Project described as 'complex' but budget is low.",
                "details": "Clarify complexity and adjust budget accordingly.",
            })

        # 6. Revision/unlimited signals
        if "unlimited" in message_lower or "endless" in message_lower:
            red_flags.append({
                "type": "unlimited_revisions",
                "severity": "high",
                "description": "Mentions 'unlimited' — potential for excessive revisions.",
                "details": "Set clear revision limits in your proposal. Offer paid revision packages for additional changes.",
            })

        # 7. Multiple deliverables in one message
        if buyer_message.count(",") > 5 or buyer_message.count("and") > 4:
            red_flags.append({
                "type": "scope_cramming",
                "severity": "low",
                "description": "Multiple requirements listed in one message — ensure scope is well-defined.",
                "details": "List all deliverables clearly and price accordingly.",
            })

        # Calculate overall risk score
        risk_score = self._calculate_risk_score(
            red_flags, vague_score, urgency_score, scope_creep_score
        )

        # Recommendations
        recommendations = self._generate_recommendations(red_flags, risk_score)

        return RiskDetectorResponse(
            risk_score=risk_score,
            red_flags=red_flags,
            scope_creep_probability=round(scope_creep_score, 2),
            vague_requirements=is_vague,
            urgency_signals=has_urgency,
            budget_mismatch=budget_mismatch,
            recommendations=recommendations,
        )

    def _check_vagueness(self, message: str) -> float:
        """Score how vague a message is (0 = very specific, 1 = very vague)."""
        score = 0.0
        message_lower = message.lower()

        # Positive signals (specific requirements)
        specific_signals = [
            "i need", "i require", "specifically", "exactly",
            "wireframe", "prototype", "mockup",
            "example", "reference", "like this", "similar to",
            "feature", "functio", "specific",
            "already", "existing", "currently",
        ]

        for signal in specific_signals:
            if signal in message_lower:
                score -= 0.15

        # Negative signals (vague)
        vague_signals = [
            "something", "kind of", "sort of", "maybe",
            "not sure", "perhaps", "possibly", "general",
            "basic", "simple", "easy", "just need",
            "nothing too", "should be", "would like",
            "i want", "make it look", "make it work",
        ]

        for signal in vague_signals:
            if signal in message_lower:
                score += 0.15

        # Length-based assessment (short messages are often vague)
        if len(message) < 100:
            score += 0.3
        elif len(message) < 200:
            score += 0.15
        elif len(message) > 500:
            score -= 0.1

        return max(0.0, min(1.0, score))

    def _calculate_risk_score(
        self,
        red_flags: list,
        vague_score: float,
        urgency_score: float,
        scope_creep_score: float,
    ) -> float:
        """Calculate overall risk score."""
        score = 0.1  # base

        for flag in red_flags:
            if flag["severity"] == "high":
                score += 0.2
            elif flag["severity"] == "medium":
                score += 0.12
            else:
                score += 0.05

        score += vague_score * 0.15
        score += urgency_score * 0.1
        score += scope_creep_score * 0.15

        return round(min(1.0, score), 2)

    def _generate_recommendations(self, red_flags: list, risk_score: float) -> List[str]:
        """Generate actionable recommendations based on detected risks."""
        recs = []

        if risk_score > 0.7:
            recs.append("HIGH RISK: Consider passing on this project or requiring a detailed brief before proceeding.")
        if risk_score > 0.5:
            recs.append("Set clear, written boundaries on scope, revisions, and timeline before starting.")

        flag_types = [f["type"] for f in red_flags]

        if "vague_requirements" in flag_types:
            recs.append("Ask for specific examples, wireframes, or reference projects to clarify requirements.")
        if "urgency_pressure" in flag_types:
            recs.append("Charge an urgency premium (25-50% above standard rate). Define what's deliverable in the timeframe.")
        if "budget_mismatch" in flag_types:
            recs.append("Propose an adjusted scope that matches the budget, or negotiate the budget upward.")
        if "scope_creep" in flag_types:
            recs.append("Define deliverables in writing. Use milestone payments. Offer a change order process for additions.")
        if "unlimited_revisions" in flag_types:
            recs.append("Include 2-3 rounds of revisions in your base price. Offer revision packages for additional rounds.")
        if "complexity_mismatch" in flag_types:
            recs.append("Clarify the actual complexity. If it's truly complex, provide a realistic quote.")

        if not recs:
            recs.append("No significant risks detected. Proceed with standard proposal process.")

        return recs
