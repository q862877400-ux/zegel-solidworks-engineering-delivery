"""★ AST 枚举全部 ToolSpec：解析 `_spec(...)` 工厂（含跨文件 import 的 batch58/60）。"""
from __future__ import annotations

import ast
import json
import re
from pathlib import Path

ROOT = Path(r"D:\AI\SW")
MCP = ROOT / "mcp-server"


def _const(node):
    try:
        return ast.literal_eval(node)
    except Exception:
        return None


def _nm(node):
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return _nm(node.value) + "." + node.attr
    if isinstance(node, ast.Call):
        return _nm(node.func)
    return None


class Factory:
    """A helper function that returns a ToolSpec; records its fixed kwargs."""

    def __init__(self, name, module_kw, function_pos_idx, fixed):
        self.name = name
        self.module_kw = module_kw
        self.function_pos_idx = function_pos_idx
        self.fixed = fixed  # pre_call / derived_args / inject


def analyse(path: Path, factories: dict):
    tree = ast.parse(path.read_text(encoding="utf-8"))
    local_factories = {}

    # 1) find local factories: `def _xxx(...) -> ToolSpec:` containing a ToolSpec(...) call
    for fn in [n for n in tree.body if isinstance(n, ast.FunctionDef)]:
        for sub in ast.walk(fn):
            if isinstance(sub, ast.Call) and (_nm(sub.func) or "").endswith("ToolSpec"):
                kw = {k.arg: k.value for k in sub.keywords if k.arg}
                args = [a.arg for a in fn.args.args]
                fpos = None
                # function usually the param whose default/bodies reference module pattern
                for i, a in enumerate(args):
                    if a in ("function", "func", "fn", "target", "func_name"):
                        fpos = i
                fixed = {
                    "module": _const(kw.get("module")),
                    "pre_call": _nm(kw.get("pre_call")) if kw.get("pre_call") is not None else None,
                    "derived_args": _nm(kw.get("derived_args")) if kw.get("derived_args") is not None else None,
                    "inject": _const(kw.get("inject")),
                }
                local_factories[fn.name] = Factory(fn.name, None, fpos, fixed)
                break

    # 2) imported factories
    for node in tree.body:
        if isinstance(node, ast.ImportFrom) and node.module:
            for a in node.names:
                if a.name in factories and a.name not in local_factories:
                    local_factories[a.name] = factories[a.name]

    # module-level constant aliases (for Param lists / string constants)
    consts = {}
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for t in node.targets:
                if isinstance(t, ast.Name):
                    consts[t.id] = node.value

    def dconst(node, depth=0):
        if depth > 5 or node is None:
            return node
        if isinstance(node, ast.Name) and node.id in consts:
            return dconst(consts[node.id], depth + 1)
        return node

    out = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        fname = _nm(node.func) or ""
        base = fname.split(".")[-1]
        pos = [dconst(a) for a in node.args]
        kw = {k.arg: dconst(k.value) for k in node.keywords if k.arg}

        if base == "ToolSpec":
            name = _const(kw.get("name")) or (_const(pos[0]) if pos else None)
            if not isinstance(name, str):
                continue
            module = _const(kw.get("module"))
            function = _const(kw.get("function"))
            if not function:
                sws = [v for v in (_const(p) for p in pos[1:8]) if isinstance(v, str) and v.startswith("sw_")]
                if module and sws:
                    function = sws[-1]
                elif len(sws) >= 2:
                    module, function = sws[0], sws[1]
            pre = _nm(kw.get("pre_call")) if kw.get("pre_call") is not None else None
            der = _nm(kw.get("derived_args")) if kw.get("derived_args") is not None else None
            inject = _const(kw.get("inject"))
            params = []
            plist = []
            if kw.get("params") is not None and isinstance(kw["params"], (ast.List, ast.Tuple)):
                plist = list(kw["params"].elts)
            plist += [c for c in pos if isinstance(c, ast.Call)
                      and (_nm(c.func) or "").endswith("Param")]
            for c in plist:
                if isinstance(c, ast.Call) and (_nm(c.func) or "").endswith("Param"):
                    pkw = {k.arg: _const(k.value) for k in c.keywords if k.arg}
                    pname = _const(c.args[0]) if c.args else None
                    params.append({"name": pname, "default": pkw.get("default"),
                                   "desc": (pkw.get("desc") or pkw.get("description") or "")})
            doc = _const(kw.get("doc"))
            title = _const(kw.get("title"))
            out.append(dict(file=path.name, name=name, module=module, function=function,
                            pre_call=pre, derived_args=der, inject=inject, doc=doc,
                            title=title, params=params, via="ToolSpec"))
            continue

        if base in local_factories:
            fac = local_factories[base]
            name = _const(kw.get("name")) or (_const(pos[0]) if pos and _const(pos[0]) else None)
            if not isinstance(name, str):
                continue
            module = _const(kw.get("module")) or fac.fixed["module"]
            function = None
            for k in ("function", "func", "fn", "target"):
                if kw.get(k) is not None:
                    function = _const(kw[k])
            if not function and fac.function_pos_idx is not None:
                idx = fac.function_pos_idx
                if idx < len(pos):
                    function = _const(pos[idx])
            if not function:
                sws = [v for v in (_const(p) for p in pos[1:8]) if isinstance(v, str) and v.startswith("sw_")]
                if module and sws:
                    function = sws[-1]
                elif len(sws) >= 2:
                    module, function = sws[0], sws[1]
            pre = fac.fixed["pre_call"]
            der = fac.fixed["derived_args"]
            inject = fac.fixed["inject"]
            params = []
            plist = []
            if kw.get("params") is not None and isinstance(kw["params"], (ast.List, ast.Tuple)):
                plist = list(kw["params"].elts)
            plist += [c for c in pos if isinstance(c, ast.Call)
                      and (_nm(c.func) or "").endswith("Param")]
            for c in plist:
                if isinstance(c, ast.Call) and (_nm(c.func) or "").endswith("Param"):
                    pkw = {k.arg: _const(k.value) for k in c.keywords if k.arg}
                    params.append({"name": _const(c.args[0]) if c.args else None,
                                   "default": pkw.get("default"),
                                   "desc": (pkw.get("desc") or pkw.get("description") or "")})
            doc = _const(kw.get("doc")) or (_const(pos[3]) if len(pos) > 3 else None)
            out.append(dict(file=path.name, name=name, module=module, function=function,
                            pre_call=pre, derived_args=der, inject=inject, doc=doc,
                            title=_const(kw.get("title")) or (_const(pos[1]) if len(pos) > 1 else None),
                            params=params, via=base))

    for f in local_factories.values():
        factories.setdefault(f.name, f)
    seen = {}
    for s in out:
        k = (s["file"], s["name"])
        if k not in seen:
            seen[k] = s
    return list(seen.values())


