import csv
import os
from typing import List, Tuple
from .models import SardarProject


def load_projects(csv_path: str) -> Tuple[List[SardarProject], dict]:
    """
    Load projects from the SardarIT projects database CSV.
    
    The CSV has the following structure:
    - Rows 1-8: Metadata (total projects, quality breakdown, top recommendations)
    - Row 9: Column headers
    - Rows 10+: Project data
    
    Returns:
        Tuple of (list of SardarProject objects, metadata dict)
    """
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"CSV file not found: {csv_path}")

    projects = []
    metadata = {
        "total_projects": 0,
        "high_quality": 0,
        "medium_quality": 0,
        "categories": [],
        "top_recommended": [],
    }

    with open(csv_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Parse metadata from the header section
    lines = content.split("\n")
    
    # Extract metadata
    for i, line in enumerate(lines[:10]):
        cols = list(csv.reader([line]))[0] if line.strip() else []
        
        if "Total Projects in Database" in line and len(cols) > 2:
            try:
                metadata["total_projects"] = int(cols[2].strip())
            except (ValueError, IndexError):
                pass
        
        if "High Quality Projects" in line and len(cols) > 2:
            try:
                metadata["high_quality"] = int(cols[2].strip())
            except (ValueError, IndexError):
                pass
        
        if "Medium Quality" in line and len(cols) > 2:
            try:
                metadata["medium_quality"] = int(cols[2].strip())
            except (ValueError, IndexError):
                pass
        
        if "Strongest Categories" in line and len(cols) > 3:
            metadata["categories"] = [c.strip() for c in cols[3].split(",")]
        
        if "Top Recommended Projects" in line and len(cols) > 3:
            # This is a multi-line section - parse the next lines
            top_recs = []
            for j in range(i + 1, min(i + 15, len(lines))):
                rec_line = lines[j].strip()
                if rec_line.startswith('"•'):
                    # Extract project name and score from format:
                    # "• https://url.com/  [Title  |  Score: X]"
                    import re
                    match = re.search(r'\[([^\]]+)\]', rec_line)
                    if match:
                        top_recs.append(match.group(1).strip())
            metadata["top_recommended"] = top_recs

    # Parse the CSV data section - find the header row
    reader = csv.reader(content.split("\n"))
    all_rows = list(reader)
    
    # Find the header row (starts with "Website URL")
    header_idx = -1
    for i, row in enumerate(all_rows):
        if row and row[0].strip() == "Website URL":
            header_idx = i
            break

    if header_idx == -1:
        raise ValueError("Could not find header row starting with 'Website URL'")

    headers = all_rows[header_idx]
    # Map column names to indices
    col_map = {h.strip(): idx for idx, h in enumerate(headers)}

    required_cols = ["Website URL", "Category", "Used Stack", "Brief Description"]
    for col in required_cols:
        if col not in col_map:
            raise ValueError(f"Required column '{col}' not found in CSV")

    # Parse project rows
    for row in all_rows[header_idx + 1:]:
        if not row or not row[0].strip():
            continue
        if len(row) < len(headers):
            # Pad short rows
            row = row + [""] * (len(headers) - len(row))

        try:
            # Extract fields with safe get
            def get_col(name):
                idx = col_map.get(name)
                return row[idx].strip() if idx is not None and idx < len(row) else ""

            url = get_col("Website URL")
            if not url:
                continue

            match_score_str = get_col("Match_Score_Potential")
            try:
                match_score = int(match_score_str) if match_score_str else 0
            except ValueError:
                match_score = 0

            project = SardarProject(
                website_url=url,
                category=get_col("Category") or "Other",
                used_stack=get_col("Used Stack") or "",
                website_features=get_col("Website Features") or "",
                brief_description=get_col("Brief Description") or "",
                main_technology=get_col("Main Technology") or "",
                quality=get_col("Quality") or "",
                keywords=get_col("Keywords") or "",
                use_case=get_col("Use_Case") or "",
                strengths=get_col("Strengths") or "",
                best_for=get_col("Best_For") or "",
                match_score_potential=match_score,
                example_use_case=get_col("Example_Use_Case") or "",
            )
            projects.append(project)
        except Exception as e:
            print(f"Warning: Skipping row: {e}")
            continue

    if "categories" not in metadata or not metadata["categories"]:
        metadata["categories"] = list(set(p.category for p in projects))

    return projects, metadata


def get_categories(projects: List[SardarProject]) -> List[str]:
    """Get unique categories from projects."""
    return sorted(list(set(p.category for p in projects if p.category)))


def get_technologies(projects: List[SardarProject]) -> List[str]:
    """Get unique main technologies from projects."""
    techs = set()
    for p in projects:
        if p.main_technology:
            # Split by "/" or "," to get individual techs
            parts = p.main_technology.replace(" + ", ",").split(",")
            for part in parts:
                t = part.strip()
                if t:
                    techs.add(t)
    return sorted(techs)


def get_features(projects: List[SardarProject]) -> List[str]:
    """Extract all unique website features mentioned in projects."""
    features = set()
    for p in projects:
        if p.website_features:
            # Features are comma-separated
            for f in p.website_features.split(","):
                f = f.strip()
                if f:
                    features.add(f)
    return sorted(features)
