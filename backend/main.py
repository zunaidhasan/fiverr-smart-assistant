import os
import sys
from typing import Optional, List
from fastapi import FastAPI, UploadFile, File, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

# Ensure the backend directory is in the path for reliable imports
_backend_dir = os.path.dirname(os.path.abspath(__file__))
if _backend_dir not in sys.path:
    sys.path.insert(0, _backend_dir)

from models import (
    SmartReplyRequest, SmartReplyResponse,
    SimilaritySearchRequest, SimilaritySearchResponse,
    ProposalOptimizerRequest, ProposalOptimizerResponse,
    RiskDetectorRequest, RiskDetectorResponse,
    DashboardMetrics, CRMResponse, CSVUploadResponse,
    SardarProject, SituationType,
)
from csv_loader import load_projects, get_categories
from reply_generator import ReplyGenerator
from similarity_search import ProjectSimilaritySearch, ProjectAnalyzer
from risk_detector import RiskDetector
from deal_intelligence import DealIntelligence, ProposalOptimizer

app = FastAPI(
    title="SardarIT Portfolio Intelligence",
    description="Portfolio intelligence system for SardarIT — matches buyer requests to 566+ web development projects in the portfolio database.",
    version="2.0.0",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global state
projects: List[SardarProject] = []
metadata: dict = {}
csv_loaded = False
DEFAULT_CSV = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "sample_data",
    "sardarit_projects_database.csv",
)


def get_projects() -> List[SardarProject]:
    """Get loaded projects or raise error."""
    if not projects:
        raise HTTPException(status_code=400, detail="No CSV data loaded. Please upload a CSV file first.")
    return projects


@app.on_event("startup")
async def startup_event():
    """Load default CSV on startup."""
    global projects, metadata, csv_loaded
    try:
        if os.path.exists(DEFAULT_CSV):
            projects, metadata = load_projects(DEFAULT_CSV)
            csv_loaded = True
            print(f"Loaded {len(projects)} projects from SardarIT database")
        else:
            print(f"Default CSV not found at {DEFAULT_CSV}")
    except Exception as e:
        print(f"Error loading default CSV: {e}")


# --- CSV Routes ---

@app.get("/api/csv/status", response_model=dict)
async def csv_status():
    """Check if CSV data is loaded."""
    return {
        "loaded": csv_loaded,
        "project_count": len(projects),
        "categories": get_categories(projects) if projects else [],
        "total_in_database": metadata.get("total_projects", 0),
        "high_quality": metadata.get("high_quality", 0),
        "top_recommended": metadata.get("top_recommended", [])[:5],
    }


