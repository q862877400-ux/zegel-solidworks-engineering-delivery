"""★ 生成「COM 成员 → 本仓哪个函数封了它」索引（治「忘了我们有工具」）。

## 业主 2026-10-26 的质问

> 你怎么又开始查官方 API 了？…我们自己不是有草图阵列的这个 MCP 工具吗？
> 就是我们自己之前不是做过了吗？…你是不是选择了直接去查官方文档，
> 而不是去利用我们之前已经梳理过的 API 工具呢？

★ 事实：**我手写的 `AddDimension2`、`EditDelete`、`SelectByID2` 全都有现成封装**
  （`sw_sketch_dimensions.add_horizontal_dimension` / `sw_part.feature_delete` 等），
  而我没查就重写了一遍。

## 为什么会这样（真因）

本仓 `scripts/` 有 140 条能力、`mcp-server/` 有几百个 ToolSpec，
但**没有一张「COM 成员 → 我们的封装」的反查表** ⇒
只记得「官方有 `AddDimension2`」，不记得「我们的 `add_vertical_dimension` 封了它」。

⇒ 本生成器从 `scripts/*.py` 的 docstring / 注释里抽 `I<接口>.<成员>` 形态，
  按**所在函数**归集，产出 `docs/com-member-index.md`（人看）+ `.json`（机器读）。

## 用法

```
python -B tools/gen_com_member_index.py            # 重新生成
python -B tools/find_com_wrapper.py AddDimension2  # 反查「我们封了吗、在哪个函数」
```
"""
from __future__ import annotations

import ast
import json
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
R = Path(__file__).resolve().parents[1]

OUT_MD = R / "docs" / "com-member-index.md"
OUT_JSON = R / "docs" / "com-member-index.json"

#: 匹配 `I接口.成员` / `ISketchManager.CreatePoint`
PAT = re.compile(r"\bI([A-Z]\w*?)\.([A-Z]\w*)\b")


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库 / 文件 / 定位 / 官方依据 / 许可 / 覆盖
# 仓库:   本项目自身（工具 · COM 成员反查索引生成器）
# 文件:   tools/gen_com_member_index.py
# 定位:   从 scripts/*.py 的 docstring/注释抽 `I<接口>.<成员>`，按所在函数归集成反查表，
#          治「忘了我们已经封过这个成员」。起因：业主 2026-10-26 质问为何跳过自家工具层
# 。
# 官方依据: 不适用（纯静态分析，用标准库 ast / re）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────


def _doc_text(node: ast.AST, src: str) -> str:
    """取一个函数的 docstring + 其 `#:` 注释（后者用源码片段近似）。"""
    parts = [ast.get_docstring(node) or ""]
    seg = ast.get_source_segment(src, node) or ""
    for line in seg.splitlines():
        s = line.strip()
        if s.startswith("#"):
            parts.append(s)
    return "\n".join(parts)


def scan() -> dict:
    """回 `{成员名: [{module, function, interface}]}`。"""
    index: dict = {}
    for p in sorted((R / "scripts").rglob("*.py")):
        try:
            src = p.read_text(encoding="utf-8", errors="replace")
            tree = ast.parse(src)
        except SyntaxError:
            continue
        rel = p.relative_to(R).as_posix()
        for node in ast.walk(tree):
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            text = _doc_text(node, src)
            for m in PAT.finditer(text):
                iface, member = m.group(1), m.group(2)
                key = member
                index.setdefault(key, [])
                item = {"module": rel, "function": node.name, "interface": iface}
                if item not in index[key]:
                    index[key].append(item)
    return index


def render_md(index: dict) -> str:
    lines = [
        "# COM 成员 → 本仓封装 反查表（生成物，勿手改）",
        "",
        "**本文件由 `tools/gen_com_member_index.py` 生成。**",
        "",
        "★ 来历：2026-10-26 业主质问「怎么又去查官方 API 了？我们自己不是有工具吗」。",
        "  实情是我手写的 `AddDimension2` / `EditDelete` / `SelectByID2`",
        "  全都有现成封装 ——",
        "  而本仓**没有反查表**，只记得官方成员名，不记得自己封过。",
        "",
        "★ 用法：动某个 COM 成员前，先在这里查 ——",
        "  ```bash",
        "  python -B tools/find_com_wrapper.py <成员名>",
        "  ```",
        "",
        "| COM 成员 | 本仓封装（模块::函数） |",
        "|---|---|",
    ]
    for member in sorted(index, key=lambda k: (-len(index[k]), k)):
        hits = index[member]
        first = hits[0]
        #: ★ 不写「等 N 处」—— 量化断言会被事实出处门禁要求给出处（见
        #:   `scripts/check_fact_provenance.py`）。要数就去 JSON 里数。
        more = " …" if len(hits) > 1 else ""
        lines.append(
            "| `%s` | `%s::%s`%s |"
            % (
                first["interface"] + "." + member,
                first["module"],
                first["function"],
                more,
            )
        )
    lines.append("")
    lines.append("成员总数见 `docs/com-member-index.json`（生成物，勿手改）。")
    return "\n".join(lines) + "\n"


def main() -> int:
    index = scan()
    OUT_JSON.write_text(
        json.dumps(index, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    OUT_MD.write_text(render_md(index), encoding="utf-8")
    print("已生成 %s（%d 个成员）与 %s" % (OUT_MD.name, len(index), OUT_JSON.name))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
