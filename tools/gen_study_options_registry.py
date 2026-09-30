#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""从 cosworks 反射清单里机械生成各 StudyOptions 族的 setter 登记表。

为什么要登记表而不是 110 个包装函数
----------------------------------
`ICWStaticStudyOptions` 单族就有 55 个 setter，逐个包一层函数
代码量大、单位信息量低。但**「这个族到底有哪些可设项」本身是有价值的信息** ——
它是「求解器能配什么」的权威清单，可被 grep、可被测试核对。

⇒ 做法：把反射确认的 setter 列表落成模块内的**字符串字面量登记表**
  （不是运行时反射 —— 那是会随 SolidWorks 版本漂移的），
  再用少数几个高频项做显式包装 + 一个受登记表约束的通用 setter。

⚠ 只读本地已生成的反射 dump，不联网、不触碰任何 COM（AGENTS.md 铁律 2）。
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
    except Exception:  # noqa: BLE001
        pass

SRC = Path(r"D:\AI\SW\_raw\reflect\iface_cosworks.txt")
OUT = Path(r"D:\AI\SW\_raw\study_options_setters.json")

FAMILIES = (
    "ICWStaticStudyOptions",
    "ICWFrequencyStudyOptions",
    "ICWBucklingStudyOptions",
    "ICWNonLinearStudyOptions",
    "ICWThermalStudyOptions",
    "ICWDynamicStudyOptions",
    "ICWFatigueStudyOptions",
    "ICWDropTestStudyOptions",
    "ICWCompositeShellOptions",
    "ICWTopologyStudyOptions",
)

IFACE = re.compile(r"^##\s+(\w+)\s*$")
SETTER = re.compile(r"^\s+Void\s+set_(\w+)\((\w[\w\.]*)\)\s*$")


def main() -> int:
    if not SRC.is_file():
        print(f"[FATAL] 找不到反射清单: {SRC}", file=sys.stderr)
        return 2

    want = set(FAMILIES)
    out: dict[str, list[tuple[str, str]]] = {f: [] for f in FAMILIES}
    current = None
    for raw in SRC.read_text(encoding="utf-8", errors="replace").splitlines():
        head = IFACE.match(raw)
        if head:
            current = head.group(1)
            continue
        if current not in want:
            continue
        m = SETTER.match(raw)
        if m:
            out[current].append((m.group(1), m.group(2)))

    import json
    serial = {k: [{"name": n, "type": t} for n, t in v] for k, v in out.items()}
    OUT.write_text(json.dumps(serial, ensure_ascii=False, indent=2), encoding="utf-8")

    total = 0
    for name, items in out.items():
        pairs = [n for n, _ in items if n.endswith("2")]
        base = [n for n, _ in items if not n.endswith("2")]
        print(f"  {name:<30} setter {len(items):>3}  "
              f"（X2 形 {len(pairs)} / 基础形 {len(base)}）")
        total += len(items)
    print(f"\n合计 {total} 个 setter -> {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
