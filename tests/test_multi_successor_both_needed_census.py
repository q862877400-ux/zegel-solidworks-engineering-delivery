"""★ spec 249：「两个后继都要」的**宿主级**先量 —— 结论 **0 靶子**（★ 裸名归集会给出 4 条**假**靶子）。"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   D:/AI/SW
# 文件:   specs/202-user-coverage-gaps/recon/official-obsolete-index.json（官方索引）
#         tests/test_deprecated_table_admission._called_names（真树被调成员名）
#         tests/test_deprecated_entry_interlock._scan_all_modules（真树扫描）
#         tests/test_obsolete_name_host_adjudication._NAME_HOST_REVIEW（248 的宿主级表态表 —— 跨规格一致）
# 定位:   247 的未过门 1 = 「16 条 `Superseded by A and B` 表达不了两个后继」；
#         ★ 本轮**先量**：真树上有没有**任何一处**「写」站点落在**两个后继的那个废弃条目**的接口上。
#         ★★ 若为 0 ⇒ **本待办没有靶子** ⇒ 写结论并**关闭**（★ 不要为了改表形态而改表形态）。
# 官方依据: 索引 `obsolete_line` 形如 `Obsolete. Superseded by [[A]] and [[B]].`（★ 两个都是后继）
#           例：`IView/Name.md`「Superseded by [[IView::GetName2]] and [[IView::SetName2]]」
# 许可:   本仓自产（无外部来源）
# 覆盖:   只读索引 / 真树源码；★ 不改 `tools/build_obsolete_index.py`、不改 `sw_com_traps`、不改任何 `scripts/sw_*.py`
# ────────────────────────────────────────────────────────────────────
from __future__ import annotations

import ast
import json
import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
for _p in (str(ROOT), str(SCRIPTS)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from tests.test_deprecated_entry_interlock import _scan_all_modules  # noqa: E402
from tests.test_deprecated_table_admission import _called_names  # noqa: E402

INDEX = ROOT / "specs/202-user-coverage-gaps/recon/official-obsolete-index.json"
LINK = re.compile(r"\[\[([^\]]+)\]\]")

#: ★ 包装器（★ 逐字同 `test_deprecated_entry_interlock._WRAPPERS` 的**读**形态 —— 这三个都只读）。
_READ_WRAPPERS = ("get_com_member", "call_com_member", "call_assembly_doc")

#: ★★★ **写站点表态表**：`(文件, 宿主表达式, 成员名)` → `(宿主接口, 依据)`。
#: ★ 真树上对「多后继条目成员名」的**写**（`ast.Attribute` 的 `Store` 上下文）**只有这 7 处**。
#: ★★★ **spec 292**：★ 键里的**行号去掉**了（★ 铁律 7：行号会漂）⇒ ★ 实测 40 个切片里破了 4 次。
_WRITE_SITE_REVIEW: dict[tuple[str, str, str], tuple[str, str]] = {
    ("sw_sheet_metal.py", "bend_allowance", "KFactor"): (
        "ICustomBendAllowance",
        "宿主 `bend_allowance` = `call_com_member(manager, \"CreateCustomBendAllowance\")` "
        "⇒ **ICustomBendAllowance**（★ 不是 `IBendsFeatureData`/`IOneBendFeatureData`/`ISheetMetalFeatureData`）。"),
    ("sw_sheet_metal.py", "cba", "KFactor"): (
        "ICustomBendAllowance",
        "同上：宿主 `cba` = `manager.CreateCustomBendAllowance()` ⇒ **ICustomBendAllowance**。"),
    ("sw_assembly.py", "mate", "Name"): (
        "IMate2",
        "宿主 `mate` = `AddMate5` 的返回值 ⇒ **IMate2**（★ 不是 `IView`）。"),
    #: ★★★ 2026-10-10 **本条已随 `sw_gear.py` 移出**（★ 业主架构指令）：
    #:   ★ 业主原话：「★ **我想让你继承上游的是工具，只是单纯的工具。**
    #:     ★ **而像齿轮这种东西，在我认知里属于方法 —— 方法错了，工具再多也没有用。**
    #:     ★ **你要从你继承的东西里面把方法筛选出来，把工具留下来，方法全部都删掉。**」✓
    #:   ★★ `sw_gear.py`（★ 渐开线齿形公式 = **方法**）已移出 `scripts/` ⇒
    #:     ★ 它那处写站点（`feature.Name = …`）**跟着走** ⇒ ★ 站点数 **7 → 6** ✓
    #:   ★ 原件在 `archive/inherited-methods/scripts/sw_gear.py`（★ **只搬不删**）✓
    ("sw_hole_features.py", "feature", "Name"): (
        "IFeature",
        "宿主 `feature` 是本函数形参（特征对象）⇒ **IFeature**（★ 不是 `IView`）。"),
    ("sw_motion.py", "study", "Name"): (
        "CWStudy",
        "宿主 `study` = `motion_member(manager, \"CreateMotionStudy\")` ⇒ **CWStudy**（cosworks 族）。"),
    ("sw_motion.py", "motor_feature", "Name"): (
        "IFeature",
        "宿主 `motor_feature` = `motion_member(motion_study, \"CreateFeature\", motor_data)` "
        "⇒ **马达特征对象**（★ 不是 15 条里任何一个接口）。"),
}

#: ★ 下界（★ 只允许增不允许减）。
#: ★★★ **2026-10-10（spec 292）一处下调 —— ★ 写了「为什么是正当减少」**：
#:   · `BASELINE_ENTRIES` **15 → 14**
#:   ★★ **真因**：**spec 261 把 `IModelDoc2::MaterialIdName` 换成了官方后继
#:     `IPartDoc::GetMaterialPropertyName2`** ⇒ ★ 该条目（`IModelDoc2::MaterialIdName` →
#:     `IPartDoc::GetMaterialPropertyName2` + `SetMaterialPropertyName2`，★ 两个后继）**不再「真树在调」**
#:     ⇒ ★ 从 `_multi_pair_entries()` 里消失。
#:   ★★ **内容断言**（★ 铁律 22）：`test_material_id_name_left_the_census_by_261` 按**名字**钉住。
BASELINE_ENTRIES = 14
#: ★★★ 2026-10-10 **7 → 6**（★ 业主架构指令 —— ★ 正当减少）：
#:   ★ 业主原话：「★ **我想让你继承上游的是工具，只是单纯的工具。**
#:     ★ **而像齿轮这种东西，在我认知里属于方法 —— 方法错了，工具再多也没有用。**」✓
#:   ★★ **减少了什么**：★ `("sw_gear.py", "feature", "Name")` 那处写站点 ——
#:     ★ `sw_gear.py`（★ 渐开线齿形公式 = **方法**）已移出 `scripts/` ⇒ ★ 站点**跟着走** ✓
#:   ★★★ **为什么是正当减少**：★ 移出 `sw_gear` 是**目的**（★ 业主令），★ 不是副作用 ✓
#:   ★ 原件在 `archive/inherited-methods/scripts/sw_gear.py`（★ **只搬不删**）✓
#:   ★★ **判据的强度没降**：★ 本测试仍**按名字**逐条核（★ 铁律 7），★ 只是少了一条合法移出的 ✓
BASELINE_WRITE_SITES = 6
#: ★★ 裸名归集会给出多少条**假**「两个后继都要」（★ 本轮实测，★ 用来把踩的坑冻成判据）。
BASELINE_BARE_NAME_FALSE_TARGETS = 4


def _multi_pair_entries() -> list[dict]:
    """★ 索引里 `Obsolete. Superseded by [[A]] and [[B]]` **且**成员名在真树被调用**的条目。"""
    if not INDEX.exists():
        return []
    data = json.loads(INDEX.read_text(encoding="utf-8"))
    entries = data if isinstance(data, list) else data.get("entries", data)
    if isinstance(entries, dict):
        entries = list(entries.values())
    called = _called_names()
    out = []
    for e in entries:
        line = e.get("obsolete_line", "") or ""
        if len(LINK.findall(line)) < 2:
            continue
        if not line.lstrip().startswith("Obsolete. Superseded by"):
            continue
        if e.get("member") not in called:
            continue
        out.append(e)
    return out


def _write_sites(members: set[str]) -> set[tuple[str, str, str]]:
    """★ 真树上对 `members` 里任一成员名的**写**站点（★ `ast.Attribute` 的 `Store` 上下文）。

    ★★ **为什么只收 `Store`**：`get_com_member(obj, "M")` 与 `obj.M(...)` 都是**读**；
    ★ 只有 `obj.M = v` 才是**写** —— ★ 而「两个后继」里**只有 Set 侧**才需要写。

    ★★★ **spec 292**：★ 站点键从 `(文件, 行号, 宿主, 成员)` 改成 **`(文件, 宿主, 成员)`** ——
      ★★ 行号会漂（★ 铁律 7）⇒ ★ 实测 40 个切片里破了 4 次 ⇒ ★ 那是**假红发生器**。
    """
    out: set[tuple[str, str, str]] = set()
    for fname, tree in _scan_all_modules():
        text = (SCRIPTS / fname).read_text(encoding="utf-8")
        for node in ast.walk(tree):
            if isinstance(node, ast.Attribute) and node.attr in members \
                    and isinstance(node.ctx, ast.Store):
                host = ast.get_source_segment(text, node.value) or ""
                out.add((fname, host, node.attr))
    return out


def _both_needed_failures(
    entries: list[dict],
    write_review: dict[tuple[str, str, str], tuple[str, str]],
) -> list[str]:
    """★ 纯函数：返回「**真的**需要两个后继」的写站点清单（★ 空 = 本待办没有靶子）。

    ★★ 判据 = 写站点的 **`(宿主接口, 成员名)`** 落在条目的 **`(interface, member)`** 集合里。
    ★ 只看成员名（裸名）**不算** —— ★ 那正是 245/248 证明会骗人的口径。
    """
    pairs = {(e["interface"], e["member"]) for e in entries}
    bad: list[str] = []
    for (f, host, member), (iface, _why) in sorted(write_review.items()):
        if (iface, member) in pairs:
            bad.append("%s 宿主 %r=%s 写 %s ⇒ 该条目**两个后继都要**"
                       % (f, host, iface, member))
    return bad


# ── ① 先量：条目数与被检写站点数 ──────────────────────────────────────
def test_census_sizes_are_frozen():
    """★ 下界：`Superseded by A and B` 且真树在调的条目 ≥ **14**；写站点 ≥ **7**。

    ★★★ **spec 292**：★ 条目 15 → **14** —— ★ `IModelDoc2::MaterialIdName` 已被 **261** 换掉
      ⇒ ★ 不再「真树在调」⇒ ★ 从清单里消失（★ 见 `test_material_id_name_left_the_census_by_261`）。
    """
    if not INDEX.exists():
        pytest.skip("官方索引不在本机 ⇒ 无数据源（★ 缺数据源 ≠ 检查失败）")
    entries = _multi_pair_entries()
    assert len(entries) >= BASELINE_ENTRIES, \
        "条目从 %d 降到 %d ⇒ 读取器可能漏了" % (BASELINE_ENTRIES, len(entries))
    sites = _write_sites({e["member"] for e in entries})
    assert len(sites) >= BASELINE_WRITE_SITES, \
        "写站点从 %d 降到 %d ⇒ 读取器可能漏了" % (BASELINE_WRITE_SITES, len(sites))


# ── ①b ★★★ **内容断言**：`MaterialIdName` 已按 261 离开清单 ────────────
def test_material_id_name_left_the_census_by_261():
    """★★★ **棘轮下调的内容断言**（★ 铁律 22）：★ `BASELINE_ENTRIES` 15 → 14 **必须能被证明**。

    ★★ 证据 = `IModelDoc2::MaterialIdName` 已被 **spec 261** 换成官方后继
    `IPartDoc::GetMaterialPropertyName2` ⇒ ★ 它**不再**出现在 `_multi_pair_entries()` 里。
    ★ 判据**按名字定位**（★ 铁律 7）：★ 逐条核 `interface::member`，★ **不是**按数量。
    """
    if not INDEX.exists():
        pytest.skip("官方索引不在本机 ⇒ 无数据源（★ 缺数据源 ≠ 检查失败）")
    got = {"%s::%s" % (e["interface"], e["member"]) for e in _multi_pair_entries()}
    assert "IModelDoc2::MaterialIdName" not in got, \
        "★ `IModelDoc2::MaterialIdName` 又回来了 ⇒ 261 的换路由被回退（★ 或该名又被调用）"
    src = (SCRIPTS / "sw_simulation.py").read_text(encoding="utf-8", errors="replace")
    assert "GetMaterialPropertyName2" in src, \
        "★ `sw_simulation.py` 里没有官方后继 `GetMaterialPropertyName2` ⇒ 261 的证据不成立"


# ── ② 每个写站点都要表态 ──────────────────────────────────────────────
def test_every_write_site_is_adjudicated():
    """★ 真树上的每个写站点都要在表态表里；★ 表里的条目也必须还在真树上（★ 双向）。"""
    if not INDEX.exists():
        pytest.skip("官方索引不在本机 ⇒ 无数据源")
    entries = _multi_pair_entries()
    sites = _write_sites({e["member"] for e in entries})
    missing = sorted(sites - set(_WRITE_SITE_REVIEW))
    assert not missing, "以下写站点未表态（★ 必须判明宿主接口）：\n%s" \
        % "\n".join("  %s:%d host=%r 写 %s" % s for s in missing)
    stale = sorted(set(_WRITE_SITE_REVIEW) - sites)
    assert not stale, "表态表里这些写站点在真树上**不存在**了（★ 空口表态）：%s" % stale


# ── ③ ★★ 核心：没有任何写站点落在「两个后继」的废弃接口上 ──────────────
def test_no_write_site_targets_a_multi_successor_interface():
    """★★★ 本待办**有没有靶子** —— ★ 结论：**0**。

    ★ 能红的判据：★ 若真树里出现 `view.Name = …`（宿主 IView）⇒ 本判据当场红。
    """
    if not INDEX.exists():
        pytest.skip("官方索引不在本机 ⇒ 无数据源")
    entries = _multi_pair_entries()
    bad = _both_needed_failures(entries, _WRITE_SITE_REVIEW)
    assert not bad, (
        "以下站点**真的**需要「两个后继」（★ 靶子表必须升级为可表达多后继）：\n%s"
        % "\n".join("  " + b for b in bad))


# ── ④ ★★ 判据**能红**（合成负例）─────────────────────────────────────
def test_criterion_is_red_able():
    """★★ 合成负例：把某条写站点的宿主接口改成 `IView` ⇒ 纯函数必须报出来。"""
    entries = [{"interface": "IView", "member": "Name"}]
    ok = {("sw_x.py", "view", "Name"): ("IView", "合成")}
    assert _both_needed_failures(entries, ok), "IView 写 Name 未被判出 ⇒ **空判据**"
    bad = {("sw_x.py", "feature", "Name"): ("IFeature", "合成")}
    assert not _both_needed_failures(entries, bad), \
        "`IFeature` 写 `Name` 被误判成靶子 ⇒ 判据过宽（★ 那正是裸名归集的病）"


# ── ⑤ ★★ 把「裸名归集会给出假靶子」冻成判据 ──────────────────────────
def test_bare_name_aggregation_would_give_false_targets():
    """★★★ **本轮的踩坑实录**：★ 只按**裸成员名**归集 ⇒ 会得出 **4 条假「两个后继都要」**
    （`KFactor` ×3 的宿主是 `ICustomBendAllowance`、`Name` 的写站点宿主是 `IMate2`/`IFeature`/`CWStudy`）。

    ★ 本判据的意义：★ 若哪天**真的**出现靶子，裸名读数会**同时**变化 ⇒ 提醒复核；
    ★ 且它把「裸名口径会骗人」这件事**留在判据里**，而不是只写在散文里。
    """
    if not INDEX.exists():
        pytest.skip("官方索引不在本机 ⇒ 无数据源")
    entries = _multi_pair_entries()
    members = {e["member"] for e in entries}
    sites = _write_sites(members)
    bare_members = {m for (_f, _h, m) in sites}
    # ★ 裸名口径下会被判成「两个后继都要」的**条目**（★ 实测 4 条 = `KFactor` ×3 + `IView::Name`）。
    false_targets = sorted(
        "%s::%s" % (e["interface"], e["member"])
        for e in entries if e["member"] in bare_members)
    assert len(false_targets) >= BASELINE_BARE_NAME_FALSE_TARGETS, \
        "裸名假靶子从 %d 降到 %d ⇒ 站点或条目变了，请复核：%s" % (
            BASELINE_BARE_NAME_FALSE_TARGETS, len(false_targets), false_targets)
    # ★ 而这些假靶子在**宿主级**判据下必须**一条都不成立**。
    assert not _both_needed_failures(entries, _WRITE_SITE_REVIEW), \
        "宿主级判据报出了靶子 ⇒ 裸名与宿主级结论不一致，请复核"


# ── ⑥ 跨规格一致：重复出现的宿主必须与 248 的表同接口 ────────────────
def test_hosts_agree_with_spec_248():
    """★ `feature` / `study` 这两个宿主在 248 的表里也有 ⇒ ★ 接口必须一致（★ 防两表漂移）。"""
    try:
        from tests.test_obsolete_name_host_adjudication import _NAME_HOST_REVIEW
    except ImportError:                                          # pragma: no cover
        pytest.skip("248 的表不在本机")
    for (_f, host, _m), (iface, _why) in _WRITE_SITE_REVIEW.items():
        if host in _NAME_HOST_REVIEW:
            other = _NAME_HOST_REVIEW[host][1]
            assert iface == other, \
                "宿主 %r 在 248 的表里是 %s、在本表里是 %s ⇒ 两表漂移" % (host, other, iface)
