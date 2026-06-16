import numpy as np
from typing import List, Optional
from collections import defaultdict, Counter
from models import SardarProject, DashboardMetrics, CRMEntry, CRMResponse
from similarity_search import ProjectAnalyzer


class DealIntelligence:
    """Compute dashboard metrics and CRM data from project database."""

    def __init__(self, projects: List[SardarProject]):
        self.projects = projects
        self.analyzer = ProjectAnalyzer(projects)

    def get_dashboard_metrics(self) -> DashboardMetrics:
        """Compute all dashboard metrics from project data."""
        total = len(self.projects)

        # Projects by category
        cat_counts = Counter(p.category for p in self.projects)
        cat_budgets = defaultdict(list)
        for p in self.projects:
            cat_budgets[p.category].append(self._estimate_budget(p))

        projects_by_category = [
            {
                "category": cat,
                "count": count,
                "technologies": self._get_top_technologies_for_category(cat),
                "estimated_budget_range": self._get_budget_range_str(cat),
            }
            for cat, count in sorted(cat_counts.items(), key=lambda x: -x[1])
        ]

        # Technology distribution
        tech_counts = Counter(p.main_technology for p in self.projects if p.main_technology)
        total_tech = sum(tech_counts.values())
        technology_distribution = [
            {
                "technology": tech,
                "count": count,
                "percentage": round(count / total_tech * 100, 1) if total_tech > 0 else 0,
            }
            for tech, count in sorted(tech_counts.items(), key=lambda x: -x[1])
        ][:15]  # Top 15 technologies

        # Feature popularity
        feature_counts = Counter()
        for p in self.projects:
            if p.website_features:
                for f in p.website_features.split(","):
                    f = f.strip()
                    if f:
                        feature_counts[f] += 1

        total_features = sum(feature_counts.values())
        feature_popularity = [
            {
                "feature": feat,
                "count": count,
                "percentage": round(count / total_features * 100, 1) if total_features > 0 else 0,
            }
            for feat, count in sorted(feature_counts.items(), key=lambda x: -x[1])
        ][:15]

        # Best paying niches (categories with highest estimated budgets)
        best_paying = sorted(
            projects_by_category,
            key=lambda x: self._avg_estimated_budget(x["category"]),
            reverse=True,
        )[:5]

        # Quality distribution
        quality_counts = Counter(p.quality for p in self.projects if p.quality)
        quality_distribution = [
            {"quality": q, "count": c}
            for q, c in sorted(quality_counts.items(), key=lambda x: -x[1])
        ]

        # Match score distribution
        score_counts = Counter(p.match_score_potential for p in self.projects)
        match_score_distribution = [
            {"score": s, "count": c}
            for s, c in sorted(score_counts.items())
        ]

        return DashboardMetrics(
            total_projects=total,
            categories=sorted(list(set(p.category for p in self.projects))),
            projects_by_category=projects_by_category,
            technology_distribution=technology_distribution,
            feature_popularity=feature_popularity,
            best_paying_niches=best_paying,
            quality_distribution=quality_distribution,
            match_score_distribution=match_score_distribution,
        )

    def _estimate_budget(self, project: SardarProject) -> float:
        """Estimate budget for a project based on its technology and features."""
        tech_budgets = {
            "react / next.js custom": 1500,
            "shopify advanced": 800,
            "wordpress + woocommerce": 600,
            "mixed (wordpress + react)": 1200,
            "laravel / custom php": 2000,
            "webflow": 500,
        }

        base = tech_budgets.get(project.main_technology.lower(), 500)

        # Bonus for features
        feature_bonus = 0
        if project.website_features:
            if "Payment Integration" in project.website_features:
                feature_bonus += 300
            if "Shopping Cart" in project.website_features:
                feature_bonus += 200
            if "Authentication/Login" in project.website_features:
                feature_bonus += 200
            if "Booking System" in project.website_features:
                feature_bonus += 150
            if "Multilingual" in project.website_features:
                feature_bonus += 150
            if "Live Chat" in project.website_features:
                feature_bonus += 100

        return base + feature_bonus

    def _avg_estimated_budget(self, category: str) -> float:
        """Get average estimated budget for a category."""
        cat_projs = [p for p in self.projects if p.category == category]
        if not cat_projs:
            return 0
        return np.mean([self._estimate_budget(p) for p in cat_projs])

    def _get_top_technologies_for_category(self, category: str) -> List[str]:
        """Get top 3 technologies used in a category."""
        techs = Counter()
        for p in self.projects:
            if p.category == category and p.main_technology:
                techs[p.main_technology] += 1
        return [t for t, _ in techs.most_common(3)]

    def _get_budget_range_str(self, category: str) -> dict:
        """Get budget range string for a category."""
        info = self.analyzer.get_budget_range(category, "")
        return {
            "min": info["min"],
            "max": info["max"],
            "average": round(info["average"], 0),
        }

    def get_crm_data(self) -> CRMResponse:
        """Generate CRM data from the project database."""
        entries = []

        for p in self.projects:
            # Determine risk flags
            risk_flags = []
            if p.quality.lower() != "high":
                risk_flags.append(f"Quality: {p.quality}")

            entry = CRMEntry(
                id=p.website_url,
                project_url=p.website_url,
                category=p.category,
                main_technology=p.main_technology,
                use_case=p.use_case,
                best_for=p.best_for,
                match_score=p.match_score_potential,
                keywords=p.keywords[:100] + "..." if len(p.keywords) > 100 else p.keywords,
                strengths=p.strengths[:100] + "..." if len(p.strengths) > 100 else p.strengths,
                risk_flags=risk_flags,
            )
            entries.append(entry)

        tech_diversity = len(set(p.main_technology for p in self.projects if p.main_technology))
        categories = sorted(list(set(p.category for p in self.projects)))

        return CRMResponse(
            entries=entries,
            total_count=len(entries),
            categories=categories,
            technology_diversity=tech_diversity,
        )


class ProposalOptimizer:
    """Optimize proposals using portfolio database and best practices."""

    def __init__(self, projects: List[SardarProject]):
        self.projects = projects
        self.analyzer = ProjectAnalyzer(projects)

    def optimize(
        self,
        client_brief: str,
        category: Optional[str] = None,
        budget: Optional[float] = None,
    ) -> dict:
        """Generate proposal optimization recommendations."""
        from reply_generator import ReplyGenerator

        generator = ReplyGenerator(self.projects)
        return generator.generate_proposal_optimizer(client_brief, category, budget)
