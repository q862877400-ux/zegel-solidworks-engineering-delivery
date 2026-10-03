"""★ 测 `run_topology_study` **兑现「报告结果是否存在」**（★ `JUDGE-C_D_E` 🔴 #14 · 含负例）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身。
# 文件:   `scripts/sw_topology.py::run_topology_study` · `collect_topology_numbers` ·
#         `mcp-server/tool_specs_batch1.py`（ToolSpec 的那句承诺）
# 定位:   ★ `JUDGE-C_D_E.md` 的 🔴 **#14**（★ `E-1 #5`）逐字：「★ `topology_run` 承诺
#   「**报告结果是否存在**」★ 实则**只返回码**」✓
#   ★★ **而那句承诺逐字在 ToolSpec 里**：★ 「Mesh and solve the topology study and
#     **report whether results exist**. ★★ A zero RunAnalysis return code does NOT mean
#     success — **judge by study results**.」✓
#   ★★★ **修法**：★ 跑完就调本模块既有的 `collect_topology_numbers` ——
#     它的判据逐字是「**不用任何返回码判成功**：★ 有结果 = `Results` 非 None
#     且 `GetPlotCount() > 0`」✓
#   许可:   本仓库 MIT。★ 无第三方代码引入。
#   覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

import ast
import io
import sys
import tokenize
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SRC = REPO / "scripts" / "sw_topology.py"
SPEC = REPO / "mcp-server" / "tool_specs_batch1.py"


def _seg(fn: str) -> str:
    """★ 取函数的**代码段**（★ **剥掉它自己的 docstring** —— ★ 事实 513）。"""
    src = SRC.read_text(encoding="utf-8", errors="replace")
    for n in ast.walk(ast.parse(src)):
        if isinstance(n, ast.FunctionDef) and n.name == fn:
            if n.body and isinstance(n.body[0], ast.Expr) and isinstance(
                    getattr(n.body[0], "value", None), ast.Constant) and isinstance(
                    n.body[0].value.value, str):
                n.body[0] = ast.Pass()
            return ast.unparse(n)
    return ""


def test_spec_promise_is_still_there() -> None:
    """★★★ **前提断言**：★ ToolSpec 那句承诺**确实**还在（★ 判据的锚点）✓"""
    t = SPEC.read_text(encoding="utf-8", errors="replace")
    assert "report whether results exist" in t, "★ ToolSpec 的承诺变了 ⇒ 判据要重看"
    assert "judge by study results" in t, "★ 后半句也没了"


def test_run_does_not_return_only_the_code() -> None:
    """★★★ 核心断言：★ 不许**只**回 `code`（★ 那正是本条病灶）✓"""
    seg = _seg("run_topology_study")
    assert seg, "★ 找不到 `run_topology_study`"
    #: ★ 不许是裸 `return code`
    assert "return code\n" not in seg + "\n", "★ 还是只 `return code`"
    assert "'results_present'" in seg or '"results_present"' in seg, "★ 没回「结果是否存在」"


def test_run_judges_by_results_not_by_code() -> None:
    """★★★ 核心断言：★ 判据必须**来自结果**（★ 而不是返回码）✓"""
    seg = _seg("run_topology_study")
    assert "collect_topology_numbers" in seg, "★ 没调本模块既有的结果读法"
    assert 'status' in seg, "★ 没看 `status`"


def test_negative_case_code_is_kept_for_compat() -> None:
    """★★ **负例 · 兼容**：★ `code` 必须**保留**（★ 向后兼容 —— 别处还在读它）✓"""
    seg = _seg("run_topology_study")
    assert "'code': code" in seg or '"code": code' in seg, "★ 把 `code` 丢了 ⇒ 破坏调用方"
    assert "RunAnalysis" in seg, "★ 连求解调用都没了"
