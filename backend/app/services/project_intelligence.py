import os
import shutil
import uuid
import logging
import json
import re
from typing import Dict, Any, List, Optional
from git import Repo
from langchain_groq import ChatGroq

logger = logging.getLogger(__name__)

# --- Component 1: Repo Loader ---
class RepoLoader:
    def __init__(self, base_dir="temp_repos"):
        self.base_dir = base_dir
        os.makedirs(self.base_dir, exist_ok=True)

    def clone_repo(self, repo_url: str) -> str:
        job_id = str(uuid.uuid4())
        repo_path = os.path.join(self.base_dir, job_id)
        try:
            logger.info(f"Cloning {repo_url} to {repo_path}")
            Repo.clone_from(repo_url, repo_path)
            return repo_path
        except Exception as e:
            logger.error(f"Clone failed: {e}")
            if os.path.exists(repo_path):
                shutil.rmtree(repo_path, ignore_errors=True)
            raise e

    def cleanup(self, path: str):
        if os.path.exists(path):
            shutil.rmtree(path, ignore_errors=True)

# --- Component 2: API Contract Service (OpenAPI First) ---
class ApiContractService:
    def detect_framework(self, path: str) -> str:
        # Check Node.js
        if os.path.exists(os.path.join(path, "package.json")):
            try:
                with open(os.path.join(path, "package.json"), 'r', encoding='utf-8') as f:
                    content = f.read().lower()
                    if '"express"' in content: return "Express.js"
                    if '"nest"' in content: return "NestJS"
                    if '"fastify"' in content: return "Fastify"
            except: pass
        
        # Check Python
        if os.path.exists(os.path.join(path, "requirements.txt")):
            try:
                with open(os.path.join(path, "requirements.txt"), 'r', encoding='utf-8') as f:
                    content = f.read().lower()
                    if "fastapi" in content: return "FastAPI"
                    if "flask" in content: return "Flask"
                    if "django" in content: return "Django"
            except: pass

        # Check Java
        if os.path.exists(os.path.join(path, "pom.xml")) or os.path.exists(os.path.join(path, "build.gradle")):
             return "Spring Boot"
             
        return "Unknown"

    def get_api_specs(self, path: str) -> Dict[str, Any]:
        """
        STRICT: Only returns specs if OpenAPI/Swagger file is found.
        Does NOT use regex/AST for routes.
        """
        search_files = ['openapi.json', 'swagger.json', 'api-docs.json']
        ignored_dirs = {'node_modules', 'venv', 'dist', 'build', '.git', '__pycache__'}
        
        for root, dirs, files in os.walk(path):
            dirs[:] = [d for d in dirs if d not in ignored_dirs]
            
            for target in search_files:
                if target in files:
                    filepath = os.path.join(root, target)
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            spec = json.load(f)
                            # Basic validation it's an OpenAPI spec
                            if "openapi" in spec or "swagger" in spec:
                                logger.info(f"OpenAPI Spec found: {filepath}")
                                return self._parse_openapi(spec, target)
                    except Exception as e:
                        logger.warning(f"Failed to parse potential OpenAPI file {filepath}: {e}")

        # If we reach here, no spec found.
        # Strict mode: Error out.
        return {"error": "OpenAPI specification not found. API intelligence unavailable."}

    def _parse_openapi(self, spec: Dict, filename: str) -> Dict[str, Any]:
        routes = []
        if "paths" in spec:
            for path, methods in spec["paths"].items():
                for method, details in methods.items():
                    if method.lower() in ['get', 'post', 'put', 'delete', 'patch', 'options', 'head']:
                        routes.append({
                            "method": method.upper(),
                            "url": path,
                            "summary": details.get("summary", ""),
                            "file": filename
                        })
        return {"routes": routes[:100]} # Limit to 100 for safety

