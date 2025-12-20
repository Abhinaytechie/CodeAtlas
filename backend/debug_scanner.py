import os
import shutil
import asyncio
from app.services.project_intelligence import ProjectIntelligenceService

def test_integration():
    print("--- Integration Test: ProjectIntelligenceService Scanner ---")
    
    # Setup temp dir
    test_dir = "temp_test_scanner"
    if os.path.exists(test_dir):
        shutil.rmtree(test_dir)
    os.makedirs(test_dir)
    
    try:
        # 1. Create Mock FastAPI Project
        with open(os.path.join(test_dir, "requirements.txt"), "w") as f:
            f.write("fastapi\nuvicorn")
            
        with open(os.path.join(test_dir, "main.py"), "w") as f:
            f.write("""
from fastapi import FastAPI, APIRouter

app = FastAPI()
router = APIRouter(prefix="/users")

@app.get("/health")
def health_check():
    return {"status": "ok"}

@router.get("/", tags=["users"])
def get_users():
    pass

@router.post("/create")
def create_user():
    pass
            """)
            
        # 2. Run Scanner
        service = ProjectIntelligenceService()
        result = service._agent_api_scanner(test_dir)
        
        print("\n[Result]")
        print(f"Framework: {result['framework']}")
        print(f"Routes Found: {len(result['routes'])}")
        for r in result['routes']:
            print(f"  - {r['method']} {r['url']}")
            
        # Assertions
        assert result['framework'] == "FastAPI"
        assert len(result['routes']) == 3
        
        routes_set = {(r['method'], r['url']) for r in result['routes']}
        assert ('GET', '/health') in routes_set
        assert ('GET', '/users/') in routes_set
        assert ('POST', '/users/create') in routes_set
        
        print("\nSUCCESS: All routes detected correctly with AST scanner.")
        
    except Exception as e:
        print(f"\nFAILED: {e}")
    finally:
        # Cleanup
        if os.path.exists(test_dir):
            shutil.rmtree(test_dir)

if __name__ == "__main__":
    test_integration()
