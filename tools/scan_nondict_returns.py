"""★ 扫「目标函数的返回**不是 dict**」的工具 —— 它们经 MCP 层会被 `json.dumps` 判死。

★ 病灶（`mcp-server/server.py:1001-1004` 逐字）：
    def _result(payload, response_format):
        if response_format == ResponseFormat.JSON:
            return json.dumps(payload, ensure_ascii=False, indent=2)   # ★ 没有 default=！
★ 而 `_run_locked`（:1031-1042）把 `_result` 包在 `try/except` 里 ⇒
  **返回原始 COM 对象（或任何不可 JSON 序列化的东西）时**：
    ★ `json.dumps` 抛 `TypeError: Object of type CDispatch is not JSON serializable`
    ⇒ ★ **被 `except` 吞掉、返回 `_tool_error`** ⇒ ★★ **能力明明建成了，MCP 调用方却收到 error**。
★ 附带：`_result` 在 markdown 分支还会 `payload.get("status", ...)` ⇒ ★ **非 dict 连 `.get` 都会炸**。
★ 判据：看目标函数的 **`return` 语句**是不是 **dict 字面量 / 已知 dict 变量**；
  ★ 是**裸调用**（如 `return model.FeatureManager.FeatureFillet(...)`）⇒ ★ 归入本族。
"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   tools/scan_nondict_returns.py
# 定位:   扫「目标函数的返回**不是 dict**」的工具 —— 它们经 MCP 层会被 `json.dumps` 判
#           死。
# 官方依据: ★ 扫**本仓**工具的目标函数返回类型一致性，★ 不涉官方签名
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

import ast
import importlib
import inspect
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
REPO = Path(Path(__file__).resolve().parents[1])
for _p in (str(REPO), str(REPO / "scripts"), str(REPO / "mcp-server")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
import register_capabilities as RC  # noqa: E402


def _fn_node(path: Path, name: str):
    try:
        src = path.read_text(encoding="utf-8", errors="replace")
        tree = ast.parse(src)
    except Exception:                                                     # noqa: BLE001
        return None, "", ""
    for n in ast.walk(tree):
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name == name:
            return n, ast.get_source_segment(src, n) or "", src
    return None, "", ""


def classify(fn_node) -> list:
    """★ 返回 (kind, snippet)：kind ∈ dict / bare / mixed / none。"""
    kinds = []
    for n in ast.walk(fn_node):
        if not isinstance(n, ast.Return) or n.value is None:
            continue
        v = n.value
        if isinstance(v, ast.Dict):
            kinds.append("dict")
        elif isinstance(v, ast.Name) and v.id.lower() in ("out", "result", "report", "res", "payload"):
            kinds.append("dict")
        elif isinstance(v, ast.Call):
            f = v.func
            fname = getattr(f, "attr", None) or getattr(f, "id", None) or ""
            kinds.append("dict" if fname.startswith(("_result", "_out", "_report")) else "bare")
        elif isinstance(v, ast.Name):
            kinds.append("dict")                     #: 变量名兜底（多半是攒好的 dict）
        else:
            kinds.append("bare")
    return kinds


rows = []
for spec in RC.all_specs():
    name = getattr(spec, "name", None) or "?"
    mod, fn = getattr(spec, "module", "") or "", getattr(spec, "function", "") or ""
    if not mod or not fn:
        continue
    node, src, _ = _fn_node(REPO / "scripts" / (mod + ".py"), fn)
    if node is None:
        continue
    kinds = classify(node)
    if not kinds:
        continue
    bad = [k for k in kinds if k == "bare"]
    if bad:
        #: ★ 取第一条裸 return 的原文，当依据
        snip = ""
        for n in ast.walk(node):
            if isinstance(n, ast.Return) and n.value is not None and not isinstance(n.value, ast.Dict):
                if isinstance(n.value, ast.Call):
                    attr = getattr(n.value.func, "attr", None) or ""
                    if not attr.startswith(("_result", "_out", "_report")):
                        snip = ast.unparse(n.value)[:78]
                        break
        rows.append((name, "%s.%s" % (mod, fn), len(bad), len(kinds), snip))

print("★ 目标函数里有**裸 return（非 dict）**的工具：**%d** 个" % len(rows))
print("%-48s %-34s %-10s %s" % ("工具", "函数", "裸/总", "第一条裸 return 原文"))
print("-" * 132)
for r in sorted(rows):
    print("%-48s %-34s %-10s %s" % (r[0].replace("solidworks_", "")[:47], r[1][:33],
                                    "%d/%d" % (r[2], r[3]), r[4]))
