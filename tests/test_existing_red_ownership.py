"""★ spec 275：**223 的 8 条既有红 —— 逐条定权属**（★ 3 条与权属无关 ⇒ 已修；★ 5 条被未提交改动阻塞）。"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   D:/AI/SW
# 文件:   specs/223-enum-fabrication-and-gate-boundaries/acceptance.md §七·B（★ 原 8 条的登记与取证）
#         tests/test_real_gap_triage_contract.py（★ B6/B7 的样本）· tests/test_com_member_helpers.py（★ B8 的判据）
# 定位:   ★ 223 的结论是**笼统一句**「权属落在**他人未提交改动**内」⇒ ★ 本轮**逐条核**它成不成立。
# 官方依据: 不适用（本项目内部纪律）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   只读；★ 只读文件与调纯函数（★ 不写任何文件）
# ────────────────────────────────────────────────────────────────────
from __future__ import annotations

import ast
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for _p in (str(ROOT), str(ROOT / "tests"), str(ROOT / "tools"), str(ROOT / "scripts")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

#: ★★★ **223 登记的 8 条既有红**（★ 逐字来自 `specs/223-*/acceptance.md` §七·B）——
#:   ★ **冻结**：★ 若有人**删掉**某个用例来「变绿」⇒ 本表会让它红 ✓
EXISTING_REDS = {
    "B1": ("tests/test_server_wiring.py", "test_expected_batch_size"),
    "B2": ("tests/test_mcp_protocol_layer.py", "test_protocol_tool_count_matches_the_two_paths_sum"),
    "B3": ("tests/test_shell_params_capability.py", "test_negative_case_the_two_count_guards_match_reality"),
    "B4": ("tests/test_effect_declarations.py", "test_effects_table_is_fresh"),
    "B5": ("tests/test_effect_declarations.py", "test_table_covers_every_tool"),
    "B6": ("tests/test_real_gap_triage_contract.py", "test_real_capabilities_default_to_should_expose"),
    "B7": ("tests/test_real_gap_triage_contract.py", "test_wrapper_rule_does_not_swallow_real_gaps"),
    "B8": ("tests/test_com_member_helpers.py", "test_every_helper_user_can_actually_import_it"),
}
#: ★★★ **被「未提交改动」阻塞的 5 条** —— ★ 成因是 `mcp-server/tool_specs_batch*.py` 的**未提交**改动
#:   （★ 工具数 459 → **479**）⇒ ★ 修它们**必须**先把那 5 个 batch 文件的**权属**定下来
#:   （★ 硬红线：**禁止改工作树里归属不明的既有改动**）⇒ ★ 处置 = **只登记不动** ✓
BLOCKED_BY_UNOWNED = {"B1", "B2", "B3", "B4", "B5"}
#: ★★ **与权属无关、本切片已修的 3 条** —— ★ 成因都在**已提交**的文件里（★ 判据自身缺陷 / 已提交规格 217）。
FIXED_BY_275 = {"B6", "B7", "B8"}
#: ★★ 阻塞的成因文件（★ 未提交改动 · ★ 工具数增长的来源）。
UNOWNED_CAUSE_FILES = (
    "mcp-server/tool_specs_batch4.py",
    "mcp-server/tool_specs_batch16.py",
    "mcp-server/tool_specs_batch35.py",
    "mcp-server/tool_specs_batch80.py",
    "mcp-server/tool_specs_batch93.py",
)
#: ★★ B6/B7 的**旧样本**（★ 已随已提交的规格 217 变成「已有」）与**新样本**。
OLD_SAMPLE = ("sw_part", "linear_pattern")
NEW_SAMPLE = ("sw_hole_features", "create_hole_pattern")


def _failures(reds, blocked, fixed, old_sample, new_sample) -> list[str]:
    """★ 纯函数：① 分类**覆盖且不相交**；② 两集**都非空**（★ 检查量为 0 判失败）。"""
    bad: list[str] = []
    if blocked & fixed:
        bad.append("两集**相交**：%s" % sorted(blocked & fixed))
    if (blocked | fixed) != set(reds):
        bad.append("分类**没覆盖全** 8 条：缺 %s" % sorted(set(reds) - (blocked | fixed)))
    if not blocked:
        bad.append("`BLOCKED_BY_UNOWNED` 为空 ⇒ 检查量为 0 ⇒ 不许通过")
    if not fixed:
        bad.append("`FIXED_BY_275` 为空 ⇒ 检查量为 0 ⇒ 不许通过")
    if old_sample == new_sample:
        bad.append("新样本 == 旧样本 ⇒ 样本没换")
    return bad


def _def_exists(rel: str, fn: str) -> bool:
    """★ 该测试文件里**仍有** `def fn(`（★ 防止「删用例 ⇒ 变绿」）。"""
    src = (ROOT / rel).read_text(encoding="utf-8", errors="replace")
    return re.search(r"(?m)^\s*def %s\s*\(" % re.escape(fn), src) is not None


# ── ① ★★★ 8 条 ID **冻结**（★ 不许靠删用例变绿）────────────────────
def test_the_eight_reds_are_still_registered():
    """★★★ 223 的 8 条**逐条仍在**（★ 文件 + `def` 都在）⇒ ★ 「删掉用例」这条捷径被堵死。"""
    assert len(EXISTING_REDS) == 8, "8 条表被改过"
    missing = ["%s → %s::%s" % (k, rel, fn) for k, (rel, fn) in sorted(EXISTING_REDS.items())
               if not _def_exists(rel, fn)]
    assert not missing, "这些用例不见了（★ 是不是被删掉来「变绿」？）：\n  " + "\n  ".join(missing)


# ── ② ★★★ 权属分类**覆盖且不相交** ──────────────────────────────────
def test_ownership_split_is_complete_and_disjoint():
    """★★★ **5 被未提交改动阻塞 + 3 与权属无关 = 8** —— ★ 这正是 223 那句笼统结论缺的东西。"""
    bad = _failures(EXISTING_REDS, BLOCKED_BY_UNOWNED, FIXED_BY_275, OLD_SAMPLE, NEW_SAMPLE)
    assert not bad, "权属分类不自洽：\n  " + "\n  ".join(bad)
    assert len(BLOCKED_BY_UNOWNED) == 5 and len(FIXED_BY_275) == 3, "5 + 3 ≠ 8"


def _two_strs(node) -> tuple | None:
    """★ `("a", "b")` 形态的**代码**字面量 ⇒ `("a","b")`；否则 `None`（★ 注释**不在 AST 里**）。"""
    if (isinstance(node, ast.Tuple) and len(node.elts) == 2
            and all(isinstance(e, ast.Constant) and isinstance(e.value, str) for e in node.elts)):
        return (node.elts[0].value, node.elts[1].value)
    return None


def _code_sample_tuples(rel: str) -> set:
    """★ 从**代码**（★ 不是注释/字符串）里抽出 `(module, name)` 样本 —— ★ 走 AST ✓

    ★★ 为什么不能用正则扫文本：★ 本文件与 `test_real_gap_triage_contract.py` 的**注释里**
      都写了样本名（★ 例如「原样本 `("sw_part","linear_pattern")` 已变「已有」」）
      ⇒ ★ 正则会把**注释**当成样本 ⇒ ★ 判据**恒真**（★ 那正是 B8 那条判据犯过的错，★ 同族）。
    """
    tree = ast.parse((ROOT / rel).read_text(encoding="utf-8", errors="replace"))
    out: set = set()
    for node in ast.walk(tree):
        #: ① `@pytest.mark.parametrize("module,name", [ (m,n), … ])`
        if isinstance(node, ast.Call):
            for a in node.args:
                if isinstance(a, (ast.List, ast.Tuple)):
                    out |= {t for el in a.elts if (t := _two_strs(el))}
        #: ② `for module, name in ( (m,n), … )`
        if isinstance(node, ast.For) and isinstance(node.iter, (ast.Tuple, ast.List)):
            out |= {t for el in node.iter.elts if (t := _two_strs(el))}
    return out


# ── ③ ★★★ B6/B7 的样本**已换**，且新样本**实测仍「该挂」** ──────────
def test_triage_samples_were_replaced_and_the_new_one_is_a_real_gap():
    """★★★ B6/B7 的样本**已换**（★ 旧样本已随**已提交**的规格 217 变「已有」）⇒
    ★ 并**实测**新样本仍是真缺口 ⇒ ★ 判据的**判别力**保住了（★ 不是靠删空变绿）。
    """
    samples = _code_sample_tuples("tests/test_real_gap_triage_contract.py")
    assert OLD_SAMPLE not in samples, "旧样本 `sw_part.linear_pattern` **还在代码里**（★ 应已换掉）"
    assert NEW_SAMPLE in samples, "新样本没写进参数表"

    import triage_real_gaps as T                                    # noqa: PLC0415
    kind, why = T.classify(*NEW_SAMPLE)
    assert kind == "该挂", "新样本实测是 %r（★ 不是真缺口 ⇒ 判别力没了）：%s" % (kind, why)


# ── ④ ★★★ B8 的判据**不认注释**（★ 只认裸调用）────────────────────
def test_helper_usage_detection_ignores_comments():
    """★★★ B8 的原判据是**正则扫文本** ⇒ ★ **把注释也算成「用到」**（★ 实测 2 处假阳性）
    ⇒ ★ 修成 **AST 裸调用**。★ 本条**必须能红**：★ 注释 ⇒ `False`；★ 裸调用 ⇒ `True`。
    """
    import test_com_member_helpers as H                             # noqa: PLC0415
    helper = "get_com_member"
    #: ★ 负例：**注释**里提到（★ 这正是 B8 的两处假阳性形态）
    assert not H._uses_helper_call('#:   ★ 取盒走 `%s(face, "GetBox")` ✓\n' % helper, helper), \
        "注释被当成调用了 ⇒ 判据仍过宽"
    #: ★ 负例：**字符串**里提到
    assert not H._uses_helper_call('MSG = "%s(x)"\n' % helper, helper), "字符串被当成调用了"
    #: ★ 负例：**限定名**调用（★ 不需要本模块导入 ⇒ 与原意图一致）
    assert not H._uses_helper_call("y = sw_part.%s(obj, 'X')\n" % helper, helper), \
        "限定名调用不该算（★ 原正则的 `(?<![\\w.])` 就是这个意思）"
    #: ★ 正例：**裸调用**（★ 这才是判据要抓的）
    assert H._uses_helper_call("y = %s(obj, 'X')\n" % helper, helper), \
        "裸调用没被抓到 ⇒ 判据被放宽成空判据"


# ── ⑤ ★★ 判据必须能红 ───────────────────────────────────────────────
def test_pure_function_is_red_able():
    """★ 五组负例：① 两集相交；② 没覆盖全；③ 阻塞集空；④ 已修集空；⑤ 新样本 == 旧样本。"""
    assert not _failures(EXISTING_REDS, BLOCKED_BY_UNOWNED, FIXED_BY_275,
                         OLD_SAMPLE, NEW_SAMPLE), "正常读数被判红 ⇒ 判据过严"
    assert _failures(EXISTING_REDS, {"B1", "B6"}, FIXED_BY_275, OLD_SAMPLE, NEW_SAMPLE), "相交却未判出"
    assert _failures(EXISTING_REDS, {"B1"}, FIXED_BY_275, OLD_SAMPLE, NEW_SAMPLE), "没覆盖全却未判出"
    assert _failures(EXISTING_REDS, set(), FIXED_BY_275, OLD_SAMPLE, NEW_SAMPLE), "阻塞集空却未判出"
    assert _failures(EXISTING_REDS, BLOCKED_BY_UNOWNED, set(), OLD_SAMPLE, NEW_SAMPLE), "已修集空却未判出"
    assert _failures(EXISTING_REDS, BLOCKED_BY_UNOWNED, FIXED_BY_275,
                     OLD_SAMPLE, OLD_SAMPLE), "样本没换却未判出"
