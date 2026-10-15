"""★ spec 247：多后继的**机械化表态**（官方措辞 ⇒ 真后继个数 ⇒ 能不能收表）。"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   D:/AI/SW
# 文件:   specs/202-user-coverage-gaps/recon/official-obsolete-index.json（官方索引）
#         C:/swapi/types/<接口>/<成员>.md（官方页原文 —— 三态措辞的**实证**）
#         tests/test_deprecated_table_admission.py（`_official_successor_count` / 六关 真源）
#         scripts/sw_com_traps.py 的 `DEPRECATED_ENTRIES`（靶子表）
# 定位:   243 的关 5 说「多后继**必须人工表态**」—— ★ 而它当时只数「全部 `[[…]]` 链接」，
#         ★ 把「`See X and the Remarks in Y`」里的**数据接口** `Y` 也算成后继。
#         ★ 本文件把「表态」**机械化**：★ 官方那句的**措辞**决定真后继个数（三态）。
# 官方依据（★ 三态各一条实证，逐字取自 `C:/swapi/types/`）：
#   · `Superseded by A and B` ⇒ `IModelDoc2\SketchTrim.md`（★ **两个都是**后继）
#   · `See X and the Remarks in Y` ⇒ `IFeatureManager\FeatureLinearPattern5.md`（★ **只有 X**）
#   · 其它 `See …` ⇒ `IDimension\GetSystemValue3.md` / `IProjectionCurveFeatureData`（★ **判不出**）
# 许可:   本仓自产（无外部来源）
# 覆盖:   只读索引 / 官方页 / 靶子表；★ 不改索引生成器
# ────────────────────────────────────────────────────────────────────
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
for _p in (str(ROOT), str(SCRIPTS)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import sw_com_traps as TRAPS                                        # noqa: E402
from tests.test_deprecated_entry_interlock import (                 # noqa: E402
    _REGISTERED, _count_deprecated_calls,
)
from tests.test_deprecated_table_admission import (                 # noqa: E402
    _MULTI_SUCCESSOR_ADJUDICATED, _admission_failures, _called_names, _index_entries,
    _index_map, _official_successor_count, _official_successor_links, _successor_links,
)

#: ★★ 本轮新收的 2 条（★ 官方措辞 = `See X and the Remarks in …` ⇒ 真后继只有 X）。
_COLLECTED = {
    "FeatureLinearPattern5": "CreateFeature",
    "FeatureLocalCurveDrivenPattern": "CreateFeature",
}

#: ★ 官方三态的**逐字实证**（★ 取自 `C:/swapi/types/`，不是编的）。
FIXTURE_SUPERSEDED_PAIR = (
    "Obsolete. Superseded by [[ISketchManager::SketchExtend]] and [[ISketchManager::SketchTrim]].")
FIXTURE_SEE_REMARKS_IN = (
    "Obsolete. See [[IFeatureManager::CreateFeature]] and the Remarks in "
    "[[ILinearPatternFeatureData]] and [[ILocalLinearPatternFeatureData]].")
FIXTURE_SEE_REMARKS_OF = (
    "Obsolete. See [[IFeatureManager::CreateFeature]] and the Remarks of "
    "[[ICurveDrivenPatternFeatureData]].")
FIXTURE_SEE_PLAIN_AB = (
    "Obsolete. See [[IDimension::GetSystemValue3]] and [[IDimension::IGetSystemValue3]].")
FIXTURE_SEE_PLAIN_REVERSED = (
    "Obsolete. See [[IProjectionCurveFeatureData]] and [[IFeatureManager::CreateDefinition]].")
FIXTURE_SINGLE = "Obsolete. Superseded by [[ISldWorks::ActivateDoc3]]."


# ── ① 纯函数三态（★ 合成输入 —— 真表为空时这几条**仍然有检查量**）─────────
def test_superseded_by_counts_all_links():
    """★ 形态一：`Superseded by A and B` ⇒ ★ **两个都是后继**（★ 表表达不了）。"""
    assert _official_successor_count(FIXTURE_SUPERSEDED_PAIR) == 2
    assert _official_successor_links(FIXTURE_SUPERSEDED_PAIR) == [
        "ISketchManager::SketchExtend", "ISketchManager::SketchTrim"]


def test_see_remarks_counts_only_the_links_before_remarks():
    """★★ 形态二：`See X and the Remarks in/of Y` ⇒ ★ **只有 X**（Y 是**数据接口**）。"""
    assert _official_successor_links(FIXTURE_SEE_REMARKS_IN) == ["IFeatureManager::CreateFeature"]
    assert _official_successor_count(FIXTURE_SEE_REMARKS_IN) == 1
    #: ★ `Remarks **of**` 是**另一种写法**（★ 247 实测：5 条 `See(other)` 里就有它）
    assert _official_successor_links(FIXTURE_SEE_REMARKS_OF) == ["IFeatureManager::CreateFeature"]


def test_see_without_remarks_is_undecidable():
    """★★ 形态三：其它 `See …` ⇒ ★ **判不出**（★ 顺序不可靠 —— 数据接口**可能在前**）。"""
    assert _official_successor_count(FIXTURE_SEE_PLAIN_AB) is None
    assert _official_successor_count(FIXTURE_SEE_PLAIN_REVERSED) is None


def test_single_link_is_counted_as_one():
    """★ 单链接 ⇒ `1`（★ 这是「过」的那一态）。"""
    assert _official_successor_count(FIXTURE_SINGLE) == 1


def test_undecidable_requires_adjudication_and_superseded_pair_is_refused():
    """★★★ 关 5 的三态**真的生效**（★ 用**合成表态表**，★ 所以真表为空也有检查量）。

    ★ 能红的判据：★ 把 `SketchTrim`（`Superseded by A and B`）塞进合成表态表
      ⇒ 关 5 **仍然红**（★ 表态**不能**把「表表达不了」的条目放行）。
    """
    entries = _index_entries()
    imap = _index_map(entries)
    called = _called_names()
    #: ① `Superseded by A and B` ⇒ **两个都是后继** ⇒ ★ **表态也不许放行**
    #:   ★★ **251 起不用 `SketchTrim`**（它的后继现在同名 ⇒ 关 4 会先拒）
    #:   ⇒ 改用 `IModelDoc2::MaterialIdName`（后继 `GetMaterialPropertyName2` 不同名）⇒ 关 5 来拒。
    t = {("IModelDoc2", "MaterialIdName"): "GetMaterialPropertyName2"}
    fails = _admission_failures(t, imap, called, entries,
                                adjudicated={("IModelDoc2", "SketchTrim"): "理由不重要"})
    assert fails and fails[0][1].startswith("multiple-official-successors"), fails
    #: ② 合成表里放一条 `See …`（判不出）⇒ ★ **未表态即红**
    line = "Obsolete. See [[IFeatureManager::CreateFeature]] and [[IFeatureManager::CreateDefinition]]."
    assert _official_successor_count(line) is None
    synth = entries + [{"interface": "IFeatureManager", "member": "DSH_SYNTH",
                        "successor": "IFeatureManager::CreateFeature",
                        "obsolete_line": line, "page": "x"}]
    synth_imap = _index_map(synth)
    t2 = {("IFeatureManager", "DSH_SYNTH"): "CreateFeature"}
    assert _admission_failures(t2, synth_imap, called, synth), "★ 未表态却没红"
    ok = _admission_failures(t2, synth_imap, called, synth,
                             adjudicated={("IFeatureManager", "DSH_SYNTH"): "已人工读过官方页"})
    assert not ok, "★ 已表态却仍红：%s" % (ok,)


# ── ② ★ 真树：真后继 = 1 的多链接条目（下界，防「检查量为 0」）────────────
def test_real_tree_multi_link_names_are_frozen():
    """★ 真树读数下界（★ 只增不减 —— 减少 = 探测器漏了）。

    ★★★ **2026-10-10（规格 301）订正 `hit 18 → 17` · `pair 16 → 15`** —— ★ **为什么是正当的**：
      ★★ **先量的结论**：★ 拿 **`HEAD` 的索引**与**工作树的索引**各算一遍 `hit` ⇒
        ★★★ **两边都是 17**（★ `lost=[]` · `gained=[]`）⇒ ★★ **`18` 从来就不是真值** ——
        ★ 它是 `specs/247` 当初**按「`SUPERSEDED-BY 16` + `SEE+REMARKS 2`」**手算的**预期值**，
        ★ 而**真算**出来是 **15 + 2 = 17**（★ 见下）。
      ★★ **哪一条被算进了"预期 16"却没算进"实际 15"**：★ `FeatureLocalCurveDrivenPattern`
        的官方句逐字是 `Obsolete. **See** [[IFeatureManager::CreateFeature]] **and the Remarks in**
        [[ILocalCurvePatternFeatureData]].` ⇒ ★★ `_official_successor_count` 判它 **= 1**
        （★ 「See X **and the Remarks in** Y」里 Y 是**说明页**、★ 不是后继）⇒ ★ 它归 **`single`**、
        ★ **不归 `pair`** ✓
      ★★★ **⇒ 这是「口径」而非「探测器漏了」**：★ `single` 仍是 **2**（★ 未变），
        ★ 而 `pair` 从**手算的 16** 变成**真算的 15** —— ★ 两条之和 **17** 一致 ✓
      ★★ **依据**（`MEMORY.md` 规则 29）：★ 下调要写「为什么是正当减少」+ ★ 规则 22：★ 补内容断言。
      ★★★ **内容断言**：★ `tests/test_no_snapshot_constants_301.py` 的
        `test_ratchet_downgrades_have_content_assertions` 守着「下调必须带按名字的断言」✓
    """
    entries = _index_entries()
    called = _called_names()
    multi = [e for e in entries if len(_successor_links(e.get("obsolete_line", ""))) >= 2]
    hit = [e for e in multi if e["member"] in called]
    single = [e for e in hit if _official_successor_count(e["obsolete_line"]) == 1]
    pair = [e for e in hit if _official_successor_count(e["obsolete_line"]) == 2]
    assert len(multi) >= 254, "多链接条目从 254 降到 %d" % len(multi)
    assert len(hit) >= 17, "真树在调的多链接条目从 17 降到 %d" % len(hit)
    assert len(single) >= 2, "真后继 = 1 的从 2 降到 %d" % len(single)
    assert len(pair) >= 15, "`Superseded by A and B` 的从 15 降到 %d" % len(pair)
    #: ★★ 内容断言（★ 规则 22）：★ **`single + pair == hit`** —— ★ 口径自洽，★ 不靠某一个绝对值
    assert len(single) + len(pair) == len(hit), (
        "★ `single(%d) + pair(%d) ≠ hit(%d)` ⇒ ★ 口径不自洽（★ 有条目没被分到桶里）"
        % (len(single), len(pair), len(hit)))


# ── ③ 收表的必须过六关（★ 真跑 `_admission_failures`）───────────────────
def test_collected_multi_successor_entries_pass_admission():
    """★★★ 本轮新收的 2 条**必须六关全过**（★ 关 5 已按措辞细化）。"""
    entries = _index_entries()
    imap = _index_map(entries)
    table = {}
    for name, succ in _COLLECTED.items():
        ifaces = {i for (i, m) in imap.keys() if m == name}
        assert len(ifaces) == 1, "%s 在索引里有多个接口" % name
        table[(next(iter(ifaces)), name)] = succ
    assert len(table) >= 2, "检查量不足：%d" % len(table)
    fails = _admission_failures(table, imap, _called_names(), entries)
    assert not fails, "★ 新收的多后继条目没过六关：%s" % (fails,)


# ── ④ 收表的在靶子表里，且后继一致 ────────────────────────────────────
def test_collected_multi_successor_entries_are_in_the_target_table():
    """★★ 新收的 2 条必须在 `DEPRECATED_ENTRIES` 里，且后继**逐字一致**。"""
    bad = []
    for name, succ in _COLLECTED.items():
        key = ("IFeatureManager", name)
        if TRAPS.DEPRECATED_ENTRIES.get(key) != succ:
            bad.append("%s: 表里是 %r，期望 %r" % (key, TRAPS.DEPRECATED_ENTRIES.get(key), succ))
    assert not bad, "★ 靶子表与预期不一致：\n" + "\n".join("  " + b for b in bad)


# ── ⑤ ★★ 表态表不许放行「两个真后继」的条目 ─────────────────────────────
def test_adjudication_never_whitelists_a_two_successor_entry():
    """★★★ 凡在表态表里的条目，其官方措辞的真后继个数**不许 > 1**（★ 表表达不了）。

    ★ 能红的判据：★ 把 `SketchTrim` 塞进表态表 ⇒ 当场红。
    """
    entries = _index_entries()
    by_key = {(e["interface"], e["member"]): e for e in entries}
    bad = []
    for key in _MULTI_SUCCESSOR_ADJUDICATED:
        e = by_key.get(key)
        if e is None:
            bad.append("%s 不在官方索引里" % (key,))
            continue
        n = _official_successor_count(e.get("obsolete_line", ""))
        if n is None or n > 1:
            bad.append("%s 的真后继个数 = %s ⇒ 不该用表态放行" % (key, n))
    assert not bad, "★ 表态表里有「表表达不了」的条目：\n" + "\n".join("  " + b for b in bad)


# ── ⑥ 表态表每条必须有依据（引用官方页路径）─────────────────────────────
def test_adjudication_entries_have_evidence():
    """★ 表态表每条的依据必须 **≥40 字** 且**引用官方页路径**（★ 不许空口表态）。

    ★★ **空表的处置**：★ 真表为空 ⇒ 本判据**没有检查量** —— ★ 所以把「依据不合格」这条
      抽成**纯函数**，由下面的合成负例证明它**能红**（★ 纪律 15）。
    """
    def _bad_evidence(adjudicated: dict) -> list[str]:
        out = []
        for key, why in adjudicated.items():
            if len(str(why)) < 40 or "swapi" not in str(why):
                out.append(str(key))
        return out

    assert not _bad_evidence(_MULTI_SUCCESSOR_ADJUDICATED), "★ 真表态表里有依据不合格的条目"
    #: ★ 合成负例（★ 证明本判据**不是空判据**）
    assert _bad_evidence({("A", "B"): "太短"}) == ["('A', 'B')"]
    assert _bad_evidence({("A", "B"): "x" * 50}) == ["('A', 'B')"]          # 没引用 swapi
    assert not _bad_evidence({("A", "B"): "读了 C:/swapi/types/A/B.md 的 Remarks" * 2})


# ── ⑦ 收表的必须有 `_REGISTERED` 登记（242 的教训 40）───────────────────
def test_collected_multi_successor_entries_are_registered_where_called():
    """★★ 凡新收且真树有调用点的名 ⇒ ★ 必须有 `_REGISTERED` 登记。"""
    counts = _count_deprecated_calls()
    missing = []
    for name in _COLLECTED:
        for fname, per in counts.items():
            if per.get(name):
                if _REGISTERED.get(fname, {}).get(name, 0) < per[name]:
                    missing.append("%s: %s 处 %d 未登记" % (fname, name, per[name]))
    assert not missing, "★ 新收条目没登记（互锁会当场红）：\n" + "\n".join("  " + m for m in missing)
    #: ★ 反向：登记不许是死条目（★ 处数必须 ≥ 登记值）
    dead = [("%s: %s" % (f, m)) for f, per in _REGISTERED.items() for m in per
            if m in _COLLECTED and counts.get(f, {}).get(m, 0) < per[m]]
    assert not dead, "★ 登记表里有死条目：%s" % dead
