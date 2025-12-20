import asyncio
import os
import sys

# Mocking the key input
print("----------------------------------------------------------------")
print("   GROQ API DEBUGGER   ")
print("----------------------------------------------------------------")
arg_key = input("Enter your Groq API Key (gsk_...): ").strip()

if not arg_key:
    print("❌ No key entered.")
    sys.exit(1)

try:
    print(f"\n1. Importing langchain_groq...")
    from langchain_groq import ChatGroq
    print("✅ Import successful.")

    print("\n2. Initializing ChatGroq...")
    llm = ChatGroq(
        temperature=0,
        groq_api_key=arg_key,
        model_name="llama-3.3-70b-versatile"
    )
    print("✅ Initialization successful.")

    print("\n3. Testing API Call (Hello World)...")
    async def test_invoke():
        try:
            response = await llm.ainvoke("Say 'Hello from Groq!'")
            print(f"\n🎉 SUCCESS! Response from Groq:\n{response.content}")
        except Exception as e:
            print(f"\n❌ API CALL FAILED: {e}")
            print("Possible causes: Invalid Key, Network Blocks, or Quota Exceeded.")

    asyncio.run(test_invoke())

except ImportError:
    print("❌ CRITICAL: langchain_groq not installed. Run 'pip install langchain-groq'")
except Exception as e:
    print(f"❌ CRITICAL ERROR: {e}")

input("\nPress Enter to exit...")
