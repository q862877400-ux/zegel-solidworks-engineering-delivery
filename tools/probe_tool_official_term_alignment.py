"""★ 检验一个假设（业主 2026-10-04）：「我们的英文词与官方文档没对应，对应上准确率就好了」。

★ 怎么机械地量「对应」：
  对每个 ToolSpec：读 `scripts/<module>.py` 里**该函数体**内逐字出现的 **COM 成员名**
  ⇒ 再比较【工具名 + 描述里的词】与【官方成员名的词】是否**有交集**
  ⇒ ★ 有交集 = 我们的命名/描述里用上了官方术语；无交集 = 没对上 ✓

★ 为什么这是可判的：★ 官方成员名来自**官方 API**（`C:\\swapi\\types`），
  所以「工具名包含官方成员的关键词」= 一个**可复核的对应关系** ✓
★ ⚠ 诚实边界：这是**词面**对应，不是**语义**对应；★ 且对**非官方成员**的工具
  （本仓自研的 Win32/GUI 层，如 `sw_gui_modal`）**这条判据不适用** —— 会单独报出来 ✓
"""
from __future__ import annotations

import ast
import io
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(Path(__file__).resolve().parents[1])
for _p in (str(ROOT), str(ROOT / "scripts"), str(ROOT / "mcp-server")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import metric_scope as ms   # ★ 口径注册表（★ 事实 517：口径必须落成代码）
import register_capabilities as rc                                    # noqa: E402

WORD = re.compile(r"[A-Za-z][A-Za-z0-9]{2,}")


def words(text: str) -> set:
    """★ 拆词：驼峰切开 + 下划线切开 + 小写化（★ 与检索器的口径一致）。"""
    text = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", " ", text)
    return {w.lower() for w in WORD.findall(text)}


def member_names(module: str, function: str) -> list:
    """★ 取该函数体内**逐字出现的 COM 成员名**（形如 `get_com_member(x, "Name")`）。"""
    p = ROOT / "scripts" / (module + ".py")
    if not p.is_file():
        return []
    try:
        tree = ast.parse(p.read_text(encoding="utf-8", errors="replace"))
    except Exception:                                                  # noqa: BLE001
        return []
    fn = None
    for n in ast.walk(tree):
        if isinstance(n, ast.FunctionDef) and n.name == function:
            fn = n
            break
    if fn is None:
        return []
    found = []
    for n in ast.walk(fn):
        #: 形如 get_com_member(obj, "Member") / _checked(obj, "Member", ...)
        if isinstance(n, ast.Call) and len(n.args) >= 2:
            a1 = n.args[1]
            if isinstance(a1, ast.Constant) and isinstance(a1.value, str):
                found.append(a1.value)
    return found


#: ★ 非官方成员的模块（本仓自研 GUI/GUI 层 ⇒ 判据不适用）
NON_API = {"sw_gui_modal", "sw_gui_focus", "sw_chamfer_geometry", "sw_capture", "sw_isolate",
           "sw_com_traps", "sw_gui_focus", "sw_gui_modal"}

rows = []
for s in rc.all_specs():
    mem = member_names(getattr(s, "module", ""), getattr(s, "function", ""))
    mem_w = set()
    for m in mem:
        mem_w |= words(m)
    #: ★ 工具面（名字 + 标题 + 描述）
    surf = words(" ".join([s.name, getattr(s, "title", "") or "", getattr(s, "doc", "") or ""]))
    overlap = mem_w & surf
    rows.append({"tool": s.name, "module": getattr(s, "module", ""), "members": mem[:3],
                 "member_words": sorted(mem_w), "overlap": sorted(overlap),
                 "n_mem": len(mem_w), "n_ovl": len(overlap),
                 "is_api": getattr(s, "module", "") not in NON_API and bool(mem)})

api = [r for r in rows if r["is_api"] and r["n_mem"]]
none_mem = [r for r in rows if not r["members"]]
aligned = [r for r in api if r["n_ovl"] > 0]
zero = [r for r in api if r["n_ovl"] == 0]

print("★ 共 %d 个 ToolSpec" % len(rows))
print()
print(ms.block_for('official_term_alignment'))
print("★ 其中**取不到 COM 成员名**的 %d 个（★ 多是纯计算/本仓自研层）" % len(none_mem))
print("★ 能取到成员名的 **%d** 个 ⇒ 用它们量「词面对应」:" % len(api))
print()
print("   ★ 工具面与官方成员名**有词交集**（对上了）: **%d / %d = %.1f%%**"
      % (len(aligned), len(api), 100.0 * len(aligned) / max(1, len(api))))
print("   ★★ **词交集为 0**（没对上）: **%d / %d = %.1f%%**"
      % (len(zero), len(api), 100.0 * len(zero) / max(1, len(api))))
print()
print("★★ 没对上的一半里，**前 20 个**（工具名 vs 它调的官方成员）:")
for r in zero[:20]:
    print("   %-46s ← %s" % (r["tool"].removeprefix("solidworks_")[:44],
                              ", ".join(r["members"])[:48]))
print()
print("★ 按域统计（未对齐数 / 该域有成员名的数）:")
agg = Counter()
tot = Counter()
for r in api:
    tot[r["module"]] += 1
    if r["n_ovl"] == 0:
        agg[r["module"]] += 1
for m, n in tot.most_common(12):
    print("   %-26s %d / %d" % (m, agg[m], n))
