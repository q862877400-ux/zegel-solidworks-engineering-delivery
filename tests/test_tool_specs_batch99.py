"""★ 批次 99 的契约测试：原生宏录制 + ★★ 「永不点 StopMacro(31)」的静态守卫。"""
# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   `mcp-server/tool_specs_batch99.py` · `scripts/sw_macro.py`
# 定位:   ★ 规格 `specs/209-union-adopt-18/` 的 **B4-1（idx 211）**；本文件钉三件事：
#         ① 契约：spec 能解析、声明名都是真形参 ✓
#         ② ★★★ **静态守卫**：源码里**不许出现** `RunCommand(31)` / `stop_macro` 的**调用**
#            —— ★ 官方枚举页逐字说它**会弹 Save As**（本仓头号死因）⇒ ★ 这条守卫是本条的核心 ✓
#         ③ ★ **判据纪律**：`ok` 必须**同时**要求成对调用与逐行都回 True，★ 且返回值里**明写限度** ✓
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
import tool_specs_batch99 as b99                              # noqa: E402

EXPECTED = 1


def test_batch99_registered():
    t = (ROOT / "mcp-server" / "register_capabilities.py").read_text(encoding="utf-8")
    assert '"tool_specs_batch99"' in t


def test_one_spec_declared_and_resolves():
    assert len(b99.SPECS_BATCH99) == EXPECTED, len(b99.SPECS_BATCH99)
    s = b99.SPECS_BATCH99[0]
    assert s.name == "solidworks_macro_record_lines", s.name
    m = importlib.import_module("scripts.%s" % s.module)
    assert callable(getattr(m, s.function, None)), (s.module, s.function)
    #: ★ 本条的注入对象是 **ISldWorks**（★ 不是文档！）—— ★ 与 `run_macro` 那条同一个对象 ✓
    assert s.inject == "sw_app", s.inject


def test_declared_params_all_exist():
    s = b99.SPECS_BATCH99[0]
    sig = inspect.signature(importlib.import_module("scripts.sw_macro").record_macro_lines)
    for p in s.params:
        assert p.name in sig.parameters, (p.name, sorted(sig.parameters))


def test_stop_macro_is_never_called():
    """★★★ **本条的守卫**：官方枚举页逐字写 `swCommands_StopMacro`(31)「**opens the Save As
    dialog**」⇒ ★★ 本仓**不许有把它传给 `RunCommand` 的调用**（★ 无头下会弹模态框）✓

    ⚠ 判据**只扫代码**（`strip_comments_and_strings`）—— ★ 因为注释里**必须**写着"31 会弹窗、
    所以我们不调它"，★ 把那句引用当成违规就会**把守卫变成噪声**（★ 与 batch93/batch97 同一处置）✓
    """
    sys.path.insert(0, str(ROOT / "scripts"))
    from check_env_pitfalls import strip_comments_and_strings
    src = (ROOT / "scripts" / "sw_macro.py").read_text(encoding="utf-8")
    code = strip_comments_and_strings(src)
    for forbidden in ('RunCommand", 31', "RunCommand\", 31", "stop_macro\"]",
                      "RECORD_COMMANDS[\"stop_macro\"]"):
        assert forbidden not in code, ("★ 出现停宏命令的调用：%s" % forbidden)
    #: ★ 反过来：**必须**有 29 那条（成对开关走的就是它）——
    #:   ⚠ 这一条查**原文**而不是 `code`：★ `record_pause_macro` 是个**字符串字面量**，
    #:   而 `strip_comments_and_strings` **连字符串一起剥**（★ 我第一版就把它剥没了 ⇒ 断言打空）✓
    assert "record_pause_macro" in src, "★ 停录制必须走 29 这个切换"
    #: ★ 而 31 的**常量本身**要留着（★ 它是「我们为什么不点它」的证据）
    assert "stop_macro" in src and 31 == importlib.import_module("scripts.sw_macro") \
        .RECORD_COMMANDS["stop_macro"]


def test_criterion_needs_both_ends_and_every_line():
    """★ `ok` = **成对调用都 True 且每一行都 True** —— ★ 缺一项都不算 ✓"""
    src = inspect.getsource(importlib.import_module("scripts.sw_macro").record_macro_lines)
    assert 'out["lines_written"] == len(items)' in src
    assert "bool(out[\"open_returned\"]) and bool(out[\"close_returned\"])" in src
    #: ★★ 返回值里**必须明写限度**（★ 「宏文件落盘」证不了）
    assert "stop_macro_warning" in src, "★ 必须把「永不点 31」的理由随返回值带出来"


def test_recording_is_always_stopped_even_on_failure():
    """★★ 录制必须在 `finally` 里停掉 —— ★ 否则 SW 会**一直录着**（★ 留给用户的脏状态）✓"""
    src = inspect.getsource(importlib.import_module("scripts.sw_macro").record_macro_lines)
    assert "finally:" in src and "toggle_macro_recording(sw_app)" in src


def test_refuses_empty_input_without_touching_com():
    import sw_macro as M
    r = M.record_macro_lines(None, "")
    assert r["ok"] is False and r["error"], r
    r2 = M.record_line(object(), "   ")
    assert r2["ok"] is False and "text" in r2["error"], r2
    #: ★ 成对函数对**空行**的处理：只剩空白的输入 ⇒ 直接拒（★ 不碰 COM）
    assert M.record_macro_lines(object(), "\n\n  \n")["ok"] is False


def test_tool_total_grew_by_one():
    assert len(rc.all_specs()) == 448, len(rc.all_specs())
