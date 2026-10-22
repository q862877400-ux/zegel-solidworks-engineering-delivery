#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""从提取出的 cosworks 官方文档页里解析出全部方法签名与参数说明。

产出 ``_raw\cosworks_signatures.md``，作为写代码时的签名依据
（替代此前「27 个 Add* 方法签名不可得」的判断 —— 那个判断是错的，
成因是 CHM 页正文以 JSON 转义形式嵌在 script 里，被误判成空壳）。

⚠ 只读本地已提取的纯文本，不联网、不执行任何内容（AGENTS.md 铁律 2）。
"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   tools/parse_cosworks_signatures.py
# 定位:   从提取出的 cosworks 官方文档页里解析出全部方法签名与参数说明。
# 官方依据: 不适用（本仓工具，不调 COM）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

import re
import sys
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
    except Exception:  # noqa: BLE001
        pass

SRC = Path(Path(__file__).resolve().parents[1] / "_raw" / "cosworks_pages")
OUT = Path(Path(__file__).resolve().parents[1] / "_raw" / "cosworks_signatures.md")

_MEMBER_PAGE = re.compile(r"ICWLoadsAndRestraintsManager~(\w+)")
# ⚠ 官方 VB 声明是**多行 + `_` 续行**的：
#     Function AddBearingLoad( _
#     ByVal CoordinateSystem As System.Object, _
#     ...
#     ) As CWBearingLoad
# 所以参数正则必须逐行匹配（re.M），且要先去掉续行的 `_` 与换行。
_VB_DECL = re.compile(r"Function\s+(\w+)\s*\((.*?)\)\s*As\s*(\w+)", re.S)
_CONTINUE = re.compile(r"[_\s]*\n[_\s]*")
# ⚠ 扁平化之后整段声明变成**一行**，再带 `^` 行首锚点就永远匹配不上
#   （初版就是因此把 31 个方法的参数全解析成空）。
#   所以这里必须**不用行首锚点**，靠 (ByVal|ByRef) 本身起头。
_PARAM_LINE = re.compile(r"(ByVal|ByRef)\s+(\w+)\s+As\s+([\w\.]+)")


def vb_declaration(text: str):
    """取 Visual Basic (Declaration) 段的完整声明。"""
    idx = text.find("Visual Basic (Declaration)")
    if idx < 0:
        return None, None, None
    window = text[idx : idx + 1500]
    match = _VB_DECL.search(window)
    if not match:
        return None, None, None
    name, params, returns = match.groups()
    flat = _CONTINUE.sub(" ", params)  # 把多行续行压成一行
    return name, _PARAM_LINE.findall(flat), returns


def param_docs(text: str, name: str) -> str:
    """取 Parameters 段里某个参数的说明。"""
    idx = text.find("Parameters")
    if idx < 0:
        return ""
    window = text[idx : idx + 1800]
    pos = window.find(name)
    if pos < 0:
        return ""
    tail = window[pos + len(name) :]
    stop = tail.find("Return Value")
    tail = tail[: stop if stop > 0 else 220]
    return " ".join(tail.split())[:200]


def return_doc(text: str) -> str:
    idx = text.find("Return Value")
    if idx < 0:
        return ""
    tail = " ".join(text[idx + len("Return Value") : idx + 260].split())
    for marker in ("Example", "Remarks", "See Also"):
        if marker in tail:
            tail = tail.split(marker)[0]
    return tail.strip()[:160]


def main() -> int:
    if not SRC.is_dir():
        print(f"[FATAL] 找不到提取目录: {SRC}", file=sys.stderr)
        return 2

    rows = []
    for path in sorted(SRC.glob("*.txt")):
        match = _MEMBER_PAGE.search(path.stem)
        if not match:
            continue
        method = match.group(1)
        text = path.read_text(encoding="utf-8", errors="replace")
        parsed = vb_declaration(text)
        if not parsed or not parsed[0]:
            continue
        name, params, returns = parsed
        rows.append(
            (method, name, returns or "", params or [], return_doc(text), path.name)
        )

    lines = [
        "# cosworks 官方方法签名（从 CHM `cosworks` 册提取）",
        "",
        "> 来源：`D:\\AI\\SW\\AI Solidworks\\官方文档\\SWhelp\\cosworks\\`",
        ">       34 个 `ICWLoadsAndRestraintsManager~<成员>` 接口页 + 13 个枚举页。",
        "> ⚠ 此前「cosworks 册是空壳、27 个 Add* 签���不可得」是**误判**：",
        ">   正文以 JSON 转义（`\\u003c` = `<`）嵌在 script 里，按 `<script>` 抓不到。",
        "> 提取工具：`D:\\AI\\SW\\tools\\extract_cosworks_docs.py`（42 页成功）。",
        "",
        "---",
        "",
    ]
    for method, vb_name, returns, params, ret_doc, src in rows:
        lines.append(f"## {method}")
        lines.append("")
        lines.append(f"- **VB 声明**：`Function {vb_name}(...) As {returns}`")
        lines.append(f"- **返回**：{ret_doc or '（官方未写说明）'}")
        if params:
            lines.append("- **参数**（据官方 Parameters 段）：")
            for direction, pname, ptype in params:
                doc = param_docs(
                    (SRC / src).read_text(encoding="utf-8", errors="replace"), pname
                )
                lines.append(
                    f"    - `{direction} {pname} As {ptype}` — {doc or '（无说明）'}"
                )
        lines.append(f"- 来源页：`{src}`")
        lines.append("")

    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"已解析 {len(rows)} 个方法 -> {OUT}")
    print(f"  文件大小 {OUT.stat().st_size} 字节")
    # 摘要
    for method, vb_name, returns, params, _, _ in rows:
        sig = ", ".join(f"{p} {t.split('.')[-1]}" for _, p, t in params)
        print(f"    {method}({sig}) -> {returns}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
