"""★ 为「每条工具改写」生成**工作简报**：一个 JSON，一个执行者一份。

为什么要有它：执行者需要的是「改哪一条、原文是什么、参数有哪些、去哪个函数核语义」，
**不是** 15 个 500 行的批次源文件。简报只放这四样，省掉大量无关行。

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   `mcp-server/register_capabilities.py::all_specs()`（工具声明真源）
#         `specs/352-tool-definition-contract/groups.json`（分组）
#         `specs/352-tool-definition-contract/pilot-en.json`（改写样板）
# 定位:   ★ 规格 352 P4 的派活工件 —— 生成物、可重跑、不入库判断。
# 官方依据: 不适用（纯静态：读 `ToolSpec`，不连 SolidWorks）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parents[1]
SPEC_DIR = ROOT / "specs" / "352-tool-definition-contract"
GROUPS = SPEC_DIR / "groups.json"
OUT = ROOT / "output" / "_briefs"


def main() -> int:
    sys.path[:0] = [str(ROOT / "mcp-server"), str(ROOT / "scripts"), str(ROOT)]
    import importlib  # noqa: PLC0415

    import register_capabilities as rc  # noqa: PLC0415

    by_mod: dict = {}
    for b in rc.BATCH_MODULES:
        mod = importlib.import_module(b)
        for k, v in vars(mod).items():
            if k.startswith("SPECS_") and isinstance(v, list):
                by_mod[b] = [s.name for s in v]
                break
    specs = {s.name: s for s in rc.all_specs()}
    groups = json.loads(GROUPS.read_text(encoding="utf-8"))["groups"]

    OUT.mkdir(parents=True, exist_ok=True)
    for g in groups:
        items = []
        for b in g["modules"]:
            for name in by_mod.get(b, []):
                s = specs[name]
                items.append(
                    {
                        "name": name,
                        "batch_file": "mcp-server/%s.py" % b,
                        "impl": "%s.%s" % (s.module, s.function),
                        "read_only": s.read_only,
                        "writes": list(s.writes) if s.writes else None,
                        #: ★★ 原文 = **改写前 doc 的逐字副本**（已搬进 evidence）
                        #:   ⇒ 执行者改写时**唯一允许的事实来源**之一 ✓
                        "evidence": (s.evidence or s.doc or "").strip(),
                        "current_doc": (s.doc or "").strip(),
                        "params": [
                            {
                                "name": p.name,
                                "kind": p.kind.__name__,
                                "required": p.is_required,
                                "default": None if p.is_required else p.default,
                                "desc": p.description,
                            }
                            for p in s.params
                        ],
                    }
                )
        p = OUT / ("%s.json" % g["id"])
        p.write_text(
            json.dumps(
                {
                    "_group": g["id"],
                    "_howto": [
                        "为 items 里每条工具写 {doc, params}；params 只写要改的参数说明。",
                        "★ 事实只许来自 evidence / current_doc / impl 函数的 docstring。",
                        "★ 首句 = <动词> <对象> <关键限定>，≤120 字符、英文、不用中文句号、不带 ★。",
                        "★ 整段 ≤600 字符；第二句起写 前置 / 副作用 / 返回什么 / 何时别用。",
                        "★ 参数说明：<它是什么>[; <取值域>][; defaults to <默认值>].（句号必须）",
                        "★ 只读工具的描述里必须出现 Read-only；会改状态的必须出现副作用词。",
                        "样板见 specs/352-tool-definition-contract/pilot-en.json。",
                    ],
                    "items": items,
                },
                ensure_ascii=False,
                indent=1,
            )
            + "\n",
            encoding="utf-8",
        )
        print("★ %s ⇒ %d 条 → %s" % (g["id"], len(items), p.relative_to(ROOT)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
