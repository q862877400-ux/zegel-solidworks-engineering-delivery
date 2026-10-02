"""★ 从四家仓库抽「操作名 → 描述」表，给分诊表里的"缺口操作"取**判据依据**。

## 为什么要有它（★ objective② 的关键一步）
```
★ `tools/union-sources.json` 的 `union_operations` 是 **349 个纯名字**（无描述）⇒
   ★★ 而分诊表 `docs/union-gap-triage.md` 的"后缀候选"档是按**词面**匹配出来的 ⇒
   ★ 抽样 24 条：**真 6 · 部分 2 · 假 16（67% 假）**。
⇒ ★★★ **要判"真缺 vs 语义等价"，必须先知道那个缺口操作**到底做什么**** ——
   ★ 而**四家的仓库里就有**：`andrewbartels1/docs/user-guide/tool-catalog/*.md` 与
     `Eduardof0nt/server.py` 的 187 个 `@mcp.tool`（每个后面带 docstring）。
   ⇒ ★★ **本脚本把两处抽成一张表**，★ 供人工/后续判据使用（★ **而不是从名字猜**）。
```

## 用法
```
python tools/extract_operation_descriptions.py            # 打印统计 + 落盘 JSON
python tools/extract_operation_descriptions.py --show 20  # 另打印前 20 条
```
"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（工具）
# 文件:   tools/extract_operation_descriptions.py
# 定位:   objective② 的判据依据抽取：把四家仓库里的「操作名 → 描述」抽出来。
# 官方依据: 不适用（★ 本脚本读的是**四家 MIT/Apache 仓库**的文本，不是官方 API）。
#   ★ 来源与许可：`Eduardof0nt/Solidworks-MCP-Server`（**MIT**）· `andrewbartels1/SolidworksMCP-python`
#   （**MIT**）—— ★ **只读其工具名与描述文本用于对照**，★ 未抄其代码。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
from __future__ import annotations

import argparse
import ast
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SWPROJECTS = Path(r"C:\swprojects")
OUT = REPO_ROOT / "docs" / "operation-descriptions.json"


def _from_andrewbartels1() -> dict[str, str]:
    """★ 从 `tool-catalog/*.md` 抽（★ 形如 `### tool_name` + 一段说明）。"""
    out: dict[str, str] = {}
    base = SWPROJECTS / "andrewbartels1" / "docs" / "user-guide" / "tool-catalog"
    if not base.is_dir():
        return out
    for f in sorted(base.glob("*.md")):
        text = f.read_text(encoding="utf-8", errors="replace")
        #: ★ 标题形如 `### 1. `name`` 或 `### name`
        for m in re.finditer(r"^#{2,4}\s*(?:\d+\.\s*)?`?([A-Za-z_][\w]*)`?\s*$", text, re.M):
            name = m.group(1)
            tail = text[m.end():m.end() + 600]
            #: ★ 取到下一个标题前的第一段非空文字
            para = []
            for line in tail.splitlines():
                s = line.strip()
                if s.startswith("#"):
                    break
                if s:
                    para.append(s)
                elif para:
                    break
            if name not in out and para:
                out[name] = " ".join(para)[:400]
    return out


def _from_eduardof0nt() -> dict[str, str]:
    """★ 从 `server.py` 的 187 个 `@mcp.tool(name=…)` + 紧随的 docstring 抽（★ 用 AST）。"""
    out: dict[str, str] = {}
    p = SWPROJECTS / "Eduardof0nt" / "server.py"
    if not p.is_file():
        return out
    src = p.read_text(encoding="utf-8", errors="replace")
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return out
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        name = None
        for dec in node.decorator_list:
            if isinstance(dec, ast.Call) and getattr(dec.func, "attr", None) == "tool":
                for kw in dec.keywords:
                    if kw.arg == "name" and isinstance(kw.value, ast.Constant):
                        name = str(kw.value.value)
        if name:
            doc = ast.get_docstring(node) or ""
            out.setdefault(name, " ".join(doc.split())[:400])
    return out


def _strip_prefix(names: dict[str, str]) -> dict[str, str]:
    """★ 同时登记**去掉前缀**的短名（★ 分诊表的"操作名"多是无前缀的，如 `arc` / `assembly`）。"""
    out = dict(names)
    for k, v in names.items():
        short = re.sub(r"^(sw_|sws_|solidworks_)", "", k)
        out.setdefault(short, v)
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--show", type=int, default=0)
    args = ap.parse_args()

    a = _from_andrewbartels1()
    e = _from_eduardof0nt()
    merged: dict[str, dict[str, str]] = {}
    for name, desc in _strip_prefix(a).items():
        merged.setdefault(name, {})["andrewbartels1"] = desc
    for name, desc in _strip_prefix(e).items():
        merged.setdefault(name, {})["Eduardof0nt"] = desc

    print("  andrewbartels1: %d 个操作名" % len(a))
    print("  Eduardof0nt   : %d 个操作名" % len(e))
    print("  合并（含去前缀短名）: **%d** 个" % len(merged))

    #: ★ 与分诊表的"缺口操作"对照：命中多少
    gap_names = []
    tri = REPO_ROOT / "docs" / "union-gap-triage.md"
    if tri.is_file():
        for line in tri.read_text(encoding="utf-8").splitlines():
            m = re.match(r"^\|\s*`([a-z0-9_]+)`\s*\|", line)
            if m:
                gap_names.append(m.group(1))
    hit = [g for g in gap_names if g in merged]
    print("  分诊表里的缺口操作: %d · **其中 %d 个能在四家找到描述**（★ 判据依据）"
          % (len(gap_names), len(hit)))

    OUT.write_text(json.dumps({"counts": {"andrewbartels1": len(a), "Eduardof0nt": len(e),
                                          "merged": len(merged), "gap_hit": len(hit)},
                               "descriptions": merged}, ensure_ascii=False, indent=1) + "\n",
                   encoding="utf-8")
    print("  产物: %s" % OUT)
    for g in hit[:args.show]:
        print("    %-28s %s" % (g, list(merged[g].values())[0][:88]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
