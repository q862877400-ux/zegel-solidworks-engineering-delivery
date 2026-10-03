"""★ 全局扫：所有 ToolSpec 里「目标函数真的读选区 且 没有 pre_call/derived_args」的工具。"""
from __future__ import annotations

import ast
import json
from pathlib import Path

ROOT = Path(r"D:\AI\SW")
SCR = ROOT / "scripts"

SEL_TOKENS = ("GetSelectedObjectCount2", "GetSelectedObject6", "GetSelectionPoint2",
              "GetSelectionPoint", "SelectionManager", "get_selection_count",
              "_get_selection_count", "_selection_count", "_selection_marks",
              "selection_count")

FAMILY = {}
for name, f in (("a", "preselect-family-a"), ("b", "preselect-family-b"),
                ("c", "preselect-family-c")):
    txt = (ROOT / "specs" / "202-user-coverage-gaps" / "recon" / f"{f}.md").read_text(encoding="utf-8")
    for tool in json.loads((ROOT / "specs" / "202-user-coverage-gaps" / "recon"
                            / "_all_specs.json").read_text(encoding="utf-8"))["specs"]:
        pass
    FAMILY[name] = txt


def func_src(module, function):
    p = SCR / f"{module}.py"
    if not p.exists():
        return None, None
    txt = p.read_text(encoding="utf-8")
    tree = ast.parse(txt)
    lines = txt.splitlines()
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == function:
            return "\n".join(lines[node.lineno - 1:node.end_lineno]), p.name
    return None, p.name


def main():
    specs = json.loads((ROOT / "specs" / "202-user-coverage-gaps" / "recon"
                        / "_all_specs.json").read_text(encoding="utf-8"))["specs"]
    hits = []
    for s in specs:
        if s["pre_call"] or s["derived_args"]:
            continue
        src, fname = func_src(s["module"], s["function"])
        if not src:
            continue
        toks = sorted({t for t in SEL_TOKENS if t in src})
        if toks:
            hits.append(dict(name=s["name"], file=s["file"], module=s["module"],
                             function=s["function"], tokens=toks,
                             in_a=s["name"] in FAMILY["a"], in_b=s["name"] in FAMILY["b"],
                             in_c=s["name"] in FAMILY["c"]))
    print(f"读选区 且 无 pre_call/derived_args：{len(hits)} 条\n")
    for h in hits:
        fam = ("A" if h["in_a"] else "") + ("B" if h["in_b"] else "") + ("C" if h["in_c"] else "") or "-"
        print(f"{h['name'][:56]:56} fam={fam:3} {h['file']:26} {h['module']}.{h['function']}  {h['tokens']}")
    (ROOT / "specs" / "202-user-coverage-gaps" / "recon" / "_global_sweep.json").write_text(
        json.dumps(hits, ensure_ascii=False, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()