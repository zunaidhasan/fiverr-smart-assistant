"""
Unit tests for the similarity search and project analysis module.

Tests cover:
- ProjectSimilaritySearch: fitting, searching, edge cases
- ProjectAnalyzer: budget range, timeline estimation, close probability
"""

import pytest
from backend.similarity_search import ProjectSimilaritySearch, ProjectAnalyzer
from backend.models import SardarProject


# ---------------------------------------------------------------------------
# Helper – build a list of SardarProject objects for tests
# ---------------------------------------------------------------------------

def make_project(
    url: str = "https://example.com",
    category: str = "Agency",
    used_stack: str = "React, Node.js",
    features: str = "Responsive Design",
    description: str = "A web development project",
    technology: str = "React / Next.js Custom",
    quality: str = "High",
    keywords: str = "web, development",
    use_case: str = "Build a website",
    strengths: str = "Fast and reliable",
    best_for: str = "Agencies",
    match_score: int = 85,
    example_use_case: str = "Used by a marketing agency",
) -> SardarProject:
    return SardarProject(
        website_url=url,
        category=category,
        used_stack=used_stack,
        website_features=features,
        brief_description=description,
        main_technology=technology,
        quality=quality,
        keywords=keywords,
        use_case=use_case,
        strengths=strengths,
        best_for=best_for,
        match_score_potential=match_score,
        example_use_case=example_use_case,
    )


SAMPLE_PROJECTS = [
    make_project(
        url="https://agency-alpha.com",
        category="Agency",
        description="Full-service digital agency with booking and responsive design",
        keywords="agency, digital, services",
        use_case="Showcase agency services online",
        strengths="Modern UI, SEO, performance",
    ),
    make_project(
        url="https://shopify-store.com",
        category="E-commerce",
        description="Shopify e-commerce store with cart and payment integration",
        keywords="ecommerce, shopify, store",
        use_case="Sell products online",
        strengths="Cart, checkout, mobile-friendly",
    ),
    make_project(
        url="https://edu-learn.com",
        category="Education",
        description="Online learning platform with video streaming and quizzes",
        keywords="education, lms, learning",
        use_case="Deliver online courses",
        strengths="Scalable, interactive, user management",
    ),
    make_project(
        url="https://health-plus.org",
        category="Healthcare",
        description="Healthcare booking and patient portal",
        keywords="healthcare, medical, booking",
        use_case="Manage patient appointments",
        strengths="HIPAA-ready, booking system",
    ),
    make_project(
        url="https://portfolio-dev.com",
        category="Portfolio",
        description="Developer portfolio with animations and contact form",
        keywords="portfolio, developer, freelance",
        use_case="Showcase development work",
        strengths="Animations, clean design, fast",
    ),
]


# ---------------------------------------------------------------------------
# ProjectSimilaritySearch – fitting
# ---------------------------------------------------------------------------

class TestProjectSimilaritySearchFit:
    """Tests for the `fit` method."""

    def test_fit_with_projects(self):
        """fit() should process documents and mark the searcher as fitted."""
        searcher = ProjectSimilaritySearch()
        searcher.fit(SAMPLE_PROJECTS)
        assert searcher._fitted is True
        assert searcher._tfidf_matrix is not None
        assert searcher._tfidf_matrix.shape[0] == len(SAMPLE_PROJECTS)

    def test_fit_with_empty_list(self):
        """fit() with an empty list should not crash and stay unfitted."""
        searcher = ProjectSimilaritySearch()
        searcher.fit([])
        assert searcher._fitted is False
        assert searcher._tfidf_matrix is None

    def test_fit_with_single_project(self):
        """fit() should work with a single project."""
        searcher = ProjectSimilaritySearch()
        searcher.fit([SAMPLE_PROJECTS[0]])
        assert searcher._fitted is True
        assert searcher._tfidf_matrix.shape[0] == 1

    def test_fit_document_content_includes_key_fields(self):
        """The document vector should combine description, keywords, use_case, strengths, category, and used_stack."""
        # We can't easily introspect the vectorizer, but we can verify the
        # search works after fitting, which validates the document was built.
        searcher = ProjectSimilaritySearch()
        searcher.fit(SAMPLE_PROJECTS)
        results = searcher.search("agency digital services", top_k=1)
        assert len(results) > 0
        # The most relevant project should be the agency one
        assert results[0][0].website_url == "https://agency-alpha.com"


