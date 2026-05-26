import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Tuple
from .models import SardarProject


class ProjectSimilaritySearch:
    """Search for similar past projects using TF-IDF and cosine similarity."""

    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            max_features=5000,
            stop_words="english",
            ngram_range=(1, 2),
            max_df=0.85,
            min_df=1,
        )
        self._fitted = False
        self._tfidf_matrix = None
        self._projects = []

    def fit(self, projects: List[SardarProject]):
        """Fit the vectorizer on project data."""
        self._projects = projects
        documents = []
        for p in projects:
            doc = f"{p.brief_description} {p.keywords} {p.use_case} {p.strengths} {p.category} {p.used_stack}"
            documents.append(doc)

        if documents:
            self._tfidf_matrix = self.vectorizer.fit_transform(documents)
            self._fitted = True

    def search(self, query: str, top_k: int = 5) -> List[Tuple[SardarProject, float]]:
        """Search for similar projects to the given query."""
        if not self._fitted or not self._projects:
            return []

        query_vec = self.vectorizer.transform([query])
        similarities = cosine_similarity(query_vec, self._tfidf_matrix).flatten()

        # Get top-k indices
        top_indices = np.argsort(similarities)[::-1][:top_k]

        results = []
        for idx in top_indices:
            similarity_score = float(similarities[idx])
            if similarity_score > 0.01:  # Filter out near-zero matches
                results.append((self._projects[idx], similarity_score))

        return results


class ProjectAnalyzer:
    """Analyze project data for patterns and insights."""

    def __init__(self, projects: List[SardarProject]):
        self.projects = projects

    def get_budget_range(self, category: str, *args, **kwargs) -> dict:
        """Get estimated budget range for a category based on project complexity."""
        # SardarIT CSV doesn't have budget data, so estimate based on project quality/complexity
        filtered = [p for p in self.projects if p.category.lower() == category.lower()]
        
        # Budget estimates based on technology stack complexity
        budget_estimates = {
            "react / next.js custom": (500, 3000),
            "shopify advanced": (300, 1500),
            "wordpress + woocommerce": (200, 2000),
            "mixed (wordpress + react)": (400, 2500),
            "laravel / custom php": (500, 3000),
            "webflow": (300, 1500),
            "other": (200, 1000),
        }

        # Determine dominant technology in this category
        techs = {}
        for p in filtered:
            tech = p.main_technology.lower()
            techs[tech] = techs.get(tech, 0) + 1

        if techs:
            main_tech = max(techs, key=techs.get)
            est = budget_estimates.get(main_tech, budget_estimates["other"])
        else:
            est = budget_estimates["other"]

        return {
            "min": est[0],
            "max": est[1],
            "average": (est[0] + est[1]) / 2,
            "median": (est[0] + est[1]) / 2,
            "count": len(filtered),
            "low_suggested": est[0],
            "high_suggested": est[1],
        }

    def get_timeline_estimate(self, category: str, budget: float, *args, **kwargs) -> dict:
        """Estimate timeline based on category and budget."""
        # Timeline estimates by project complexity
        timeline_map = {
            "Agency": (7, 21),
            "E-commerce": (10, 30),
            "Education": (10, 25),
            "Healthcare": (7, 21),
            "Portfolio": (5, 14),
            "Real Estate": (7, 21),
            "Restaurant": (7, 14),
            "SaaS": (14, 45),
        }

        base = timeline_map.get(category, (7, 21))
        
        # Scale by budget (higher budget = more time)
        if budget > 0:
            budget_factor = min(2.0, max(0.5, budget / 500))
            estimated = int(base[0] * budget_factor)
        else:
            estimated = base[0]

        return {
            "estimated_days": max(3, estimated),
            "confidence": "high",
            "range": [base[0], base[1]],
            "similar_projects_analyzed": len([p for p in self.projects if p.category == category]),
        }

    def estimate_close_probability(self, project_data: dict) -> float:
        """Estimate probability of closing a deal based on historical patterns."""
        score = 0.5  # base

        # Factor 1: Category has many projects (established market)
        category = project_data.get("category", "")
        cat_projects = [p for p in self.projects if p.category.lower() == category.lower()]
        if len(cat_projects) > 20:
            score += 0.15
        elif len(cat_projects) > 10:
            score += 0.1
        elif len(cat_projects) > 0:
            score += 0.05

        # Factor 2: Message quality (length as proxy)
        message = project_data.get("buyer_message", "")
        if len(message) > 200:
            score += 0.1
        elif len(message) < 50:
            score -= 0.1

        # Factor 3: Timeline reasonableness
        timeline = project_data.get("timeline_days", 0)
        if 2 <= timeline <= 30:
            score += 0.05
        elif timeline < 1:
            score -= 0.1

        return max(0.0, min(1.0, round(score, 2)))
