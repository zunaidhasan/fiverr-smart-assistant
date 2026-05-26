from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date
from enum import Enum


class PageCategory(str, Enum):
    AGENCY = "Agency"
    ECOMMERCE = "E-commerce"
    EDUCATION = "Education"
    HEALTHCARE = "Healthcare"
    PORTFOLIO = "Portfolio"
    REAL_ESTATE = "Real Estate"
    RESTAURANT = "Restaurant"
    SAAS = "SaaS"
    BLOG = "Blog/News"
    OTHER = "Other"


class SardarProject(BaseModel):
    """A project from the SardarIT web development portfolio database."""
    website_url: str
    category: str
    used_stack: str
    website_features: str
    brief_description: str
    main_technology: str
    quality: str
    keywords: str
    use_case: str
    strengths: str
    best_for: str
    match_score_potential: int
    example_use_case: str


class SituationType(str, Enum):
    TECHNICAL_PROJECT = "technical_project"
    CREATIVE_PROJECT = "creative_project"
    URGENT_FIX = "urgent_fix"
    DATA_ENTRY = "data_entry"
    CONSULTING = "consulting"
    ONGOING_SUPPORT = "ongoing_support"
    GENERAL = "general"


class CSVUploadResponse(BaseModel):
    message: str
    project_count: int
    categories: List[str]
    total_projects_in_database: int = 0


# --- Request / Response Models ---

class SmartReplyRequest(BaseModel):
    client_message: str
    situation_type: Optional[SituationType] = None
    category: Optional[str] = None


class SmartReplyResponse(BaseModel):
    draft_reply: str
    relevant_past_projects: List[dict]
    suggested_tone: str
    questions_to_ask: List[str]
    estimated_quote_range: dict
    confidence_score: float


class SimilaritySearchRequest(BaseModel):
    client_brief: str
    top_k: int = 5


class SimilaritySearchResponse(BaseModel):
    similar_projects: List[dict]
    query_summary: str
    total_matches: int = 0


class ProposalOptimizerRequest(BaseModel):
    client_brief: str
    category: Optional[str] = None
    budget: Optional[float] = None


class ProposalOptimizerResponse(BaseModel):
    portfolio_examples: List[dict]
    relevant_experience: List[str]
    risk_signals: List[str]
    questions_to_ask: List[str]
    recommended_structure: List[str]
    suggested_quote_range: dict
    estimated_timeline: str


class RiskDetectorRequest(BaseModel):
    buyer_message: str
    budget: Optional[float] = None
    category: Optional[str] = None


class RiskDetectorResponse(BaseModel):
    risk_score: float
    red_flags: List[dict]
    scope_creep_probability: float
    vague_requirements: bool
    urgency_signals: bool
    budget_mismatch: Optional[dict] = None
    recommendations: List[str]


class DashboardMetrics(BaseModel):
    total_projects: int
    categories: List[str]
    projects_by_category: List[dict]
    technology_distribution: List[dict]
    feature_popularity: List[dict]
    best_paying_niches: List[dict]
    quality_distribution: List[dict]
    match_score_distribution: List[dict]


class CRMEntry(BaseModel):
    id: str
    project_url: str
    category: str
    main_technology: str
    use_case: str
    best_for: str
    match_score: int
    keywords: str
    strengths: str
    risk_flags: List[str] = []


class CRMResponse(BaseModel):
    entries: List[CRMEntry]
    total_count: int
    categories: List[str]
    technology_diversity: int