# ---------------------------------------------------------------------------
# ProjectSimilaritySearch – searching
# ---------------------------------------------------------------------------

class TestProjectSimilaritySearchSearch:
    """Tests for the `search` method."""

    def test_search_returns_results(self):
        """search() should return a list of (project, score) tuples."""
        searcher = ProjectSimilaritySearch()
        searcher.fit(SAMPLE_PROJECTS)
        results = searcher.search("e-commerce store with cart", top_k=3)
        assert len(results) > 0
        assert len(results) <= 3
        assert all(isinstance(r[0], SardarProject) for r in results)
        assert all(isinstance(r[1], float) for r in results)

    def test_search_respects_top_k(self):
        """search() should return at most top_k results."""
        searcher = ProjectSimilaritySearch()
        searcher.fit(SAMPLE_PROJECTS)
        for k in [1, 2, 3, 5]:
            results = searcher.search("web development", top_k=k)
            assert len(results) <= k, f"Expected ≤{k} results, got {len(results)}"

    def test_search_returns_nothing_if_not_fitted(self):
        """search() on an unfitted searcher should return empty list."""
        searcher = ProjectSimilaritySearch()
        results = searcher.search("anything")
        assert results == []

    def test_search_with_empty_query_does_not_crash(self):
        """search() with an empty query string should not crash."""
        searcher = ProjectSimilaritySearch()
        searcher.fit(SAMPLE_PROJECTS)
        results = searcher.search("")
        assert isinstance(results, list)

    def test_search_orders_by_similarity_descending(self):
        """Results should be ordered from most similar to least similar."""
        searcher = ProjectSimilaritySearch()
        searcher.fit(SAMPLE_PROJECTS)
        results = searcher.search("e-commerce online store sell products", top_k=5)
        scores = [score for _, score in results]
        assert scores == sorted(scores, reverse=True), (
            f"Scores not descending: {scores}"
        )

    def test_search_relevant_project_comes_first(self):
        """The most relevant project for a given query should rank first."""
        searcher = ProjectSimilaritySearch()
        searcher.fit(SAMPLE_PROJECTS)
        results = searcher.search("online courses video learning education", top_k=5)
        if results:
            assert results[0][0].website_url == "https://edu-learn.com"

    def test_search_agency_query(self):
        """Agency-related query should rank the agency project highest."""
        searcher = ProjectSimilaritySearch()
        searcher.fit(SAMPLE_PROJECTS)
        results = searcher.search("agency services digital marketing", top_k=5)
        if results:
            assert results[0][0].website_url == "https://agency-alpha.com"

    def test_search_healthcare_query(self):
        """Healthcare-related query should rank the healthcare project highest."""
        searcher = ProjectSimilaritySearch()
        searcher.fit(SAMPLE_PROJECTS)
        results = searcher.search("patient appointment booking healthcare", top_k=5)
        if results:
            assert results[0][0].website_url == "https://health-plus.org"

    def test_search_with_unrelated_query_filters_low_scores(self):
        """An unrelated query should return 0 results (scores below 0.01 threshold)."""
        searcher = ProjectSimilaritySearch()
        searcher.fit(SAMPLE_PROJECTS)
        results = searcher.search("quantum physics space exploration", top_k=5)
        assert len(results) == 0, f"Expected 0 results for unrelated query, got {len(results)}"


# ---------------------------------------------------------------------------
# ProjectAnalyzer – get_budget_range
# ---------------------------------------------------------------------------

