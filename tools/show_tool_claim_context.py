"""打印一个工具的「核验上下文」：模型可见描述 + 实现 + 草稿成员 + 官方页原文。

用途：`specs/353` P2c 的人工复核要让核验人**一眼看到该看的四样东西**，
不必自己拼路径、也不必凭印象。
  ```bash
  python -B tools/show_tool_claim_context.py --tool solidworks_sketch_start
  ```

输出四段：
  ① 模型可见描述（真握手那一份）· ② 实现文件里该函数的源码
  ③ 草稿登记的成员（接口.成员 + 官方页路径 + 页里的原文锚点）
  ④ 每个成员官方页的**正文**（Description / Signature / Remarks），供逐字引用

★ 只读：不写文件、不连 SolidWorks。

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（规格 353 P2c 复核用的取证打印器）
# 文件:   `tools/gen_tool_official_claims.py`（成员提取与官方页定位，复用）
#         `scripts/check_tool_official_claims.py`（判据；本工具不重新判定）
#         `docs/tool-official-claims/README.md`（记录格式与核验动作）
# 定位:   ★ 业主 2026-11-01「不能根据记忆和印象…必须去官方 API 文档」⇒
#         把「该读的那几页」直接摆到核验人眼前，避免他只看我们的描述。
# 官方依据: `C:\\swapi\\types\\<接口>\\<成员>.md`（正文 + front-matter）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   单个工具；**不连 SolidWorks**
# ─────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

import argparse
import ast
import json
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parents[1]
DRAFT = ROOT / "docs" / "tool-official-claims" / "_draft-all.json"


def source_of(impl: str) -> str:
    """⇒ 实现函数（含其 docstring 与函数体）的源码文本。

    :param impl: `相对路径:函数名`。
    """
    rel, _, func = impl.rpartition(":")
    path = ROOT / rel
    if not path.is_file():
        return "（实现文件不存在：%s）" % rel
    text = path.read_text(encoding="utf-8", errors="replace")
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return text[:2000]
    lines = text.splitlines()
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == func:
            end = getattr(node, "end_lineno", node.lineno + 60)
            return "\n".join(lines[node.lineno - 1 : min(end, node.lineno + 119)])
    return "（函数 %s 不存在）" % func


def main(argv=None) -> int:
    """命令行入口。

    :param argv: 命令行参数。
    """
    ap = argparse.ArgumentParser(description="打印工具核验上下文（规格 353）")
    ap.add_argument("--tool", required=True)
    ap.add_argument("--page-chars", type=int, default=2400, help="每个官方页最多打印多少字符")
    args = ap.parse_args(argv)

    data = {r["tool"]: r for r in json.loads(DRAFT.read_text(encoding="utf-8"))["records"]}
    rec = data.get(args.tool)
    if rec is None:
        print("✗ 草稿里没有 %s（可能实现找不到）" % args.tool)
        return 2
    sys.path.insert(0, str(ROOT / "mcp-server"))
    sys.path.insert(0, str(ROOT / "tools"))
    from mcp_tools_list import tools_list  # noqa: PLC0415

    doc = next((t.get("description", "") for t in tools_list() if t["name"] == args.tool), "")
    print("① 模型可见描述\n%s\n" % (doc or "（空）"))
    print("② 实现：%s\n%s\n" % (rec["impl"], source_of(rec["impl"])))
    print("③ 草稿登记的成员（%d 个）" % len(rec.get("members") or []))
    for m in rec.get("members") or []:
        print("   %s.%s  %s" % (m.get("interface"), m.get("member"), m.get("path") or "（无页，已记账）"))
        if m.get("anchor"):
            print("        锚点：%s" % m["anchor"][:160])
        if m.get("documented") is False:
            print("        gap：%s" % str(m.get("gap"))[:160])
    print("\n④ 官方页原文")
    for m in rec.get("members") or []:
        path = Path(m.get("path") or "")
        if not path.is_file():
            print("   —— %s.%s：无官方页（%s）" % (m.get("interface"), m.get("member"), path))
            continue
        text = re.sub(r"\n{3,}", "\n\n", path.read_text(encoding="utf-8", errors="replace"))
        print("   —— %s.%s  %s" % (m.get("interface"), m.get("member"), path))
        print(text[: args.page_chars])
        print("   …（截断）\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