def main():
    files = sorted(MCP.glob("tool_specs_batch*.py"),
                   key=lambda p: int(re.search(r"batch(\d+)", p.name).group(1)))
    factories = {}
    all_specs = []
    per_file = {}
    for f in files:
        s = analyse(f, factories)
        per_file[f.name] = len(s)
        all_specs.extend(s)
    names = [s["name"] for s in all_specs]
    dupes = sorted({n for n in names if names.count(n) > 1})
    miss_fn = [s["name"] for s in all_specs if not s["function"]]
    miss_mod = [s["name"] for s in all_specs if not s["module"]]
    with_pre = [s for s in all_specs if s["pre_call"]]
    payload = dict(total_specs=len(all_specs), files=len(files), per_file=per_file,
                   dupe_names=dupes, missing_function=miss_fn, missing_module=miss_mod,
                   with_pre_call=len(with_pre), specs=all_specs)
    outp = ROOT / "specs" / "202-user-coverage-gaps" / "recon" / "_all_specs.json"
    outp.write_text(json.dumps(payload, ensure_ascii=False, indent=1), encoding="utf-8")
    print("files:", len(files), "specs:", len(all_specs), "with_pre_call:", len(with_pre))
    print("dupes:", len(dupes), dupes[:10])
    print("missing_function:", len(miss_fn), miss_fn[:20])
    print("missing_module:", len(miss_mod), miss_mod[:20])
    print("pre_call names:", sorted({s["pre_call"] for s in with_pre}))


if __name__ == "__main__":
    main()