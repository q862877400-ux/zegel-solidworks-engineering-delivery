"""★ 测「`shell_params` 这条能力」—— ★ 含**负例**（★ 不许碰指针接口/前置）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身 + 官方 `C:\swapi\types\IShellFeatureData\*.md`
# 文件:   tests/test_shell_params_capability.py（★ 新）
# 定位:   ★ 阶段 5「按缺口密度补能力」的**第一格**：★
#   ★★ 密度图（`output/density-gap-map.json`）里 **`查 × 特征` = 官方 451、★ 我们 8** ⇒
#     ★★★ **⇒ 那是最大的一格**；★ 而本仓有 **6 个"能写"的特征工具、★ 一个读都没有** ⇒
#       ★★★★ **⇒ 那正是**「能写不能读」**** ✓
#   ★★★★★ **⚠ 而 `IRevolveFeatureData` **查不到****（★ `C:\swapi\types\` 下没有那个目录）⇒
#     按**铁律 5**：★ **停下、★ 不用相似名字蒙混** ⇒ **改做 `shell`** ✓
#   **真机证据**：★ `tools/probe_shell_params_recheck.py` ·
#     ★ `output/shell-params-capability-recheck.json` ⇒
#     ★★ **板 60×40×10（毫米）⇒ 抽壳 2 mm ⇒ 读回 `Thickness = 2.0`** ⇒
#       ★★★ **⇒ 单位口径 = **随文档单位**（★ 第八族）** ✓
#   许可:   本仓库 MIT。★ 无第三方代码引入。
#   覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

import ast
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
TESTS = REPO / "tests"
SKILLS = REPO / "scripts"
sys.path.insert(0, str(SKILLS))
sys.path.insert(0, str(TESTS))
from _funcbody import func_source  # noqa: E402

SRC = SKILLS / "sw_feature_readback.py"
SPEC = REPO / "mcp-server" / "tool_specs_batch77.py"


def test_reads_the_five_readable_members() -> None:
    """★★★ 核心断言：★ 它读那**五个可读**的成员（★ 逐条查过官方页）✓"""
    body = func_source(SRC.read_text(encoding="utf-8", errors="replace"), "shell_params")
    for name in ("Thickness", "Direction", "FacesRemovedCount",
                 "GetMultipleThicknessFacesCount", "GetMultipleThicknessAtIndex"):
        assert '"%s"' % name in body, "★ 函数体里没读 `%s`" % name


def test_does_not_touch_pointer_or_precondition_members() -> None:
    """★★★★ 核心断言：★ **不碰**指针接口与前置（★ 用**调用形态**判，★ 不是名字出现）✓

    ★★ **为什么查调用形态**：★ 那些名字**就在 docstring 的「不读」清单里**
      （★ 那是**记录**、★ 不是调用）—— ★ 本会话这一条已经踩过**四次** ✓
    """
    body = func_source(SRC.read_text(encoding="utf-8", errors="replace"), "shell_params")
    for bad in ("IGetFacesRemoved", "IGetMultipleThicknessFaces", "IAccessSelections",
                "ISetFacesRemoved", "ISetMultipleThicknessFaces",
                "FacesRemoved", "MultipleThicknessFaces",
                "AccessSelections", "ReleaseSelectionAccess"):
        for shape in ('get_com_member(fd, "%s"' % bad, 'get_com_member(feat, "%s"' % bad,
                      'safe_get_com_member(fd, "%s"' % bad):
            assert shape not in body, "★ 函数体里**调了** `%s`（★ 指针接口/前置）" % bad
    #: ★★ 而那份「不读」清单**必须还在**（★ 那是给下一个人省的功夫）✓
    assert "不读" in body, "★ 那份「不读」清单不见了"


def test_negative_case_the_spec_is_registered_with_the_right_shape() -> None:
    """★★★ **负例 · ToolSpec 的形状**：★ `inject="model"`、★ 只有一个 `feature_name` ✓"""
    t = SPEC.read_text(encoding="utf-8", errors="replace")
    assert 'name="solidworks_shell_params"' in t, "★ 没挂 ToolSpec"
    tree = ast.parse(t)
    found = None
    for n in ast.walk(tree):
        if isinstance(n, ast.Call) and getattr(n.func, "id", "") == "ToolSpec":
            for kw in n.keywords:
                if kw.arg == "name" and getattr(kw.value, "value", "") == \
                        "solidworks_shell_params":
                    found = n
    assert found is not None, "★ 找不到那个 ToolSpec 调用"
    kws = {kw.arg: kw.value for kw in found.keywords}
    assert getattr(kws["inject"], "value", None) == "model", "★ `inject` 应当是 `model`"
    assert getattr(kws["function"], "value", None) == "shell_params"


def test_negative_case_the_unit_readout_is_recorded() -> None:
    """★★★★ **负例 · 单位读数要**记在能力里****（★ 那是本会话最贵的一批读数）✓"""
    body = func_source(SRC.read_text(encoding="utf-8", errors="replace"), "shell_params")
    assert "2.0" in body, "★ 真机读出的 `Thickness = 2.0` 没记进去"
    assert "随文档单位" in body, "★ 单位口径的**结论**没记进去"
    assert "probe_shell_params_recheck" in body, "★ 证据脚本没点名"


def test_negative_case_the_two_count_guards_match_reality() -> None:
    """★★★★ **负例 · 两个「钉死数量」守卫要与实际相符** ✓

    ★★ **为什么**：★ 本轮主动同步了那两处（★ 288 → 289 · ★ 333 → 334）⇒
      ★★★ **若哪天有人加了工具却没同步，本测试就红** ✓
      （★ 而那正是那两条自己写的「**加了就要同时改这里**」）✓
    """
    sys.path.insert(0, str(REPO / "mcp-server"))
    import register_capabilities as rc
    n = len(rc.all_specs())
    t1 = (TESTS / "test_server_wiring.py").read_text(encoding="utf-8", errors="replace")
    assert "assert len(all_specs()) == %d" % n in t1, (
        "★ `test_server_wiring` 的钉死数（★ 应是 %d）没跟上" % n)
    t2 = (TESTS / "test_mcp_protocol_layer.py").read_text(encoding="utf-8", errors="replace")
    #: ★★ 协议层那个数**不是** ToolSpec 数（★ 它还含 server.py 那一路）⇒
    #:   ★ 这里只核**它跟上了** —— ★ 判据是「**那些旧值已经不在了**」✓
    #:   ★★★ **⚠ 本判据的写法值记**：★ 查的是**旧值**、★ 而不是写死新值 ⇒
    #:     因为新值**每加一个工具就要改**、★ 而旧值**一旦被替换就永远不该回来** ✓
    #:     ★★ （★ 本会话正是这么踩过一次：★ 我把本行自己的判据文本也替换了 ⇒
    #:       ★ 于是它变成查 `33000`、★ **判据形同虚设** —— ★ 已回退）✓
    stale = ["assert n == 333, (", "assert n == 334, ("]
    assert not any(x in t2 for x in stale), (
        "★ 协议层那个钉死数还是旧的（★ 应是 335 以上）：%r"
        % [x for x in stale if x in t2])
