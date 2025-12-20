import asyncio
import os
import sys

# Add project root to sys path to allow imports
sys.path.insert(0, os.getcwd())

from app.services.ai_roadmap import ai_service, AIRoadmapService

print("----------------------------------------------------------------")
print("   SERVICE LAYER DEBUGGER   ")
print("----------------------------------------------------------------")

arg_key = input("Enter your Groq API Key (gsk_...): ").strip()

if not arg_key:
    print("❌ No key entered. Exiting.")
    sys.exit(1)

async def test_service():
    print(f"\n1. Testing generate_roadmap with key length {len(arg_key)}...")
    
    role = "Backend Developer"
    days = 30
    weak_patterns = ["Dynamic Programming", "Graphs"]
    
    try:
        # We manually instantiate to be sure, or use the imported instance
        service = AIRoadmapService()
        
        print("   Invoking _generate_real_ai...")
        # calling the internal method directly to isolate it? 
        # Or the public method. Let's call the public one.
        result = await service.generate_roadmap(
            role=role,
            days=days,
            weak_patterns=weak_patterns,
            api_key=arg_key
        )
        
        print("\n🎉 SUCCESS! Generated Roadmap:")
        print(f"Title: {result.get('title')}")
        print(f"Patterns Count: {len(result.get('patterns', []))}")
        print("First Pattern:", result.get('patterns', [])[0].get('name'))
        
    except Exception as e:
        print(f"\n❌ SERVICE FAILED: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_service())
