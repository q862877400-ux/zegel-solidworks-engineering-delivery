"""★ 批次 98 的契约测试：工程图中心线 + ★★ "选不上「与」选了没用"必须分开。"""
# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   `mcp-server/tool_specs_batch98.py` · `scripts/sw_drawing_create_missing.py`
# 定位:   ★ 规格 `specs/209-union-adopt-18/` 的 **B2-3（idx 52）**；本文件钉三件事：
#         ① 契约：spec 能解析、声明名都是真形参、**必填形参全声明** ✓
#         ② ★★ **`swViewEntityType_e` 四值**逐值对齐官方 ✓
#         ③ ★★ **两种失败必须分开**：**选不上**（选区 0 ⇒ **调它之前**就报错）
#            与 **选了也没用**（Δ=0）—— ★ 这是本条的判据纪律 ✓
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
import tool_specs_batch98 as b98                              # noqa: E402

EXPECTED = 1


def test_batch98_registered():
    t = (ROOT / "mcp-server" / "register_capabilities.py").read_text(encoding="utf-8")
    assert '"tool_specs_batch98"' in t


def test_one_spec_declared_and_resolves():
    assert len(b98.SPECS_BATCH98) == EXPECTED, len(b98.SPECS_BATCH98)
    s = b98.SPECS_BATCH98[0]
    assert s.name == "solidworks_drawing_insert_center_lines", s.name
    m = importlib.import_module("scripts.%s" % s.module)
    assert callable(getattr(m, s.function, None)), (s.module, s.function)
    assert s.inject == "model"


def test_declared_params_all_exist_and_required_are_declared():
    s = b98.SPECS_BATCH98[0]
    sig = inspect.signature(
        importlib.import_module("scripts.sw_drawing_create_missing").insert_center_lines)
    for p in s.params:
        assert p.name in sig.parameters, (p.name, sorted(sig.parameters))
    required = [n for n, p in sig.parameters.items()
                if p.default is inspect.Parameter.empty and n != "model"]
    declared = {p.name for p in s.params}
    assert not [n for n in required if n not in declared], (required, declared)


def test_view_entity_type_table_matches_official():
    """★ 官方 `swViewEntityType_e`：**Edge=1 · Vertex=2 · Face=3 · SilhouetteEdge=4** —— 逐值钉住 ✓"""
    from sw_drawing_create_missing import VIEW_ENTITY_TYPES
    assert VIEW_ENTITY_TYPES == {"edge": 1, "vertex": 2, "face": 3,
                                 "silhouette_edge": 4}, VIEW_ENTITY_TYPES


def test_two_kinds_of_failure_are_separated():
    """★★★ **本条的判据纪律**：**选不上**（选区 0）与 **选了也没用**（Δ=0）**必须分开** ——
    ★ 前者是**前置没备成**（本函数**在调它之前**就报错，★ 不构成「能力无效」的证据）；
    ★ 后者才是「选了也没用」的证据。★ 源码里两句话必须都在 ✓"""
    src = inspect.getsource(
        importlib.import_module("scripts.sw_drawing_create_missing").insert_center_lines)
    assert "选中后回读计数为 0" in src, "★ 必须把「选不上」单独拦住"
    assert "选了也没用" in src, "★ 必须把「选了也没用」单独说出来"
    #: ★ 判据必须是 **回读增量**，不是它回的 ICenterLine
    assert "GetCenterLineCount" in src and "centerline_delta" in src
    assert "out[\"ok\"] = bool(out[\"centerline_delta\"] and out[\"centerline_delta\"] > 0)" in src


def test_empty_dispatch_variant_is_used_for_the_component_argument():
    """★★ 本仓**已知事实 33**：**空 Dispatch 形参不能传 Python `None`**（会 `类型不匹配`）——
    ★ 我第一次就是传 `None`，四种实体类型**全部**报错 ⇒ ★ 现在必须用
    `create_empty_dispatch_variant()` ✓"""
    src = inspect.getsource(
        importlib.import_module("scripts.sw_drawing_create_missing").insert_center_lines)
    assert "create_empty_dispatch_variant()" in src, "★ 空 Dispatch 形参必须包 VARIANT"
    assert '"GetVisibleEntities2", None' not in src, "★ 不许再传裸 None"


def test_refuses_before_calling_when_nothing_to_select():
    """★ 前置不成立时**不许**硬调（★ 那样只会得到静默空结果）：非法类型 / 无视图 / 越界
    ⇒ 都在**调用之前**返回 `ok=False` 且带原因 ✓"""
    import sw_drawing_create_missing as DM
    #: ⚠ 用**非 None 的假对象**去撞枚举校验 —— ★ 用 `None` 会先撞上「model 为 None」那条早退
    #:   （★ 我第一次就是这么写的：**判据没打到它想测的那条分支** —— 已改）✓
    bad = DM.insert_center_lines(object(), entity_type="nonsense")
    assert bad["ok"] is False and "entity_type" in bad["error"], bad
    assert DM.insert_center_lines(None)["ok"] is False
    assert "model 为 None" in DM.insert_center_lines(None)["error"]


def test_tool_total_grew_by_one():
    assert len(rc.all_specs()) == 447, len(rc.all_specs())