# --- Component 3: Architecture Mapper (Static Hints) ---
class ArchitectureMapper:
    def map_architecture(self, path: str) -> str:
        """
        Visualizes imports or directory structure.
        """
        nodes = set()
        edges = set()
        
        # Simple Regex for imports (Fallback, robust)
        js_import_pattern = re.compile(r"""(?:import\s+.*\s+from\s+['"](.*)['"])|(?:require\(['"](.*)['"])""")
        py_import_pattern = re.compile(r"""(?:from\s+(\S+)\s+import)|(?:import\s+(\S+))""")
        
        target_ext = {'.js', '.jsx', '.ts', '.tsx', '.py'}
        ignored_dirs = {'node_modules', 'venv', 'dist', 'build', '.git', 'test', 'tests', '__pycache__'}
        file_map = {}

        # 1. Collect Nodes
        for root, dirs, files in os.walk(path):
            dirs[:] = [d for d in dirs if d not in ignored_dirs]
            for file in files:
                if os.path.splitext(file)[1] in target_ext:
                    node_name = os.path.splitext(file)[0]
                    if node_name in file_map: node_name = f"{node_name}_{os.path.basename(root)}"
                    file_map[node_name] = file
                    nodes.add(node_name)

        # 2. Scan Imports (Regex)
        for root, dirs, files in os.walk(path):
            dirs[:] = [d for d in dirs if d not in ignored_dirs]
            for file in files:
                ext = os.path.splitext(file)[1]
                if ext not in target_ext: continue
                
                source_node = os.path.splitext(file)[0]
                if source_node in file_map and file_map[source_node] != file:
                     source_node = f"{source_node}_{os.path.basename(root)}"
                
                try:
                    with open(os.path.join(root, file), 'r', encoding='utf-8', errors='ignore') as f:
                        lines = f.readlines()
                        for line in lines:
                             target = None
                             if ext in ['.js', '.jsx', '.ts', '.tsx']:
                                 m = js_import_pattern.search(line)
                                 if m: target = m.group(1) or m.group(2)
                             elif ext == '.py':
                                 m = py_import_pattern.search(line)
                                 if m: target = m.group(1) or m.group(2)
                             
                             if target:
                                 # Basic Clean
                                 target = os.path.basename(target).split('.')[0]
                                 if target in nodes and target != source_node:
                                      edges.add(f"    {source_node} --> {target}")
                except: pass

        # Fallback to Directory Graph if sparse
        if len(edges) < 3:
             edges = set()
             for root, dirs, files in os.walk(path):
                dirs[:] = [d for d in dirs if d not in ignored_dirs]
                parent = os.path.basename(root) if root != path else "Root"
                for d in dirs: edges.add(f"    {parent} --> {d}[/{d}/]")
                for i, f in enumerate(files):
                    if i < 5 and os.path.splitext(f)[1] in target_ext:
                        edges.add(f"    {parent} -.-> {os.path.splitext(f)[0]}")

        if not edges:
            edges.add("    Root --> src")

        return "graph TD\n    subgraph Architecture\n" + "\n".join(list(edges)[:50]) + "\n    end"

# --- Component 4: Docs Generator (LLM) ---
class DocsGenerator:
    async def generate_readme(self, path: str, api_key: str) -> str:
        if not api_key: return "# README\n\nGenerated without API Key."
        
        structure = ""
        deps = ""
        for root, dirs, files in os.walk(path):
            if '.git' in root or 'node_modules' in root: continue
            level = root.replace(path, '').count(os.sep)
            if level > 2: continue # Limit depth
            indent = ' ' * 4 * level
            structure += f"{indent}{os.path.basename(root)}/\n"
            for f in files:
                structure += f"{indent}    {f}\n"
                if f in ['package.json', 'requirements.txt', 'pom.xml']:
                    try:
                        with open(os.path.join(root, f), 'r') as df: deps += df.read()[:500] + "\n"
                    except: pass
            if len(structure) > 1500: break

        chat = ChatGroq(temperature=0.2, groq_api_key=api_key, model_name="llama-3.3-70b-versatile")
        prompt = f"""
       Act as a Principal Software Engineer and Technical Writer.

Your task is to write a professional, accurate README.md for this codebase.
The README must reflect the ACTUAL functionality of the project inferred from
the file structure and dependencies — do NOT assume AI-related features unless
clearly indicated.

File Structure:
{structure}

Dependencies:
{deps}

Guidelines:
- Infer functionality from folder names, file names, and dependencies
  (e.g., auth, api, routes, services, controllers, utils, config, db).
- If a feature is not clearly supported by the codebase, do NOT invent it.
- Keep the tone professional, concise, and production-ready.
- Avoid buzzwords and marketing fluff.
- Assume this README is for developers who will run, maintain, or extend the project.

Sections required:

1. 📌 Title & Description
   - Infer a meaningful project name if not explicitly available.
   - Provide a clear one-paragraph description of what the application does.

2. 🧱 Architecture Overview
   - Briefly explain how the project is structured (frontend/backend/modules/services).
   - Mention major layers or components and their responsibilities.

3. 🛠 Tech Stack (Badges)
   - List languages, frameworks, databases, and tooling inferred from dependencies.
   - Use standard shields.io-style badges.

4. ✨ Key Features
   - List concrete, observable features (e.g., authentication, REST APIs,
     CRUD operations, configuration management, logging, integrations).
   - Base features strictly on code evidence.

5. 📂 Project Structure
   - Explain the purpose of key directories and files.

6. ⚙️ Configuration
   - Mention environment variables, config files, or setup requirements if present.

7. 🚀 Setup & Run Instructions
   - Provide step-by-step instructions to install dependencies and run the project.
   - Include separate steps for development and production if applicable.

8. 🧪 Testing (if applicable)
   - Describe how tests are organized and how to run them, if test tooling is detected.

9. 📦 Build / Deployment (if applicable)
   - Explain build steps, scripts, or deployment assumptions if present.

10. 🤝 Contributing
    - Include basic contribution guidelines.

11. 📄 License
    - Mention license if identifiable, otherwise note that it is unspecified.

Important:
- Accuracy is more important than completeness.
- If something is unclear, describe it conservatively.

        """
        try:
             res = await chat.ainvoke(prompt)
             return res.content
        except Exception as e:
             logger.error(f"LLM generation failed: {e}")
             return "# API Error\nFailed to generate README."

    async def generate_openapi_spec(self, path: str, framework: str, api_key: str) -> Optional[str]:
        """
        Bootstrap an OpenAPI spec using LLM if none exists.
        """
        if not api_key: return None
        
        # 1. Scout for Router Files
        candidates = []
        ignored_dirs = {'node_modules', 'venv', 'dist', 'build', '.git', '__pycache__', 'test', 'tests'}
        
        # Heuristics
        patterns = []
        if framework == "FastAPI":
            patterns = ["APIRouter", "FastAPI(", "@app.", "@router."]
        elif framework in ["Express.js", "NestJS", "Fastify"]:
            patterns = [".get(", ".post(", "Router(", "@Controller", "@Get"]
        elif framework == "Spring Boot":
            patterns = ["@RestController", "@RequestMapping", "@GetMapping"]
        else:
            # Generic fallback
            patterns = ["api", "route", "endpoint", "http"]

        for root, dirs, files in os.walk(path):
            dirs[:] = [d for d in dirs if d not in ignored_dirs]
            for file in files:
                ext = os.path.splitext(file)[1]
                if ext not in ['.py', '.js', '.ts', '.java', '.go', '.cs']: continue
                
                try:
                    fpath = os.path.join(root, file)
                    with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        # If file contains framework keywords
                        if any(p in content for p in patterns):
                            # Limit file size context
                            candidates.append(f"--- File: {file} ---\n{content[:3000]}\n")
                            if len(candidates) >= 10: break # Token safety
                except: pass
            if len(candidates) >= 10: break

        if not candidates: 
            return None

        # 2. LLM Gen
        chat = ChatGroq(temperature=0.1, groq_api_key=api_key, model_name="llama-3.3-70b-versatile")
        
        context = "\n".join(candidates)
        prompt = f"""
        You are an API Architect. Generate a valid OpenAPI 3.0 JSON specification for the following code snippets.
        
        Rules:
        1. Output ONLY valid JSON. 
        2. Do NOT output markdown key `json`.
        3. Do NOT output any conversational text.
        4. Start immediately with {{ and end with }}.
        
        Codebase:
        {context}
        """
        
        try:
            res = await chat.ainvoke(prompt)
            content = res.content.strip()
            
            # Robust JSON Extraction
            start_idx = content.find('{')
            end_idx = content.rfind('}')
            
            if start_idx != -1 and end_idx != -1:
                content = content[start_idx : end_idx + 1]
            
            # Validation parse
            json.loads(content) 
            return content
        except Exception as e:
            logger.error(f"AI OpenAPI Gen failed: {e}")
            logger.error(f"Raw Content: {res.content[:500] if 'res' in locals() else 'No response'}")
            return None

