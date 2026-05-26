"""
Shared pytest fixtures for backend tests.

IMPORTANT: Run tests from the project root so the package hierarchy is preserved.
  cd freelancer-assistant
  python -m pytest backend/tests/ -v

Or set PYTHONPATH to include the project root:
  set PYTHONPATH=%CD%
  py -m pytest backend/tests/ -v
"""

import os
import sys
import pytest

# Add the project root (freelancer-assistant/) to sys.path so that
# "from backend.csv_loader import ..." works and relative imports
# inside backend/ modules resolve correctly.
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

FIXTURES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fixtures")
SAMPLE_CSV = os.path.join(FIXTURES_DIR, "sample_projects.csv")


@pytest.fixture
def sample_csv_path() -> str:
    """Path to the sample projects CSV fixture."""
    return SAMPLE_CSV


@pytest.fixture
def sample_metadata() -> dict:
    """Expected metadata from the sample CSV."""
    return {
        "total_projects": 6,
        "high_quality": 3,
        "medium_quality": 2,
        "categories": ["Agency", "E-commerce", "Education"],
        "top_recommended": [
            "Alpha Agency | Score: 95",
            "Shopify Store | Score: 92",
            "Edu Learn Platform | Score: 88",
        ],
    }


@pytest.fixture
def loaded_projects(sample_csv_path):
    """Load projects from the sample CSV using the actual loader.
    Returns (projects, metadata, categories, technologies, features)."""
    from backend.csv_loader import load_projects, get_categories, get_technologies, get_features
    projects, metadata = load_projects(sample_csv_path)
    return (
        projects,
        metadata,
        get_categories(projects),
        get_technologies(projects),
        get_features(projects),
    )


@pytest.fixture
def loaded_projects_only(loaded_projects):
    """Just the parsed project list."""
    return loaded_projects[0]


@pytest.fixture
def loaded_metadata_only(loaded_projects):
    """Just the metadata dict."""
    return loaded_projects[1]


@pytest.fixture
def loaded_categories_only(loaded_projects):
    """Just the categories list."""
    return loaded_projects[2]
