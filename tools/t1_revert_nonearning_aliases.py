"""★ T1-6：按 D-2 判据收口 —— 留下**真提升**的 5 个别名，回退其余 5 个。"""
from __future__ import annotations

import ast
import json
import sys
from pathlib import Path

ROOT = Path(Path(__file__).resolve().parents[1])
MCP = ROOT / "mcp-server"
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
MARK = "★ 别名:"

joint = json.loads((ROOT / "output" / "t1-joint-gain.json").read_text(encoding="utf-8"))
keep = {r["tool"] for r in joint["rows"] if r["delta"] and r["delta"] > 0}
drop = {r["tool"] for r in joint["rows"] if not (r["delta"] and r["delta"] > 0)}
print("★ 留下（联合下有提升）: %d 个" % len(keep))
for t in sorted(keep):
    r = next(x for x in joint["rows"] if x["tool"] == t)
    print("   ✓ %-40s %s → %s" % (t.removeprefix("solidworks_"), r["rank_stripped"], r["rank_joint"]))
print("★ 回退（无提升 ⇒ 别名挣不到字节）: %d 个" % len(drop))
for t in sorted(drop):
    r = next(x for x in joint["rows"] if x["tool"] == t)
    print("   ✗ %-40s %s → %s" % (t.removeprefix("solidworks_"), r["rank_stripped"], r["rank_joint"]))


def strip_alias(path: Path, tool: str) -> str:
    """★ 精确移除那一段 `★ 别名: …`（★ 只删我插的那段，别的不动）。"""
    src = path.read_text(encoding="utf-8")
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        kw = {k.arg: k.value for k in node.keywords if k.arg}
        nm = kw.get("name")
        if not (isinstance(nm, ast.Constant) and nm.value == tool):
            continue
        doc = kw.get("doc")
        val = getattr(doc, "value", "")
        if MARK not in val:
            return "没有别名行"
        head = val.split(MARK)[0].rstrip()
        #: ★ 直接把整个 doc 值重写成"剥掉别名"的版本（★ 源码里是字面量，重写安全且可核对）
        lines = src.splitlines(keepends=True)
        endline = lines[doc.end_lineno - 1]
        #: ★ 把该值的源码区间替换成一个单行字面量（★ 用 repr 保证转义正确）
        start = lines[doc.lineno - 1][:doc.col_offset]
        newline = "%s%r%s" % (start, head, endline[
            len(endline.encode("utf-8")[:doc.end_col_offset].decode("utf-8", "ignore")):])
        lines[doc.lineno - 1:doc.end_lineno] = [newline]
        path.write_text("".join(lines), encoding="utf-8")
        ast.parse(path.read_text(encoding="utf-8"))      #: ★ 立刻语法自检
        return "已回退"
    return "没找到该 ToolSpec"


for tool in sorted(drop):
    hit = None
    for f in sorted(MCP.glob("tool_specs_batch*.py")):
        if ('"%s"' % tool) in f.read_text(encoding="utf-8"):
            hit = f
            break
    if hit is None:
        print("   ★ 没找到声明: %s" % tool)
        continue
    print("   %-42s %s · %s" % (tool.removeprefix("solidworks_"), hit.name, strip_alias(hit, tool)))
