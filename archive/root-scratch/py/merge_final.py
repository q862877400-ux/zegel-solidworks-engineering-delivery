# -*- coding: utf-8 -*-
"""把 interop 维度并进 12 份 sw_api_* 索引（最终版，逐文件原子写 + 语法自检）。"""
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

BLOCK = """
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   SolidWorks 官方 interop 程序集**自身的元数据**
# 文件:   D:\\AI\\SW\\interop-dimension-census.json（40,921 行全量普查）
# 定位:   每个成员的**调用属性**维度 —— 属性方向 / 是否内部使用 / DISPID。
# ⚑ 这三个维度**不是本项目推断的**，官方程序集里本来就有：
#     · CanRead / CanWrite   ← System.Reflection.PropertyInfo
#     · FHidden              ← SolidWorks 标「内部使用」的属性
#                              （⚠ 全 assembly 命中 0 次 [Obsolete]
#                                —— 记 obsolete 这一栏永远是空的）
#     · DispIdAttribute      ← makepy 生成物的主键，可精确 join
# ⚑ 已用三个独立源交叉验证（typelib / interop DLL / makepy），
#   只写属性 10 个三源一致、数量对账吻合。
# ⚠ 读取方式是**纯元数据**（读程序集 / typelib），
#   **未启动 SolidWorks 进程、未做任何 COM 实例化调用**。
# 覆盖:   后续同级定义
# ⚠ 本组为静态照录，未在本机实测 SolidWorks 行为（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
"""


def short(t: str) -> str:
    n = t.split(".")[-1]
    return n[:-5] if n.endswith("Class") else n


def main() -> int:
    rows = json.loads(CENSUS.read_text(encoding="utf-8"))
    ro: dict[str, set] = defaultdict(set)
    wo: dict[str, set] = defaultdict(set)
    hid: dict[str, set] = defaultdict(set)
    disp: dict[str, dict] = defaultdict(dict)
    for r in rows:
        f = short(r["type"])
        # ⚑ 属性形态在 interop 里带 ``get_``/``set_`` 前缀，**COM 名没有** ——
        #   与本索引其余部分（ARITY / PROPERTIES）保持同一套归一。
        # 2)无条件3剥4 get_/set_ 前缀：SolidWorks 的方法名一律 PascalCase，
        #    绝不会出现小写 get_ 前缀 => 剥了不会误伤。早先按 kind 判定，
        #    漏掉了既标 hidden 又是属性的 get_Dummy001 / set_Dummy001。
        n = r["name"]
        if n[:4] in ("get_", "set_"):
            n = n[4:]
        if r.get("hidden"):
            hid[f].add(n)
        raw = r.get("disp_id")
        if raw is not None:
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

    counts = {"READONLY": 0, "WRITEONLY": 0, "HIDDEN": 0, "DISPID": 0}
    for p in sorted(SCRIPTS.glob("sw_api_*.py")):
        src = p.read_text(encoding="utf-8")
        if "WRITEONLY: dict" in src:          # 已注入过，跳过
            continue
        fams = re.findall(r"^    '(I\w+)': \{", src, re.M)
        if not fams:
            continue
        out: list[str] = [src.rstrip("\n"), "", BLOCK.rstrip("\n"), ""]

        for label, pool_map in (("READONLY", ro), ("WRITEONLY", wo), ("HIDDEN", hid)):
            lines: list[str] = []
            for f in fams:
                pool = pool_map.get(f)
                if not pool:
                    continue
                lines.append("    %r: (" % f)
                for k in sorted(pool):
                    lines.append("        %r," % k)
                lines.append("    ),")
                counts[label] += len(pool)
            if lines:
                out.append("%s: dict[str, tuple[str, ...]] = {" % label)
                out.append("\n".join(lines))
                out.append("}")
                out.append("")

        # ⚑⚑ DISPID 只能是**补充信息**，不能当成新成员来源 ——
        #   普查里有 COM 内部分发口（`IGetXxx`）与 coclass 重复项，
        #   全收进来会凭空多出几千个「已登记成员」，门禁直接红。
        #   ⇒ 只收**本索引已经有的**成员。
        known: dict[str, set] = {}
        for f in fams:
            blk = re.search(r"^    '%s': \{\n(.*?)\n    \}," % re.escape(f),
                            src, re.M | re.S)
            if not blk:
                continue
            known[f] = (set(re.findall(r"^        '(\w+)': \d+,$", blk.group(1), re.M))
                        | set(re.findall(r"^        '(\w+)',$", blk.group(1), re.M)))
        lines = []
        for f in fams:
            d = {k: v for k, v in disp.get(f, {}).items() if k in known.get(f, set())}
            if not d:
                continue
            lines.append("    %r: {" % f)
            for k, v in sorted(d.items()):
                lines.append("        %r: %d," % (k, v))
            lines.append("    },")
            counts["DISPID"] += len(d)
        if lines:
            out.append("DISPID: dict[str, dict[str, int]] = {")
            out.append("\n".join(lines))
            out.append("}")

        text = "\n".join(out) + "\n"
        try:
            ast.parse(text)
        except SyntaxError as exc:
            print("  [FATAL] %s 语法错: %s" % (p.name, exc))
            return 2
        p.write_text(text, encoding="utf-8")
        print("  %-30s %d 族" % (p.name, len(fams)))
    print()
    print("  注入合计: " + " / ".join("%s=%d" % kv for kv in counts.items()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
