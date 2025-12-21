
import os
import sys

# Add backend to path
sys.path.append(os.getcwd())

from app.services.project_intelligence import project_intelligence_service

def test():
    print("Testing Tree-sitter...")
    test_file = "app/main.py"
    if not os.path.exists(test_file):
        print(f"File {test_file} not found")
        return

    imports = project_intelligence_service._get_imports_with_treesitter(test_file, ".py")
    print(f"Imports found in {test_file}:")
    for i in imports:
        print(f" - {i}")

    if not imports:
        print("NO IMPORTS FOUND - TREE SITTER FAILED")
    else:
        print("SUCCESS")

if __name__ == "__main__":
    test()
