"""硬门禁：`GetSystemValue2` 的每个调用点**必须**做完量纲判断，否则报错退出 1。

## 防的是什么（根因 B 的另一半）

2026-10-26：示教器把 `IDimension.GetSystemValue2` 的返回值一律 ×1000 当毫米，
业主草图的 `ANGLE` 被记成 `785.398 mm`（= 0.7854 rad × 1000）——**假数值**。

我当时只改了那一处。**但只改一处不是根因修复**：只要还允许"取出数值就直接乘"，
下一次在新地方又会犯。⇒ 本门禁把这条纪律变成可执行的检查：

```
调用点必须满足其一：
  ① 位于 scripts/sw_units.py（量纲分派的唯一实现处）；
  ② 所在函数里出现量纲分派标记（dimension_reading / m_to_mm / rad_to_deg /
     unit_unverified / value_deg / value_rad / raw_system_value）——
     即"这个函数显式处理了量的类型"；
  ③ 该行正上方 3 行内有 `#: unit-dispatch:` 注释（人工判过、写明理由）。
```

## 用法

```bash
python -B scripts/check_dimension_units.py          # 人读报告
python -B scripts/check_dimension_units.py --check  # 只回退出码（门禁用）
```
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
R = Path(__file__).resolve().parents[1]

#: 允许持有裸调用的文件（量纲分派的实现处）
OWNER = "scripts/sw_units.py"
#: 同一函数内出现这些标记，就算"已做量纲判断"
DISPATCH_MARKERS = (
    "dimension_reading", "m_to_mm", "rad_to_deg",
    "unit_unverified", "raw_system_value", "value_deg", "value_rad",
)
#: 人工豁免标记（要求写明理由）
EXEMPT_MARK = "#: unit-dispatch:"


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库 / 文件 / 定位 / 官方依据 / 许可 / 覆盖
# 仓库:   本项目自身（门禁 · 尺寸量纲）
# 文件:   scripts/check_dimension_units.py
# 定位:   拦住「GetSystemValue2 取出数值不判量纲就换算」的复发。
#          起因：2026-10-26 角度被当长度 ×1000 记成 785.398mm（假数值）。
# 官方依据: `IDimension.GetSystemValue2` 的 Remarks（长度米 / 角度弧度）；
#          量纲分派实现在 scripts/sw_units.py。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────


def _enclosing_function(lines: list, idx: int) -> str:
    """回 idx 所在函数的**全文**（用于找量纲分派标记）；找不到回空串。"""
    start = 0
    for i in range(idx, -1, -1):
        if re.match(r"^\s*(?:def|class)\s", lines[i]):
            start = i
            break
    end = len(lines)
    base = len(lines[start]) - len(lines[start].lstrip())
    for i in range(start + 1, len(lines)):
        s = lines[i]
        if not s.strip():
            continue
        ind = len(s) - len(s.lstrip())
        if ind <= base and re.match(r"^\s*(?:def|class)\s", s):
            end = i
            break
    return "\n".join(lines[start:end])


def scan() -> tuple:
    """回 (合法点列表, 违规点列表)；每项 = (文件, 行号, 行文本)。"""
    ok, bad = [], []
    for path in sorted((R / "scripts").glob("*.py")):
        rel = "scripts/" + path.name
        lines = open(path, encoding="utf-8", errors="replace").read().splitlines()
        in_doc = False
        for i, line in enumerate(lines):
            #: ★ 必须跟踪三引号状态：文档里大量**文字提及** GetSystemValue2，
            #:   不排除会把「说明」当成「调用点」（第一版就误报了 2 条）。
            marks = line.count('"""')
            if marks:
                if marks == 1:
                    in_doc = not in_doc
                    continue
                if in_doc:
                    in_doc = not in_doc if marks % 2 else in_doc
                    continue
            if in_doc:
                continue
            if "GetSystemValue2" not in line:
                continue
            s = line.strip()
            if s.startswith("#") or s.startswith("*"):
                continue
            if not re.search(r"GetSystemValue2\"?\s*[,)]", s) and \
               not re.search(r"GetSystemValue2\(", s):
                continue
            if rel == OWNER:
                ok.append((rel, i + 1, s))
                continue
            fn = _enclosing_function(lines, i)
            if any(mk in fn for mk in DISPATCH_MARKERS):
                ok.append((rel, i + 1, s))
                continue
            near = "\n".join(lines[max(0, i - 3):i])
            if EXEMPT_MARK in near:
                ok.append((rel, i + 1, s))
                continue
            bad.append((rel, i + 1, s))
    return ok, bad


def main() -> int:
    ok, bad = scan()
    check_only = "--check" in sys.argv
    if not check_only:
        print("尺寸量纲门禁 · `GetSystemValue2` 调用点")
        print(f"  合法 {len(ok)} 个")
        for rel, ln, s in ok:
            print(f"    ✓ {rel}:{ln}  {s[:80]}")
    if bad:
        print(f"\n✗ {len(bad)} 个调用点**没做量纲判断**：")
        for rel, ln, s in bad:
            print(f"   {rel}:{ln}  {s[:90]}")
        print("\n  修法：改用 `sw_units.dimension_reading(dim, relation_type)`；"
              "确实要自己读就按类型分派（m_to_mm / rad_to_deg），"
              "或在正上方写 `#: unit-dispatch: <理由>`。")
        return 1
    if not check_only:
        print("\n✓ 所有调用点都做了量纲判断")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
