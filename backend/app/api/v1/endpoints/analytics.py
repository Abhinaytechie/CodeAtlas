from typing import List, Any
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from app.core.database import get_db
from datetime import datetime
from app.api.v1 import deps

router = APIRouter()

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

@router.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive, listen for client messages if any
            data = await websocket.receive_text()
            # Echo back or process
            # await manager.broadcast(f"User {user_id} says: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@router.get("/kpis")
def get_kpis(
    db: Any = Depends(get_db),
    current_user: dict = Depends(deps.get_current_user)
) -> Any:
    """
    Get high-level KPIs for the analytics dashboard
    """
    user_id = str(current_user["_id"])
    user = db.user_stats.find_one({"user_id": user_id})
    if not user:
        # Return empty stats if no stats record exists yet
        return {
            "mastery_score": 0,
            "skills_mastered": 0,
            "streak": 0,
            "interview_readiness": "N/A"
        }
    
    # Calculate Mastery
    solved_count = len(user.get("solved_problems", []))
    streak = user.get("streak_days", 0)
    
    # Calculate Interview Scores
    sessions = list(db.interview_sessions.find({"user_id": user_id, "status": "completed"}))
    avg_score = 0
    if sessions:
        # Assuming we store score in session (we need to ensure this happens in /end)
        scores = [s.get("score", 0) for s in sessions if "score" in s]
        if scores:
            avg_score = sum(scores) / len(scores)
            
    return {
        "mastery_score": solved_count * 10, # Dummy XP logic
        "skills_mastered": solved_count,
        "streak": streak,
        "interview_readiness": round(avg_score, 1) or "N/A"
    }

@router.get("/skills")
def get_skill_distribution(
    db: Any = Depends(get_db),
    current_user: dict = Depends(deps.get_current_user)
) -> Any:
    """
    Get skill breakdown (e.g. by Track)
    """
    # In a real app, we would join this with the Roadmap definition
    # For now, we return dummy distribution based on counts
    return [
        {"name": "DSA", "value": 45, "fill": "#8884d8"},
        {"name": "System Design", "value": 25, "fill": "#82ca9d"},
        {"name": "Behavioral", "value": 10, "fill": "#ffc658"},
        {"name": "Projects", "value": 20, "fill": "#ff8042"}
    ]

@router.get("/interviews")
def get_interview_trends(
    db: Any = Depends(get_db),
    current_user: dict = Depends(deps.get_current_user)
) -> Any:
    """
    Get recent interview performance trend
    """
    user_id = str(current_user["_id"])
    
    sessions = list(db.interview_sessions.find({"user_id": user_id}).sort("created_at", 1).limit(10))
    data = []
    for s in sessions:
        # Calculate approximate score based on feedback or dummy logic if missing
        # For now, generate a random-ish score if missing based on turns count
        score = s.get("score", 60 + (len(s.get("turns", [])) * 2)) 
        score = min(score, 100)
        data.append({
            "date": s.get("created_at", datetime.now()).strftime("%b %d"),
            "score": score
        })
    
    if not data:
        return [
           {"date": "No Data", "score": 0}
        ]
    return data

@router.get("/feedback")
def get_recent_feedback(
    db: Any = Depends(get_db),
    current_user: dict = Depends(deps.get_current_user)
) -> Any:
    """
    Get aggregated feedback from recent sessions.
    """
    user_id = str(current_user["_id"])
    
    # Get last 3 sessions
    sessions = list(db.interview_sessions.find({"user_id": user_id}).sort("created_at", -1).limit(3))
    
    feedback_items = []
    for s in sessions:
        for turn in s.get("turns", []):
            if turn.get("role") == "assistant" and turn.get("feedback_snapshot"):
                # Clean up feedback string
                fb = turn["feedback_snapshot"].strip()
                if len(fb) > 5 and fb not in feedback_items:
                    feedback_items.append(fb)
    
    # Return top 5 unique feedback items
    return feedback_items[:5]
