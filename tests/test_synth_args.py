"""★ 实参合成器的契约与两侧：★ 先看**真函数签名**的类型，★ 再看名字后缀。"""
# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   `tools/survive_sweep.py` 的 `synth_args`
# 定位:   ★ 规格 `specs/210-declarative-effects` 的 **B3**。★ 起因（真机拆解）：
#   ★★ 存活普查里 4 条工具败在「给错了参数类型」—— 实录用例：
#     · `automation_get_flag(pref)` ⇒ ★ 我给了**字符串** ⇒ 真函数要 `int` ⇒
#       ★ 报 `invalid literal for int(): 'MCP_CALIB'` ✗
#     · `config_set_custom_properties(properties)` ⇒ ★ 我给了字符串 ⇒ 真函数要 `dict` ⇒
#       ★ 报 `'str' object has no attribute 'items'` ✗
# 判据:   ★★ **判序**：★ ① **真函数签名的类型注解**（★ 它是**真的**）→ ★ ② 名字后缀（★ 是**猜的**）
#     → ★ ③ 兜底字符串 ✓
#   ★★ 并**如实承认限度**：★ `ToolSpec.params` 的 `annotation` **全是 `None`** ⇒
#     ★ 类型只能从**底层真函数**取；★ 而**真函数也没注解**的形参 ⇒ ★ **无从知道** ⇒
#     ★ 如实留 `undecided`，★ **不许拿名字瞎猜成本该对的** ✓（★ 铁律 5 的精神）✓
# 官方依据: 无 —— ★ 我方探针口径，如实标注 ✓
# 许可:   本仓库 MIT。无第三方代码引入。覆盖: 全文件
# ─────────────────────────────────────────────────────────────────────
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for _p in (str(ROOT), str(ROOT / "tools"), str(ROOT / "mcp-server"), str(ROOT / "scripts")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import survive_sweep as SS                                       # noqa: E402


def _spec(name):
    import register_capabilities as rc
    for s in rc.all_specs():
        if s.name == name:
            return s
    return None


def test_dict_param_gets_a_dict_not_a_string():
    """★★ **真机实录的那一条**：★ `properties` 要 **dict** ⇒ ★ 合成器必须给 dict ✓
    ★（★ 修前给的是字符串 ⇒ 真机报 `'str' object has no attribute 'items'` ✗）"""
    got = SS.synth_args(_spec("solidworks_config_set_custom_properties"))
    assert isinstance(got.get("properties"), dict), got


def test_signature_types_win_over_name_heuristics():
    """★★ **判序判据**：★ 真签名的类型注解**优先于**名字后缀 ✓

    ★★ 样本的选择本身有讲究（★ 我第一版选错了两次）：
      · ★ 第一次拿 `sw_connect.normalize_doc_type` ⇒ ★★ **它自己也没注解**（`inspect._empty`）
        ⇒ ★ 只能走启发式 ⇒ ★ **证不了判序** ✗
      · ★ 第二次想用临时模块 ⇒ ★★ **注入不进去**：★ `synth_args` 按 `scripts.<module>` 导入，
        ★ 而 `scripts` 是**真包**、★ 它的 `__path__` 不认临时目录 ✗
      ⇒ ★ 正解：★ 在**真仓**里挑一个**真有注解**的函数 ✓
    ★★ 为什么挑 `process_id`：★ 它的名字**没有任何后缀**能命中启发式
      ⇒ ★ 启发式只会给兜底字符串 `'MCP_CALIB'`
      ⇒ ★★ **只有注解能把它变成 `int`** ⇒ ★ 于是这条测试**真能分辨两条路径** ✓
    """
    class _P:
        def __init__(self, name):
            self.name = name
            self.default = Ellipsis

    class _S:
        module = "sw_addin_host"                 # ★ 真模块 ✓
        function = "_process_is_running"         # ★ 真函数，`process_id: int` ✓
        params = [_P("process_id")]

    got = SS.synth_args(_S())
    assert isinstance(got["process_id"], int), got


def test_params_without_any_type_stay_honest_strings():
    """★★ **限度如实**：★ 真函数**也没注解**的形参 ⇒ ★ 它只能是兜底字符串 ✓
    ★★ 这不是 bug，★ 是**信息不存在** ⇒ ★ 那类工具会留 `undecided`（★ 铁律 5）✓"""
    got = SS.synth_args(_spec("solidworks_automation_get_flag"))
    assert got.get("pref") == "MCP_CALIB", got


def test_optional_params_are_not_synthesized():
    """★ 有默认值的形参**不许**合成（★ 合成了会盖掉工具的默认语义）✓"""
    import inspect
    import types
    spec = _spec("solidworks_config_set_custom_properties")
    sig = inspect.signature(
        getattr(__import__("scripts." + spec.module, fromlist=["x"]), spec.function))
    optional = {n for n, p in sig.parameters.items() if p.default is not inspect.Parameter.empty}
    got = SS.synth_args(spec)
    assert not (set(got) & optional), (got, optional)
