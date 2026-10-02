r"""@brief 探针：`scripts/sw_*.py` 里**哪些模块带长度参数、却没声明单位**。

## 起因（2026-10-01 轮 132）
`scripts/sw_part.py` 的 **14 处** docstring 写「单位: 米」，而实测**是毫米**。
★ 关键不是"写错了"，而是：**脚本层的单位声明没有任何机器约束**
（工具层有规则 2 的 `_mm` 后缀守着，脚本层没有）。

## 本轮先**量假阳性率**，再决定能不能做门禁（本项目的纪律）
判法（**有界、可复核**，不是"聪明的启发式"）：
1. **长度词表**（显式写出来）：radius / diameter / depth / thickness / distance /
   width / height / length / offset / spacing / pitch / cx / cy / cz / x1 / y1 …；
2. 某模块的**公开函数**里出现这些**形参名** ⇒ 认为它"带长度参数"；
3. 看它的**源码里有没有单位声明**（`单位` / `毫米` / `米` / `mm` / `meter` 之类）。

⇒ 输出：**「带长度参数但一处单位声明都没有」**的模块清单。

## ⚠ 这是**探针**，不是门禁
本项目的经验（`020`/`021`/`022`/`027`/`029`/`032`/`037`）：
**按名字做的检查假阳性率高**。所以先量、再判、**不直接接门禁**。

# ── 来源 ──
# 仓库:   本项目自身（只读探针）
# 文件:   tools/probe_unit_declarations.py
# 定位:   给「脚本层单位无人守」这件事取证（轮 133）。
# 官方依据: 不适用（本项目内部工具）。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import ast
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.stdout.reconfigure(encoding="utf-8")

#: 显式的**长度词表**（有界、可复核 —— 不是"聪明的启发式"）
LENGTH_WORDS = (
    "radius", "diameter", "depth", "thickness", "distance", "width", "height",
    "length", "offset", "spacing", "pitch", "cx", "cy", "cz", "dx", "dy", "dz",
    "x1", "y1", "z1", "x2", "y2", "z2", "x_mm", "y_mm", "z_mm", "size",
)

#: 单位声明的**任意一种**写法
UNIT_MARK = re.compile(
    r"单位\s*[:：]|毫米|millimet|\bmm\b|meter|米（|（米）|（毫米）", re.IGNORECASE)


# ⚠⚠ **2026-10-01 轮 133 的结论：本探针不能当判据，而且这个判据的原理不成立。**
#   实测假阳性 **4/4 = 100%** —— `lot_size`（批量大小）/ `depth`（树深度）/
#   `width`（窗口宽）/ `dx,dy`（屏幕像素）**全被误判成长度参数**。
#   ★ 根因：**「长度词表」无法区分「几何长度」与「同名的非几何量」** —— 那是**语义**判断。
#   ⇒ 详 `docs/script-layer-units.md`。**不要把它接进门禁。**
#   ★ 脚本层单位的**唯一可靠办法是实测**（`051` 轮 132 就是真机量出来的）。


def public_functions(path: Path):
    try:
        tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"))
    except SyntaxError:
        return []
    out = []
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and not node.name.startswith("_"):
            out.append((node.name, [a.arg for a in node.args.args]))
    return out


def main() -> int:
    flagged, declared, no_len = [], [], []
    for p in sorted((ROOT / "scripts").glob("sw_*.py")):
        if p.stem.startswith("sw_api_"):
            continue
        text = p.read_text(encoding="utf-8", errors="replace")
        fns = public_functions(p)
        len_fns = [(n, a) for n, a in fns
                   if any(any(w == str(x).lower() or str(x).lower().endswith("_" + w)
                              for w in LENGTH_WORDS) for x in a)]
        if not len_fns:
            no_len.append(p.stem)
            continue
        (flagged if not UNIT_MARK.search(text) else declared).append((p.stem, len(len_fns)))

    print("`scripts/sw_*.py`（不含 API 名登记表）：")
    print("  带长度参数的模块 · **已声明单位**: %d" % len(declared))
    for s, n in declared:
        print("      %-34s %d 个带长度参数的公开函数" % (s, n))
    print()
    print("  带长度参数的模块 · ★ **一处单位声明都没有**: %d" % len(flagged))
    for s, n in flagged:
        print("    ★ %-32s %d 个带长度参数的公开函数" % (s, n))
    print()
    print("  没有（按词表看）长度参数的模块: %d ⇒ %s" % (len(no_len), no_len[:10]))
    print()
    print("⚠ **不下「该接门禁」的结论** —— 这份清单要**人工逐条看**：")
    print("   ① 有的是**别名**（形参名刚好撞上词表）⇒ 假阳性；")
    print("   ② 有的模块单位**由调用方决定**（例如单纯转发）⇒ 假阳性；")
    print("   ③ 有的**真的没写** ⇒ 那才是发现。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
