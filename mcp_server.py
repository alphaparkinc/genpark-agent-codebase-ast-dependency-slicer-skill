import sys, json
from client import CodebaseASTDependencySlicer

def handle_mcp():
    slicer = CodebaseASTDependencySlicer()
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        print(json.dumps(slicer.run_benchmark_ast_slicing(), indent=2))
        return

    for line in sys.stdin:
        if not line.strip(): continue
        try:
            req = json.loads(line)
            method = req.get("method")
            msg_id = req.get("id")
            
            if method == "initialize":
                resp = {"jsonrpc": "2.0", "id": msg_id, "result": {
                    "protocolVersion": "2024-11-05",
                    "serverInfo": {"name": "genpark-agent-codebase-ast-dependency-slicer-skill", "version": "1.0.0"},
                    "capabilities": {"tools": {}}
                }}
            elif method == "tools/list":
                resp = {"jsonrpc": "2.0", "id": msg_id, "result": {"tools": [
                    {"name": "extract_import_graph", "description": "Extract file-level import relationships.", "inputSchema": {"type": "object", "properties": {"file_contents_map": {"type": "object"}}}},
                    {"name": "slice_symbol_dependencies", "description": "Generate minimal transitive sub-graph for symbol.", "inputSchema": {"type": "object", "properties": {"target_symbol": {"type": "string"}, "code_snippet": {"type": "string"}}}},
                    {"name": "run_benchmark_ast_slicing", "description": "Benchmark AST slicing speed and graph resolution.", "inputSchema": {"type": "object"}}
                ]}}
            elif method == "tools/call":
                tname = req.get("params", {}).get("name")
                args = req.get("params", {}).get("arguments", {})
                if tname == "extract_import_graph":
                    res = slicer.extract_import_graph(args.get("file_contents_map", {}))
                elif tname == "slice_symbol_dependencies":
                    res = slicer.slice_symbol_dependencies(args.get("target_symbol", ""), args.get("code_snippet", ""))
                else:
                    res = slicer.run_benchmark_ast_slicing()
                resp = {"jsonrpc": "2.0", "id": msg_id, "result": {"content": [{"type": "text", "text": json.dumps(res, indent=2)}]}}
            else:
                resp = {"jsonrpc": "2.0", "id": msg_id, "error": {"code": -32601, "message": "Method not found"}}
            
            sys.stdout.write(json.dumps(resp) + "\n")
            sys.stdout.flush()
        except Exception as e:
            sys.stdout.write(json.dumps({"jsonrpc": "2.0", "error": {"code": -32000, "message": str(e)}}) + "\n")
            sys.stdout.flush()

if __name__ == "__main__":
    handle_mcp()
