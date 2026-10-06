"""★ 批次 97 的契约测试：BOM 气泡（AutoBalloon5）+ ★★ 判据必须是纯回读增量。"""
# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   `mcp-server/tool_specs_batch97.py` · `scripts/sw_drawing_create_missing.py`
# 定位:   ★ 规格 `specs/209-union-adopt-18/` 的 **B2-2（idx 34）**；本文件钉三件事：
#         ① 契约：spec 能解析、**必填形参一个不差**（本函数的形参**全有默认值** ⇒ 声明可省）✓
#         ② ★★ **判据契约**：`ok` 必须由 **`GetNoteCount` 的增量**决定，
#            ★ **不许**再依赖 `AutoBalloon5` 返回的数组（★ 那正是别家错的地方）✓
#         ③ ★ **前置四步**里的第 1 步（**先选中视图/图纸**）要在返回值里可核 ✓
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
from __future__ import annotations

import importlib
import inspect
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for _p in (str(ROOT), str(ROOT / "scripts"), str(ROOT / "mcp-server")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import register_capabilities as rc                            # noqa: E402
import tool_specs_batch97 as b97                              # noqa: E402

EXPECTED = 1


def test_batch97_registered():
    t = (ROOT / "mcp-server" / "register_capabilities.py").read_text(encoding="utf-8")
    assert '"tool_specs_batch97"' in t


def test_one_spec_declared_and_resolves():
    assert len(b97.SPECS_BATCH97) == EXPECTED, len(b97.SPECS_BATCH97)
    s = b97.SPECS_BATCH97[0]
    assert s.name == "solidworks_drawing_insert_balloons", s.name
    m = importlib.import_module("scripts.%s" % s.module)
    assert callable(getattr(m, s.function, None)), (s.module, s.function)
    assert s.inject == "model"


def test_declared_params_all_exist_on_the_function():
    """★ 声明名必须都是目标函数**真有的**形参（★ 反向漏声明由 `check_param_binding` 管）✓"""
    s = b97.SPECS_BATCH97[0]
    sig = inspect.signature(
        importlib.import_module("scripts.sw_drawing_create_missing").auto_insert_balloons)
    for p in s.params:
        assert p.name in sig.parameters, (p.name, sorted(sig.parameters))
    #: ★ 本函数**全有默认值** ⇒ 「必填形参」为空 ⇒ 声明可省；★ 断言这一点以免将来误判
    required = [n for n, p in sig.parameters.items()
                if p.default is inspect.Parameter.empty and n != "model"]
    assert required == [], required


def test_criterion_is_the_note_count_delta_not_the_returned_array():
    """★★★ **本批的核心**：`ok` 必须由 **`sum(IView::GetNoteCount)` 的增量**决定 ——
    ★ 不许依赖 `AutoBalloon5` **返回的数组**（★ 别家 `bool(result)` 错在这里）；
    ★ 且**不许**再用 `delta >= 0`（★ **差 0 = 什么都没插，却会通过**）✓

    ⚠ **本用例第一版把"注释里引用的旧判据"也报成了违规**（★ 交接文档 trap 4 的同一形态：
    「会喊狼的守卫会被无视」）⇒ ★ 修法照本仓既有的做法：**负面断言只扫代码**
    （用 `scripts/check_env_pitfalls.strip_comments_and_strings` 把注释与字符串剥掉），
    ★ **正面断言才看原文** ✓ —— 与 `tests/test_tool_specs_batch93.py` **同一处置** ✓
    """
    sys.path.insert(0, str(ROOT / "scripts"))
    from check_env_pitfalls import strip_comments_and_strings
    src = inspect.getsource(
        importlib.import_module("scripts.sw_drawing_create_missing").auto_insert_balloons)
    code = strip_comments_and_strings(src)
    assert "delta is not None and delta > 0" in src, "★ ok 必须是纯回读增量 > 0"
    assert "delta >= 0" not in code, "★ 旧的松判据不许留在**代码**里（注释里引用它是防它的证据）"
    assert "bool(balloon_notes) and" not in code, "★ 旧判据（依赖返回数组）不许留在**代码**里"


def test_return_shape_carries_both_readings_and_the_official_precondition():
    """★ 返回值要**两个读数都带**（增量 + 返回数组长度），★ 并写明官方那个 BOM 表前置 ——
    ★ 这样调用方自己就能看出「Δ=0 而返回数组非空」这种**必须存疑**的情形 ✓

    ★ 注意：本用例**扫源码**而不是调 `auto_insert_balloons(None)` ——
    ★ 因为 `model=None` 走的是**早退分支**，那个分支的返回体**不完整**（只有 `ok/op/error`）✓
    """
    src = inspect.getsource(
        importlib.import_module("scripts.sw_drawing_create_missing").auto_insert_balloons)
    for key in ("note_count_before", "note_count_after", "note_count_delta",
                "balloon_note_count", "returned_is_none", "criterion",
                "official_precondition_bom_table", "preconditions_held"):
        assert '"%s"' % key in src, (key,)
    #: ★ 早退分支**只回** `ok/op/error` —— ★ 把它也钉住（免得有人以为它有完整形状）
    import sw_drawing_create_missing as DM
    early = DM.auto_insert_balloons(None)
    assert early["ok"] is False and set(early) == {"ok", "op", "error"}, early


def test_tool_total_grew_by_one():
    assert len(rc.all_specs()) == 446, len(rc.all_specs())
