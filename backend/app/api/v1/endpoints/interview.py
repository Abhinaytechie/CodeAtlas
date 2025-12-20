from typing import Any
from fastapi import APIRouter, Depends, HTTPException, Body, Header, UploadFile, File
from app.core.database import get_db
from app.services.ai_interview import ai_interview_service
from app.services.resume_parser import resume_parser_service
from datetime import datetime
from bson import ObjectId

router = APIRouter()

@router.post("/resume/upload")
async def upload_resume(
    file: UploadFile = File(...),
    x_groq_api_key: str | None = Header(default=None, alias="x-groq-api-key"),
) -> Any:
    """
    Upload and parse a PDF resume. Returns extracted text and structured context.
    """
    if not x_groq_api_key:
         raise HTTPException(status_code=400, detail="Groq API Key (x-groq-api-key) header is required")

    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    
    try:
        # 1. Extract Text
        content = await file.read()
        import io
        file_stream = io.BytesIO(content)
        resume_text = resume_parser_service.extract_text_from_pdf(file_stream)
        
        # 2. Parse with AI
        resume_context = await resume_parser_service.parse_resume(resume_text, x_groq_api_key)
        
        return {
            "resume_text": resume_text,
            "resume_context": resume_context
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/start")
async def start_interview(
    body: dict = Body(...),
    x_groq_api_key: str | None = Header(default=None, alias="x-groq-api-key"),
    db: Any = Depends(get_db)
) -> Any:
    """
    Start a new AI Interview Session.
    Inputs: role, company, type, resume_text (optional), resume_context (optional)
    """
    role = body.get("role", "Backend Developer")
    company = body.get("company", "Product-based")
    interview_type = body.get("type", "DSA")
    resume_text = body.get("resume_text")
    resume_context = body.get("resume_context") # Allow pre-parsed context
    
    # 1. Parse Resume if provided AND context is missing
    if resume_text and not resume_context and len(resume_text.strip()) > 50:
        try:
            resume_context = await resume_parser_service.parse_resume(resume_text, x_groq_api_key)
        except Exception as e:
            print(f"Resume parsing failed: {e}")
            # Continue without resume if parsing fails (graceful degradation)
    
    # 2. Get/Create User (Demo hack)
    user = db.user_stats.find_one(sort=[("_id", -1)])
    user_id = user["user_id"] if user else "demo_user"
    
    # 3. Call AI Service to generate opening
    try:
        opening = await ai_interview_service.start_session(
            role=role, 
            company=company, 
            type=interview_type,
            api_key=x_groq_api_key,
            resume_context=resume_context
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        
    # 4. Create Session in DB
    session_doc = {
        "user_id": user_id,
        "role": role,
        "company": company,
        "type": interview_type,
        "resume_context": resume_context, # Persist for future turns
        "status": "active",
        "created_at": datetime.utcnow(),
        "turns": [
            {
                "role": "assistant",
                "question": opening["question"],
                "context": opening.get("context"),
                "timestamp": datetime.utcnow()
            }
        ]
    }
    
    result = db.interview_sessions.insert_one(session_doc)
    
    return {
        "session_id": str(result.inserted_id),
        "question": opening["question"],
        "context": opening.get("context")
    }

@router.post("/{session_id}/reply")
async def reply_to_interview(
    session_id: str,
    body: dict = Body(...),
    x_groq_api_key: str | None = Header(default=None, alias="x-groq-api-key"),
    db: Any = Depends(get_db)
) -> Any:
    """
    Process user answer and get next question.
    """
    user_answer = body.get("answer")
    
    # 1. Retrieve Session
    try:
        session = db.interview_sessions.find_one({"_id": ObjectId(session_id)})
    except:
        raise HTTPException(status_code=400, detail="Invalid Session ID")
        
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
        
    # 2. Append User Answer to History
    current_turns = session.get("turns", [])
    
    # Structure for AI Service
    history_for_ai = []
    for t in current_turns:
        if t["role"] == "assistant":
            history_for_ai.append({"question": t["question"], "user_answer": ""})
        elif t["role"] == "user":
            if history_for_ai:
                history_for_ai[-1]["user_answer"] = t["answer"]
                
    # 3. Call AI Service
    try:
        ai_response = await ai_interview_service.process_turn(
            history=history_for_ai,
            last_answer=user_answer,
            role=session["role"],
            company=session["company"],
            api_key=x_groq_api_key,
            resume_context=session.get("resume_context") # Pass persisted context
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        
    # 4. Update DB (Push User Answer AND New Question)
    new_user_turn = {
        "role": "user",
        "answer": user_answer,
        "timestamp": datetime.utcnow()
    }
    
    new_ai_turn = {
        "role": "assistant",
        "question": ai_response["next_question"],
        "feedback_snapshot": ai_response.get("feedback_snapshot"),
        "timestamp": datetime.utcnow()
    }
    
    db.interview_sessions.update_one(
        {"_id": ObjectId(session_id)},
        {"$push": {"turns": {"$each": [new_user_turn, new_ai_turn]}}}
    )
    
    return {
        "next_question": ai_response["next_question"],
        "feedback_snapshot": ai_response.get("feedback_snapshot")
    }

@router.get("/history")
def get_interview_history(db: Any = Depends(get_db)) -> Any:
    # Hack: Demo user
    user = db.user_stats.find_one(sort=[("_id", -1)])
    user_id = user["user_id"] if user else "demo_user"
    
    cursor = db.interview_sessions.find({"user_id": user_id}).sort("created_at", -1).limit(10)
    sessions = []
    for s in cursor:
        s["_id"] = str(s["_id"])
        sessions.append(s)
        
    return sessions
