from fastapi import APIRouter
from app.api.v1.endpoints import auth, roadmap, dashboard, interview, users, analytics, vault, project

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(roadmap.router, prefix="/roadmap", tags=["roadmap"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
api_router.include_router(interview.router, prefix="/interview", tags=["interview"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
api_router.include_router(vault.router, prefix="/vault", tags=["vault"])
api_router.include_router(project.router, prefix="/project", tags=["project"])
