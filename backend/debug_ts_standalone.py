
import os

def _get_imports_with_treesitter(file_path: str, ext: str):
    try:
        from tree_sitter_languages import get_language, get_parser
        
        lang_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.jsx': 'javascript',
            '.ts': 'typescript', 
            '.tsx': 'typescript'
        }
        lang_name = lang_map.get(ext)
        if not lang_name: 
            print("No lang name")
            return []

        language = get_language(lang_name)
        parser = get_parser(lang_name)
        
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            code = f.read()
            
        tree = parser.parse(bytes(code, "utf8"))
        
        imports = []
        
        if lang_name == 'python':
            query = language.query("""
            (import_statement (dotted_name) @module)
            (import_from_statement module: (dotted_name) @module)
            """)
            captures = query.captures(tree.root_node)
            for node, name in captures:
                # Capture is tuple (Node, str)
                imports.append(code[node.start_byte:node.end_byte])
                
        elif lang_name in ['javascript', 'typescript']:
            # Import .. from 'x'
            # require('x')
            query = language.query("""
            (import_statement source: (string (string_fragment) @module))
            (call_expression
                function: (identifier) @func
                arguments: (arguments (string (string_fragment) @module))
                (#eq? @func "require")
            )
            """)
            captures = query.captures(tree.root_node)
            for node, name in captures:
                if name == "module":
                     imports.append(code[node.start_byte:node.end_byte])
                 
        return imports
        
    except Exception as e:
        print(f"Error: {e}")
        return []

if __name__ == "__main__":
    print("Testing Standalone Tree-sitter...")
    # Create dummy file
    with open("test_dummy.py", "w") as f:
        f.write("import os\nfrom typing import List")
        
    imports = _get_imports_with_treesitter("test_dummy.py", ".py")
    print(f"Imports: {imports}")
    
    # Cleanup
    try:
        os.remove("test_dummy.py")
    except: pass
