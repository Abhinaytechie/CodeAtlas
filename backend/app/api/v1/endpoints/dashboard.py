from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from app.core.database import get_db
from app.core.content import QUESTION_BANK
from datetime import datetime, timedelta

# For now, we manually get the user assuming we are authenticated.
# In a real app, we'd use dependencies.get_current_user

router = APIRouter()

@router.get("/stats")
def get_user_stats(
    db: Any = Depends(get_db),
) -> Any:
    """
    Get real-time user statistics with detailed breakdown.
    """
    # Hack for demo: Get last created user stat
    user_stat = db.user_stats.find_one(sort=[("_id", -1)])
    
    if not user_stat:
        # Fallback
        return {
            "problems_solved": 0,
            "total_problems": len(QUESTION_BANK),
            "streak_days": 0,
            "weak_pattern": "None",
            "solved_problems": [],
            "stats_by_difficulty": {"Easy": 0, "Medium": 0, "Hard": 0},
            "next_problems": []
        }
        
    solved_ids = user_stat.get("solved_problems", [])
    
    # Calculate Difficulty Breakdown
    stats_by_difficulty = {"Easy": 0, "Medium": 0, "Hard": 0}
    # Create a map for fast lookup
    q_map = {q["id"]: q for q in QUESTION_BANK}
    
    for pid in solved_ids:
        if pid in q_map:
            diff = q_map[pid]["difficulty"]
            stats_by_difficulty[diff] = stats_by_difficulty.get(diff, 0) + 1

    # Get "Up Next" problems (Recommendation engine)
    # Filter out solved ones
    unsolved_easy = [q for q in QUESTION_BANK if q["difficulty"] == "Easy" and q["id"] not in solved_ids]
    next_problems = unsolved_easy[:3]

    return {
        "problems_solved": len(solved_ids),
        "total_problems": len(QUESTION_BANK),
        "streak_days": user_stat.get("streak", 0),
        "weak_pattern": user_stat.get("weak_patterns", ["None"])[0] if user_stat.get("weak_patterns") else "None",
        "solved_problems": solved_ids,
        "stats_by_difficulty": stats_by_difficulty,
        "next_problems": next_problems
    }

@router.post("/solve/{problem_id}")
def toggle_problem(
    problem_id: str,
    db: Any = Depends(get_db)
) -> Any:
    """
    Toggle a problem as solved/unsolved.
    Updates streak and solved count.
    """
    # Hack for demo: Get last created user stat
    # Hack for demo: Get last created user stat or create one
    user_stat = db.user_stats.find_one(sort=[("_id", -1)])
    
    if not user_stat:
        # Create default user stats if missing
        user_stat = {
            "user_id": "demo_user",
            "solved_problems": [],
            "streak_dates": [],
            "streak": 0,
            "solved_count": 0,
            "created_at": datetime.utcnow()
        }
        result = db.user_stats.insert_one(user_stat)
        user_stat["_id"] = result.inserted_id
        
    solved_ids = user_stat.get("solved_problems", [])
    streak_dates = user_stat.get("streak_dates", [])
    today_str = datetime.now().date().isoformat()
    
    is_solving = problem_id not in solved_ids
    
    if is_solving:
        if problem_id not in solved_ids:
            solved_ids.append(problem_id)
        # Update Streak Date if not already present for today
        if today_str not in streak_dates:
            streak_dates.append(today_str)
            streak_dates.sort() # Keep sorted
    else:
        if problem_id in solved_ids:
            solved_ids.remove(problem_id)
            
    # Calculate Streak
    # Iterate backwards from today
    current_streak = 0
    check_date = datetime.now().date()
    
    # Convert string dates back to objects for comparison
    date_objs = {datetime.fromisoformat(d).date() for d in streak_dates}
    
    while check_date in date_objs:
        current_streak += 1
        check_date -= timedelta(days=1)
        
    # Update DB
    db.user_stats.update_one(
        {"_id": user_stat["_id"]},
        {
            "$set": {
                "solved_problems": solved_ids,
                "streak_dates": streak_dates,
                "solved_count": len(solved_ids),
                "streak": current_streak
            }
        },
        upsert=True
    )
    
@router.post("/progress")
def update_progress(
    item: dict,
    db: Any = Depends(get_db)
) -> Any:
    """
    Bulk update solved problems (Manual Save).
    Replaces the entire list of solved problems and recalculates streaks.
    """
    solved_ids = item.get("solved_ids", [])
    
    # Hack: Get/Create User Stats
    user_stat = db.user_stats.find_one(sort=[("_id", -1)])
    if not user_stat:
        user_stat = {
            "user_id": "demo_user",
            "solved_problems": [],
            "streak_dates": [],
            "streak": 0,
            "solved_count": 0,
            "created_at": datetime.utcnow()
        }
        result = db.user_stats.insert_one(user_stat)
        user_stat["_id"] = result.inserted_id

    old_solved_ids = set(user_stat.get("solved_problems", []))
    new_solved_ids = set(solved_ids)
    
    # Check if any NEW problem was solved (to increment streak)
    # Only if we added problems that weren't there before
    newly_solved = new_solved_ids - old_solved_ids
    
    streak_dates = user_stat.get("streak_dates", [])
    today_str = datetime.now().date().isoformat()
    
    if newly_solved:
        if today_str not in streak_dates:
            streak_dates.append(today_str)
            streak_dates.sort()

    # Recalculate Streak
    current_streak = 0
    check_date = datetime.now().date()
    date_objs = {datetime.fromisoformat(d).date() for d in streak_dates}
    
    while check_date in date_objs:
        current_streak += 1
        check_date -= timedelta(days=1)

    # Update DB
    db.user_stats.update_one(
        {"_id": user_stat["_id"]},
        {
            "$set": {
                "solved_problems": list(new_solved_ids),
                "streak_dates": streak_dates,
                "solved_count": len(new_solved_ids),
                "streak": current_streak
            }
        },
        upsert=True
    )
    
    return {"status": "success", "solved_count": len(new_solved_ids), "streak": current_streak}
