"""★ 规格 301 判据：判据**不许钉快照绝对值** —— 同源 / 按名字 / 动态，三者必居其一。"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   `tests/test_dispatch_entry_guard.py` / `_resolution.py` / `_call_site_dedup.py` /
#         `_byref_guard.py`（★ 四个 dispatch 测试 —— **同源**）
#         `tests/test_routing_plan_real_hits.py`（★ 键 —— **按名字**）
#         `tests/test_dispatch_byref_guard.py` / `_resolution.py`（★ 负例 —— **动态**）
#         `tests/test_sw_drawing_view_contract.py`（★ 旧行为反转）
#         `MEMORY.md` 规则 16 / 22 / 28 / 29 / 30 / 32（★ 本规格的六条依据）
# 定位:   ★★ 起因：★ 广域回归 **15 条既有红**，★ 逐条查明**全是同一族**：
#         ① 判据钉了「某个快照的绝对值」（★ 行号/计数**本来就会变**）
#         ② 判据钉了「已被有意反转的旧行为」
#         ★★★ **⇒ 本文件把「修根」的**形态**钉住** —— ★ 免得下一轮又有人把常数抄回去。
# 官方依据: 不适用（本项目内部纪律）
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 覆盖:   只读（★ 不连 COM；★ 不跑子进程）
# ─────────────────────────────────────────────────────────────────────
from __future__ import annotations

import ast
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TESTS = ROOT / "tests"
SCRIPTS = ROOT / "scripts"

#: ★★ **必须与门禁同源**的四个 dispatch 测试（★ 它们各有一条「读数 ≥ 下界」的判据）
DISPATCH_TESTS = (
    "test_dispatch_entry_guard.py",
    "test_dispatch_resolution.py",
    "test_dispatch_call_site_dedup.py",
    "test_dispatch_byref_guard.py",
)
#: ★★★ **第二批**（★ 2026-10-10 同轮补 · ★ 同一族的另外 5 条）
#:   ★ 它们各有**不同的**形态 ⇒ ★ 判据也各不相同（★ 见下两条测试）。
SECOND_WAVE = (
    "test_dispatch_blindspot_guard.py",       # ★ 与门禁同源
    "test_deprecated_admissible_disposition.py",   # ★ 比对去行号
    "test_deprecated_multi_successor_adjudication.py",  # ★ 口径订正
    "test_base_flange_root_cause.py",         # ★ 旧行为反转（随规格 278）
)


def _src(name: str) -> str:
    return (TESTS / name).read_text(encoding="utf-8", errors="replace")


def test_judges_import_the_gate_baseline():
    """★★★ FR-001：四个 dispatch 测试必须**从门禁 import 下界**（★ 不抄常数）。

    ★★ **依据**（`MEMORY.md` 规则 16 逐字）：「门禁数三套口径别混 … ★ **别拿一个数去核另一个**」。

    ★ 判据：★ 每个文件里**都要有** `import check_dispatch_*` 的语句 ——
      ★★ 那是「同源」的**可核形态**（★ 只写注释说"同源"不算）。
    """
    bad = []
    for name in DISPATCH_TESTS:
        src = _src(name)
        if not re.search(r"^import check_dispatch_\w+ as _\w+_gate", src, re.M):
            bad.append(name)
    assert not bad, (
        "★ 以下测试**没有**从门禁 import 下界 ⇒ ★ 它们仍钉着**某个快照的绝对值**：\n  "
        + "\n  ".join(bad))


def test_shrink_negative_cases_are_dynamic():
    """★★★ FR-002：「下界承重」的负例**被测试的那个量**必须**动态**取实测。

    ★★ **为什么**：★ 硬写 `312`（★ 那时实测 311）⇒ ★★ 实测**涨到 316** 后
      `316 >= 312` ⇒ **不红** ⇒ ★★★ **判据静默失效**（★ 它本该证明「下界承重」）。

    ★★ **作用范围**（★ 别误报）：★ 只核**被抬高的那个量** ——
      · `test_sites_baseline_shrink_is_red` ⇒ ★ 核 **`sites`**（★ 要动态）；
      · `test_entries_baseline_shrink_is_red` ⇒ ★ 核 **`entries`** ——
        ★ 它把 `entries` 抬到 22（★ 实测 21）⇒ ★★ **那个 22 才是承重的量**；
        ★ 而它同时写的 `311` 是**另一个量**（★ 不参与该判据的承重）⇒ ★ **不算问题**。
      ★★★ **这正是本规格的教训**：「**钉哪一个量**」要**逐条看**，★ 不能一刀切。
    """
    for name, shrink_attr in (("test_dispatch_byref_guard.py", "sites"),
                              ("test_dispatch_resolution.py", "sites")):
        src = _src(name)
        tree = ast.parse(src)
        body = ""
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == "test_%s_baseline_shrink_is_red" % shrink_attr:
                body = ast.get_source_segment(src, node) or ""
                break
        assert body, "★ `%s` 里找不到 `test_%s_baseline_shrink_is_red`" % (name, shrink_attr)
        #: ★★ 判据：**必须**先跑一次读实测（★ 那才是动态的形态）
        assert "rc0, out0 = run_gate(None)" in body, (
            "★ `%s::test_%s_baseline_shrink_is_red` **没有先跑一次读实测** ⇒ ★ 它硬写了绝对值"
            "（★ 实测涨过那个值就**静默失效**）：\n%s" % (name, shrink_attr, body))


def test_routing_plan_keys_are_not_line_numbers():
    """★★ FR-004：`_PLAN` 的键**不许是行号**（★ 键必须是 `(文件, 包围函数)`）。

    ★★ **依据**（`MEMORY.md` 规则 32 逐字）：「★★★ **证据表不许钉行号**」。
    ★ 判据：★ AST 解析 `_PLAN` 的键 —— ★ 第二项**必须**是字符串（★ 不是 `int`）。
    """
    src = _src("test_routing_plan_real_hits.py")
    tree = ast.parse(src)
    keys: list = []
    for node in ast.walk(tree):
        if isinstance(node, ast.AnnAssign) and getattr(node.target, "id", "") == "_PLAN":
            val = node.value
            if isinstance(val, ast.Dict):
                keys = list(val.keys)
    assert keys, "★ 找不到 `_PLAN` 的字面量字典"
    bad = []
    for k in keys:
        if not (isinstance(k, ast.Tuple) and len(k.elts) == 2):
            bad.append(ast.unparse(k))
            continue
        second = k.elts[1]
        if not (isinstance(second, ast.Constant) and isinstance(second.value, str)):
            bad.append(ast.unparse(k))
    assert not bad, (
        "★★ `_PLAN` 的键**第二项不是字符串** ⇒ 它还在钉**行号**（★ 加注释就会漂）：\n  "
        + "\n  ".join(bad))


def test_ratchet_downgrades_have_content_assertions():
    """★★★ FR-005：棘轮下调必须补**内容断言**（★ `MEMORY.md` 规则 22）。

    ★★ **本规格下调了**：`BASELINE_SITES 7→5` · `BASELINE_NAMES 6→4` · `REAL_HITS 6名7处→4名5处`
    ★ 判据：★ `test_routing_plan_real_hits.py` 里**必须**有那条按名字的内容断言。
    """
    src = _src("test_routing_plan_real_hits.py")
    assert "def test_the_two_adapt_args_entries_are_closed_in_spec_261" in src, (
        "★ 缺内容断言 ⇒ ★ 计数棘轮**接不住**「有人写回去」（★ 规则 22）")
    #: ★ 内容断言必须**真的按名字**核（★ 不是只核条数）
    tree = ast.parse(src)
    body = ""
    for node in ast.walk(tree):
        if (isinstance(node, ast.FunctionDef)
                and node.name == "test_the_two_adapt_args_entries_are_closed_in_spec_261"):
            body = ast.get_source_segment(src, node) or ""
    assert "KFactor" in body and "MaterialIdName" in body, (
        "★ 内容断言没有**按名字**核那两个被移出的成员")
    #: ★★ 且必须**指回 spec 261**（★ 否则「已收口」是空话）
    assert "261" in body, "★ 内容断言没指回 `spec 261` ⇒ 「已收口」失去依据"


def test_iview_name_fallback_is_intentionally_removed():
    """★★★ FR-003：`get_view_name` 的兜底**必须**已删（★ `spec 256` 的有意行为）。

    ★★ **依据**（`MEMORY.md` 规则 28）：「改实现前先搜『有没有测试钉住旧行为』——
      ★ 不同步改就等于**在断言错的东西**」。
    ★ 判据：★ ① 实现里**不许**回落调 `Name`；★ ② 判据必须断言**空串**（★ 不是 `V2`）。
    """
    impl = (SCRIPTS / "sw_drawing_view.py").read_text(encoding="utf-8", errors="replace")
    tree = ast.parse(impl)
    body = ""
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "get_view_name":
            body = ast.get_source_segment(impl, node) or ""
    assert body, "★ 找不到 `get_view_name`"
    #: ★① 不许回落调废弃成员 `Name`
    assert '"Name"' not in body and "'Name'" not in body, (
        "★★ `get_view_name` **回落调了废弃成员 `Name`** ⇒ ★ 与 `spec 256` 的结论矛盾"
        "（★ 那条逐字：「★ **不换一个废弃成员再试**」）：\n%s" % body)
    #: ★② 判据必须断言**空串**
    t = _src("test_sw_drawing_view_contract.py")
    assert 'get_view_name(object()) == ""' in t, (
        "★ 判据没有断言**空串** ⇒ ★ 它可能还钉着「回落取 `V2`」那个**旧行为**（★ 规则 28）")


def test_second_wave_uses_the_same_four_fixes():
    """★★★ **第二批**（★ 同轮的另外 5 条）也必须用**同族**的修法。

    ★★ 逐条形态（★ 每条的**病不同** ⇒ 修法也不同，★ 但都在本规格的四条之内）：

    | ★ 文件 | ★ 病 | ★ 修法 |
    |---|---|---|
    | `test_dispatch_blindspot_guard.py` | ★ 把下界当实际值 | ★★ **同源**（import `BASELINE_COVERED`） |
    | `test_deprecated_admissible_disposition.py` | ★★ 站点**逐字相等**（含行号） | ★★ **按 `(文件, 宿主表达式)`**（★ 规则 32） |
    | `test_deprecated_multi_successor_adjudication.py` | ★ 手算的**预期值** ≠ 真算 | ★★ **口径订正**（★ 且补 `single+pair==hit` 自洽断言） |
    | `test_base_flange_root_cause.py` | ★★ **旧行为已被规格 278 反转** | ★★ **同步反转**（★ 规则 28） |
    """
    #: ★ ① 盲区门禁：★ 必须与门禁同源
    b = _src("test_dispatch_blindspot_guard.py")
    assert re.search(r"^import check_dispatch_blindspot_guard as _\w+_gate", b, re.M), (
        "★ `test_dispatch_blindspot_guard.py` 没有从门禁 import 下界 ⇒ ★ 仍钉着快照绝对值")
    #: ★ ② 处置表：★ 比对必须**去行号**（★ 规则 32）
    d = _src("test_deprecated_admissible_disposition.py")
    assert "projected" in d and "(f, h) for (f, _ln, h) in" in d, (
        "★ `test_deprecated_admissible_disposition.py` 的比对**没去掉行号** ⇒ ★ 代码一改就假红")
    #: ★ ③ 多后继：★ 必须有**口径自洽**断言（★ 不靠某一个绝对值）
    m = _src("test_deprecated_multi_successor_adjudication.py")
    assert "len(single) + len(pair) == len(hit)" in m, (
        "★ `test_deprecated_multi_successor_adjudication.py` 缺**口径自洽**断言")
    #: ★ ④ 基体法兰：★ 必须**反转**（★ 随规格 278）
    f = _src("test_base_flange_root_cause.py")
    assert "not scaled" in f, (
        "★ `test_base_flange_root_cause.py` 的夹具判据**没反转** ⇒ ★ 它还在断言规格 278 已修掉的旧行为")


def test_second_wave_has_no_hardcoded_snapshot_constants():
    """★★★ **第二批**里也不许有「快照绝对值」出现在**断言**里。

    ★★ 依据同 `test_no_hardcoded_snapshot_constants_in_dispatch_judges`（★ 规则 16）。
    """
    #: ★★ 第二批实测的「旧硬写值」
    STALE = ("362", "363", "18", "16", "0.03")
    bad = []
    for name in SECOND_WAVE:
        for i, line in enumerate(_src(name).splitlines(), 1):
            stripped = line.strip()
            if stripped.startswith("#"):
                continue                      # ★ 注释里留着来历**是对的**
            if "assert" not in stripped:
                continue
            #: ★ 放宽：★ `>= N` 的**下界**写法是**合法**的（★ 那不是「逐字相等」）
            if re.search(r"(>=|<=)\s*\d", stripped):
                continue
            for tok in STALE:
                if re.search(r"\b%s\b" % re.escape(tok), stripped):
                    bad.append("%s:%d %s" % (name, i, stripped[:110]))
    assert not bad, (
        "★★ 以下**断言**里仍钉着快照绝对值 ⇒ ★ 真树一变就红：\n  " + "\n  ".join(bad))


def test_no_hardcoded_snapshot_constants_in_dispatch_judges():
    """★★★ **总判据**：四个 dispatch 测试里**不许**再出现那三个「快照绝对值」的字面量。

    ★★ 三个量（★ 它们**会随真树变**）：`可见调用点` / `可解析调用点` / `已核调用点`。
    ★ 判据：★ 这些数字**只许**出现在**注释**里（★ 说明来历），★ **不许**出现在**断言**里。
    """
    #: ★★ 本规格实测的「旧硬写值」（★ 它们**不该**再出现在断言里）
    STALE = ("1183", "1185", "312", "311")
    bad = []
    for name in DISPATCH_TESTS:
        for i, line in enumerate(_src(name).splitlines(), 1):
            stripped = line.strip()
            if stripped.startswith("#"):
                continue                      # ★ 注释里留着来历**是对的**
            if "assert" not in stripped:
                continue
            for tok in STALE:
                if re.search(r"\b%s\b" % tok, stripped):
                    bad.append("%s:%d %s" % (name, i, stripped[:110]))
    assert not bad, (
        "★★ 以下**断言**里仍钉着快照绝对值 ⇒ ★ 真树一变就红（★ 应改成 import 下界 / 动态）：\n  "
        + "\n  ".join(bad))