@app.post("/api/csv/upload", response_model=CSVUploadResponse)
async def upload_csv(file: UploadFile = File(...)):
    """Upload a SardarIT project database CSV file."""
    global projects, metadata, csv_loaded

    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Please upload a CSV file.")

    try:
        content = await file.read()
        temp_path = "/tmp/uploaded_projects.csv"
        with open(temp_path, "wb") as f:
            f.write(content)

        projects, metadata = load_projects(temp_path)
        csv_loaded = True
        os.remove(temp_path)

        categories = get_categories(projects)

        return CSVUploadResponse(
            message=f"Successfully loaded {len(projects)} projects from SardarIT database",
            project_count=len(projects),
            categories=categories,
            total_projects_in_database=metadata.get("total_projects", 0),
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error processing CSV: {str(e)}")


# --- Smart Reply Routes ---

@app.post("/api/reply/generate", response_model=SmartReplyResponse)
async def generate_reply(request: SmartReplyRequest):
    """Generate a smart reply for a buyer message."""
    projs = get_projects()
    generator = ReplyGenerator(projs)
    return generator.generate(
        client_message=request.client_message,
        situation_type=request.situation_type,
        category=request.category,
    )


@app.get("/api/reply/templates")
async def list_templates():
    """List all available reply templates."""
    from templates import TEMPLATE_REGISTRY, TONES, SituationType
    return {
        "templates": [
            {
                "name": t.name,
                "situation_type": t.situation_type.value,
                "tone": t.tone,
                "strength": t.strength,
            }
            for t in TEMPLATE_REGISTRY.values()
        ],
        "situation_types": [s.value for s in SituationType],
        "tones": TONES,
    }


@app.post("/api/reply/detect-situation")
async def detect_situation(message: str = Query(..., min_length=1)):
    """Auto-detect situation type from a message."""
    from templates import detect_situation_type
    result = detect_situation_type(message)
    return {"situation_type": result.value}


# --- Similarity Search Routes ---

@app.post("/api/similarity/search", response_model=SimilaritySearchResponse)
async def search_similar(request: SimilaritySearchRequest):
    """Search for similar past projects in the database."""
    projs = get_projects()
    searcher = ProjectSimilaritySearch()
    searcher.fit(projs)
    results = searcher.search(request.client_brief, top_k=request.top_k)

    import re
    def url_to_title(url: str) -> str:
        name = url.replace("https://", "").replace("http://", "").replace("www.", "")
        name = name.split("/")[0]
        name = name.split(".")[0]
        name = re.sub(r'[-_]', ' ', name)
        return name.title()

    similar_projects = []
    for proj, score in results:
        similar_projects.append({
            "project_id": proj.website_url,
            "title": url_to_title(proj.website_url),
            "url": proj.website_url,
            "category": proj.category,
            "technology": proj.main_technology,
            "stack_used": proj.used_stack,
            "description": proj.brief_description,
            "features": proj.website_features,
            "use_case": proj.use_case,
            "strengths": proj.strengths,
            "match_score": proj.match_score_potential,
            "quality": proj.quality,
            "similarity_score": round(score, 3),
        })

    return SimilaritySearchResponse(
        similar_projects=similar_projects,
        query_summary=f"Found {len(similar_projects)} matching projects in the portfolio database",
        total_matches=len(similar_projects),
    )


# --- Proposal Optimizer Routes ---

@app.post("/api/proposal/optimize", response_model=dict)
async def optimize_proposal(request: ProposalOptimizerRequest):
    """Generate proposal optimization recommendations."""
    projs = get_projects()
    optimizer = ProposalOptimizer(projs)
    return optimizer.optimize(
        client_brief=request.client_brief,
        category=request.category,
        budget=request.budget,
    )


# --- Risk Detector Routes ---

@app.post("/api/risk/analyze", response_model=RiskDetectorResponse)
async def analyze_risk(request: RiskDetectorRequest):
    """Analyze a buyer message for risks and red flags."""
    projs = get_projects()
    detector = RiskDetector(projs)
    return detector.analyze(
        buyer_message=request.buyer_message,
        budget=request.budget,
        category=request.category,
    )


# --- Dashboard Routes ---

@app.get("/api/dashboard/metrics", response_model=DashboardMetrics)
async def get_dashboard_metrics():
    """Get dashboard metrics from the portfolio database."""
    projs = get_projects()
    intelligence = DealIntelligence(projs)
    return intelligence.get_dashboard_metrics()


@app.get("/api/crm", response_model=CRMResponse)
async def get_crm_data():
    """Get CRM-style view of the portfolio database."""
    projs = get_projects()
    intelligence = DealIntelligence(projs)
    return intelligence.get_crm_data()


# --- Projects Routes ---

@app.get("/api/projects")
async def list_projects(
    category: Optional[str] = None,
    technology: Optional[str] = None,
    min_match_score: Optional[int] = None,
    limit: int = Query(default=50, le=500),
):
    """List all projects with optional filters."""
    projs = get_projects()

    import re
    def url_to_title(url: str) -> str:
        name = url.replace("https://", "").replace("http://", "").replace("www.", "")
        name = name.split("/")[0]
        name = name.split(".")[0]
        name = re.sub(r'[-_]', ' ', name)
        return name.title()

    filtered = projs
    if category:
        filtered = [p for p in filtered if p.category.lower() == category.lower()]
    if technology:
        filtered = [p for p in filtered if technology.lower() in p.main_technology.lower()]
    if min_match_score is not None:
        filtered = [p for p in filtered if p.match_score_potential >= min_match_score]

    return {
        "projects": [
            {
                "id": p.website_url,
                "title": url_to_title(p.website_url),
                "url": p.website_url,
                "category": p.category,
                "technology": p.main_technology,
                "stack": p.used_stack,
                "features": p.website_features,
                "description": p.brief_description[:150] + "..." if len(p.brief_description) > 150 else p.brief_description,
                "match_score": p.match_score_potential,
                "quality": p.quality,
            }
            for p in filtered[:limit]
        ],
        "total": len(filtered),
        "returned": min(len(filtered), limit),
    }


@app.get("/api/projects/categories")
async def get_project_categories():
    """Get all project categories with stats."""
    projs = get_projects()
    cats = get_categories(projs)
    result = []
    for cat in cats:
        cat_projs = [p for p in projs if p.category == cat]
        result.append({
            "category": cat,
            "count": len(cat_projs),
            "technologies": list(set(p.main_technology for p in cat_projs)),
            "high_quality_count": len([p for p in cat_projs if p.quality.lower() == "high"]),
        })
    return {"categories": result}


# --- Health Check ---

@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "ok",
        "csv_loaded": csv_loaded,
        "project_count": len(projects),
        "database_total": metadata.get("total_projects", 0),
        "version": "2.0.0",
    }


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", "8000"))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
