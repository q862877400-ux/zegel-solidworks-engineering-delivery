"""★ spec 246：`admissible` 候选的收表处置（六关 + 宿主级 + 两边签名）。"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   D:/AI/SW
# 文件:   specs/202-user-coverage-gaps/recon/official-obsolete-index.json（官方索引）
#         C:/swapi/types/*/<成员>.md（官方页：两边签名）
#         scripts/sw_com_traps.py 的 `DEPRECATED_ENTRIES`（靶子表）
#         tests/test_deprecated_table_admission.py（**六关** `_admission_failures` 真源）
#         tests/test_deprecated_entry_interlock.py（调用口径 + `_REGISTERED` 真源）
# 定位:   242/243 给出了「能不能收」的六关；★ 245 证明「按**裸成员名**判会一半是假命中」
#         ⇒ ★ 本文件把「242/243 口径的 15 个 `admissible` 候选」**逐条处置**：
#         ★ 每条给出 `code` + 宿主接口 + 依据 + 证据站点，★ 并把 `collected` 的写进靶子表。
# 官方依据: 逐条的 `Obsolete. Superseded by [[…]]` 与两边签名，见 `scripts/sw_com_traps.py`
#         的 `DEPRECATED_ENTRIES` 注释块（★ spec 246 段）与 `output/_probe246_signatures.py` 的读数。
# 许可:   本仓自产（无外部来源）
# 覆盖:   只读索引 / 官方页 / 真树源码 / 靶子表；★ 不改索引生成器
# ────────────────────────────────────────────────────────────────────
from __future__ import annotations

import ast
import sys
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
for _p in (str(ROOT), str(SCRIPTS)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import sw_com_traps as TRAPS                                        # noqa: E402
from tests.test_deprecated_entry_interlock import (                 # noqa: E402
    _REGISTERED, _WRAPPERS, _count_deprecated_calls, _scan_all_modules,
)
from tests.test_deprecated_table_admission import (                 # noqa: E402
    _admission_failures, _called_names, _chain_terminal, _index_entries, _index_map,
)

COLLECTED = "collected"                             # 已收进靶子表
ALREADY = "already-in-table"                        # 本轮之前已在靶子表里
REJ_MULTI = "reject-multi-successor"                # 关 5：官方那句点名多个后继
REJ_PAGE = "reject-successor-page-missing"          # 关 6：后继页在 C:/swapi 里不存在
REJ_HOST = "reject-host-interface-mismatch"         # ★★ 246 新增：宿主接口 ≠ 条目接口（假命中）
CODES = {COLLECTED, ALREADY, REJ_MULTI, REJ_PAGE, REJ_HOST}

#: ★★★ **处置表**（★ 键 = 命中名；值 = (code, 宿主接口, 依据, 证据站点)）。
#: ★ `宿主接口` = 真树调用点的**宿主表达式所指向的接口**（★ 人工判定，依据写在下一字段）。
#: ★ 证据站点 = `(文件, 行号, 宿主表达式源码)` —— ★ 必须与重算结果**逐字对上**（判据 5）。
_DISPOSITION: dict[str, tuple[str, str, str, tuple[tuple[str, int, str], ...]]] = {
    "ActivateDoc2": (
        COLLECTED, "ISldWorks",
        "宿主 `sw` / `dynamic_sw` = ISldWorks，★ 与条目接口同；官方 `ActivateDoc2.md` ⇒ "
        "`[[ISldWorks::ActivateDoc3]]`（两边签名已读：`(Name, Silent, out Errors)` → "
        "`(Name, UseUserPreferences, Option, out Errors)`）。★ 三处是 `ActivateDoc3` 的**兜底分支**。",
        (("sw_assembly.py", 113, "sw"),
         ("sw_export.py", 407, "sw"),
         ("sw_export.py", 413, "dynamic_sw"),
         ("sw_review.py", 586, "sw")),
    ),
    "Add2": (
        REJ_HOST, "IEquationMgr",
        "★ 条目是 `ICustomPropertyManager::Add2`，而真树宿主 `mgr` = `_manager(model)` ⇒ **IEquationMgr** "
        "⇒ ★ **假命中**（`IEquationMgr::Add2` 非废弃，官方索引里 `Add2` 只有 ICustomPropertyManager 一条）。",
        (("sw_equation.py", 83, "mgr"),),
    ),
    "AddMate5": (
        ALREADY, "IAssemblyDoc",
        "★ 本轮之前已在靶子表（spec 241 收）；宿主 `asm_model` / `doc` = IAssemblyDoc，与条目接口同。",
        (("sw_assembly.py", 415, "asm_model"),
         ("sw_assembly_doc.py", 364, "doc")),
    ),
    "AutoDimension2": (
        COLLECTED, "ISketch",
        "宿主 `active` = `sketch or _safe_com_member(model.SketchManager, \"ActiveSketch\")` ⇒ **ISketch**，"
        "与条目接口同；官方 `AutoDimension2.md` ⇒ `[[ISketchManager::FullyDefineSketch]]`（★ 跨接口）。",
        (("sw_part.py", 934, "active"),),
    ),
    "FeatureCircularPattern4": (
        COLLECTED, "IFeatureManager",
        "宿主 `model.FeatureManager` = IFeatureManager，与条目接口同；官方字面后继 `FeatureCircularPattern5` "
        "★ **自己也废弃** ⇒ 链终点 `[[IFeatureManager::CreateFeature]]`。",
        (("sw_part.py", 1677, "model.FeatureManager"),),
    ),
    "FeatureLinearPattern5": (
        REJ_MULTI, "IFeatureManager",
        "★ 关 5：官方那句点名 **3** 个链接（`CreateFeature` + `ILinearPatternFeatureData` + "
        "`ILocalLinearPatternFeatureData`）⇒ 多后继必须人工表态，本轮不收。",
        (("sw_part.py", 1536, "model.FeatureManager"),
         ("sw_part.py", 2544, 'get_com_member(model, "FeatureManager")')),
    ),
    "FeatureLocalCurveDrivenPattern": (
        REJ_MULTI, "IFeatureManager",
        "★ 关 5：官方那句点名 **2** 个链接（`CreateFeature` + `ILocalCurvePatternFeatureData`）。",
        (("sw_pattern.py", 548, "fm"),),
    ),
    "GetActiveSketch2": (
        REJ_PAGE, "IModelDoc2",
        "★ 关 6：链终点 `SketchManager::ActiveSketch` 的页在 `C:/swapi/types/` 里**不存在**"
        "（★ 索引记的是 `SketchManager::ActiveSketch`，缺 `I` 前缀 ⇒ 页名对不上）⇒ 必须人工核。",
        (("sw_sketch_edit.py", 125, "model"),),
    ),
    "GetExplodedViewCount": (
        COLLECTED, "IAssemblyDoc",
        "宿主 `doc`（`call_assembly_doc`）= IAssemblyDoc，与条目接口同；官方 ⇒ "
        "`[[IAssemblyDoc::GetExplodedViewCount2]]`（`()` → `(ConfigurationName)`）。",
        (("sw_assembly_doc.py", 693, "doc"),),
    ),
    "GetModelDoc": (
        REJ_HOST, "IView",
        "★ 条目是 `IComponent2::GetModelDoc`，而真树宿主 `view` ⇒ **IView** ⇒ ★ **假命中**"
        "（`IView::GetModelDoc` 非废弃）。",
        (("sw_view.py", 460, "view"),),
    ),
    "GetUserPreferenceIntegerValue": (
        REJ_HOST, "ISldWorks",
        "★ 条目是 `IModelDoc2::GetUserPreferenceIntegerValue`，而真树宿主 `app` = "
        "`IModelDoc2.GetSldWorks` 取到的**应用对象** ⇒ **ISldWorks** ⇒ ★ **假命中**；"
        "★ 且官方后继 `IModelDocExtension::GetUserPreferenceInteger` 是**2 参的另一个方法**"
        "（★ `sw_units.py:134` 的注释已逐字写明）。",
        (("sw_units.py", 139, "app"),),
    ),
    "InsertFormToolFeature": (
        REJ_MULTI, "IFeatureManager",
        "★ 关 5：官方那句点名 **2** 个链接（`CreateDefinition` + `CreateFeature`）。",
        (("sw_sheet_metal.py", 1440, "_mgr"),),
    ),
    "ResumeSelectionList": (
        COLLECTED, "ISelectionMgr",
        "宿主 `selection` = ISelectionMgr，与条目接口同；官方 ⇒ `[[ISelectionMgr::ResumeSelectionList2]]`"
        "（`()` → `(Append)`）。",
        (("sw_selection.py", 337, "selection"),),
    ),
    "SaveAs": (
        ALREADY, "IModelDocExtension",
        "★ 本轮之前已在靶子表（`IModelDocExtension::SaveAs` / `SaveAs2` ⇒ `SaveAs3`）；"
        "宿主 `model.Extension` = IModelDocExtension。",
        (("sw_connect.py", 1167, "model.Extension"),),
    ),
    #: ★★ **spec 251 起 `SketchTrim` 不再出现在这里** —— 生成器接了「同名链接优先」规则后，
    #:   索引给的后继就是同名的 `ISketchManager::SketchTrim` ⇒ ★ **关 4（同名）把它拒了**
    #:   ⇒ ★ 它**不再是 `admissible` 候选** ⇒ ★ 处置表同步删行（★ 判据 ① 的候选数 15 → **14**）。
}

#: ★ `collected` 的期望后继（★ 必须与靶子表**逐字一致**）。
_COLLECTED_SUCCESSOR = {
    "ActivateDoc2": "ActivateDoc3",
    "AutoDimension2": "FullyDefineSketch",
    "FeatureCircularPattern4": "CreateFeature",
    "GetExplodedViewCount": "GetExplodedViewCount2",
    "ResumeSelectionList": "ResumeSelectionList2",
}


@lru_cache(maxsize=1)
def _index() -> tuple[list[dict], dict, set]:
    entries = _index_entries()
    return entries, _index_map(entries), _called_names()


def _candidates() -> dict[str, list[tuple[str, str]]]:
    """★ 复算 242/243 口径的 `admissible` 候选（★ **不自己造过滤器**）。"""
    entries, imap, called = _index()
    by_name: dict[str, list[tuple[str, str]]] = {}
    for e in entries:
        by_name.setdefault(e["member"], []).append((e["interface"], e["member"]))
    out: dict[str, list[tuple[str, str]]] = {}
    for name in sorted({e["member"] for e in entries} & called):
        terms = {k: _chain_terminal(k[0], k[1], imap) for k in by_name[name]}
        distinct = {t for t in terms.values() if t is not None}
        if len(distinct) != 1:
            continue
        t = next(iter(distinct))
        if t[1] == name or t[1] not in called:
            continue
        out[name] = by_name[name]
    return out


def _candidate_sites() -> dict[str, set[tuple[str, int, str]]]:
    """★ 重算候选名的**真树调用点**（文件, 行号, 宿主表达式）—— ★ 两种形态都收。"""
    want = set(_candidates())
    out: dict[str, set[tuple[str, int, str]]] = {}
    for fname, tree in _scan_all_modules():
        text = (SCRIPTS / fname).read_text(encoding="utf-8")
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            func = node.func
            if isinstance(func, ast.Attribute) and func.attr in want:
                out.setdefault(func.attr, set()).add(
                    (fname, node.lineno, ast.get_source_segment(text, func.value) or ""))
            elif isinstance(func, ast.Name) and func.id in _WRAPPERS \
                    and len(node.args) >= 2 and isinstance(node.args[1], ast.Constant) \
                    and node.args[1].value in want:
                out.setdefault(node.args[1].value, set()).add(
                    (fname, node.lineno, ast.get_source_segment(text, node.args[0]) or ""))
    return out


def _entry_interface(name: str) -> str | None:
    """★ 该候选名在官方索引里的**条目接口**（★ 一名一条 = 复算口径保证）。"""
    ifaces = {i for (i, _m) in _candidates()[name]}
    return next(iter(ifaces)) if len(ifaces) == 1 else None


# ── ① 覆盖：每个候选都要处置 ──────────────────────────────────────────
def test_all_candidates_are_dispositioned():
    """★★ 候选集合（重算）必须**全部**在处置表里 —— ★ 少一个即红。"""
    cands = set(_candidates())
    #: ★ 251 起：`SketchTrim` 因「同名链接优先」被关 4 拒 ⇒ 候选 **15 → 14**。
    assert len(cands) >= 14, "候选从 14 降到 %d ⇒ 读取器可能漏了" % len(cands)
    missing = sorted(cands - set(_DISPOSITION))
    assert not missing, "以下候选未处置：\n%s" % "\n".join("  " + m for m in missing)


# ── ② 封闭词表 ────────────────────────────────────────────────────────
def test_codes_are_closed_vocabulary():
    """★ 处置码必须落在封闭词表里（★ 不许写"待定 / 存疑"糊过去）。"""
    bad = sorted(n for n, (c, _i, _w, _e) in _DISPOSITION.items() if c not in CODES)
    assert not bad, "以下条目的 code 不在封闭词表 %s 里：%s" % (sorted(CODES), bad)


# ── ③ ★★ 收表的必须过**六关**（真跑 243 的 `_admission_failures`）────────
def test_collected_entries_pass_admission():
    """★★★ `collected` 的每条**必须六关全过**（★ 直接跑真函数，不是手抄结论）。

    ★ 能红的判据：★ 把任一条 `collected` 的后继改成"字面后继"（如 `FeatureCircularPattern5`）
      ⇒ 关 2（链终点）当场红。
    """
    entries, imap, called = _index()
    table = {}
    for name, (code, _iface, _why, _ev) in _DISPOSITION.items():
        if code != COLLECTED:
            continue
        assert name in _COLLECTED_SUCCESSOR, (
            "★ %s 判成 `collected` 却没在 `_COLLECTED_SUCCESSOR` 里写期望后继 "
            "（★ 两处必须同步，否则本判据会 KeyError 而不是给出可读的失败）" % name)
        for (iface, member) in _candidates()[name]:
            table[(iface, member)] = _COLLECTED_SUCCESSOR[name]
    assert len(table) >= 5, "`collected` 只剩 %d 条 ⇒ 检查量不足" % len(table)
    fails = _admission_failures(table, imap, called, entries)
    assert not fails, "★ 以下 `collected` 条目**没过六关**：%s" % (fails,)


# ── ④ 收表的必须在靶子表里，且后继逐字一致 ─────────────────────────────
def test_collected_entries_are_in_the_target_table():
    """★★ `collected` 的每条**必须已进 `DEPRECATED_ENTRIES`**，且后继与处置表**逐字一致**。"""
    bad = []
    for name, succ in _COLLECTED_SUCCESSOR.items():
        assert _DISPOSITION[name][0] == COLLECTED, "%s 的 code 与 `_COLLECTED_SUCCESSOR` 不一致" % name
        ifaces = {i for (i, _m) in _candidates()[name]}
        assert len(ifaces) == 1, "%s 在索引里有多个接口 ⇒ 本判据的假设不成立" % name
        key = (next(iter(ifaces)), name)
        if TRAPS.DEPRECATED_ENTRIES.get(key) != succ:
            bad.append("%s: 表里是 %r，期望 %r" % (key, TRAPS.DEPRECATED_ENTRIES.get(key), succ))
    #: ★ 反向一致性：★ 判成 `collected` 的名**必须**都在 `_COLLECTED_SUCCESSOR` 里（防两处漂移）
    only_code = sorted(n for n, (c, _i, _w, _e) in _DISPOSITION.items()
                       if c == COLLECTED and n not in _COLLECTED_SUCCESSOR)
    assert not only_code, "★ 以下名判成 `collected` 却没写期望后继：%s" % only_code
    assert not bad, "★ 靶子表与处置表不一致：\n" + "\n".join("  " + b for b in bad)


# ── ⑤ ★★ 宿主接口必须与条目接口一致（245 的教训） ─────────────────────
def test_collected_entries_have_matching_host_interface():
    """★★★ `collected` 的条目：★ **真树调用点的宿主接口必须 == 条目接口**。

    ★ 这是 245 的教训的判据化：★ 按**裸成员名**判会**一半是假命中**
      （`SketchTrim` 的宿主是 `ISketchManager`、`Add2` 的宿主是 `IEquationMgr`…）。
    ★ 能红的判据：★ 把 `Add2` 改成 `collected` ⇒ 宿主 `IEquationMgr` ≠ 条目 `ICustomPropertyManager` ⇒ 红。
    """
    bad = []
    for name, (code, host_iface, _why, _ev) in _DISPOSITION.items():
        if code != COLLECTED:
            continue
        entry_iface = _entry_interface(name)
        if host_iface != entry_iface:
            bad.append("%s: 宿主接口 %s ≠ 条目接口 %s" % (name, host_iface, entry_iface))
    assert not bad, "★ 收表的条目里宿主接口与条目接口不一致（★ 那是假命中）：\n%s" % (
        "\n".join("  " + b for b in bad),)


# ── ⑥ ★★ 宿主不匹配的**不许**进靶子表 ─────────────────────────────────
def test_host_mismatch_candidates_are_not_collected():
    """★★★ `reject-host-interface-mismatch` 的名**不许**出现在 `DEPRECATED_ENTRIES` 里。

    ★ 理由：★ 收了它 ⇒ 靶子表会**按名**禁止一个**我们并没有在调**的成员
      （★ 而真正在调的那个是同名的**另一个接口**的成员）⇒ ★ 判据会**指错人**。
    """
    offenders = sorted(n for n, (c, _i, _w, _e) in _DISPOSITION.items() if c == REJ_HOST
                       and any(m == n for (_iface, m) in TRAPS.DEPRECATED_ENTRIES))
    assert not offenders, (
        "★ 以下名是**宿主接口不匹配的假命中**，却被收进了靶子表 ⇒ 判据会指错人：%s" % offenders)


# ── ⑦ 证据站点必须与重算结果逐字对上（含检查量下界） ──────────────────
def test_evidence_sites_match_recomputed_sites():
    """★★ 证据站点必须是**重算站点集合的子集**；★ 并钉住检查量（事实 46：检查量为 0 判失败）。

    ★★★ **2026-10-10（规格 301）订正：比对**去掉行号**（★ 按 `(文件, 宿主表达式)`）** ——
      ★ **为什么是正当的**：★ `MEMORY.md` 规则 32 逐字 ——
        「★★★ **证据表不许钉行号，也不许判「站点逐字相等」** … ★★ 因为「站点逐字相等」把
         「**代码变了**」与「**读取器坏了**」判成**同形** ⇒ ★ **每次改代码都假红**」。
      ★★ **现场**：★ 本表原按 `(文件, 行号, 宿主表达式)` 比 ⇒ ★★ 那 8 处**行号全漂了**
        （★ `sw_assembly.py:415` · `sw_part.py:1536/2544` · `sw_sheet_metal.py:1440` …）
        ⇒ ★★★ **判据恒红**（★ 而**代码一处没坏**）。
      ★★★ **⇒ 正解**：★ 比 **`(文件, 宿主表达式)`** —— ★★ **保留原意图**（★ 站点必须真的存在、
        ★ 且宿主表达式**逐字**对得上）、★ 而**不随行号漂** ✓
    """
    hits = _candidate_sites()
    #: ★★ 把重算站点**投影**成 `(文件, 宿主表达式)`（★ 去掉行号 —— 规则 32）
    projected = {name: {(f, h) for (f, _ln, h) in sites} for name, sites in hits.items()}
    checked = sum(len(ev) for (_c, _i, _w, ev) in _DISPOSITION.values())
    assert len(_DISPOSITION) >= 14, "处置表只剩 %d 条 ⇒ 检查量不足" % len(_DISPOSITION)
    assert checked >= 14, "证据站点只剩 %d 个 ⇒ 检查量不足" % checked
    bad = []
    for name, (_c, _i, _w, ev) in _DISPOSITION.items():
        assert ev, "%s 的证据站点为空（★ 不许空口处置）" % name
        for (fname, _ln, host) in ev:
            if (fname, host) not in projected.get(name, set()):
                bad.append("%s 的证据 %s（宿主=%r）不在重算站点里" % (name, fname, host))
    assert not bad, "证据与重算站点不符：\n" + "\n".join("  " + b for b in bad)


# ── ⑧ ★★ 收表的必须有 `_REGISTERED` 登记（242 的教训 40）──────────────
def test_collected_entries_are_registered_where_called():
    """★★★ 凡 `collected` 且**真树有调用点**的名 ⇒ ★ **必须有 `_REGISTERED` 登记**
    （★ 242 的教训 40：加一条进表 ⇒ 互锁会把**现有调用**判成违规）。

    ★ 能红的判据：★ 删掉 `sw_part.py` 的 `AutoDimension2` 登记 ⇒ 当场红。
    """
    counts = _count_deprecated_calls()
    missing = []
    for name, (code, _iface, _why, _ev) in _DISPOSITION.items():
        if code not in (COLLECTED, ALREADY):
            continue
        for fname, per in counts.items():
            if per.get(name):
                if _REGISTERED.get(fname, {}).get(name, 0) < per[name]:
                    missing.append("%s: %s 处 %d 未登记" % (fname, name, per[name]))
    assert not missing, "★ 收进靶子表但**没登记**（互锁会当场红）：\n" + "\n".join("  " + m for m in missing)
