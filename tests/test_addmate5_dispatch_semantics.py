"""★ spec 291：**`AddMate5` 分流语义复核** —— 两处 docstring 的「该怎么换」与官方/登记表**不一致** ⇒ 订正记档。"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   D:/AI/SW
# 文件:   C:\swapi\types\IAssemblyDoc\AddMate5.md（★ 三条分流 · ★ 官方逐字）
#         C:\swapi\types\IAssemblyDoc\AddConcentricMateWithTolerance.md（★★ **前置：父标准同心配合必须已存在**）
#         C:\swapi\types\IAssemblyDoc\AddDistanceMate.md（★★ **FirstArcCondition/SecondArcCondition 只对柱面距离有效**）
#         scripts/sw_assembly.py::add_mate5_checked（★ 「该怎么换」段）
#         scripts/sw_assembly_doc.py::add_mate（★ 「该怎么换」段）
#         scripts/sw_com_traps.py:296-298（★ 登记表**已经**写对：偏心同心 / 柱面距离 + 「一个参数定不下来」）
#         tests/test_deprecated_entry_interlock.py:80-96（★ `_REGISTERED` **已经**写对 · ★ 真名 `add_mate5_checked`）
#         specs/241-deprecated-entry-interlock-coverage/acceptance.md（★★ 核心事实四 · ★★ 核心事实五）
# 定位:   ★★ 复核「分流语义」是否**与官方 + 本仓三处权威记录一致**。
#         ★★★ 结论：**不一致** —— 两处 docstring 的「该怎么换」把分流写成「按 `mate_type` 数值」，
#           ① 丢了限定词（官方是 **Misaligned** concentric / **Cylindrical** distance）·
#           ② 与 241 核心事实四（「一个 `mate_type` 定不下来」）**直接矛盾** ·
#           ③ 漏了后继的**前置**（父标准同心配合 / 两圆柱面）·
#           ④ `sw_assembly_doc.py` 那处还**指错了调用方名**（`add_mate` 在 `sw_assembly.py` 里**不存在**）。
# 判据:   ★★★ **未表态即红**（铁律 3）：取「该怎么换」段（★ **按标记定位，不按行号**）⇒
#         ① 必须含**偏心的同心**限定词 + **圆柱面距离**限定词；② 必须含「一个 `mate_type` 定不下来」类表态；
#         ③ `sw_assembly_doc.py` 必须写出**真调用方** `add_mate5_checked`；④ ★ **边界冻结**：路由**不得**被改。
# 官方依据: `AddMate5.md:12`（Obsolete → `CreateMate`）· `:39-43`（三条分流）·
#           `AddConcentricMateWithTolerance.md:27-29`（前置 + ★★ **反向指回 `AddMate5`** ⇒ 循环引用）·
#           `AddDistanceMate.md:22-23,34,78`（柱面距离专用参数 + 选择要求）
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 覆盖:   只读（★ 现场读源码与官方页；★ 本文件不写任何文件）
# ────────────────────────────────────────────────────────────────────
from __future__ import annotations

import ast
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASM = ROOT / "scripts" / "sw_assembly.py"
DOC = ROOT / "scripts" / "sw_assembly_doc.py"
OFF_DIR = Path(r"C:\swapi\types\IAssemblyDoc")
OFF_MATE5 = OFF_DIR / "AddMate5.md"
OFF_CONC = OFF_DIR / "AddConcentricMateWithTolerance.md"
OFF_DIST = OFF_DIR / "AddDistanceMate.md"

#: ★★ **约定（★ 人写死，门禁只按它查 —— 铁律 5）**：官方英文限定词 ↔ 本仓中文限定词。
#:   ★ 这不是"自动挑选"：映射表是**显式**的，且由 `test_official_successor_pages_state_their_preconditions`
#:   逐条锚回**官方原文**（★ 铁律 6：别比对测试里手抄的常量）。
CONCENTRIC_QUALIFIERS = ("偏心", "misaligned", "Misaligned")
DISTANCE_QUALIFIERS = ("圆柱", "cylindrical", "Cylindrical")
#: ★★ **封闭词表**：必须**显式表态**「一个 `mate_type` 定不下来」（★ 241 核心事实四的逐字）。
MATE_TYPE_INSUFFICIENT = ("定不下来", "不足以", "不能只凭")
#: ★★★ **真调用方**（★ 241 核心事实五：`sw_assembly.py` 里**没有** `add_mate`）。
REAL_CALLER = "add_mate5_checked"
PHANTOM_CALLER = "add_mate"


# ── 取点（★ 按名字 + 按标记，不按行号） ───────────────────────────────
def _func_names(path: Path) -> set:
    """★ 该文件的全部**顶层/嵌套** `def` 名（★ AST）。"""
    tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"))
    return {n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)}


def _docstring(path: Path, funcname: str):
    """★ 按**函数名**取 docstring；★ 找不到 ⇒ `None`（★ 调用方必须**显式判红**，不许静默降级）。"""
    tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"))
    for n in ast.walk(tree):
        if isinstance(n, ast.FunctionDef) and n.name == funcname:
            return ast.get_docstring(n, clean=False) or ""
    return None


def _how_to_switch(ds):
    """★ 取「该怎么换」段：★ 从标记起到下一个「前置」标记（★ 缺任一标记 ⇒ `None`，**不静默降级**）。"""
    if ds is None:
        return None
    i = ds.find("该怎么换")
    if i == -1:
        return None
    j = ds.find("前置", i)
    seg = ds[i: j if j != -1 else len(ds)]
    return seg or None


def _failures(asm_seg, doc_seg, doc_ds, asm_names) -> list:
    """★ 纯函数（★ 判据必须能在合成输入上红）：返回**问题清单**（空 = 通过）。"""
    bad: list = []
    for label, seg in (("sw_assembly.py", asm_seg), ("sw_assembly_doc.py", doc_seg)):
        if not seg:
            bad.append("★ %s：取不到「该怎么换」段（★ 标记丢了 ⇒ 不静默降级成 0）" % label)
            continue
        if not any(q in seg for q in CONCENTRIC_QUALIFIERS):
            bad.append("★ %s：丢了**偏心同心**限定词" % label)
        if not any(q in seg for q in DISTANCE_QUALIFIERS):
            bad.append("★ %s：丢了**圆柱面距离**限定词" % label)
        if not any(q in seg for q in MATE_TYPE_INSUFFICIENT):
            bad.append("★ %s：没表态「一个 `mate_type` 定不下来」" % label)
    if doc_ds is None or REAL_CALLER not in doc_ds:
        bad.append("★ `sw_assembly_doc.py::add_mate` 没写出真调用方 `%s`" % REAL_CALLER)
    if REAL_CALLER not in asm_names:
        bad.append("★ `sw_assembly.py` 里没有 `%s`（★ 前提不成立）" % REAL_CALLER)
    if PHANTOM_CALLER in asm_names:
        bad.append("★ `sw_assembly.py` 里**居然**有 `%s`（★ 241 核心事实五被推翻 ⇒ 本判据要重看）"
                   % PHANTOM_CALLER)
    return bad


# ── ① ★★ **锚点**：官方两页真的写了**前置**（★ 判据的期望值锚回原文） ──
def test_official_successor_pages_state_their_preconditions():
    """★★★ **前提断言**（★ 铁律 6：锚回**官方原文**，不比对测试里手抄的常量）✓

    ★ `AddConcentricMateWithTolerance.md` 逐字：「A **parent** non-misaligned (i.e., **standard**)
      concentric mate **must already exist**」+ 「**NOTE:** The typical way to add a standard
      concentric mate is to use [[IAssemblyDoc::**AddMate5**]]」
      ⇒ ★★★ **那是循环引用**（`AddMate5.md` 说偏心同心走它，它说标准同心走 `AddMate5`）
      ⇒ ★★ **后继不是 drop-in 替换**。
    ★ `AddDistanceMate.md` 逐字：`FirstArcCondition`/`SecondArcCondition`「valid only for
      **cylindrical** distance mates」+ 「the selections must be two **cylindrical faces** or one
      cylindrical face and one axis」⇒ ★★ **柱面距离是硬前置**。
    """
    if not (OFF_MATE5.is_file() and OFF_CONC.is_file() and OFF_DIST.is_file()):
        return                                                       # ★ 官方源不在本机 ⇒ 跳过（★ 缺数据源 ≠ 检查失败）
    t5 = OFF_MATE5.read_text(encoding="utf-8", errors="replace")
    assert "Obsolete" in t5 and "CreateMate" in t5, "★ 废弃链变了 ⇒ 判据要重看"
    for name in ("AddConcentricMateWithTolerance", "AddDistanceMate"):
        assert name in t5, "★ 官方 Remarks 里的分流 `%s` 不见了" % name

    tc = OFF_CONC.read_text(encoding="utf-8", errors="replace")
    for token in ("parent", "standard", "must already exist", "AddMate5"):
        assert token in tc, "★ `AddConcentricMateWithTolerance.md` 少了 `%s` ⇒ 前置断言失效" % token

    td = OFF_DIST.read_text(encoding="utf-8", errors="replace")
    for token in ("cylindrical", "cylindrical faces"):
        assert token in td, "★ `AddDistanceMate.md` 少了 `%s` ⇒ 柱面前置断言失效" % token


# ── ② ★★★ **核心**：两处「该怎么换」必须保留官方限定词 ────────────────
def test_how_to_switch_keeps_the_official_qualifiers():
    """★★★ 官方限定词**不得丢**：★ 是 **偏心的**同心 / **圆柱面的**距离，★ 不是"同心 / 距离"。

    ★ 为什么这是真判据：★ 丢了限定词 ⇒ 下一轮会**按 `mate_type` 一把梭** ⇒
      ★★ **普通（对齐的）同心配合**与**平面距离配合**被误路由到
      `AddConcentricMateWithTolerance` / `AddDistanceMate` —— ★ 而官方要求它们走 `CreateMate`。
    """
    asm_seg = _how_to_switch(_docstring(ASM, "add_mate5_checked"))
    doc_seg = _how_to_switch(_docstring(DOC, "add_mate"))
    for label, seg in (("sw_assembly.py", asm_seg), ("sw_assembly_doc.py", doc_seg)):
        assert seg, "★ %s：取不到「该怎么换」段（★ 不静默降级）" % label
        assert any(q in seg for q in CONCENTRIC_QUALIFIERS), \
            "★ %s：「该怎么换」丢了**偏心同心**限定词" % label
        assert any(q in seg for q in DISTANCE_QUALIFIERS), \
            "★ %s：「该怎么换」丢了**圆柱面距离**限定词" % label


# ── ③ ★★★ **核心**：必须表态「一个 `mate_type` 定不下来」 ─────────────
def test_how_to_switch_says_mate_type_alone_cannot_decide():
    """★★★ **未表态即红**（★ 铁律 3）：★ 241 核心事实四已证 ——
    ★ `swMateDISTANCE` 既可能**平面距离**（⇒ `CreateMate`）也可能**柱面距离**（⇒ `AddDistanceMate`）
    ⇒ ★★ **一个 `mate_type` 定不下来**（★ 还要看**选中实体的几何**）。

    ★★ 所以「该怎么换」里**必须**有这句表态；★ 只写"按 `mate_type` 分流"= **把错的规矩留给下一轮**。
    """
    asm_seg = _how_to_switch(_docstring(ASM, "add_mate5_checked"))
    doc_seg = _how_to_switch(_docstring(DOC, "add_mate"))
    for label, seg in (("sw_assembly.py", asm_seg), ("sw_assembly_doc.py", doc_seg)):
        assert seg, "★ %s：取不到「该怎么换」段" % label
        assert any(t in seg for t in MATE_TYPE_INSUFFICIENT), \
            "★ %s：「该怎么换」没表态「一个 `mate_type` 定不下来」⇒ 与 241 核心事实四矛盾" % label


# ── ④ ★★★ **核心**：`sw_assembly_doc.py` 必须写出**真调用方** ─────────
def test_doc_site_names_the_real_caller():
    """★★★ 241 核心事实五：★ `scripts/sw_assembly.py` 里**没有** `add_mate`
    （★ 真名 `add_mate5_checked(asm_model, mate_type, …)`）。

    ★★ 所以 `sw_assembly_doc.py::add_mate` 的「该怎么换」**不得**指向一个**不存在的函数** ——
      ★ 那正是「交接单前提**第十次**被推翻」的成因；★ 本轮把它**钉死**。
    """
    assert REAL_CALLER in _func_names(ASM), "★ `sw_assembly.py` 里没有 `%s`" % REAL_CALLER
    assert PHANTOM_CALLER not in _func_names(ASM), \
        "★ `sw_assembly.py` 里**居然**有 `%s`（★ 241 核心事实五被推翻）" % PHANTOM_CALLER
    ds = _docstring(DOC, "add_mate")
    assert ds is not None, "★ 取不到 `sw_assembly_doc.py::add_mate` 的 docstring"
    assert REAL_CALLER in ds, "★ `sw_assembly_doc.py` 没写出真调用方 `%s`" % REAL_CALLER


# ── ⑤ ★★ **边界冻结**：本轮**只订正记档、不动路由** ─────────────────
def test_routing_is_frozen_this_round():
    """★★ **边界冻结**（★ 「断言"不加什么"必须不命中」）：★ 两处**仍然**调 `AddMate5`。

    ★★ 为什么必须有这条：★ 本轮是**文档订正**、★ 不是换路由（★ 换它**必须真机验** · 铁律 2）⇒
      ★ 若有人借"修文档"之名**顺手换掉路由** ⇒ ★ **本判据当场红**。
    """
    asm_src = "\n".join(l for l in ASM.read_text(encoding="utf-8", errors="replace").splitlines()
                        if not l.lstrip().startswith("#"))
    assert ".AddMate5(" in asm_src, "★ `sw_assembly.py` 的 `AddMate5` 调用没了（★ 本轮不该动路由）"
    doc_src = DOC.read_text(encoding="utf-8", errors="replace")
    assert '"AddMate5"' in doc_src, "★ `sw_assembly_doc.py` 的 `AddMate5` 直传没了（★ 本轮不该动路由）"


# ── ⑥ ★★ 判据必须能红（★ 纯函数合成负例） ───────────────────────────
def test_pure_function_is_red_able():
    """★ 六组负例：① 段取不到；② 丢偏心限定词；③ 丢柱面限定词；④ 缺「定不下来」表态；
    ⑤ 没写 `add_mate5_checked`；⑥ 前提被推翻（`sw_assembly.py` 冒出 `add_mate`）。"""
    good_seg = "该怎么换：偏心同心 ⇒ A · 圆柱面距离 ⇒ B · 一个 `mate_type` 定不下来"
    good_ds = "…调用方是 `%s`…" % REAL_CALLER
    good_names = {"add_mate5_checked"}
    assert not _failures(good_seg, good_seg, good_ds, good_names), "正常读数被判红 ⇒ 判据过严"
    assert _failures(None, good_seg, good_ds, good_names), "段取不到却未判出"
    assert _failures("该怎么换：同心 ⇒ A", good_seg, good_ds, good_names), "丢偏心限定词却未判出"
    assert _failures("该怎么换：偏心同心 ⇒ A", good_seg, good_ds, good_names), "丢柱面限定词却未判出"
    assert _failures("该怎么换：偏心同心 ⇒ A · 圆柱面距离 ⇒ B", good_seg, good_ds, good_names), \
        "缺「定不下来」表态却未判出"
    assert _failures(good_seg, good_seg, "…没写真调用方…", good_names), "没写 `add_mate5_checked` 却未判出"
    assert _failures(good_seg, good_seg, good_ds, {"add_mate"}), "前提被推翻却未判出"
