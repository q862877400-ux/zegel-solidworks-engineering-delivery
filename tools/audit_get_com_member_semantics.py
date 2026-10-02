r"""@brief 审计：`get_com_member(x, "Name")`（**无实参**）的调用点里，哪些 `Name` 是**方法**？

## 为什么要查（2026-10-01 轮 143 查出的机制）
`sw_connect.get_com_member` 在**没有实参**时会「**先试调一次**」以分辨属性与方法
⇒ ★ **对 COM 成员，「取」就等于「调」**。
⚠ 危险面：**无必填参数且有副作用**的成员（`InsertDeleteHole()`、`File*` 写盘方法）
会**被「取」这个动作静默执行**。
⇒ ★ 本轮把**影响面**量清楚：**哪些调用点**会踩到这个机制。

## 判法（**结构**：源码形态 × 反射成员表）
```
① 扫 scripts/ + mcp-server/ 里**无实参**的 `get_com_member(obj, "Name")` 调用点；
② 在出厂反射 `iface_*.txt` 里找 `Name` 的声明；
③ 若它**是方法**（声明带 `(`）⇒ ★ 那个调用点**会真的调一次**（若它没有必填参数）
   ⚠ 若有必填参数 ⇒ 抛 `DISP_E_PARAMNOTOPTIONAL`（本轮的 `InsertDome` 就是这种）
```
⚠ 这是**结构**判据（源码形态 + 名字在反射里的种类），**不做语义推断** ⇒ 可靠。

# ── 来源 ──
# 仓库:   本项目自身（只读审计）
# 文件:   tools/audit_get_com_member_semantics.py
# 定位:   给 Spec Kit `063` 取证：`get_com_member`「取即调」的影响面。
# 官方依据: 出厂反射 `D:\AI\SW\_raw\**\iface_*.txt`
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import ast
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.stdout.reconfigure(encoding="utf-8")

RAW = Path(r"D:\AI\SW\_raw")
OUT = Path(r"D:\AI\SW\output\get_com_member-semantics-audit.json")
#: 明显**只读**的方法名（试探性调它们无害）—— 留着好把清单缩到"要看的那几个"
HARMLESS_PREFIX = ("Get", "Is", "Has", "IGet")


def reflection_members() -> dict:
    """`名字 -> {'methods': [...], 'props': [...]}`（来自出厂反射）。"""
    table: dict = defaultdict(lambda: {"methods": [], "props": []})
    for p in RAW.rglob("iface_*.txt"):
        for line in p.read_text(encoding="utf-8", errors="replace").splitlines():
            s = line.strip()
            m = re.match(r"^(?:Void|Boolean|Int32|Double|String|Object|SketchSegment|"
                         r"Feature|Face2|Body2|[\w.]+)\s+(\w+)\s*\((.*)\)$", s)
            if m and "(" in s:
                table[m.group(1)]["methods"].append(m.group(2))
                continue
            m2 = re.match(r"^([\w.]+)\s+(\w+)\s*$", s)
            if m2 and not s.startswith(("//", "#")):
                table[m2.group(2)]["props"].append(m2.group(1))
    return table


def find_call_sites():
    """**无实参**的 `get_com_member(obj, "Name")` 调用点。"""
    sites = []
    for base in ("scripts", "mcp-server"):
        for p in sorted((ROOT / base).glob("*.py")):
            try:
                tree = ast.parse(p.read_text(encoding="utf-8", errors="replace"))
            except SyntaxError:
                continue
            for node in ast.walk(tree):
                if not isinstance(node, ast.Call):
                    continue
                f = node.func
                name = f.id if isinstance(f, ast.Name) else (
                    f.attr if isinstance(f, ast.Attribute) else None)
                if name not in ("get_com_member", "safe_get_com_member"):
                    continue
                if len(node.args) < 2 or node.args[1].__class__ is not ast.Constant:
                    continue
                member = node.args[1].value
                if not isinstance(member, str):
                    continue
                bare = len(node.args) == 2 and not node.keywords
                sites.append({"file": str(p.relative_to(ROOT)), "line": node.lineno,
                              "member": member, "no_args": bare})
    return sites


def main() -> int:
    table = reflection_members()
    sites = find_call_sites()
    print("  `get_com_member` 调用点（能静态取到成员名）: **%d**" % len(sites))
    total = sum(1 for _ in sites)
    no_arg = [s for s in sites if s["no_args"]]
    print("    其中**无实参**（会走「先试调一次」那条路）: **%d**" % len(no_arg))
    print()

    #: 分类
    by_member = defaultdict(list)
    for s in no_arg:
        by_member[s["member"]].append(s)

    as_method, as_prop, unknown = [], [], []
    for member, ss in sorted(by_member.items()):
        info = table.get(member)
        if not info:
            unknown.append((member, ss))
        elif info["methods"]:
            as_method.append((member, ss, info["methods"][:2]))
        else:
            as_prop.append((member, ss))

    print("  ── ① `Name` 在反射里**是方法** ⇒ ★ 这些调用点**会真的调一次** ──")
    print("     共 **%d** 个不同的成员名 / **%d** 个调用点" %
          (len(as_method), sum(len(x[1]) for x in as_method)))
    harmless = 0
    for member, ss, sigs in as_method:
        ro = member.startswith(HARMLESS_PREFIX)
        harmless += 1 if ro else 0
        flag = "（**只读**前缀 ⇒ 试探无害）" if ro else "★★ **要看**"
        print("     %-34s %d 处 %s  例: %s" % (member, len(ss), flag, sigs[0][:40] if sigs else ""))
    print()
    print("  ── ② `Name` 在反射里**只有属性** ⇒ 试探调会失败但**无害** ──")
    print("     共 **%d** 个成员名" % len(as_prop))
    for member, ss in as_prop[:8]:
        print("     %-34s %d 处" % (member, len(ss)))
    if len(as_prop) > 8:
        print("     …（还有 %d 个）" % (len(as_prop) - 8))
    print()
    print("  ── ③ 反射里**查不到**该名字 ⇒ 属「查不到」（铁律 5），另记 ──")
    print("     共 **%d** 个成员名 %s" % (len(unknown), [u[0] for u in unknown[:8]]))

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({
        "total_sites": total, "no_arg_sites": len(no_arg),
        "as_method": [{"member": m, "sites": s, "sigs": sig} for m, s, sig in as_method],
        "as_property": [{"member": m, "sites": s} for m, s in as_prop],
        "unknown": [{"member": m, "sites": s} for m, s in unknown],
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print()
    print("  证据: %s" % OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