class TestProjectAnalyzerGetBudgetRange:
    """Tests for the `get_budget_range` method."""

    def test_returns_dict_with_expected_keys(self):
        """Should return a dictionary with min, max, average, etc."""
        analyzer = ProjectAnalyzer(SAMPLE_PROJECTS)
        result = analyzer.get_budget_range("Agency")
        expected_keys = {"min", "max", "average", "median", "count", "low_suggested", "high_suggested"}
        assert expected_keys.issubset(result.keys()), f"Missing keys: {expected_keys - result.keys()}"

    def test_returns_valid_numbers(self):
        """min should be <= max, both should be positive."""
        analyzer = ProjectAnalyzer(SAMPLE_PROJECTS)
        result = analyzer.get_budget_range("E-commerce")
        assert result["min"] > 0
        assert result["max"] > 0
        assert result["min"] <= result["max"]
        assert result["average"] >= result["min"]

    def test_category_with_known_technology(self):
        """Should use the budget estimate for the dominant technology."""
        analyzer = ProjectAnalyzer(SAMPLE_PROJECTS)
        # Agency projects use "React / Next.js Custom" → (500, 3000)
        result = analyzer.get_budget_range("Agency")
        assert result["min"] == 500
        assert result["max"] == 3000

    def test_category_with_different_technology(self):
        """E-commerce projects use "Shopify Advanced" → (300, 1500)."""
        analyzer = ProjectAnalyzer(SAMPLE_PROJECTS)
        result = analyzer.get_budget_range("E-commerce")
        assert result["min"] == 300
        assert result["max"] == 1500

    def test_unknown_category_uses_fallback(self):
        """Unknown categories should fall back to 'other' → (200, 1000)."""
        analyzer = ProjectAnalyzer(SAMPLE_PROJECTS)
        result = analyzer.get_budget_range("Unknown Category")
        assert result["min"] == 200
        assert result["max"] == 1000

    def test_count_reflects_projects_in_category(self):
        """count should be the number of projects in that category."""
        analyzer = ProjectAnalyzer(SAMPLE_PROJECTS)
        result = analyzer.get_budget_range("Agency")
        assert result["count"] == 1  # Only one agency project in fixtures
        result2 = analyzer.get_budget_range("Healthcare")
        assert result2["count"] == 1

    def test_case_insensitive_category_matching(self):
        """Category matching should be case-insensitive."""
        analyzer = ProjectAnalyzer(SAMPLE_PROJECTS)
        r1 = analyzer.get_budget_range("agency")
        r2 = analyzer.get_budget_range("AGENCY")
        r3 = analyzer.get_budget_range("Agency")
        assert r1["count"] == r2["count"] == r3["count"]


# ---------------------------------------------------------------------------
# ProjectAnalyzer – get_timeline_estimate
# ---------------------------------------------------------------------------

class TestProjectAnalyzerGetTimelineEstimate:
    """Tests for the `get_timeline_estimate` method."""

    def test_returns_dict_with_expected_keys(self):
        """Should return dict with estimated_days, confidence, range, similar_projects_analyzed."""
        analyzer = ProjectAnalyzer(SAMPLE_PROJECTS)
        result = analyzer.get_timeline_estimate("Agency", 1000)
        expected_keys = {"estimated_days", "confidence", "range", "similar_projects_analyzed"}
        assert expected_keys.issubset(result.keys())

    def test_returns_positive_days(self):
        """estimated_days should be at least 3."""
        analyzer = ProjectAnalyzer(SAMPLE_PROJECTS)
        result = analyzer.get_timeline_estimate("Portfolio", 100)
        assert result["estimated_days"] >= 3

    def test_higher_budget_increases_timeline(self):
        """A higher budget should scale the timeline up."""
        analyzer = ProjectAnalyzer(SAMPLE_PROJECTS)
        low_budget = analyzer.get_timeline_estimate("Agency", 200)
        high_budget = analyzer.get_timeline_estimate("Agency", 5000)
        assert high_budget["estimated_days"] >= low_budget["estimated_days"]

    def test_education_category_timeline(self):
        """Education category should use (10, 25) as base range."""
        analyzer = ProjectAnalyzer(SAMPLE_PROJECTS)
        result = analyzer.get_timeline_estimate("Education", 1000)
        assert result["range"] == [10, 25]

    def test_saas_category_timeline(self):
        """SaaS category should use (14, 45) as base range."""
        analyzer = ProjectAnalyzer(SAMPLE_PROJECTS)
        result = analyzer.get_timeline_estimate("SaaS", 2000)
        assert result["range"] == [14, 45]

    def test_unknown_category_falls_back(self):
        """Unknown categories should use the default (7, 21)."""
        analyzer = ProjectAnalyzer(SAMPLE_PROJECTS)
        result = analyzer.get_timeline_estimate("Unknown", 500)
        assert result["range"] == [7, 21]

    def test_similar_projects_analyzed_count(self):
        """similar_projects_analyzed should count projects in that category."""
        analyzer = ProjectAnalyzer(SAMPLE_PROJECTS)
        result = analyzer.get_timeline_estimate("Portfolio", 500)
        assert result["similar_projects_analyzed"] == 1


