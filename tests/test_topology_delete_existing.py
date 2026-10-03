"""★ 测 `create_topology_study` **兑现「同名先删」**（★ `JUDGE-C_D_E` 🔴 #14 · E-1 #6 · 含负例）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身 + **官方示例**（`_raw/**/Create_Topology_Study_Example_VBA.txt`）
# 文件:   `scripts/sw_topology.py::create_topology_study` · `sw_simulation_study.delete_study` ·
#         `mcp-server/tool_specs_batch1.py`（Param 的承诺）
# 定位:   ★ `JUDGE-C_D_E.md` 的 🔴 **#14**（★ `E-1 #6`）逐字：「★ `create_study` 的 Param 承诺
#   「**同名先删**」★ 实则**把同名当错误码 2** 且**无任何删除调用**」✓
#   ★★★★ **依据是官方示例**（★ 我读了 `Create_Topology_Study_Example_VBA.txt` L131-135）：
#     ```
#     ' Create Topology Study 1
#     NewStudyName = "Topology Study 1"
#     ★★ StudyManagerObj.DeleteStudy NewStudyName          ← ★ 先删同名
#     ★★★ Set CWNewStudy = StudyManagerObj.CreateNewStudy3(NewStudyName, 13, 0, ErrorCodeObj)
#     ```
#   ⇒ ★ **调用序 `DeleteStudy` ⇒ `CreateNewStudy3`** ✓
#   许可:   本仓库 MIT。★ 无第三方代码引入。
#   覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

import ast
import inspect
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "scripts"))

SRC = REPO / "scripts" / "sw_topology.py"
SPEC = REPO / "mcp-server" / "tool_specs_batch1.py"
OFFICIAL = REPO / "_raw"


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


def test_official_example_has_delete_before_create() -> None:
    """★★★ **前提断言**：★ 官方示例**确实**是「先删后建」（★ 判据的锚点）✓"""
    if not OFFICIAL.is_dir():
        return                                                            # ★ 官方示例不在本机 ⇒ 跳过
    hits = []
    for f in OFFICIAL.rglob("Create_Topology_Study_Example_VBA.txt"):
        hits += f.read_text(encoding="utf-8", errors="replace").splitlines()
    assert hits, "★ 官方示例不在"
    txt = "\n".join(hits)
    assert "DeleteStudy NewStudyName" in txt, "★ 官方示例里没有那句「先删」了 ⇒ 判据要重看"
    i_del = txt.find("DeleteStudy NewStudyName")
    i_new = txt.find("CreateNewStudy3(NewStudyName")
    assert i_del != -1 and i_new != -1 and i_del < i_new, "★ 官方示例的次序变了"


def test_capability_calls_delete_study() -> None:
    """★★★ 核心断言：★ 能力层**必须**先调 `delete_study` ✓"""
    seg = _seg("create_topology_study")
    assert seg, "★ 找不到 `create_topology_study`"
    assert "delete_study(manager" in seg, "★ 仍然**没有删除调用**（★ 那正是本条病灶）"
    assert "CreateNewStudy3" in seg, "★ 建研究那步没了"


def test_negative_case_return_shape_is_unchanged() -> None:
    """★★★ **负例 · 兼容**：★ **返回必须仍是 2 元**（★ `tools/` 里有人解包 2 元）✓

    ★★ 为什么重要：★ 纪律是「**`tools/` 只报不动**」⇒ ★★ **不能为了加信息而改返回形状** ——
      ★★★ 那会**逼着去改 `tools/`** ⇒ ★ **所以本轮改用**开关参数**而不是加返回值** ✓
    """
    code = (REPO / "scripts" / "sw_topology.py").read_text(encoding="utf-8", errors="replace")
    import importlib
    mod = importlib.import_module("sw_topology")
    assert "delete_existing" in inspect.signature(mod.create_topology_study).parameters, (
        "★ 没给开关参数 ⇒ 无法关闭「先删」")
    #: ★ 函数体最后必须仍是 2 元返回
    seg = _seg("create_topology_study")
    assert "return (study, entry_name)" in seg or "return study, entry_name" in seg, (
        "★ 返回形状变了 ⇒ 会破坏解包 2 元的调用方")
    assert "delete_note" not in code.split("def create_topology_study")[1].split("return")[-1], (
        "★ 把 `delete_note` 混进返回值了")


def test_negative_case_delete_failure_is_tolerated() -> None:
    """★★ **负例 · 容错**：★ 同名不存在时 `DeleteStudy` 会报错 ⇒ **必须容错**（★ 首次建是正常路径）✓"""
    seg = _seg("create_topology_study")
    assert "except Exception" in seg, "★ 没兜住 `DeleteStudy` 的错 ⇒ 首次建会炸"
