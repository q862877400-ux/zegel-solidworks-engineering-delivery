"""★ 精确扫「**前置**依赖调用方选区」的工具族（★ 比 bunny 的"读到选区"精确）。

★ 判据（Lead 自己定，★ 与 bunny 的口径区别写在这里）：
  · bunny 用「函数体里**读到**选区」⇒ ★ 会把「**报告**选区」的工具（`measure_selection` /
    `selection_count` / `resolve_selection`）也算进去 ⇒ ★ **过宽**（★ 实测反证：
    `drawing_insert_surface_finish_symbol` 也没有 `pre_call`，★ 而它**真机建成过**）。
  · 本脚本用**更硬的两条信号**（满足其一才算）：
    ① ★ 函数返回的 dict 里有 **`preconditions_held`**，且同函数内有选区读（`GetSelectedObjectCount2`
       / `SelectionManager` / `_selection_marks` / `resolve_selection`）⇒ ★ **自报前置**；
    ② ★ 函数在**进入后**对选区计数做**比较/抛错**（同一个 `if` 语句里同时出现选区读与
       `raise` / `>= 1` / `< 1` / `not ` / `== 0`）。
  · ★ 两类都**不算**：只把选区**写进返回值**、或**主动去选**（`SelectByID2` / `Select4` /
    `resolve_selection` 作为**动作**）—— ★ 后者是"自己选"，不受事实 503 影响。
"""
from __future__ import annotations

import ast
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
REPO = Path(Path(__file__).resolve().parents[1])
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "mcp-server"))
sys.path.insert(0, str(REPO / "scripts"))
import register_capabilities as RC  # noqa: E402

READ_TOKENS = ("GetSelectedObjectCount2", "SelectionManager", "_selection_marks",
               "GetSelectedObject6", "GetSelectedObjectCount")
#: ★ 「要求」的信号词（在同一函数里与选区读同现才算）
REQUIRE_TOKENS = ("preconditions_held", "前置未成立", "没有选择", "未选择", "请先选", "先选好")


def func_src(mod_name: str, fn_name: str):
    p = REPO / "scripts" / (mod_name + ".py")
    if not p.is_file():
        return None
    try:
        tree = ast.parse(p.read_text(encoding="utf-8", errors="replace"))
    except SyntaxError:
        return None
    for n in ast.walk(tree):
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name == fn_name:
            return ast.get_source_segment(p.read_text(encoding="utf-8", errors="replace"), n) or ""
    return None


rows = []
for spec in RC.all_specs():
    name = getattr(spec, "name", None)
    if not name:
        continue
    pc = getattr(spec, "pre_call", None)
    if pc is not None:
        continue                                   #: ★ 有 pre_call 的**安全**，不看
    src = func_src(getattr(spec, "module", "") or "", getattr(spec, "function", "") or "")
    if not src:
        continue
    reads = [t for t in READ_TOKENS if t in src]
    if not reads:
        continue
    requires = [t for t in REQUIRE_TOKENS if t in src]
    #: ★★ 硬信号②：同一函数里"选区读"与"比较/抛错"同现
    hard = bool(requires)
    if not hard:
        for line in src.splitlines():
            if any(t in line for t in READ_TOKENS) and any(
                    k in line for k in (">= 1", "< 1", "== 0", "!= 0", "not ", "raise")):
                hard = True
                break
    rows.append((name, getattr(spec, "module", ""), getattr(spec, "function", ""),
                 ",".join(reads)[:34], ",".join(requires)[:22], "★硬" if hard else "软(仅报告)"))
rows.sort(key=lambda r: (r[5] != "★硬", r[0]))
hard = [r for r in rows if r[5] == "★硬"]
print("无 pre_call 且读到选区的工具：%d 条（★ 其中判据②命中的 **%d 条**）" % (len(rows), len(hard)))
print("%-50s %-22s %s" % ("工具", "读取的成员", "判据"))
print("-" * 108)
for r in rows:
    print("%-50s %-22s %s" % (r[0].replace("solidworks_", "")[:49], r[3], r[5]))
print()
print("★★ **判据②命中（最可能是真危险）**：")
for r in hard:
    print("   %-50s %s.%s" % (r[0].replace("solidworks_", "")[:49], r[1], r[2]))
