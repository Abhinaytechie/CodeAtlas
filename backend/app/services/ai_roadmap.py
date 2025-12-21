import json
import logging
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from typing import Optional
try:
    from ddgs import DDGS
except ImportError:
    from duckduckgo_search import DDGS

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
        - SKILLS: Each skill MUST have a unique 'id' (kebab-case slug) and 'resources' (best free resources links).
        - CONTENT: Practical, recruiter-aligned expectations. No motivational fluff.
        
        CRITICAL RESOURCE RULES:
        1. ONLY use stable, high-authority links (Official Docs, MDN, Python.org, React.dev).
        2. For DSA: Use NeetCode.io, Striver (TakeUForward), or LeetCode specific problem links.
        3. For Courses: Use Coursera, Udemy, or freeCodeCamp.
        4. YOUTUBE PLAYLISTS: MUST include high-quality playlists.
        5. **TRICK FOR YOUTUBE**: Do NOT guess the URL. Set 'url' to "SEARCH: <Channel Name> <Topic> Playlist".
           Example: "SEARCH: Striver Graph Series Playlist" or "SEARCH: Hitesh Choudhary JavaScript Playlist".
        6. DO NOT use placeholders like "example.com" or "youtube.com/...".
        7. Blogs ARE allowed (Medium, personal blogs, etc.) ONLY IF:
           - The content is widely referenced
           - The link is stable and publicly accessible
        
        8. AUTHORITATIVE YOUTUBE CREATOR MAPPING (Use these matching creators found in SEARCH):
           - Java / OOP / Spring Boot -> Telusko, Java Brains, in28Minutes
           - Data Structures & Algorithms -> Striver (Take U Forward), NeetCode, Abdul Bari
           - JavaScript / Frontend -> Hitesh Choudhary, Akshay Saini, Traversy Media
           - React -> React.dev (official), Codevolution, Hitesh Choudhary
           - Backend / Node.js -> Piyush Garg, Traversy Media
           - Machine Learning / Data Science -> Krish Naik, codebasics, freeCodeCamp
           - System Design -> Gaurav Sen, Tech Dummies
           - Databases / SQL -> freeCodeCamp, Telusko

        9. CORE SKILLS RULE:
           - For 'Core Skills' track, you MUST use a YouTube Playlist from the AUTHORITATIVE MAPPING above.

        PROJECTS TRACK RULES (CRITICAL):
        - Every Project MUST have exactly 2 resources:
          1. A YouTube Playlist: Use "SEARCH: Build <Project Name> <Tech Stack> Playlist" (prefer mapped creators).
          2. A Real Project Link (GitHub): Use "GITHUB: <Project Name> <Tech Stack> implementation".
             - Example: "GITHUB: E-commerce app MERN stack implementation"
             - This allows the system to find REAL user repositories.
        - STRICTLY FORBIDDEN: Do NOT link to official documentation (like React docs) for projects.

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
                                        {{ "title": "NeetCode Arrays", "url": "https://neetcode.io/roadmap" }},
                                        {{ "title": "Striver Graph Series", "url": "SEARCH: Striver Graph Series Playlist" }}
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
        
        response = await chain.ainvoke({
            "role": role
        })
        
        content = response.content.strip()
        print(f"DEBUG: Raw LLM Response: {content[:500]}...")
        
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
             if content.startswith("```json"):
                content = content[7:]
             if content.endswith("```"):
                content = content[:-3]
             data = json.loads(content)
             
        # ENFORCE IDs
        if data and "levels" in data:
            data = await self._enrich_resources(data) # Changed name to generic enrichment
            for level in data["levels"]:
                for track in level.get("tracks", []):
                    for skill in track.get("skills", []):
                        if "id" not in skill or not skill["id"]:
                            slug = skill.get("name", "unknown").lower().replace(" & ", "-").replace(" ", "-")
                            skill["id"] = slug
                            
        return data

    async def _enrich_resources(self, data):
        """
        Scans the roadmap for 'SEARCH:' (YouTube) and 'GITHUB:' (DuckDuckGo) URLs and resolves them.
        """
        import asyncio
        logger.info("Starting Resource Enrichment...")
        
        try:
            for level in data.get("levels", []):
                for track in level.get("tracks", []):
                    for skill in track.get("skills", []):
                        for resource in skill.get("resources", []):
                            url = resource.get("url", "")
                            
                            # 1. YouTube Handler
                            if url.startswith("SEARCH:"):
                                query = url.replace("SEARCH:", "").strip()
                                print(f"DEBUG: Resolving YouTube: {query}")
                                try:
                                    # Use DDGS for Video Search (Replacing broken youtube-search-python)
                                    loop = asyncio.get_event_loop()
                                    def _yt_search():
                                        with DDGS() as ddgs:
                                            # Search for videos
                                            results = list(ddgs.videos(query, max_results=1))
                                            return results
                                    
                                    results = await loop.run_in_executor(None, _yt_search)
                                    
                                    if results:
                                        # DDGS video result usually has 'content' as URL or 'json' data
                                        # Looking at the test output, it seems to return a dict with 'content' as the link
                                        video_link = results[0].get('content') 
                                        if not video_link:
                                             video_link = results[0].get('embed_url') # Fallback
                                        
                                        if video_link:
                                            resource['url'] = video_link
                                            print(f"DEBUG: Resolved to {video_link}")
                                        else:
                                            resource['url'] = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
                                    else:
                                        resource['url'] = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
                                        
                                except Exception as e:
                                    print(f"YouTube Error: {e}")
                                    resource['url'] = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
                                    
                            # 2. GitHub Handler
                            elif url.startswith("GITHUB:"):
                                query = url.replace("GITHUB:", "").strip()
                                print(f"DEBUG: Resolving GitHub: {query}")
                                try:
                                    # Run DDGS in executor to avoid blocking loop
                                    loop = asyncio.get_event_loop()
                                    def _gh_search():
                                        # Search filtering for github.com
                                        with DDGS() as ddgs:
                                            # site:github.com "query"
                                            # We try to get top 2 results and pick the best non-official-looking one if possible,
                                            # or just the top result.
                                            results = list(ddgs.text(f"site:github.com {query}", max_results=1))
                                            return results
                                    
                                    results = await loop.run_in_executor(None, _gh_search)
                                    if results:
                                        found_url = results[0]['href']
                                        resource['url'] = found_url
                                        print(f"DEBUG: GitHub Resolved: {found_url}")
                                    else:
                                        # Fallback to general search
                                        resource['url'] = f"https://github.com/search?q={query.replace(' ', '+')}"
                                        
                                except Exception as e:
                                    print(f"GitHub Search Error: {e}")
                                    resource['url'] = f"https://github.com/search?q={query.replace(' ', '+')}"

                            # 3. Validation & Sanitization (Final Pass)
                            resource['url'] = self._sanitize_url(resource['url'])

            return data
        except Exception as e:
            logger.error(f"Enrichment Error: {e}")
            return data

    def _sanitize_url(self, url: str) -> str:
        """
        Ensures strict HTTP/HTTPS formatting to preventing local file access behavior.
        """
        if not url:
            return "#"
        
        # If LLM returns "SEARCH:..." that failed to resolve, force it to a Google Search
        if url.startswith("SEARCH:") or url.startswith("GITHUB:"):
             query = url.replace("SEARCH:", "").replace("GITHUB:", "").strip()
             return f"https://www.google.com/search?q={query.replace(' ', '+')}"

        # If LLM returned a local path or generic placeholder
        if url.lower().startswith("file:") or url.lower().startswith("d:") or url.lower().startswith("c:"):
             return "https://www.google.com/search?q=roadmap+resource"
             
        if not url.startswith("http"):
            return f"https://{url}"
            
        return url

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