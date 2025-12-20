import os
import shutil
import uuid
import logging
import json
from typing import Dict, Any, List
from git import Repo
from langchain_groq import ChatGroq

logger = logging.getLogger(__name__)

class ProjectIntelligenceService:
    def __init__(self):
        self.temp_base = "temp_repos"
        os.makedirs(self.temp_base, exist_ok=True)

    async def analyze_project_structure(self, repo_url: str, api_key: str) -> Dict[str, Any]:
        """
        Stage 1: Clone & Map Architecture (Mermaid).
        """
        job_id = str(uuid.uuid4())
        repo_path = os.path.join(self.temp_base, job_id)
        
        try:
            # 1. Clone
            Repo.clone_from(repo_url, repo_path)
            
            # 2. Map Architecture (Deterministic Scan)
            graph_data = self._agent_architecture_map(repo_path)
            
            return {
                "job_id": job_id,
                "graph_data": graph_data, # For Mermaid
                "repo_path_id": job_id # Keep for step 2
            }
        except Exception as e:
            logger.error(f"Analysis failed: {e}")
            raise e

    async def generate_docs(self, job_id: str, api_key: str) -> Dict[str, str]:
        """
        Stage 2: Generate Documentation (README + API Specs).
        """
        repo_path = os.path.join(self.temp_base, job_id)
        if not os.path.exists(repo_path):
             return {"error": "Repo session expired. Please analyze again."}

        # Agent: Docs Engineer (LLM)
        readme = await self._agent_docs_engineer(repo_path, api_key)
        
        # Agent: API Scanner (Heuristic)
        api_data = self._agent_api_scanner(repo_path)
        
        # Cleanup after docs done
        shutil.rmtree(repo_path, ignore_errors=True)
        
        return {
            "readme": readme,
            "api_specs": api_data["routes"],
            "detected_framework": api_data["framework"]
        }

    def _agent_architecture_map(self, path: str) -> str:
        """
        Scans code imports to build a Mermaid Flowchart.
        Uses Regex to find explicit imports (Python/JS).
        Fall backs to Directory Tree if no imports found.
        """
        import re
        nodes = set()
        edges = set()
        
        # Regex Patterns
        # JS: import X from './path' or require('./path')
        js_import_pattern = re.compile(r"""(?:import\s+.*\s+from\s+['"](.*)['"])|(?:require\(['"](.*)['"])""")
        # Python: from x import y or import x
        py_import_pattern = re.compile(r"""(?:from\s+(\S+)\s+import)|(?:import\s+(\S+))""")

        target_ext = {'.js', '.jsx', '.ts', '.tsx', '.py'}
        ignored_dirs = {'node_modules', 'venv', 'dist', 'build', '.git', 'test', 'tests', '__pycache__'}
        
        file_map = {} # basename -> full path for resolution

        # Pass 1: Collect Nodes
        for root, dirs, files in os.walk(path):
            dirs[:] = [d for d in dirs if d not in ignored_dirs]
            for file in files:
                if os.path.splitext(file)[1] in target_ext:
                    node_name = os.path.splitext(file)[0]
                    # dedup identical filenames (e.g. index.js)
                    if node_name in file_map: node_name = f"{node_name}_{os.path.basename(root)}"
                    
                    file_map[node_name] = file
                    # Store simpler map for partial matching: "auth" -> "auth_service"
                    nodes.add(node_name)

        # Pass 2: Scan Imports
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
                            # 1. Check JS Imports
                            if ext in ['.js', '.jsx', '.ts', '.tsx']:
                                match = js_import_pattern.search(line)
                                if match:
                                    target = match.group(1) or match.group(2)
                                    if not target: continue
                                    # Resolve "./components/Button" -> "Button"
                                    target_base = os.path.basename(target)
                                    target_name = os.path.splitext(target_base)[0]
                                    if target_name in nodes and target_name != source_node:
                                        edges.add(f"    {source_node} --> {target_name}")

                            # 2. Check Python Imports
                            if ext == '.py':
                                match = py_import_pattern.search(line)
                                if match:
                                    target = match.group(1) or match.group(2)
                                    if not target: continue
                                    # Resolve "app.services.auth" -> "auth"
                                    target_name = target.split('.')[-1] 
                                    if target_name in nodes and target_name != source_node:
                                        edges.add(f"    {source_node} --> {target_name}")
                except: pass

        # Fallback: Directory Structure Graph
        if len(edges) < 3:
            logger.info("Few explicit imports found. Falling back to Directory Graph.")
            edges = set() # Clear sparse edges
            for root, dirs, files in os.walk(path):
                dirs[:] = [d for d in dirs if d not in ignored_dirs]
                
                parent_dir = os.path.basename(root)
                if root == path: parent_dir = "Root"
                
                # Link Parent -> Child Dir
                for d in dirs:
                    edges.add(f"    {parent_dir} --> {d}[/{d}/]")
                
                # Link Parent -> Files (Max 5 per dir to avoid clutter)
                count = 0
                for f in files:
                    if os.path.splitext(f)[1] in target_ext:
                        if count < 5:
                            f_node = os.path.splitext(f)[0]
                            edges.add(f"    {parent_dir} -.-> {f_node}")
                            count += 1
                        
            # Ensure at least minimal structure
            if not edges:
                edges.add("    Root --> src")
                edges.add("    src --> App")

        # Build Mermaid
        graph = "graph TD\n"
        graph += "    subgraph System Architecture\n"
        graph += "\n".join(list(edges)[:40]) # Limit to 40 edges
        graph += "\n    end"
        
        return graph

    async def _agent_docs_engineer(self, path: str, api_key: str) -> str:
        """
        Generates a High-Quality README.
        """
        if not api_key: return "# README\n\nGenerated without API Key."
        
        # Read Structure + package.json/requirements.txt
        structure = ""
        deps = ""
        for root, dirs, files in os.walk(path):
            if '.git' in root or 'node_modules' in root: continue
            level = root.replace(path, '').count(os.sep)
            indent = ' ' * 4 * (level)
            structure += f"{indent}{os.path.basename(root)}/\n"
            subindent = ' ' * 4 * (level + 1)
            for f in files:
                structure += f"{subindent}{f}\n"
                if f in ['package.json', 'requirements.txt']:
                    try:
                        with open(os.path.join(root, f), 'r') as df: deps += df.read() + "\n"
                    except: pass
            if len(structure) > 2000: break # Token limit

        chat = ChatGroq(temperature=0.2, groq_api_key=api_key, model_name="llama-3.3-70b-versatile")
        
        prompt = f"""
        You are a Senior Developer. Write a professional README.md for this project.
        
        Files:
        {structure}
        
        Dependencies:
        {deps[:1000]}
        
        Include:
        1. 🚀 Project Title & One-line Description (Infer from file names/deps)
        2. 🛠 Tech Stack (Badges)
        3. ✨ Key Features (Infer from file names like 'auth', 'cart', 'payment')
        4. 📦 Installation Guide
        """
        
        res = await chat.ainvoke(prompt)
        return res.content

    def _agent_api_scanner(self, path: str) -> Dict[str, Any]:
        """
        Scans for Backend Routes using Framework-Aware Static Analysis.
        1. Detects Framework (package.json, requirements.txt, pom.xml).
        2. Applies specific extraction rules.
        """
        import re
        
        framework = "Unknown"
        routes = []
        
        # 1. Framework Detection
        # Check Node.js
        package_json_path = os.path.join(path, "package.json")
        if os.path.exists(package_json_path):
            try:
                with open(package_json_path, 'r', encoding='utf-8') as f:
                    content = f.read().lower()
                    if '"express"' in content: framework = "Express.js"
                    elif '"nest"' in content: framework = "NestJS"
                    elif '"fastify"' in content: framework = "Fastify"
            except: pass

        # Check Python
        req_txt_path = os.path.join(path, "requirements.txt")
        if os.path.exists(req_txt_path):
            try:
                with open(req_txt_path, 'r', encoding='utf-8') as f:
                    content = f.read().lower()
                    if "fastapi" in content: framework = "FastAPI"
                    elif "flask" in content: framework = "Flask"
                    elif "django" in content: framework = "Django"
            except: pass
            
        # Check Java (Spring Boot)
        pom_path = os.path.join(path, "pom.xml")
        gradle_path = os.path.join(path, "build.gradle")
        if os.path.exists(pom_path) or os.path.exists(gradle_path):
            framework = "Spring Boot"

        if framework == "Unknown":
            logger.warning("No known API framework detected. Skipping endpoint scan.")
            return {"framework": "Unknown", "routes": []}

        # 2. Targeted Extraction Rules
        ignored_dirs = {'node_modules', 'venv', 'dist', 'build', '.git', 'test', 'tests', '__pycache__', 'target'}

        # Regex Definitions
        py_fastapi_pattern = re.compile(r"""@(?:router|app|api_router)\.(get|post|put|delete|patch)\s*\(\s*['"]([^'"]+)['"]""")
        js_express_pattern = re.compile(r"""(?:router|app)\.(get|post|put|delete|patch)\s*\(\s*['"]([^'"]+)['"]""")
        
        # Spring Boot Patterns
        # Class level: @RequestMapping("/api/v1") or @RequestMapping(value = "/api/v1") matches before "class"
        java_class_req_pattern = re.compile(r"""@RequestMapping\s*\(\s*(?:value\s*=\s*|path\s*=\s*)?["']([^"']+)["']""")
        # Method level: @GetMapping("/users")
        java_method_pattern = re.compile(r"""@(Get|Post|Put|Delete|Patch)Mapping\s*\(\s*(?:value\s*=\s*|path\s*=\s*)?["']([^"']+)["']""")

        for root, dirs, files in os.walk(path):
            dirs[:] = [d for d in dirs if d not in ignored_dirs]
            
            for file in files:
                ext = os.path.splitext(file)[1]
                
                try:
                    # PYTHON SCANNERS
                    if ext == '.py':
                        if framework == "FastAPI":
                            try:
                                import ast
                                with open(os.path.join(root, file), 'r', encoding='utf-8', errors='ignore') as f:
                                    file_content = f.read()
                                    tree = ast.parse(file_content)
                                    
                                    # 1. Find Prefixes
                                    prefixes = {}
                                    for node in ast.walk(tree):
                                        if isinstance(node, ast.Assign):
                                            for target in node.targets:
                                                if isinstance(target, ast.Name):
                                                    var_name = target.id
                                                    if isinstance(node.value, ast.Call) and isinstance(node.value.func, ast.Name):
                                                        if node.value.func.id == "APIRouter":
                                                            for keyword in node.value.keywords:
                                                                if keyword.arg == "prefix" and isinstance(keyword.value, ast.Constant):
                                                                    prefixes[var_name] = keyword.value.value

                                    # 2. Find Routes
                                    for node in ast.walk(tree):
                                        if isinstance(node, ast.FunctionDef):
                                            for decorator in node.decorator_list:
                                                if isinstance(decorator, ast.Call) and isinstance(decorator.func, ast.Attribute):
                                                    method_name = decorator.func.attr
                                                    if method_name in ['get', 'post', 'put', 'delete', 'patch']:
                                                        # Resolve router variable
                                                        router_var = None
                                                        if isinstance(decorator.func.value, ast.Name):
                                                            router_var = decorator.func.value.id
                                                        
                                                        # Resolve Path
                                                        path = None
                                                        if decorator.args and isinstance(decorator.args[0], ast.Constant):
                                                            path = decorator.args[0].value
                                                        
                                                        if path is not None:
                                                            prefix = prefixes.get(router_var, "")
                                                            full_path = f"{prefix}{path}".replace("//", "/")
                                                            routes.append({"method": method_name.upper(), "url": full_path, "file": file})
                            except Exception:
                                pass # Fallback or skip file on parse error

                    # JS SCANNERS
                    elif ext in ['.js', '.ts', '.jsx', '.tsx']:
                        if framework == "Express.js":
                             with open(os.path.join(root, file), 'r', encoding='utf-8', errors='ignore') as f:
                                content = f.read()
                                # Improved Regex to catch variable router names
                                # matches: app.get('/path'), router.post('/path'), v1Router.put('/path')
                                matches = re.findall(r"""(?:\w+)\.(get|post|put|delete|patch)\s*\(\s*['"]([^'"]+)['"]""", content)
                                for method, url in matches:
                                    routes.append({"method": method.upper(), "url": url, "file": file})

                    # JAVA SCANNERS
                    elif ext == '.java':
                         if framework == "Spring Boot":
                            with open(os.path.join(root, file), 'r', encoding='utf-8', errors='ignore') as f:
                                content = f.read()
                                # 1. Check if Controller
                                if "@RestController" in content or "@Controller" in content:
                                    base_path = ""
                                    # 2. Extract Class Level Mapping (Look before "class" keyword)
                                    class_idx = content.find("class ")
                                    if class_idx != -1:
                                        pre_class = content[:class_idx]
                                        # Find last occurrence of RequestMapping before class? Or just one. 
                                        # Usually there's only one relevant one on the class.
                                        base_match = java_class_req_pattern.search(pre_class)
                                        if base_match:
                                            base_path = base_match.group(1)
                                    
                                    # 3. Extract Method Level Mappings
                                    matches = java_method_pattern.findall(content)
                                    for method_type, url in matches: # method_type will be Get, Post etc
                                        # Combine paths: /base + /method -> /base/method (handle slashes)
                                        # Ensure no double slash unless intentional, but generally clean up
                                        full_url = f"{base_path}/{url}".replace("//", "/")
                                        if not full_url.startswith("/"): full_url = "/" + full_url
                                        
                                        http_method = method_type.upper() 
                                        routes.append({"method": http_method, "url": full_url, "file": file})

                except Exception:
                    pass
                    
        # Deduplicate
        unique_routes = []
        seen = set()
        for r in routes:
            key = f"{r['method']}:{r['url']}"
            if key not in seen:
                seen.add(key)
                unique_routes.append(r)

        return {"framework": framework, "routes": unique_routes[:50]}

project_intelligence_service = ProjectIntelligenceService()
