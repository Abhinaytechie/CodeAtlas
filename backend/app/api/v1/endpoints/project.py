from typing import Any
from fastapi import APIRouter, Depends, HTTPException, Body, Header
from app.core.database import get_db
from app.services.project_intelligence import project_intelligence_service

router = APIRouter()

@router.post("/visualize")
async def project_visualize(
    body: dict = Body(...),
    x_groq_api_key: str | None = Header(default=None, alias="x-groq-api-key"),
    db: Any = Depends(get_db)
) -> Any:
    """
    Step 1: Get Mermaid Graph Data.
    """
    repo_url = body.get("repo_url")
    if not repo_url:
        raise HTTPException(status_code=400, detail="Repo URL is required")
        
    try:
        result = await project_intelligence_service.analyze_project_structure(repo_url, x_groq_api_key)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/docs")
async def project_docs(
    body: dict = Body(...),
    x_groq_api_key: str | None = Header(default=None, alias="x-groq-api-key"),
    db: Any = Depends(get_db)
) -> Any:
    """
    Step 2: Generate README & API Specs.
    """
    job_id = body.get("job_id")
    if not job_id:
        raise HTTPException(status_code=400, detail="Job ID required (from visualize step)")
        
    try:
        result = await project_intelligence_service.generate_docs(job_id, x_groq_api_key)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
