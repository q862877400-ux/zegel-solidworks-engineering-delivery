import sys
sys.path.insert(0, "mcp-server")
import importlib
want = {"create_one_bend", "create_draft", "create_edge_flange", "create_gusset", "create_base_flange", "create_swept_flange"}
for i in (2, 3, 4):
    m = importlib.import_module("tool_specs_batch%d" % i)
    specs = next(getattr(m, n) for n in dir(m) if n.startswith("SPECS_"))
    for s in specs:
        if s.function in want:
            print("### %s  [batch%d]  module=%s function=%s" % (s.name, i, s.module, s.function))
            print("    doc: %s" % (s.doc or "(none)"))
            print("    params: %s" % [p.name for p in s.params])
            print("    pre_call: %s  derived_args: %s" % (bool(s.pre_call), bool(s.derived_args)))
