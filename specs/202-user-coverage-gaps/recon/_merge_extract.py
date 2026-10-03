"""★ AST 枚举 mcp-server/tool_specs_batch*.py 里的全部 ToolSpec（不 import）。"""
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


def _name(node):
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return _name(node.value) + "." + node.attr
    if isinstance(node, ast.Call):
        return _name(node.func)
    return None


def scan_file(path: Path):
    """Return list of spec dicts found in one file (handles ToolSpec(...) and _spec(...))."""
    tree = ast.parse(path.read_text(encoding="utf-8"))
    # collect module-level constants so we can resolve simple aliases
    consts = {}
    for node in tree.body:
        if isinstance(node, (ast.Assign, ast.AnnAssign)):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            val = node.value
            for t in targets:
                if isinstance(t, ast.Name):
                    consts[t.id] = val

    def resolve(node, depth=0):
        """Follow Name -> assigned node, up to a few hops."""
        if depth > 6 or node is None:
            return node
        if isinstance(node, ast.Name) and node.id in consts:
            return resolve(consts[node.id], depth + 1)
        if isinstance(node, ast.Call):
            fn = _name(node.func)
            if fn and fn.split(".")[-1] in ("ToolSpec", "_spec"):
                return node
            # _spec(name, module, function, ...) style
            return node
        return node

    out = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            fn = _name(node.func) or ""
            base = fn.split(".")[-1]
            if base not in ("ToolSpec", "_spec"):
                continue
            kw = {k.arg: k.value for k in node.keywords if k.arg}
            # positional: infer ToolSpec(name, module, function, ...) or _spec(...)
            pos = list(node.args)
            name = None
            module = None
            function = None
            if base == "ToolSpec":
                cand = [kw.get("name"), (pos[0] if len(pos) > 0 else None),
                        kw.get("tool_name"), kw.get("tool")]
                for c in cand:
                    v = _const(c) if c is not None else None
                    if isinstance(v, str) and v:
                        name = v
                        break
                for key in ("module", "module_name"):
                    if key in kw:
                        v = _const(kw[key])
                        if isinstance(v, str):
                            module = v
                for key in ("function", "func", "function_name", "fn"):
                    if key in kw:
                        v = _const(kw[key])
                        if isinstance(v, str):
                            function = v
                # positional fallbacks
                if module is None:
                    for c in pos[1:6]:
                        v = _const(c)
                        if isinstance(v, str) and re.match(r"^sw_", v):
                            module = v
                            break
                if function is None:
                    got = False
                    for c in pos[1:7]:
                        v = _const(c)
                        if isinstance(v, str) and re.match(r"^sw_", v):
                            if module is None:
                                module = v
                            else:
                                function = v
                            got = True
                if function is None and module is not None:
                    # last sw_* positional may be the function when module known separately
                    pass
            else:  # _spec(...)
                v0 = _const(pos[0]) if pos else None
                if isinstance(v0, str):
                    name = v0
                for key in ("module",):
                    if key in kw:
                        v = _const(kw[key])
                        if isinstance(v, str):
                            module = v
                for key in ("function", "func", "fn", "target"):
                    if key in kw:
                        v = _const(kw[key])
                        if isinstance(v, str):
                            function = v
                if module is None or function is None:
                    sws = []
                    for c in pos[1:8]:
                        v = _const(c)
                        if isinstance(v, str) and re.match(r"^sw_", v):
                            sws.append(v)
                    if module is None and sws:
                        module = sws[0]
                    if function is None and len(sws) > 1:
                        function = sws[1]
            if not name:
                continue
            pre = None
            if "pre_call" in kw:
                pre = _name(kw["pre_call"]) or ast.dump(kw["pre_call"])[:80]
            elif len(pos) > 0:
                # some specs pass pre_call positionally - hard to tell; mark unknown
                pass
            derived = None
            if "derived_args" in kw:
                derived = _name(kw["derived_args"]) or "?"
            inject = None
            if "inject" in kw:
                inject = _const(kw["inject"])
            doc = _const(kw.get("doc")) if "doc" in kw else None
            params = []
            for c in pos:
                if _name(c) == "Param" or (isinstance(c, ast.Call) and (_name(c.func) or "").endswith("Param")):
                    pname = _const(c.args[0]) if c.args else None
                    pkw = {k.arg: _const(k.value) for k in c.keywords if k.arg}
                    params.append({"name": pname, "default": pkw.get("default"),
                                   "desc": pkw.get("desc") or pkw.get("description")})
            out.append({
                "file": path.name, "name": name, "module": module, "function": function,
                "pre_call": pre, "derived_args": derived, "inject": inject,
                "doc": doc, "params": params,
            })
    # dedupe by (file,name)
    seen = {}
    for s in out:
        k = (s["file"], s["name"])
        if k not in seen or (s["module"] and not seen[k]["module"]):
            seen[k] = s
    return list(seen.values())


def main():
    files = sorted(MCP.glob("tool_specs_batch*.py"),
                   key=lambda p: int(re.search(r"batch(\d+)", p.name).group(1)))
    all_specs = []
    per_file = {}
    for f in files:
        s = scan_file(f)
        per_file[f.name] = len(s)
        all_specs.extend(s)
    names = [s["name"] for s in all_specs]
    dupes = sorted({n for n in names if names.count(n) > 1})
    missing_fn = [s["name"] for s in all_specs if not s["function"]]
    missing_mod = [s["name"] for s in all_specs if not s["module"]]
    payload = {
        "total_specs": len(all_specs),
        "files": len(files),
        "per_file": per_file,
        "dupe_names": dupes,
        "missing_function": missing_fn,
        "missing_module": missing_mod,
        "specs": all_specs,
    }
    outp = ROOT / "specs" / "202-user-coverage-gaps" / "recon" / "_all_specs.json"
    outp.write_text(json.dumps(payload, ensure_ascii=False, indent=1), encoding="utf-8")
    print("files:", len(files), "specs:", len(all_specs))
    print("dupes:", len(dupes), dupes[:10])
    print("missing_function:", len(missing_fn), missing_fn[:15])
    print("missing_module:", len(missing_mod), missing_mod[:15])


if __name__ == "__main__":
    main()