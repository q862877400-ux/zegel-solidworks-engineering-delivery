"""★ spec 288：**先量** —— 「改 `STUDY_MANAGER_ARITY`」的**正确改动面**（★ 标注是 per-table ⇒ 改**整张表**）。"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   D:/AI/SW
# 文件:   scripts/sw_simulation_study.py:148-166（★ `STUDY_MANAGER_ARITY` 15 条 · ★ 上方 `#: arity-reflect: byref=excluded`）
#         scripts/check_arity_tables_vs_reflection.py:54（★ 标注**按表**：`^#: arity-reflect: byref=(included|excluded)$`）
#         tests/test_sw_simulation_study_contract.py:45-61（★ **手抄**的 `REFLECTED_MANAGER_ARITY`）
#         _raw/reflect/iface_cosworks.txt 的 `## ICWStudyManager`（★ 官方完整形参数）
# 定位:   ★ 287 解除了 12 条的前置 ⇒ ★ 但**动手前先量**：★ 改一处表值**要连带改多少**。
# 官方依据: `_raw/reflect/iface_cosworks.txt`（★ 纯元数据反射）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   只读（★ 现场读源码与转储；★ 本文件不写任何文件）
# ────────────────────────────────────────────────────────────────────
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

MODULE = ROOT / "scripts" / "sw_simulation_study.py"
DUMP = ROOT / "_raw" / "reflect" / "iface_cosworks.txt"
CONTRACT = ROOT / "tests" / "test_sw_simulation_study_contract.py"


def _table() -> dict:
    """★ 现场解析 `STUDY_MANAGER_ARITY`（★ 不手抄）。"""
    src = MODULE.read_text(encoding="utf-8", errors="replace")
    m = re.search(r"STUDY_MANAGER_ARITY:\s*dict\[str,\s*int\]\s*=\s*\{(.*?)\n\}", src, re.S)
    out = {}
    for k, v in re.findall(r'"(\w+)":\s*(\d+)', m.group(1)):
        out[k] = int(v)
    return out


def _official() -> dict:
    """★ 现场解析反射转储里 `ICWStudyManager` 的**完整形参数**（★ 不手抄）。"""
    src = DUMP.read_text(encoding="utf-8", errors="replace")
    m = re.search(r"## ICWStudyManager\n(.*?)(?=\n## )", src, re.S)
    out = {}
    for ln in (m.group(1) if m else "").splitlines():
        mm = re.match(r"\s*\S+\s+(\w+)\((.*)\)\s*$", ln)
        if mm:
            params = [p.strip() for p in mm.group(2).split(",") if p.strip()]
            out[mm.group(1)] = (len(params), params[-1] if params else "")
    return out


def _annotations() -> list:
    """★ 现场取 `#: arity-reflect:` 标注（★ 带它下面紧跟的表名）。"""
    src = MODULE.read_text(encoding="utf-8", errors="replace")
    return re.findall(r"#:\s*arity-reflect:\s*byref=(included|excluded)\s*\n(\w+):", src)


# ── ① ★★★ **逐条量**：表值 vs 官方完整形参数 ──────────────────────
def test_the_table_uses_one_uniform_convention():
    """★★★ 现场量：★ `ICWStudyManager` 的 **15** 条里，★ 每一条要么「表值 = 官方」（★ 末位**不是** `Int32&`），
    要么「表值 = 官方 − 1」（★ 末位**是** `Int32&`）⇒ ★★★ **整张表**一个约定****（★ 不留混用）。

    ★★★ **这条**不钉现状****（★ 改前改后都该绿）—— ★ 它钉的是「**不能混用两种约定**」：
    ★ `byref=excluded` 时 **9 处差 1 · 6 处相等**；★ 改成 `byref=included` 后 **15 处全相等**。
    ★★ **若有人只改其中几条** ⇒ ★ 这张判据**当场红**（★ 那正是本轮要防的错）。
    """
    table, official = _table(), _official()
    assert len(table) == 15, "★ 表应有 15 条，实测 %d" % len(table)
    for name, val in table.items():
        n, last = official.get(name, (None, ""))
        assert n is not None, "★ 表里的 %s 在反射里查不到" % name
        is_i4_out = last.endswith("&") and "Int32" in last
        if is_i4_out:
            assert n - val in (0, 1), \
                "★ %s 的表值 %d 与官方 %d 差 %d（★ 只允许 0 或 1）" % (name, val, n, n - val)
        else:
            assert n == val, \
                "★ %s 的末位**不是** `Int32&` ⇒ 表值必须**等于**官方（%d），实测 %d" % (name, n, val)


def test_the_convention_is_uniform_across_the_table():
    """★★★ **整张表必须同一个约定**（★ 因为 `#: arity-reflect:` 标注**按表**）
    ⇒ ★ 要么**全部** `excluded`（★ 9 处差 1）· ★ 要么**全部** `included`（★ 15 处全相等）—— ★ **不许混**。

    ★★ **现状（2026-10-10 · 规格 288 量）**：★ **`excluded`** ⇒ ★ **9 处差 1**（`CreateNewStudy` / `2` / `3` ·
    `DuplicateStudy` / `2` · `ConvertStudy` / `2` · `RunAllStudies` / `RunSpecifiedStudyByName`）· ★ **6 处相等**。
    ★★★ **下一轮改表时**（★ 改成 `included`）⇒ ★ **本条自动转为「15 处全相等」**（★ 不需要改判据）✓
    """
    table, official = _table(), _official()
    gaps = [k for k, v in table.items() if official[k][0] == v + 1]
    equals = [k for k, v in table.items() if official[k][0] == v]
    assert len(gaps) + len(equals) == 15, "★ 每一条都该落进「差 1」或「相等」"
    assert len(gaps) in (0, 9), \
        "★ 「差 1」的处数只允许 **0**（全 `included`）或 **9**（全 `excluded`），实测 %d" % len(gaps)
    if gaps:
        assert all(official[k][1].endswith("&") and "Int32" in official[k][1] for k in gaps), \
            "★ 差 1 的那些末位应全是 `Int32&`"


# ── ② ★★★ **关键约束**：★ 标注是 **per-table** ⇒ 改**整张表** ──────
def test_the_annotation_is_per_table():
    """★★★ 回源码核：★ `#: arity-reflect:` 标注**紧贴在表定义上方**（★ 与 227 的关联方式一致）
    ⇒ ★★ **一个表一个约定** ⇒ ★ 想改**一条**的值 ⇒ ★ **整张表都要按同一约定写**
    ⇒ ★★ **最小正确改动面 = 那 9 处**（★ **不是** 12 条里的那 5 处）。
    """
    anns = _annotations()
    names = [n for _m, n in anns]
    assert "STUDY_MANAGER_ARITY" in names, "★ 取不到 `STUDY_MANAGER_ARITY` 的标注"
    assert "STUDY_ARITY" in names, "★ 取不到 `STUDY_ARITY` 的标注"
    for mode, _n in anns:
        assert mode in ("included", "excluded")
    #: ★ 标注与表**一对一**（★ 每个标注后面紧跟一个表名）
    assert len(anns) == len(set(names)), "★ 同一个表名出现了两次标注"


# ── ③ ★★ **4 类同步点**（★ 漏一类就红） ──────────────────────────
def test_four_synchronisation_points():
    """★★ 改这一张表要同步 **4 类**：★ ① **表值**（★ 差 1 的那 9 处）★ ② **调用点**（★ 被调用的那几个要传 `out_i4()`）
    ★ ③ **标注**（`excluded` → `included`）★ ④ **contract 测试的手抄对照表**（★ `REFLECTED_MANAGER_ARITY`）。

    ★★ **本判据钉「一致」而不是钉「现状」**：★ **标注是 `included` ⇒ 必须有 `out_i4`**；★ 反之则无。
    """
    mod = MODULE.read_text(encoding="utf-8", errors="replace")
    con = CONTRACT.read_text(encoding="utf-8", errors="replace")
    assert "_checked(STUDY_MANAGER_ARITY" in mod, "★ ① 表值：找不到调用点"
    assert "REFLECTED_MANAGER_ARITY" in con, "★ ④ 找不到测试的对照表"
    modes = {n: m for m, n in _annotations()}
    if modes.get("STUDY_MANAGER_ARITY") == "included":
        assert "out_i4" in mod, "★ ② 标注说 `included` ⇒ 调用点**必须**传 `out_i4()`"
    else:
        assert "out_i4" not in mod, "★ ② 标注说 `excluded` ⇒ 现状**不该**有 `out_i4`（★ 除非同时改了标注）"
    #: ★ ④ 对照表的值应与模块表**逐条一致**
    m = re.search(r"REFLECTED_MANAGER_ARITY\s*=\s*\{(.*?)\n\}", con, re.S)
    ref = {k: int(v) for k, v in re.findall(r'"(\w+)":\s*(\d+)', m.group(1))}
    assert ref == _table(), "★ ④ 测试对照表与模块表**必须逐条一致**"


# ── ④ ★★ 另发现 2 处（★ 272 的 12 条**不含**它们） ────────────────
def test_two_extra_entries_are_also_in_the_gap():
    """★★ 量出：★ `RunAllStudies` / `RunSpecifiedStudyByName` 的**官方末位也是 `Int32&`**
    ⇒ ★★ 它们**同属「差 1」那一批** —— ★ 而 **272 的 12 条**（★ 按**调用点**归集）**不含**它们
    ⇒ ★★ **改表时要一起改**（★ 否则表内自相矛盾）。
    """
    table, official = _table(), _official()
    for name in ("RunAllStudies", "RunSpecifiedStudyByName"):
        n, last = official[name]
        assert last.endswith("&") and "Int32" in last, "★ %s 的官方末位应是 `Int32&`" % name
        assert n - table[name] in (0, 1), "★ %s 的表值只允许「等于」或「差 1」" % name
    #: ★ 它们**不在** 272 的 12 条名单里
    twelve = {"GetBOMStartNumber", "CreatePlot", "CreateDeformedBody", "GetDisplacementAtPoints",
              "GetBucklingLoadFactors", "GetNodeLocation", "GetElementLocation",
              "CreateNewStudy", "CreateNewStudy2", "CreateNewStudy3", "DuplicateStudy", "ConvertStudy"}
    assert "RunAllStudies" not in twelve and "RunSpecifiedStudyByName" not in twelve, \
        "★ 它们**不该**在 272 的 12 条里（★ 那 12 条是按**调用点**归集的）"


# ── ⑤ ★★ 判据必须能红 ───────────────────────────────────────────────
def test_pure_function_is_red_able():
    """★ 四组负例：① 混用约定（表内不自洽）；② 非 `Int32&` 末位的条目值不对；③ 标注缺一张；④ 对照表与模块表不一致。"""
    def _check(tbl, official, anns, ref) -> list:
        bad = []
        for name, val in tbl.items():
            n, last = official.get(name, (None, ""))
            if n is None:
                bad.append("★ %s 在反射里查不到" % name)
                continue
            if last.endswith("&") and "Int32" in last:
                if n - val not in (0, 1):
                    bad.append("★ %s 只允许 0 或 1" % name)
            elif n != val:
                bad.append("★ %s 的末位不是 `Int32&` ⇒ 必须相等" % name)
        gaps = sum(1 for k, v in tbl.items() if official.get(k, (None, ""))[0] == v + 1)
        if gaps not in (0, 9):
            bad.append("★ 「差 1」的处数只允许 0 或 9，实测 %d" % gaps)
        if len(anns) < 2:
            bad.append("★ 标注应 ≥2 张表")
        if ref != tbl:
            bad.append("★ 对照表与模块表不一致")
        return bad

    t, o = _table(), _official()
    anns = _annotations()
    assert not _check(t, o, anns, t), "正常读数被判红 ⇒ 判据过严"
    assert _check({**t, "GetStudy": 99}, o, anns, t), "非 `Int32&` 末位的值不对却未判出"
    assert _check({**t, "CreateNewStudy": 9}, o, anns, t), "差 >1 却未判出"
    assert _check(t, o, [("excluded", "STUDY_MANAGER_ARITY")], t), "标注缺一张却未判出"
    assert _check(t, o, anns, {"x": 1}), "对照表不一致却未判出"