# --- Main Facade ---
class ProjectIntelligenceService:
    def __init__(self):
        self.loader = RepoLoader()
        self.api_service = ApiContractService()
        self.arch_mapper = ArchitectureMapper()
        self.docs_gen = DocsGenerator()

    async def analyze_project_structure(self, repo_url: str, api_key: str) -> Dict[str, Any]:
        """ Step 1: Clone & Map """
        repo_path = self.loader.clone_repo(repo_url)
        graph = self.arch_mapper.map_architecture(repo_path)
        job_id = os.path.basename(repo_path)
        return {"job_id": job_id, "graph_data": graph, "repo_path_id": job_id}

    async def generate_docs(self, job_id: str, api_key: str) -> Dict[str, Any]:
        """ Step 2: Docs & API Specs """
        repo_path = os.path.join(self.loader.base_dir, job_id)
        if not os.path.exists(repo_path):
             return {"error": "Session expired"}

        readme = await self.docs_gen.generate_readme(repo_path, api_key)
        framework = self.api_service.detect_framework(repo_path)
        
        # 1. Try Standard Discovery (OpenAPI First)
        api_data = self.api_service.get_api_specs(repo_path)
        
        specs = []
        warnings = []
        if "error" in api_data:
             warnings.append(api_data["error"])
        else:
             specs = api_data.get("routes", [])

        # Clean up
        self.loader.cleanup(repo_path)

        return {
            "readme": readme,
            "api_specs": specs,
            "detected_framework": framework, 
            "warnings": warnings,
            "ai_generated_spec": False
        }

    async def generate_ai_openapi_for_repo(self, repo_url: str, api_key: str) -> Dict[str, Any]:
        """
        Standalone method to generate OpenAPI spec for a repo URL.
        """
        repo_path = self.loader.clone_repo(repo_url)
        try:
            framework = self.api_service.detect_framework(repo_path)
            ai_spec = await self.docs_gen.generate_openapi_spec(repo_path, framework, api_key)
            
            routes = []
            if ai_spec:
                 try:
                     spec = json.loads(ai_spec)
                     parsed = self.api_service._parse_openapi(spec, "generated_openapi.json")
                     routes = parsed.get("routes", [])
                 except: pass
            
            return {
                "spec_json": ai_spec,
                "routes": routes,
                "framework": framework
            }
        finally:
            self.loader.cleanup(repo_path)

project_intelligence_service = ProjectIntelligenceService()
