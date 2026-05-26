import random
from typing import List, Optional
from .models import SardarProject, SituationType, SmartReplyResponse
from .templates import (
    TEMPLATE_REGISTRY,
    detect_situation_type,
    get_templates_for_situation,
    TONES,
)
from .similarity_search import ProjectSimilaritySearch, ProjectAnalyzer
import numpy as np


class ReplyGenerator:
    """Generates smart, personalized replies using portfolio references and templates."""

    def __init__(self, projects: List[SardarProject]):
        self.projects = projects
        self.similarity_search = ProjectSimilaritySearch()
        self.similarity_search.fit(projects)
        self.analyzer = ProjectAnalyzer(projects)

    def generate(
        self,
        client_message: str,
        situation_type: Optional[SituationType] = None,
        category: Optional[str] = None,
    ) -> SmartReplyResponse:
        """Generate a smart reply for a client message."""
        import re

        # Auto-detect situation if not provided
        if situation_type is None:
            situation_type = detect_situation_type(client_message)

        # Find similar past projects
        similar_projects = self.similarity_search.search(client_message, top_k=5)

        # Get category from similar projects or provided category
        if category is None and similar_projects:
            category = similar_projects[0][0].category

        # Extract a project title from the URL
        def url_to_title(url: str) -> str:
            """Convert a URL to a readable project name."""
            name = url.replace("https://", "").replace("http://", "").replace("www.", "")
            name = name.split("/")[0]
            name = name.split(".")[0]
            # Convert kebab/snake case to title
            name = re.sub(r'[-_]', ' ', name)
            name = name.title()
            return name

        # Select best template
        templates = get_templates_for_situation(situation_type)
        best_template = templates[0] if templates else list(TEMPLATE_REGISTRY.values())[0]

        # Determine tone
        suggested_tone = best_template.tone
        tone_description = TONES.get(suggested_tone, "Professional and direct.")

        # Get budget estimate
        budget_info = self.analyzer.get_budget_range(category or "", client_message)
        estimated_budget = max(100, int(budget_info["average"] * random.uniform(0.8, 1.2)))
        estimated_budget_max = int(estimated_budget * random.uniform(1.3, 1.8))

        # Get timeline estimate
        timeline_info = self.analyzer.get_timeline_estimate(category or "", estimated_budget, client_message)

        # Prepare reference project
        reference = ""
        ref_tech = ""
        if similar_projects:
            ref_project = similar_projects[0][0]
            reference = url_to_title(ref_project.website_url)
            ref_tech = ref_project.used_stack or ref_project.main_technology
            if len(reference) > 60:
                reference = reference[:57] + "..."

        # Prepare questions
        questions = best_template.questions[:3]
        questions_text = "\n".join([f"- {q}" for q in questions])

        # Build technology mention
        tech_mention = f"including {ref_tech}" if ref_tech else ""

        # Generate the draft reply
        draft_reply = best_template.personalize(
            buyer_name="[Buyer Name]",
            project_title="[Project Title]",
            category=category or "this area",
            reference_project=reference,
            reference_outcome=f"a high-quality project {tech_mention}",
            questions_text=questions_text,
            estimated_budget=estimated_budget,
            estimated_budget_max=estimated_budget_max,
            timeline=timeline_info["estimated_days"],
            timeline_max=timeline_info["range"][1] if timeline_info["range"] else timeline_info["estimated_days"] + 5,
            start_date="[Start Date]",
            freelancer_name="[Your Name]",
        )

        # Map past projects for response
        past_project_refs = []
        for proj, score in similar_projects:
            past_project_refs.append({
                "project_id": proj.website_url,
                "title": url_to_title(proj.website_url),
                "url": proj.website_url,
                "category": proj.category,
                "technology": proj.main_technology,
                "stack_used": proj.used_stack,
                "description": proj.brief_description[:100] + "..." if len(proj.brief_description) > 100 else proj.brief_description,
                "match_score": proj.match_score_potential,
                "similarity_score": round(score, 3),
                "quality": proj.quality,
            })

        # Confidence score based on how good our data is
        confidence = self._calculate_confidence(similar_projects, situation_type, category)

        return SmartReplyResponse(
            draft_reply=draft_reply,
            relevant_past_projects=past_project_refs,
            suggested_tone=tone_description,
            questions_to_ask=questions,
            estimated_quote_range={
                "min": estimated_budget,
                "max": estimated_budget_max,
                "currency": "USD",
                "confidence": budget_info.get("count", 0) > 0,
            },
            confidence_score=confidence,
        )

    def _calculate_confidence(
        self,
        similar_projects: list,
        situation_type: SituationType,
        category: Optional[str],
    ) -> float:
        """Calculate confidence score for the generated reply."""
        score = 0.5  # base

        # More similar projects = higher confidence
        if similar_projects:
            avg_similarity = np.mean([s[1] for s in similar_projects])
            score += min(0.3, avg_similarity * 0.3)

        # Have data in this category?
        if category:
            category_projects = [p for p in self.projects if p.category.lower() == category.lower()]
            if len(category_projects) > 30:
                score += 0.2
            elif len(category_projects) > 10:
                score += 0.15
            elif len(category_projects) > 3:
                score += 0.1

        # Known situation type
        if situation_type != SituationType.GENERAL:
            score += 0.05

        return min(1.0, round(score, 2))

    def generate_proposal_optimizer(
        self,
        client_brief: str,
        category: Optional[str] = None,
        budget: Optional[float] = None,
    ) -> dict:
        """Generate optimized proposal recommendations."""
        import re

        def url_to_title(url: str) -> str:
            name = url.replace("https://", "").replace("http://", "").replace("www.", "")
            name = name.split("/")[0]
            name = name.split(".")[0]
            name = re.sub(r'[-_]', ' ', name)
            return name.title()

        similar = self.similarity_search.search(client_brief, top_k=8)

        # Portfolio examples
        portfolio_examples = []
        for proj, score in similar[:5]:
            portfolio_examples.append({
                "title": url_to_title(proj.website_url),
                "url": proj.website_url,
                "category": proj.category,
                "technology": proj.main_technology,
                "stack": proj.used_stack,
                "description": proj.brief_description[:100] + "..." if len(proj.brief_description) > 100 else proj.brief_description,
                "strengths": proj.strengths,
                "match_score": proj.match_score_potential,
                "relevance_score": round(score, 3),
            })

        # Relevant experience
        relevant_experience = []
        if portfolio_examples:
            cats = set(e["category"] for e in portfolio_examples)
            for c in cats:
                count = len([p for p in self.projects if p.category == c])
                relevant_experience.append(f"Built {count} {c.lower()} projects in the portfolio database")

        # Risk signals
        risk_signals = self._detect_risk_signals(client_brief)

        # Questions to ask
        situation = detect_situation_type(client_brief)
        templates = get_templates_for_situation(situation)
        questions = templates[0].questions[:4] if templates else []

        # Recommended structure
        structure = [
            "Brief understanding summary (show you read and understood)",
            "Relevant portfolio examples (2-3 similar projects from your database)",
            "Technology expertise (mention relevant tech from similar projects)",
            "Proposed approach and methodology",
            "Timeline estimate with milestones",
            "Budget/quote (range or fixed)",
            "Questions for clarification",
            "Clear call to action",
        ]

        # Quote range
        detected_category = category or (similar[0][0].category if similar else "General")
        budget_info = self.analyzer.get_budget_range(detected_category, client_brief)
        base = budget if budget else budget_info["average"]
        quote_min = max(100, int(base * 0.8))
        quote_max = int(base * 1.5)

        # Timeline
        timeline = self.analyzer.get_timeline_estimate(detected_category, base, client_brief)

        return {
            "portfolio_examples": portfolio_examples,
            "relevant_experience": relevant_experience,
            "risk_signals": risk_signals,
            "questions_to_ask": questions,
            "recommended_structure": structure,
            "suggested_quote_range": {
                "min": quote_min,
                "max": quote_max,
                "currency": "USD",
            },
            "estimated_timeline": f"{timeline['estimated_days']} days (range: {timeline['range'][0]}-{timeline['range'][1]} days)",
        }

    def _detect_risk_signals(self, message: str) -> List[str]:
        """Detect potential risk signals in a client message."""
        signals = []
        message_lower = message.lower()

        if "urgent" in message_lower or "asap" in message_lower:
            signals.append("Client is in a rush — scope creep risk if requirements aren't clear")
        if len(message) < 80:
            signals.append("Very brief message — may indicate vague requirements")
        if "unlimited" in message_lower:
            signals.append("Mentions 'unlimited' — potential scope issues")
        if "budget" not in message_lower and "$" not in message:
            signals.append("No budget mentioned — may lead to negotiation friction")
        if "complex" in message_lower or "difficult" in message_lower:
            signals.append("Client acknowledges complexity — set clear boundaries early")
        if "cheap" in message_lower or "low budget" in message_lower:
            signals.append("Budget-conscious — manage expectations on quality vs. cost")
        if "revolutionary" in message_lower or "next big" in message_lower:
            signals.append("Grand vision — clarify feasibility and scope")

        return signals