# ---------------------------------------------------------------------------
# ProjectAnalyzer – estimate_close_probability
# ---------------------------------------------------------------------------

class TestProjectAnalyzerEstimateCloseProbability:
    """Tests for the `estimate_close_probability` method."""

    def test_returns_float_between_0_and_1(self):
        """Should return a float between 0.0 and 1.0."""
        analyzer = ProjectAnalyzer(SAMPLE_PROJECTS)
        prob = analyzer.estimate_close_probability({"category": "Agency", "buyer_message": "I need a website with many features and specific requirements that I've detailed extensively", "timeline_days": 14})
        assert 0.0 <= prob <= 1.0

    def test_high_quality_message_increases_probability(self):
        """A detailed message should increase close probability."""
        analyzer = ProjectAnalyzer(SAMPLE_PROJECTS)
        long_msg = "I need a comprehensive website that includes a booking system, payment integration, user authentication, and a content management system. I have detailed wireframes and a clear vision for the project."
        short_msg = "Need website"
        prob_long = analyzer.estimate_close_probability({"category": "Agency", "buyer_message": long_msg, "timeline_days": 14})
        prob_short = analyzer.estimate_close_probability({"category": "Agency", "buyer_message": short_msg, "timeline_days": 14})
        assert prob_long >= prob_short

    def test_well_established_category_boosts_score(self):
        """A category with many projects should add to the base score."""
        # Add enough projects to the same category to trigger the boost
        many_projects = SAMPLE_PROJECTS + [
            make_project(url=f"https://extra{i}.com", category="Agency")
            for i in range(20)
        ]
        analyzer = ProjectAnalyzer(many_projects)
        prob = analyzer.estimate_close_probability({"category": "Agency", "buyer_message": "Detailed message about a project", "timeline_days": 14})
        # Base is 0.5, category with >20 projects adds 0.15, message >200 chars adds 0.1 = 0.75
        assert prob >= 0.7

    def test_very_short_message_reduces_probability(self):
        """A very short message (<50 chars) should reduce probability."""
        analyzer = ProjectAnalyzer(SAMPLE_PROJECTS)
        prob = analyzer.estimate_close_probability({"category": "Portfolio", "buyer_message": "Short", "timeline_days": 14})
        # Base 0.5, short msg subtracts 0.1 = 0.4
        assert prob <= 0.5

    def test_unreasonable_timeline_reduces_probability(self):
        """Timeline < 1 day should reduce close probability."""
        analyzer = ProjectAnalyzer(SAMPLE_PROJECTS)
        prob = analyzer.estimate_close_probability({"category": "Agency", "buyer_message": "Detailed message with enough characters to pass the threshold for a good quality message that provides specific requirements.", "timeline_days": 0})
        # Base 0.5, timeline < 1 subtracts 0.1 = 0.4
        assert prob <= 0.5

    def test_reasonable_timeline_boosts(self):
        """Timeline between 2 and 30 days should add a small boost."""
        analyzer = ProjectAnalyzer(SAMPLE_PROJECTS)
        prob = analyzer.estimate_close_probability({"category": "Agency", "buyer_message": "Detailed message about building a comprehensive website with multiple features and specific technical requirements.", "timeline_days": 14})
        assert prob >= 0.5

    def test_no_category_match(self):
        """A category with zero projects should not add anything (base stays 0.5)."""
        analyzer = ProjectAnalyzer(SAMPLE_PROJECTS)
        prob = analyzer.estimate_close_probability({"category": "AbsolutelyUnknownCategory", "buyer_message": "Brief", "timeline_days": 0})
        # Base 0.5, short msg -0.1, bad timeline -0.1 = 0.3
        assert prob == 0.3
