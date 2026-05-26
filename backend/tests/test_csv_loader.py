"""
Unit tests for the CSV loader module.

Tests parsing of the SardarIT project database CSV format including:
- Metadata extraction from header rows
- Project data row parsing
- Error handling for missing/malformed files
- Helper functions: get_categories, get_technologies, get_features
"""

import os
import tempfile
import pytest

from backend.csv_loader import (
    load_projects,
    get_categories,
    get_technologies,
    get_features,
)
from backend.models import SardarProject


# ---------------------------------------------------------------------------
# load_projects – basic functionality
# ---------------------------------------------------------------------------

class TestLoadProjects:
    """Tests for the main `load_projects` function."""

    def test_loads_all_projects(self, loaded_projects):
        """Should return the expected number of project records."""
        projects, *_ = loaded_projects
        assert len(projects) == 6

    def test_returns_metadata(self, loaded_projects, sample_metadata):
        """Should extract metadata from the header rows."""
        _, metadata, *_ = loaded_projects
        for key in ("total_projects", "high_quality", "medium_quality", "categories", "top_recommended"):
            assert key in metadata, f"Missing metadata key: {key}"
        assert metadata["total_projects"] == sample_metadata["total_projects"]
        assert metadata["high_quality"] == sample_metadata["high_quality"]
        assert metadata["medium_quality"] == sample_metadata["medium_quality"]
        assert "Agency" in metadata["categories"]

    def test_top_recommended_parsed(self, loaded_projects, sample_metadata):
        """Should extract top recommended project descriptions from bullet rows."""
        _, metadata, *_ = loaded_projects
        assert len(metadata["top_recommended"]) > 0
        # Should contain at least the first recommended project
        assert any("Alpha Agency" in r for r in metadata["top_recommended"])

    def test_project_fields_are_correct_type(self, loaded_projects):
        """Each project should be a SardarProject with the right types."""
        projects, *_ = loaded_projects
        proj = projects[0]
        assert isinstance(proj, SardarProject)
        assert isinstance(proj.website_url, str)
        assert isinstance(proj.category, str)
        assert isinstance(proj.used_stack, str)
        assert isinstance(proj.website_features, str)
        assert isinstance(proj.brief_description, str)
        assert isinstance(proj.main_technology, str)
        assert isinstance(proj.quality, str)
        assert isinstance(proj.keywords, str)
        assert isinstance(proj.use_case, str)
        assert isinstance(proj.strengths, str)
        assert isinstance(proj.best_for, str)
        assert isinstance(proj.match_score_potential, int)
        assert isinstance(proj.example_use_case, str)

    def test_project_urls_loaded(self, loaded_projects):
        """Each project should have a non-empty website_url."""
        projects, *_ = loaded_projects
        urls = [p.website_url for p in projects]
        assert all(url for url in urls), "Some projects have empty website_url"
        assert "https://agency-alpha.com" in urls
        assert "https://shopify-store.com" in urls
        assert "https://edu-learn.com" in urls
        assert "https://health-plus.org" in urls
        assert "https://portfolio-dev.com" in urls
        assert "https://realty-pro.com" in urls

    def test_match_score_parsed_correctly(self, loaded_projects):
        """Match_Score_Potential should be parsed as int."""
        projects, *_ = loaded_projects
        scores = {p.website_url: p.match_score_potential for p in projects}
        assert scores["https://agency-alpha.com"] == 95
        assert scores["https://shopify-store.com"] == 92
        assert scores["https://edu-learn.com"] == 88
        assert scores["https://health-plus.org"] == 85
        assert scores["https://portfolio-dev.com"] == 78
        assert scores["https://realty-pro.com"] == 65

    def test_quality_values_preserved(self, loaded_projects):
        """Quality field should be preserved exactly as in CSV."""
        projects, *_ = loaded_projects
        qualities = {p.website_url: p.quality for p in projects}
        assert qualities["https://agency-alpha.com"] == "High"
        assert qualities["https://shopify-store.com"] == "High"
        assert qualities["https://edu-learn.com"] == "Medium"
        assert qualities["https://health-plus.org"] == "High"
        assert qualities["https://portfolio-dev.com"] == "Medium"
        assert qualities["https://realty-pro.com"] == "Low"

    def test_category_values(self, loaded_projects):
        """Category should be correct for each project."""
        projects, *_ = loaded_projects
        cats = {p.website_url: p.category for p in projects}
        assert cats["https://agency-alpha.com"] == "Agency"
        assert cats["https://shopify-store.com"] == "E-commerce"
        assert cats["https://edu-learn.com"] == "Education"
        assert cats["https://health-plus.org"] == "Healthcare"
        assert cats["https://portfolio-dev.com"] == "Portfolio"
        assert cats["https://realty-pro.com"] == "Real Estate"

    def test_fields_with_commas_are_concatenated(self, loaded_projects):
        """Fields like website_features that contain commas should be whole."""
        projects, *_ = loaded_projects
        agency = [p for p in projects if p.website_url == "https://agency-alpha.com"][0]
        # Features should contain both features from the CSV
        assert "Responsive Design" in agency.website_features
        assert "Authentication/Login" in agency.website_features
        assert "Booking System" in agency.website_features

    def test_load_projects_raises_on_missing_file(self):
        """Should raise FileNotFoundError when CSV doesn't exist."""
        with pytest.raises(FileNotFoundError):
            load_projects("/tmp/nonexistent_file.csv")

    def test_load_projects_raises_on_bad_format(self):
        """Should raise ValueError when CSV has no 'Website URL' header."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            f.write("Some,Random,Data\n1,2,3\n")
            bad_path = f.name

        try:
            with pytest.raises(ValueError, match="Could not find header row"):
                load_projects(bad_path)
        finally:
            os.unlink(bad_path)

    def test_handles_empty_project_rows(self):
        """Should skip rows with empty first column."""
        content = (
            'Website URL,Category,Used Stack,Website Features,Brief Description,'
            'Main Technology,Quality,Keywords,Use_Case,Strengths,Best_For,'
            'Match_Score_Potential,Example_Use_Case\n'
            'https://example.com,Agency,"Tech A",Feature A,"A project",Tech,High,'
            'kw,use,str,bf,90,example\n'
            ',,,,\n'
            'https://example2.com,Portfolio,"Tech B",Feature B,"Another project",'
            'Tech2,Medium,kw2,use2,str2,bf2,80,example2\n'
        )
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            f.write(content)
            path = f.name

        try:
            projects, _ = load_projects(path)
            assert len(projects) == 2
        finally:
            os.unlink(path)


# ---------------------------------------------------------------------------
# get_categories
# ---------------------------------------------------------------------------

class TestGetCategories:
    """Tests for the `get_categories` helper."""

    def test_returns_sorted_unique_categories(self, loaded_projects):
        """Should return alphabetically sorted unique categories."""
        projects, _, categories, *_ = loaded_projects
        assert categories == sorted(categories)
        assert "Agency" in categories
        assert "E-commerce" in categories
        assert "Education" in categories
        assert "Healthcare" in categories
        assert "Portfolio" in categories
        assert "Real Estate" in categories
        assert len(categories) == 6

    def test_returns_empty_for_empty_list(self):
        """Should return empty list when projects list is empty."""
        assert get_categories([]) == []

    def test_excludes_empty_category_strings(self):
        """Should exclude projects with empty category."""
        projects = [
            SardarProject(
                website_url="https://a.com",
                category="",
                used_stack="",
                website_features="",
                brief_description="",
                main_technology="",
                quality="",
                keywords="",
                use_case="",
                strengths="",
                best_for="",
                match_score_potential=0,
                example_use_case="",
            ),
            SardarProject(
                website_url="https://b.com",
                category="Agency",
                used_stack="",
                website_features="",
                brief_description="",
                main_technology="",
                quality="",
                keywords="",
                use_case="",
                strengths="",
                best_for="",
                match_score_potential=0,
                example_use_case="",
            ),
        ]
        assert get_categories(projects) == ["Agency"]


# ---------------------------------------------------------------------------
# get_technologies
# ---------------------------------------------------------------------------

class TestGetTechnologies:
    """Tests for the `get_technologies` helper."""

    def test_returns_sorted_unique_technologies(self, loaded_projects):
        """Should return technologies split by comma, sorted."""
        projects, _, _, technologies, *_ = loaded_projects
        assert technologies == sorted(technologies)
        assert "React" in technologies
        assert "Node.js" in technologies
        assert "PostgreSQL" in technologies
        assert "Liquid" in technologies
        assert "Alpine.js" in technologies

    def test_splits_on_plus(self):
        """Should replace ' + ' with ',' so multi-tech fields are split."""
        _, _, _, technologies, *_ = loaded_projects
        # The sample CSV has: "React, Node.js, PostgreSQL" → should be split
        assert "React" in technologies
        assert "Node.js" in technologies
        assert "PostgreSQL" in technologies
        # Technologies that don't contain commas or ' + ' should stay intact
        assert "React / Next.js Custom" in technologies

    def test_returns_empty_for_no_technology(self):
        """Should return empty list when no projects have main_technology."""
        projects = [
            SardarProject(
                website_url="https://a.com",
                category="Agency",
                used_stack="",
                website_features="",
                brief_description="",
                main_technology="",
                quality="",
                keywords="",
                use_case="",
                strengths="",
                best_for="",
                match_score_potential=0,
                example_use_case="",
            ),
        ]
        assert get_technologies(projects) == []

    def test_deduplicates_technologies(self):
        """Should not include duplicate technologies."""
        projects = [
            SardarProject(
                website_url="https://a.com",
                category="Agency",
                used_stack="",
                website_features="",
                brief_description="",
                main_technology="React, Node.js",
                quality="",
                keywords="",
                use_case="",
                strengths="",
                best_for="",
                match_score_potential=0,
                example_use_case="",
            ),
            SardarProject(
                website_url="https://b.com",
                category="Portfolio",
                used_stack="",
                website_features="",
                brief_description="",
                main_technology="React, TypeScript",
                quality="",
                keywords="",
                use_case="",
                strengths="",
                best_for="",
                match_score_potential=0,
                example_use_case="",
            ),
        ]
        techs = get_technologies(projects)
        assert techs == sorted(["React", "Node.js", "TypeScript"])


# ---------------------------------------------------------------------------
# get_features
# ---------------------------------------------------------------------------

class TestGetFeatures:
    """Tests for the `get_features` helper."""

    def test_returns_sorted_unique_features(self, loaded_projects):
        """Should return unique features sorted alphabetically."""
        projects, _, _, _, features = loaded_projects
        assert features == sorted(features)
        assert "Responsive Design" in features
        assert "Authentication/Login" in features
        assert "Booking System" in features
        assert "Shopping Cart" in features
        assert "Payment Integration" in features
        assert "SEO Optimization" in features
        assert "Video Streaming" in features
        assert "Quiz System" in features
        assert "Appointment Booking" in features
        assert "Patient Portal" in features
        assert "Animations" in features
        assert "Contact Form" in features
        assert "Property Search" in features
        assert "Map Integration" in features
        assert "Agent Profiles" in features

    def test_returns_empty_for_no_features(self):
        """Should return empty list when no projects have features."""
        projects = [
            SardarProject(
                website_url="https://a.com",
                category="Agency",
                used_stack="",
                website_features="",
                brief_description="",
                main_technology="",
                quality="",
                keywords="",
                use_case="",
                strengths="",
                best_for="",
                match_score_potential=0,
                example_use_case="",
            ),
        ]
        assert get_features(projects) == []

    def test_strips_whitespace(self):
        """Should strip whitespace from individual features."""
        projects = [
            SardarProject(
                website_url="https://a.com",
                category="Agency",
                used_stack="",
                website_features="  Feature A , Feature B , Feature C  ",
                brief_description="",
                main_technology="",
                quality="",
                keywords="",
                use_case="",
                strengths="",
                best_for="",
                match_score_potential=0,
                example_use_case="",
            ),
        ]
        features = get_features(projects)
        assert "Feature A" in features
        assert "Feature B" in features
        assert "Feature C" in features
