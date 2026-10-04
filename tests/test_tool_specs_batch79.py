"""★ 批次 79 的契约测试：**FR-008 的两半真的挂上了**（爆炸视图 9 + 宏 8 = 17）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   `mcp-server/tool_specs_batch79.py`（★ 被测）· `scripts/sw_assembly_doc.py` 的爆炸视图段 ·
#         `scripts/sw_macro.py`（新建）· `scripts/sw_macro_guard.py`（既有）
# 定位:   ★ 规格 202 的 **FR-008**（爆炸视图 + 宏/VBA 执行 MUST 可用）· 规格 204 的 SC-002/SC-004
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
from __future__ import annotations

import importlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for _p in (str(ROOT), str(ROOT / "scripts"), str(ROOT / "mcp-server")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import register_capabilities as rc                            # noqa: E402

EXPLODED = ("create_exploded_view", "auto_explode", "view_explode_assembly", "view_collapse_assembly",
            "show_exploded", "get_exploded_view_names", "get_exploded_view_count",
            "get_exploded_view_configuration_name", "edit_explode_parameters")
MACRO_GUARD = ("normalize_model_family", "build_prompt", "extract_vba_code", "validate_vba_macro",
               "select_template_key", "fallback_macro_for_request", "write_macro_file")


def _by_name():
    return {getattr(s, "name", ""): s for s in rc.all_specs()}


def test_batch79_is_registered():
    """★ 批次必须进 `BATCH_MODULES`（★ 声明了不注册 = 到不了运行期）。"""
    t = (ROOT / "mcp-server" / "register_capabilities.py").read_text(encoding="utf-8")
    assert '"tool_specs_batch79"' in t, "★ batch79 没进 BATCH_MODULES"


def test_all_seventeen_tools_reach_all_specs():
    """★★ FR-008 的两半：**9 个爆炸视图 + 8 个宏**都要在 `all_specs()` 里。"""
    names = {getattr(s, "name", "") for s in rc.all_specs()}
    assert "solidworks_assembly_view_collapse" in names, names
    got_exploded = {n for n in names if n.startswith("solidworks_assembly_")}
    assert len([n for n in got_exploded if "explode" in n or "exploded" in n]) == 8, got_exploded
    got_macro = {n for n in names if n.startswith("solidworks_macro_")}
    assert len(got_macro) == 8, got_macro                       # 7 个文本 + 1 个执行


def test_target_functions_resolve():
    """★ 每个工具都能解析到**真实函数**（★ 拼错只有运行期才炸）。"""
    for s in rc.all_specs():
        n = getattr(s, "name", "")
        if not (n.startswith("solidworks_macro_") or n.startswith("solidworks_assembly_")):
            continue
        if n in ("solidworks_assembly_check_interference", "solidworks_assembly_list_mates",
                 "solidworks_assembly_list_components"):
            continue                                            #: 既有的三个（不属本批）
        m = importlib.import_module("scripts.%s" % s.module)
        assert callable(getattr(m, s.function, None)), "%s → %s.%s" % (n, s.module, s.function)


def test_macro_run_exposes_the_out_error_contract():
    """★★ `RunMacro2` 官方签名是 **4 入 + 1 out** ⇒ 工具必须暴露 `options`，且回调 `error_name`。"""
    spec = _by_name()["solidworks_macro_run"]
    assert getattr(spec, "inject", "") == "sw_app", spec
    assert [p.name for p in spec.params] == ["file_path", "module_name", "procedure_name", "options"]
    doc = getattr(spec, "doc", "") or ""
    assert "error_name" in doc and "swRunMacroError_e" in doc, doc
    #: ★ 枚举两源一致（官方页 28 == 出厂反射 28，按成员比对）
    from scripts import sw_macro as sm
    assert len(sm.RUN_MACRO_ERRORS) == 28, len(sm.RUN_MACRO_ERRORS)
    assert sm.RUN_MACRO_OPTIONS == {"default": 0, "unload_after_run": 1}


def test_exploded_tools_use_the_document_inject_and_no_coordinates():
    """★★ 爆炸视图工具：★ 注入键必须是 **`doc`**（= 目标函数的**首参名**）· ★ 参数里没有裸坐标（规则 3）。

    ★★★ 为什么是 `doc` 而不是 `asm_model`（★ 这条是门禁当场教我的）：
      ★ 我第一版写 `inject="asm_model"` ⇒ `check_param_binding` 报
        「`inject='asm_model'` **不在函数的形参表里**（形参：['doc']）—— `register()` 不传
        `inject_as` ⇒ **注入键字面上等于 inject 的值**」⇒ 运行期必
        `TypeError: unexpected keyword argument 'asm_model'`（事实 502/169）✓
      ★ 正解 = 按 `RESOLVERS` 那张表**自己的设计意图**加一行 `"doc": resolve_model`，
        ★ **而不是**把包装的形参改名（`sw_assembly_doc.py` 既有的 `add_mate(doc)` 全用 `doc`）✓
    """
    for n, s in _by_name().items():
        if not n.startswith("solidworks_assembly_") or "explode" not in n + getattr(s, "function", ""):
            continue
        assert getattr(s, "inject", "") == "doc", (n, s.inject)
        for p in getattr(s, "params", []) or []:
            low = p.name.lower()
            assert low not in ("x", "y", "z", "point", "coord", "center", "origin"), (n, p.name)


def test_macro_text_tools_are_pure():
    """★ 7 个宏文本工具**不注入**任何 COM 对象（★ 纯函数 ⇒ 可离线调、无挂起风险）。"""
    by = _by_name()
    for fn in MACRO_GUARD:
        spec = next((s for s in by.values() if getattr(s, "function", "") == fn), None)
        assert spec is not None, "★ 没挂上: %s" % fn
        assert getattr(spec, "inject", "") == "", (fn, spec.inject)
