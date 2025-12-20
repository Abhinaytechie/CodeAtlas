import json
import logging
from typing import List, Dict, Any
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from datetime import datetime

logger = logging.getLogger(__name__)

class AIInterviewService:
    def __init__(self):
        # We will initialize LLM dynamically with the user's key
        pass

    async def start_session(self, role: str, company: str, type: str, api_key: str, resume_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Initializes the interview context and generates the first question.
        Includes Resume Context if provided.
        """
        llm = self._get_llm(api_key)
        
        resume_prompt_addendum = ""
        if resume_context:
            skills = ", ".join(resume_context.get("skills", [])[:10])
            projects = ", ".join([p.get("name") for p in resume_context.get("projects", [])[:3]])
            resume_prompt_addendum = f"""
            CRITICAL: This is a Resume-Based Interview.
            Candidate Claims:
            - Skills: {skills}
            - Projects: {projects}
            
            Your Goal: Verify these claims. Start by picking one project or skill from the resume and asking a deep technical question about it.
            Do NOT ask generic "tell me about yourself". Jump straight into "I see you used Redis in Project X...".
            """
        
        prompt_template = f"""
        You are a Senior {{role}} Interviewer at a {{company}} company.
        Your goal is to conduct a realistic {{type}} interview.
        
        {resume_prompt_addendum}
        
        Context:
        - Candidate is applying for: {{role}}
        - Company Style: {{company}}
        - Interview Focus: {{type}}
        
        Task:
        Generate the FIRST opening question for this interview.
        
        Output Format: JSON
        {{{{
            "question": "The actual question text",
            "context": "Why you are asking this (hidden from candidate)",
            "difficulty": "Easy/Medium/Hard"
        }}}}
        """
        
        prompt = PromptTemplate(
            template=prompt_template,
            input_variables=["role", "company", "type"]
        )
        
        chain = prompt | llm
        try:
            response = await chain.ainvoke({
                "role": role,
                "company": company,
                "type": type
            })
            content = self._clean_json(response.content)
            return json.loads(content)
        except Exception as e:
            logger.error(f"Failed to start interview: {e}")
            raise e

    async def process_turn(self, 
                           history: List[Dict], 
                           last_answer: str, 
                           role: str,
                           company: str,
                           api_key: str,
                           resume_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Analyzes the user's answer and generates the NEXT question or follow-up.
        """
        llm = self._get_llm(api_key)
        
        resume_instruction = ""
        if resume_context:
            resume_instruction = "Verify their claims against their resume. If they struggle, point out the discrepancy with what they claimed."

        # Construct simplified history for context
        history_text = ""
        for turn in history[-3:]: # Keep last 3 turns for context
            history_text += f"Interviewer: {turn.get('question')}\nCandidate: {turn.get('user_answer')}\n"

        prompt_template = f"""
        You are a Senior {{role}} Interviewer at a {{company}} company.
        {resume_instruction}
        
        Conversation History:
        {{history_text}}
        
        Candidate's Last Answer: "{{last_answer}}"
        
        Task:
        1. Evaluate the answer briefly (internal logic).
        2. Decide the next step:
           - If answer is good: Ask a harder follow-up or move to next topic.
           - If answer is vauge: Ask for clarification.
           - If answer is wrong: corrections? No, in an interview you typically probe or move on.
           
        Output Format: JSON
        {{{{
            "feedback_snapshot": "Brief internal rating (e.g. 'Good understanding of HashMaps')",
            "next_question": "The next question text",
            "type": "Follow-up/New Topic",
            "difficulty": "Easy/Medium/Hard"
        }}}}
        """
        
        prompt = PromptTemplate(
            template=prompt_template,
            input_variables=["role", "company", "history_text", "last_answer"]
        )
        
        chain = prompt | llm
        try:
            response = await chain.ainvoke({
                "role": role,
                "company": company,
                "history_text": history_text,
                "last_answer": last_answer
            })
            content = self._clean_json(response.content)
            return json.loads(content)
        except Exception as e:
            logger.error(f"Failed to process turn: {e}")
            raise e

    def _get_llm(self, api_key: str):
        return ChatGroq(
            temperature=0.7,
            groq_api_key=api_key,
            model_name="llama-3.3-70b-versatile",
            max_tokens=2000
        )
        
    def _clean_json(self, content: str) -> str:
        """Helper to clean LLM markdown response"""
        content = content.strip()
        if content.startswith("```json"):
            content = content[7:]
        if content.endswith("```"):
            content = content[:-3]
        return content

ai_interview_service = AIInterviewService()
