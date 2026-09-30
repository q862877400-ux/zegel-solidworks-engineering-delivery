# -*- coding: utf-8 -*-
"""把 interop 维度普查（census）并进 12 份 sw_api_* 索引。

来源：官方 interop 程序集自身的元数据（`PropertyInfo.CanRead/CanWrite`、
`[OutAttribute]`、`TypeLibFuncAttribute(FHidden)`、`DispIdAttribute`），
纯读元数据，**不启动 SolidWorks、不做任何 COM 实例化调用**。

注入 4 张新表（成员名 → 元数据），与既有 ARITY / PROPERTIES 并列：
    READONLY   只读属性名
    WRITEONLY  只写属性名（**读它会报 -2147352567**，必须拦）
    HIDDEN     内部使用成员（`Dummy1..19` 之类，**不该调**）
    DISPID     成员名 → dispid（makepy 产物的主键，可精确 join）
"""
from __future__ import annotations

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


def short(t: str) -> str:
    n = t.split(".")[-1]
    return n[:-5] if n.endswith("Class") else n


def main() -> int:
    rows = json.loads(CENSUS.read_text(encoding="utf-8"))
    ro, wo, rw, hid, disp = (defaultdict(set), defaultdict(set),
                              defaultdict(set), defaultdict(set), {})
    for r in rows:
        f, n = short(r["type"]), r["name"]
        if r.get("hidden"):
            hid[f].add(n)
        if r.get("disp_id") is not None:
            disp[(f, n)] = r["disp_id"]
        if r["kind"] == "property":
            if r["can_write"] and not r["can_read"]:
                wo[f].add(n)
            elif r["can_read"] and not r["can_write"]:
                ro[f].add(n)
            elif r["can_read"]:
                rw[f].add(n)

    total = {"READONLY": 0, "WRITEONLY": 0, "HIDDEN": 0, "DISPID": 0}
    for p in sorted(SCRIPTS.glob("sw_api_*.py")):
        src = p.read_text(encoding="utf-8")
        fams = re.findall(r"^    '(I\w+)': \{", src, re.M)
        if not fams:
            continue
        blocks = []
        for f in fams:
            a = sorted(ro.get(f, set()))
            b = sorted(wo.get(f, set()))
            h = sorted(hid.get(f, set()))
            d = {n: i for (ff, n), i in disp.items() if ff == f}
            for tbl, items, key in (("READONLY", a, "READONLY"),
                                     ("WRITEONLY", b, "WRITEONLY"),
                                     ("HIDDEN", h, "HIDDEN")):
                body = "".join("    %r: (" % f + "".join("        %r,\n" % x for x in items) + "    ),\n")
                blocks.append("### %s\n%s}\n" % (tbl, body))
                total[key] += len(items)
            body = "".join("    %r: {\n        %r: %d,\n    },\n" % (f, n, i) for n, i in sorted(d.items()))
            blocks.append(body.rstrip("\n") if body else "")
            total["DISPID"] += len(d)
        raw = "\n".join(x for x in blocks if x)
        head, _, rest = HEADER.partition("@@READONLY@@")
        seg_r, _, rest2 = rest.partition("@@WRITEONLY@@")
        seg_w, _, rest3 = rest2.partition("@@HIDDEN@@")
        seg_h, _, seg_d = rest3.partition("@@DISPID@@")
        body = (head + "READONLY: dict[str, tuple[str, ...]] = {\n" + seg_r
                + "WRITEONLY: dict[str, tuple[str, ...]] = {\n" + seg_w
                + "HIDDEN: dict[str, tuple[str, ...]] = {\n" + seg_h
                + "DISPID: dict[str, dict[str, int]] = {\n" + seg_d.rstrip("### DISPID\n")
                + raw.rstrip("\n") + "\n")
        new = src.rstrip("\n") + "\n\n\n" + body
        p.write_text(new, encoding="utf-8")
        import ast
        ast.parse(new)
        print("  %-30s %d 族" % (p.name, len(fams)))
    print()
    print("  注入合计: " + " / ".join(f"{k}={v}" for k, v in total.items()))
    return 0


HEADER = '''# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   SolidWorks 官方 interop 程序集**自身的元数据**
# 文件:   D:\\AI\\SW\\interop-dimension-census.json（40,921 行全量普查）
# 定位:   每个成员的**调用属性**维度 —— 属性方向、是否内部使用、DISPID。
# ⚑ 这些维度**不是本项目推断的**，是官方程序集里本来就有的：
#     · CanRead / CanWrite   ← System.Reflection.PropertyInfo
#     · [OutAttribute]       ← 参数方向（决定要不要包 VARIANT 拿回值）
#     · FHidden              ← SolidWorks 用来标「内部使用」的属性
#                              （⚠ **全 assembly 命中 0 次 [Obsolete]**
#                                —— 记 obsolete 这一栏永远是空的）
#     · DispIdAttribute      ← 与 makepy 生成物的主键，可精确 join
# ⚑ 已用三个独立源交叉验证（typelib / interop DLL / makepy），
#   只写属性 10 个三源完全一致、数量对账吻合。
# ⚠ 读取方式是**纯元数据**（读程序集 / typelib），
#   **未启动 SolidWorks 进程、未做任何 COM 实例化调用**。
# 覆盖:   后续同级定义
# ⚠ 本组为静态照录，未在本机实测 SolidWorks 行为（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
#: 只读属性 —— 只能读，传 set 会失败
@@READONLY@@
#: 只写属性 —— ⚠ **读它会报 -2147352567「无法读只写属性」**
#: （错误文本随 UI 语言变化；pywin32 源码里无此消息，属本地化 HRESULT）
@@WRITEONLY@@
#: 内部使用成员 —— 官方标了 FHidden，**不应当作公开能力调用**
#: （典型是 `Dummy1..19` 这类占位，以及 `IModelDocExtension.ExtractImageData`）
@@HIDDEN@@
#: 成员名 → DISPID（makepy 生成物用它做主键，可与 wrapper 精确 join）
@@DISPID@@
'''

if __name__ == "__main__":
    raise SystemExit(main())
