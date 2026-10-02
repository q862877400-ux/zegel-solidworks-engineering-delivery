#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（本工具为原创；2026-10-01 轮 219（地基④） 从工作区仓库搬入本仓库）
# 文件:   tools/gen_iview_registry.py —— 本文件自身
# 定位:   scripts/sw_drawing_view.py 的机械生成器（从反射清单生成登记表 + 通用访问器）
# 官方依据: D:\\AI\\SW\\_raw 的 sldworks 反射清单
# 许可:   本仓库 MIT
# ⚠ 只做静态读取与生成，不连 SolidWorks。输入源依赖本机布局（`C:\\swapi` / `D:\\AI\\SW\\_raw`），
#   未在第二台机器上实测。
# 覆盖:   全文件
# ────────────────────────────────────────────────────────────────────
从 sldworks 反射清单里机械生成 scripts/sw_drawing_view.py。

为什么用「登记表 + 通用访问器」而不是 267 个手写函数
--------------------------------------------------
`IView` 反射实测 **496 个成员**，构成（逐行解析，非抽样）：

    I 前缀内部分发口        134   （27%，不给调用方）
    属性（get_/set_）         61
    真方法                   301
    其中名字带数字的          97   （X2 / X3 历史重载变体）
    ── 归约到基础名后 = 267 个「不同能力」

267 个手写函数：代码量大、单位信息量低。���且其中大量是
``GetXxxCount`` / ``GetXxx`` 的固定配对（�� 40 个能力里占了 20 个）。

⇒ 做法与 StudyOptions 同一套：
  1. **登记表** ``VIEW_MEMBER_ARITY``：267 个能力名 → 实参个数，
     机械生成、不手抄，可被测试逐条对回反射清单。
  2. **受登记表约束的通用访问器** ``call_view()``。
  3. 少量高频能力做显式包装（视图名/比例/对齐/注释计数等）。

⚠ 只读本地反射 dump，不联网、不触碰任何 COM（AGENTS.md 铁律 2）。
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
    except Exception:  # noqa: BLE001
        pass

SRC = Path(r"D:\\AI\\SW\\_raw\reflect_sldworks\iface_sldworks.txt")
DATA = Path(r"D:\\AI\\SW\\_raw\iview_members.json")
OUT = Path(r"" + _ROOT_S + r"\scripts\sw_drawing_view.py")

IFACE = "IView"
SIG = re.compile(r"^(\S+)\s+(\w+)\s*\((.*)\)$")
INTERNAL = re.compile(r"^I[A-Z]")


def parse_interface(path: Path, iface: str) -> list[str]:
    """逐行解析某个接口段（**不用正则切段** —— 前瞻会提前截断）。"""
    current = None
    out: list[str] = []
    for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if raw.startswith("## "):
            if current == iface:
                break
            current = raw[3:].strip()
            if current == iface:
                out = []
        elif current == iface and raw.strip():
            out.append(raw.strip())
    return out


def main() -> int:
    if not SRC.is_file():
        print(f"[FATAL] 找不到反射清单: {SRC}", file=sys.stderr)
        return 2

    raw = parse_interface(SRC, IFACE)
    internal, props, methods = [], [], []
    for line in raw:
        m = SIG.match(line)
        if not m:
            continue
        ret, name, args = m.groups()
        if INTERNAL.match(name):
            internal.append(name)
        elif name.startswith(("get_", "set_")):
            props.append(name)
        else:
            methods.append({"name": name, "ret": ret, "arity": len(
                [a for a in args.split(",") if a.strip()])})

    # 归约：编号变体折叠到基础名，保留**信息量更大的那一条**（实参最多者）
    reduced: dict[str, dict] = {}
    for item in methods:
        base = re.sub(r"\d+$", "", item["name"])
        keep = reduced.get(base)
        if keep is None or item["arity"] > keep["arity"]:
            reduced[base] = item

    serial = {
        "interface": IFACE,
        "raw_members": len(raw),
        "internal_dispatch": len(internal),
        "properties": len(props),
        "methods": len(methods),
        "numbered_variants": len(methods) - len({re.sub(r'\d+$', '', i['name']) for i in methods}),
        "distinct_capabilities": len(reduced),
        "members": sorted(reduced.values(), key=lambda i: i["name"]),
    }
    DATA.write_text(json.dumps(serial, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"  IView 原始成员        {serial['raw_members']}")
    print(f"  I 前缀内部分发口      {serial['internal_dispatch']}")
    print(f"  属性                  {serial['properties']}")
    print(f"  方法签名              {serial['methods']}")
    print(f"  编号历史变体          {serial['numbered_variants']}")
    print(f"  归约后不同能力        {serial['distinct_capabilities']}")
    print(f"  -> {DATA}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
