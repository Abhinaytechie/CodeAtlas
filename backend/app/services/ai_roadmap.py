import json
import logging
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from typing import Optional

logger = logging.getLogger(__name__)

class AIRoadmapService:
    def __init__(self):
        pass
        
    async def generate_roadmap(self, role: str, days: int, weak_patterns: list[str], api_key: Optional[str] = None) -> dict:
        """
        Generates a NeetCode-style roadmap.
        If api_key is provided, uses Groq.
        Otherwise, falls back to simulation.
        """
        if api_key:
            try:
                print(f"DEBUG: Attempting Real AI Generation for {role} using Groq. Key Length: {len(api_key)}")
                logger.info(f"Generating real AI roadmap for role: {role}")
                return await self._generate_real_ai(role, days, weak_patterns, api_key)
            except Exception as e:
                # Log to file for agent to read
                import traceback
                with open("ai_error.log", "w") as f:
                    f.write(traceback.format_exc())
                
                print(f"DEBUG: Real AI Generation Failed: {e}")
                logger.error(f"AI Generation failed: {e}")
                logger.info("Falling back to simulation.")
                return self._get_simulated_response(role, weak_patterns)
                
        else:
            print("DEBUG: No API Key found. Using Simulation.")
            logger.info("No API Key provided. Using simulation mode.")
            return self._get_simulated_response(role, weak_patterns)

    async def _generate_real_ai(self, role, days, weak_patterns, api_key):
        print(f"DEBUG: Entering _generate_real_ai with Groq model llama-3.3-70b-versatile")
        
        llm = ChatGroq(
            temperature=0.7,
            groq_api_key=api_key,
            model_name="llama-3.3-70b-versatile",
            max_tokens=8000 # Increase token limit for long JSONs
        )
        
        # NOTE: We use double curly braces {{ }} for JSON structure to escape them in f-strings/PromptTemplate
        prompt_template = """
        You are an expert Software Engineering Placement Mentor with experience in backend, AI/ML, data, and full-stack roles.
        Design a role-specific interview preparation roadmap for: {role}.

        Constraints:
        - SKILL-BASED: Do NOT use days or weeks. Focus on mastery.
        - REALISTIC: Targeted at Indian on-campus/off-campus placements.
        - STRUCTURE: Divide into 3 Levels: Beginner, Intermediate, Advanced.
        - TRACKS: Each level must have parallel tracks: DSA, Core Skills, Projects, Interview Signals.
        - SKILLS: Each skill MUST have a unique 'id' (kebab-case slug) and 'resources' (best free links).
        - CONTENT: Practical, recruiter-aligned expectations. No motivational fluff.

        JSON Structure:
        {{
            "title": "{role} Placement Mastery Roadmap",
            "is_simulated": false,
            "description": "A skill-based, tiered roadmap to get you interview-ready.",
            "levels": [
                {{
                    "name": "Beginner (Foundational)",
                    "description": "Building the bedrock. Cannot clear interviews without this.",
                    "tracks": [
                        {{
                            "category": "DSA",
                            "skills": [
                                {{
                                    "id": "arrays-strings-mastery",
                                    "name": "Arrays & Strings Mastery",
                                    "description": "Two Pointers, Sliding Window basics.",
                                    "status": "Not Started",
                                    "resources": [
                                        {{ "title": "NeetCode Arrays", "url": "https://youtu.be/..." }},
                                        {{ "title": "GFG Article", "url": "https://geeksforgeeks.org/..." }}
                                    ]
                                }}
                            ]
                        }}
                    ]
                }}
            ]
        }}
        """
        
        if weak_patterns:
            weak_patterns_str = ", ".join(weak_patterns)
            prompt_template += f"""
            CRITICAL INSTRUCTION:
            The user explicitly mentioned these weak areas: {weak_patterns_str}.
            You MUST include a dedicated track or heavy emphasis on these topics in the 'Beginner' or 'Intermediate' levels.
            Label them as 'Focus Area' in the description.
            """
        
        prompt = PromptTemplate(
            template=prompt_template,
            input_variables=["role"]
        )
        
        chain = prompt | llm
        
        # We don't need 'days' or 'weak_patterns' strictly anymore, but we can pass them if needed.
        # For now, let's keep the call simple.
        response = await chain.ainvoke({
            "role": role
        })
        
        # Clean response content (sometimes LLM wraps in ```json ... ```)
        content = response.content.strip()
        print(f"DEBUG: Raw LLM Response: {content[:500]}...")
        
        # Robust JSON Extraction
        import re
        data = None
        try:
             # Find JSON object using regex (non-greedy match for outermost brackets)
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                data = json.loads(json_str)
            else:
                raise ValueError("No JSON found in response")
        except json.JSONDecodeError:
            # Fallback: Try to clean markdown tags if regex failed (unlikely for well-formed JSON)
             if content.startswith("```json"):
                content = content[7:]
             if content.endswith("```"):
                content = content[:-3]
             data = json.loads(content)
             
        # ENFORCE IDs: Post-process to ensure every skill has an ID
        if data and "levels" in data:
            for level in data["levels"]:
                for track in level.get("tracks", []):
                    for skill in track.get("skills", []):
                        if "id" not in skill or not skill["id"]:
                            # Generate simple slug from name
                            slug = skill.get("name", "unknown").lower().replace(" & ", "-").replace(" ", "-")
                            skill["id"] = slug
                            
        return data

    def _get_simulated_response(self, role, weak_patterns):
        """
        Returns a rich, pre-defined JSON matching the new Skill-Based structure.
        """
        return {
            "title": f"{role} Mastery Roadmap (Simulated)",
            "is_simulated": True,
            "description": "A skill-based, tiered roadmap to get you interview-ready (No API Key).",
            "levels": [
                {
                    "name": "Beginner (Foundational)",
                    "description": "Building the bedrock. Cannot clear interviews without this.",
                    "tracks": [
                        {
                            "category": "DSA",
                            "skills": [
                                {
                                    "id": "arrays-strings", 
                                    "name": "Arrays & Strings", 
                                    "description": "Basics of memory, iteration, and simple modifications.", 
                                    "status": "Not Started",
                                    "resources": [{"title": "NeetCode Arrays", "url": "https://neetcode.io/roadmap"}]
                                },
                                {
                                    "id": "linked-lists", 
                                    "name": "Linked Lists", 
                                    "description": "Pointer manipulation and memory chaining.", 
                                    "status": "Not Started",
                                    "resources": [{"title": "Visualizing Linked Lists", "url": "https://visualgo.net/en/list"}]
                                }
                            ]
                        },
                        {
                            "category": "Core Skills",
                            "skills": [
                                {"id": "language-mastery", "name": "Language Mastery", "description": "Deep dive into your primary language (Python/Java/C++).", "status": "Not Started"}
                            ]
                        }
                    ]
                },
                {
                    "name": "Intermediate (Interview-Ready)",
                    "description": "The standard required for most product companies.",
                    "tracks": [
                        {
                            "category": "DSA",
                            "skills": [
                                {"id": "trees-graphs", "name": "Trees & Graphs", "description": "BFS, DFS, and recursive traversals.", "status": "Not Started"},
                                {"id": "dynamic-programming", "name": "Dynamic Programming", "description": "Optimizing recursion with caching.", "status": "Not Started"}
                            ]
                        },
                        {
                            "category": "Projects",
                            "skills": [
                                {"id": "full-stack-app", "name": "Full Stack App", "description": "Build a CRUD app with Auth and Database.", "status": "Not Started"}
                            ]
                        }
                    ]
                },
                {
                    "name": "Advanced (Top-Tier)",
                    "description": "System Design and complex problem solving.",
                    "tracks": [
                        {
                            "category": "DSA",
                            "skills": [
                                {"id": "advanced-graphs", "name": "Advanced Graphs", "description": "Dijkstra, Union Find, Topological Sort.", "status": "Not Started"}
                            ]
                        },
                        {
                            "category": "System Design",
                            "skills": [
                                {"id": "scalability", "name": "Scalability", "description": "Load balancing, Caching, Sharding.", "status": "Not Started"}
                            ]
                        }
                    ]
                }
            ]
        }

ai_service = AIRoadmapService()
