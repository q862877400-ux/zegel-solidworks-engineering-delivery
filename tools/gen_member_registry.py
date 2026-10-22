#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""通用「接口族成员登记表」生成器。

这套做法本项目已经用到第三遍（StudyOptions 242 setter / IView 207 能力 /
本轮的 IAssemblyDoc·ICurve·IDimensionTolerance），每次都手写一遍生成器是重复劳动，
且第三次证明**必须先查构成再决定手写还是登记表**：

    接口族            原始   I前缀  属性  方法  编号变体  归约后能力
    IView            496    134    61   301      94       207
    IAssemblyDoc     211     25    13   173      41       133
    ICurve            69     25     4    40       9        31
    IDimensionTolerance 27     0     8    19       3        16

⇒ 共同形态：**大量 I 前缀内部分发口 + 大量编号历史变体**，
   手写 N 个函数会把「覆盖」刷成没有信息量的数字。

本脚本的职责：从反射清单逐行解析 → 折叠编号变体 → 落成 JSON + Python 模块。

⚑ 逐行解析而不是正则切段
------------------------
正则前瞻 ``(?=\\r?\\n## |\\Z)`` 会**提前截断**
（实测把 116 行的 IModelView 段截成 3761 字符，导致误判 SetCallout 的归属）。
逐行解析以「下一个 `## ` 行为段尾」为界，无歧义。

⚠ 只读本地反射 dump，不联网、不触碰任何 COM（AGENTS.md 铁律 2）。
"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   tools/gen_member_registry.py
# 定位:   通用「接口族成员登记表」生成器。
# 官方依据: 不适用（本仓工具，不调 COM）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
    except Exception:  # noqa: BLE001
        pass

REFLECT = Path(Path(__file__).resolve().parents[1] / "_raw" / "reflect_sldworks" / "iface_sldworks.txt")
RAW = Path(Path(__file__).resolve().parents[1] / "_raw")
SIG = re.compile(r"^(\S+)\s+(\w+)\s*\((.*)\)$")
INTERNAL = re.compile(r"^I[A-Z]")


def parse_blocks(path: Path) -> dict[str, list[str]]:
    """逐行解析整个反射清单 → {接口名: [签名行, …]}。"""
    blocks: dict[str, list[str]] = {}
    current = None
    for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if raw.startswith("## "):
            current = raw[3:].strip()
            blocks.setdefault(current, [])
        elif current and raw.strip():
            blocks[current].append(raw.strip())
    return blocks


def analyze(blocks: dict[str, list[str]], iface: str, fold: bool = False) -> dict:
    """统计某接口族的构成。

    ⚠⚑ ``fold`` 默认 **False** —— 不折叠编号变体。这不是保守，是**必要**：
    SolidWorks 的编号成员**不是重载，是不同版本的不同操作**。实测：
        FeatureExtrusion2  凸台拉伸（旧版，已废弃）
        FeatureExtrusion3  凸台拉伸（23 参）
    折叠到基础名会产出 ``FeatureExtrusion`` —— **该成员在官方 API 中不存在**，
    照它调用必然失败。⇒ 编号成员**逐个保留**，只做登记不做合并。
    """
    raw = blocks.get(iface, [])
    internal: list[str] = []
    props: list[str] = []
    methods: list[dict] = []
    for line in raw:
        m = SIG.match(line)
        if not m:
            continue
        _ret, name, args = m.groups()
        if INTERNAL.match(name):
            internal.append(name)
        elif name.startswith(("get_", "set_")):
            props.append(name[4:])
        else:
            # ⚑⚑ arity 口径 = **调用方要传的实参个数，排除 by-ref 出参**。
            #   反射里 `Void GetErrorMessages(Object&, Object&, Object&)` 是
            # **0 参** —— 三个全是 [out]。早先版本 `len([a for a in args.split(",") ...]
            # )`
            #   把它们都算成实参 ⇒ 本机实测 **1,566 条表项里 100 条口径错（6.4%）**，
            #   表现为「护栏按 3 参要求，调用方却一个都不该传」，运行必被自己拦下。
            #   ⇒ 口径统一为「非 & 结尾的参数个数」。
            _params = [a.strip() for a in args.split(",") if a.strip()]
            methods.append({
                "name": name,
                "arity": len([a for a in _params if not a.endswith("&")]),
            })
    if fold:
        reduced: dict[str, dict] = {}
        for item in methods:
            base = re.sub(r"\d+$", "", item["name"])
            keep = reduced.get(base)
            if keep is None or item["arity"] > keep["arity"]:
                reduced[base] = item
        members = sorted(reduced.values(), key=lambda i: i["name"])
    else:
        members = sorted(methods, key=lambda i: i["name"])
    return {
        "interface": iface,
        "raw_members": len(raw),
        "internal_dispatch": len(internal),
        "property_count": len(props),
        "method_count": len(methods),
        "distinct_capabilities": len(members),
        "folded": bool(fold),
        "properties": sorted(set(props)),
        "members": members,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="接口族成员登记表生成器")
    parser.add_argument("interfaces", nargs="+", help="接口名，如 IAssemblyDoc")
    parser.add_argument("--reflect", default=str(REFLECT))
    args = parser.parse_args()

    path = Path(args.reflect)
    if not path.is_file():
        print(f"[FATAL] 找不到反射清单: {path}", file=sys.stderr)
        return 2
    blocks = parse_blocks(path)

    all_out: dict[str, dict] = {}
    for iface in args.interfaces:
        info = analyze(blocks, iface)
        if info["raw_members"] == 0:
            print(f"[WARN] 反射清单里没有 {iface} 段")
            continue
        all_out[iface] = info
        print(f"### {iface}")
        print(f"    原始成员     {info['raw_members']}")
        print(f"    I 前缀分发口 {info['internal_dispatch']}")
        print(f"    属性         {info['property_count']}")
        print(f"    方法         {info['method_count']}")
        print(f"    归约后能力   {info['distinct_capabilities']}")

    if not all_out:
        return 1
    out = RAW / "member_registry.json"
    out.write_text(json.dumps(all_out, ensure_ascii=False, indent=2),
                   encoding="utf-8")
    print(f"\n-> {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
