import sys, json, ast, re

class CodebaseASTDependencySlicer:
    """
    Codebase AST Dependency Slicer for Autonomous Coding Agents.
    Parses Python ASTs, maps module import graphs, and slices out minimum
    sufficient context for refactorings without dumping entire files into prompts.
    """
    def extract_import_graph(self, file_contents_map):
        graph = {}
        for fname, code in file_contents_map.items():
            imports = set()
            try:
                tree = ast.parse(code)
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for n in node.names: imports.add(n.name)
                    elif isinstance(node, ast.ImportFrom):
                        if node.module: imports.add(node.module)
            except Exception:
                # Regex fallback
                for line in code.splitlines():
                    m = re.match(r"^(?:from\s+([\w\.]+)\s+import|import\s+([\w\.]+))", line.strip())
                    if m: imports.add(m.group(1) or m.group(2))

            graph[fname] = sorted(list(imports))
        return graph

    def slice_symbol_dependencies(self, target_symbol, code_snippet):
        functions = []
        classes = []
        try:
            tree = ast.parse(code_snippet)
            for node in ast.iter_child_nodes(tree):
                if isinstance(node, ast.FunctionDef):
                    functions.append({"name": node.name, "args": [a.arg for a in node.args.args], "doc": ast.get_docstring(node)})
                elif isinstance(node, ast.ClassDef):
                    methods = [n.name for n in node.body if isinstance(n, ast.FunctionDef)]
                    classes.append({"name": node.name, "methods": methods, "doc": ast.get_docstring(node)})
        except Exception as e:
            return {"error": f"AST parse failed: {e}"}

        matches = [f for f in functions if f["name"] == target_symbol] + [c for c in classes if c["name"] == target_symbol]
        return {
            "target_symbol": target_symbol,
            "found_definitions": matches,
            "total_symbols_indexed": len(functions) + len(classes),
            "slice_ready": len(matches) > 0
        }

    def run_benchmark_ast_slicing(self):
        sample_code_a = """
import os, sys
from utils import helper_calc

class OrderProcessor:
    def process(self, order_id):
        return helper_calc(order_id)
"""
        sample_code_b = """
def helper_calc(val):
    return val * 10
"""
        files = {"main.py": sample_code_a, "utils.py": sample_code_b}
        graph = self.extract_import_graph(files)
        slice_res = self.slice_symbol_dependencies("OrderProcessor", sample_code_a)

        return {
            "suite": "Codebase AST Dependency Slicer Benchmark",
            "import_graph": graph,
            "symbol_slice": slice_res,
            "ast_parsing_engine": "Python Standard Library 'ast' Module"
        }
