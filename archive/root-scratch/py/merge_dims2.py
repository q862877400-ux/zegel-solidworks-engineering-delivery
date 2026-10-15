# -*- coding: utf-8 -*-
"""把 interop 维度普查并进 12 份 sw_api_* 索引（重写版，从零来）。"""
from __future__ import annotations

import ast
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except Exception:
        pass

CENSUS = Path(r"D:\AI\SW\interop-dimension-census.json")
SCRIPTS = Path(r"C:\swprojects\sw-skill-fork\scripts")

DOC = '''# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   SolidWorks 官方 interop 程序集**自身的元数据**
# 文件:   D:\\AI\\SW\\interop-dimension-census.json（40,921 行全量普查）
# 定位:   每个成员的**调用属性**维度 —— 属性方向、是否内部使用、DISPID。
# ⚑ 这些维度**不是本项目推断的**，是官方程序集里本来就有的：
#     · CanRead / CanWrite   ← System.Reflection.PropertyInfo
#     · [OutAttribute]       ← 参数方向（决定要不要包 VARIANT 拿回值）
#     · FHidden              ← SolidWorks 标「内部使用」的属性
#                              （⚠ **全 assembly 命中 0 次 [Obsolete]**
#                                —— 记 obsolete 这一栏永远是空的）
#     · DispIdAttribute      ← makepy 生成物的主键，可精确 join
# ⚑ 已用三个独立源交叉验证（typelib / interop DLL / makepy），
#   只写属性 10 个三源完全一致、数量对账吻合。
# ⚠ 读取方式是**纯元数据**（读程序集 / typelib），
#   **未启动 SolidWorks 进程、未做任何 COM 实例化调用**。
# 覆盖:   后续同级定义
# ⚠ 本组为静态照录，未在本机实测 SolidWorks 行为（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
'''

TABLES = [
    ("READONLY",
     "只读属性 —— 只能读，传 set 会失败",
     ": dict[str, tuple[str, ...]]"),
    ("WRITEONLY",
     "只写属性 —— ⚠ **读它会报 -2147352567「无法读只写属性」**"
     "（错误文本随 UI 语言变化；pywin32 源码里无此消息，属本地化 HRESULT）",
     ": dict[str, tuple[str, ...]]"),
    ("HIDDEN",
     "内部使用成员 —— 官方标了 FHidden，**不应当作公开能力调用**"
     "（典型是 `Dummy1..19` 这类占位，以及 `IModelDocExtension.ExtractImageData`）",
     ": dict[str, tuple[str, ...]]"),
    ("DISPID",
     "成员名 → DISPID（makepy 生成物用它做主键，可与 wrapper 精确 join）",
     ": dict[str, dict[str, int]]"),
]


def short(t: str) -> str:
    n = t.split(".")[-1]
    return n[:-5] if n.endswith("Class") else n


def render(name: str, desc: str, ann: str, body: str) -> str:
    return f"#: {desc}\n{name}{ann} = {{{body}}}\n\n\n"


def main() -> int:
    rows = json.loads(CENSUS.read_text(encoding="utf-8"))
    ro: dict[str, set] = defaultdict(set)
    wo: dict[str, set] = defaultdict(set)
    hid: dict[str, set] = defaultdict(set)
    disp: dict[str, dict] = defaultdict(dict)
    for r in rows:
        f, n = short(r["type"]), r["name"]
        if r.get("hidden"):
            hid[f].add(n)
        raw = r.get("disp_id")
        if raw is not None:
            # ⚑ 普查里 disp_id 混了 str / int，个别值还带前导 "="（如 "=2150"）
            try:
                disp[f][n] = int(str(raw).lstrip("="))
            except (TypeError, ValueError):
                pass
        if r["kind"] != "property":
            continue
        if r["can_write"] and not r["can_read"]:
            wo[f].add(n)
        elif r["can_read"] and not r["can_write"]:
            ro[f].add(n)

    totals = {t[0]: 0 for t in TABLES}
    for p in sorted(SCRIPTS.glob("sw_api_*.py")):
        src = p.read_text(encoding="utf-8")
        fams = re.findall(r"^    '(I\w+)': \{", src, re.M)
        if not fams:
            continue
        out = [src.rstrip("\n"), "", "", DOC.rstrip("\n"), ""]
        for name, desc, ann in TABLES:
            lines = []
            for f in fams:
                if name == "DISPID":
                    d = disp.get(f)
                    if not d:
                        continue
                    lines.append("    %r: {" % f)
                    for k, v in sorted(d.items()):
                        lines.append("        %r: %d," % (k, v))
                    lines.append("    },")
                    totals[name] += len(d)
                else:
                    pool = {"READONLY": ro, "WRITEONLY": wo, "HIDDEN": hid}[name].get(f)
                    if not pool:
                        continue
                    for k in sorted(pool):
                        lines.append("    %r: (%r,)," % (f, k))
                    totals[name] += len(pool)
            if not lines:
                continue
            out.append(render(name, desc, ann, "\n".join(lines) + "\n").rstrip("\n"))
        text = "\n".join(out) + "\n"
        ast.parse(text)                      # 落盘前先确保能编译
        p.write_text(text, encoding="utf-8")
        print("  %-30s %d 族" % (p.name, len(fams)))
    print()
    print("  注入合计: " + " / ".join(f"{k}={v}" for k, v in totals.items()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
