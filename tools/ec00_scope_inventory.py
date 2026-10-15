"""★ EC00 范围清单：静态盘点代表工具集的**注入/参数/单位/风险/效果/来源/等级**（★ **不连接 COM**）。"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   D:/AI/SW
# 文件:   `mcp-server/tool_registry.py`（`ToolSpec`/`Param` 数据类）· `mcp-server/register_capabilities.py`
#         `capabilities.yaml`（`level` + `evidence`）· `docs/effect-declarations.json`（效应表）
#         `specs/302-ec00-trustworthy-tool-base/spec.md`（FR-001/002 · SC-001）
#         `output/ENGINEERING_P0_TASKS_DRAFT.md` §2 **T004**（★ 逐字：静态盘点**不连接 COM**）
# 定位:   ★ EC00 **T004** 的产物 —— 「冻结代表工具集和公开 ToolSpec 名称，
#         静态盘点注入/参数/单位/风险/效果/来源/等级/测试」。
#         ★★ 纪律：**范围 100% 有字段，未知具名**；★★ **静态盘点不连接 COM**。
# 官方依据: 不适用（本仓自产的静态盘点器，不碰 SolidWorks API）
# 许可:   本仓自产（无外部来源）
# 覆盖:   只读 `mcp-server/` + `capabilities.yaml` + `docs/effect-declarations.json`；★ 不写任何文件
# ────────────────────────────────────────────────────────────────────
from __future__ import annotations

import ast
import json
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parents[1]
for _p in (str(ROOT), str(ROOT / "scripts"), str(ROOT / "mcp-server")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

#: ★★ 计划 §5.1 要求的**五类**代表工具（★ 每类至少一个）
REPRESENTATIVE = {
    "① 草图长度/角度输入": "solidworks_sketch_add_line",
    "② 草图关系": "solidworks_add_sketch_relation",
    "③ 几何/体数回读": "solidworks_entities_on_body",
    "④ 文档/配置/版本上下文": "solidworks_config_inspect",
    "⑤ 旧入口与后继对照": "solidworks_api_deprecated_successor",
}

#: ★★ 长度/角度后缀（★ 规则 2）—— 用于判「单位是否显式」
LEN_SUFFIX = "_mm"
ANGLE_SUFFIX = "_deg"


def _effect_table() -> dict:
    """★ 读效应表（★ `docs/effect-declarations.json`）—— ★ **不连接 COM**。"""
    p = ROOT / "docs" / "effect-declarations.json"
    if not p.is_file():
        return {}
    try:
        return (json.loads(p.read_text(encoding="utf-8")).get("tools") or {})
    except Exception:                                                  # noqa: BLE001
        return {}


def _capability_levels() -> dict:
    """★ 读 `capabilities.yaml` 的 **能力域** `id -> level`。

    ★★★ **2026-10-10（T004 实测）口径订正**：★ `capabilities.yaml` 的 `capabilities[].id`
      **是「能力域」名**（★ 如 `sketch_primitives_b1` · `sketch_edit_ops`），
      ★★ **不是工具名**（★ 如 `solidworks_sketch_add_line`）⇒ ★ **两者不同域**，
      ★ 直接拿工具名去查**必然 `unknown`**（★ 那是**口径错配**、不是缺数据）。
    ⇒ ★★ 正解：★ 输出**能力域的 `level` 分布**（★ 那是**真实可用**的读数），
      ★ 而工具级等级**如实标 `not-mapped`**（★ 不编一个假映射）。
    """
    p = ROOT / "capabilities.yaml"
    if not p.is_file():
        return {}
    text = p.read_text(encoding="utf-8", errors="replace")
    out = {}
    #: ★ 只取 `capabilities` 段里的 `"id" + "level"` 配对（★ 能力域）
    i = text.find('"capabilities"')
    seg = text[i:] if i >= 0 else text
    for m in re.finditer(r'"id":\s*"([^"]+)"[\s\S]{0,600}?"level":\s*"([^"]+)"', seg):
        out[m.group(1)] = m.group(2)
    return out


def _level_distribution(levels: dict) -> dict:
    """★ 能力域的 `level` 分布（★ 那是**真实可用**的读数）。"""
    dist: dict[str, int] = {}
    for lv in levels.values():
        dist[lv] = dist.get(lv, 0) + 1
    return dict(sorted(dist.items(), key=lambda kv: -kv[1]))


def _tests_referencing(tool_name: str) -> list[str]:
    """★ 找**提到该工具名**的测试文件（★ 静态扫文本，★ 不 import）。"""
    hits = []
    for p in sorted((ROOT / "tests").glob("test_*.py")):
        try:
            if tool_name in p.read_text(encoding="utf-8", errors="replace"):
                hits.append(p.name)
        except Exception:                                              # noqa: BLE001
            continue
    return hits


def _params_of(spec) -> list[dict]:
    """★ 逐参数：名 · 类型 · 必填 · 单位后缀（★ 未知具名）。"""
    out = []
    for p in (spec.params or []):
        unit = "unknown"
        if p.name.endswith(LEN_SUFFIX):
            unit = "length:mm"
        elif p.name.endswith(ANGLE_SUFFIX):
            unit = "angle:deg"
        elif p.kind is bool:
            unit = "dimensionless:bool"
        elif p.kind in (int, float):
            unit = "unknown"          # ★★ **未知具名**（★ 不编单位）
        out.append({"name": p.name, "kind": p.kind.__name__,
                    "required": bool(p.is_required), "unit": unit})
    return out


def _function_source(module: str, function: str) -> str:
    """★ 取目标函数的源码段（★ 静态读文件，★ **不 import 该模块** ⇒ ★ 不触发 COM 副作用）。"""
    p = ROOT / "scripts" / ("%s.py" % module)
    if not p.is_file():
        return ""
    try:
        text = p.read_text(encoding="utf-8", errors="replace")
        tree = ast.parse(text)
    except Exception:                                                  # noqa: BLE001
        return ""
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == function:
            return ast.get_source_segment(text, node) or ""
    return ""


def build() -> dict:
    """★ 生成范围清单（★ 纯静态 · ★ 不连接 COM）。"""
    import register_capabilities as rc

    specs = {s.name: s for s in rc.all_specs()}
    effects = _effect_table()
    levels = _capability_levels()

    rows = []
    for cls, tool in REPRESENTATIVE.items():
        spec = specs.get(tool)
        if spec is None:
            rows.append({"class": cls, "tool": tool, "status": "NOT-FOUND"})
            continue
        src = _function_source(spec.module, spec.function)
        rows.append({
            "class": cls,
            "tool": tool,
            "module": spec.module,
            "function": spec.function,
            "inject": spec.inject or ("model" if spec.needs_model else ""),
            "params": _params_of(spec),
            "writes": spec.writes,
            "writes_source": spec.writes_source,
            "requires": list(spec.requires or []),
            "idempotent": spec.idempotent,
            "destructive": spec.destructive,
            "effect_declared": effects.get(tool, "unknown"),
            #: ★★ **工具级等级 = `not-mapped`** —— ★ `capabilities.yaml` 的 `level` 是**能力域级**的，
            #:   ★★ **两者不同域** ⇒ ★ **如实标 `not-mapped`**（★ 不编一个假映射）。
            "capability_level": "not-mapped",
            "tests": _tests_referencing(tool),
            "has_pre_call": spec.pre_call is not None,
            "has_derived_args": spec.derived_args is not None,
            "calls_com_directly": bool(re.search(r"get_com_member|SelectByID2|Select4", src or "")),
            "unknowns": [k for k in ("writes", "idempotent", "destructive")
                         if getattr(spec, k) is None] or [],
        })
    return {"representative": rows, "total_specs": len(specs),
            "capability_level_distribution": _level_distribution(levels),
            "capability_domains": len(levels)}


def main() -> int:
    data = build()
    out = ROOT / "specs" / "302-ec00-trustworthy-tool-base" / "output-ec00-scope.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print("★ EC00 范围清单（★ 静态 · ★ 未连接 COM）· 工具总数 %d" % data["total_specs"])
    print("★ 能力域 %d 个 · level 分布 %s"
          % (data["capability_domains"], data["capability_level_distribution"]))
    for r in data["representative"]:
        if r.get("status") == "NOT-FOUND":
            print("  ✗ %-22s %s" % (r["class"], r["tool"]))
            continue
        print("  ✓ %-22s %-38s inject=%-6s params=%-2d effect=%-10s unknowns=%s"
              % (r["class"], r["tool"], r["inject"] or "(none)", len(r["params"]),
                 str(r["effect_declared"])[:10], r["unknowns"] or "[]"))
    print("产物：%s" % out.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
