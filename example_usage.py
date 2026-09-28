from client import CodebaseASTDependencySlicer
import json

def test():
    s = CodebaseASTDependencySlicer()
    print("=== Testing Codebase AST Dependency Slicer ===")
    res = s.run_benchmark_ast_slicing()
    print(json.dumps(res, indent=2))

if __name__ == "__main__":
    test()
