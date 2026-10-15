"""★ spec 274：真机实测 —— **`Double&` 出参不吃 by-ref VARIANT**（`out_double` 的假设被证伪）。"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   D:/AI/SW
# 文件:   output/_probe274_double_out.txt（★ 真机读数原文）
#         scripts/sw_connect.py:513-568（`out_i4` / `out_dispatch` ⇒ ★ **真机验证通过**）
#         scripts/sw_sensor.py:39-48（`out_double` / `out_bstr` ⇒ ★ 注释自认「形态照 `out_i4` 的结论」= **类推**）
# 定位:   ★ 273 量出 12 条里 **6 个 `Double&`** ⇒ ★ 接线前必须先知道 `Double&` 该怎么传 —— ★ 本轮真机量了。
# 官方依据: 反射转储 `IBody2.GetExtremePoint(Double, Double, Double, Double&, Double&, Double&)` ·
#         `IModelDocExtension.GetWhatsWrong(Object&, Object&, Object&)`
# 许可:   本仓自产（无外部来源）
# 覆盖:   只读；★ 不改任何文件（★ 真机读数由 `output/_probe274_double_out.py` 产出）
# ────────────────────────────────────────────────────────────────────
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
for _p in (str(ROOT), str(SCRIPTS)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

#: ★★★ **真机读数**（SolidWorks **34.4.1** · ★ 只读打开 `output/fixtures/刀柄_Holder.sldprt`）。
#:   ★ 每个方法是 `{形态: 是否通过}`；★ 通过 = 调用返回且不抛。
DOUBLE_OUT_FORMS = {          #: `IBody2::GetExtremePoint(Double, Double, Double, Double&, Double&, Double&)`
    "by-ref VARIANT": False,  #: ★ `TypeError: float() argument must be … not 'VARIANT'`
    "bare value": True,       #: ★ 裸 `0.0` ⇒ `ret=(True, 0.0275, 0.0, 0.0)`（★ 出参**随返回元组回来**）
    "omitted": True,          #: ★ 省略 ⇒ 同上
}
OBJECT_OUT_FORMS = {          #: `IModelDocExtension::GetWhatsWrong(Object&, Object&, Object&)`
    "by-ref VARIANT": True,   #: ★ 通过（★ 与 253 一致）
    "bare value": False,      #: ★ `DISP_E_TYPEMISMATCH`（-2147352571）
    "omitted": False,         #: ★ `DISP_E_PARAMNOTOPTIONAL`（-2147352561）
}
#: ★★ **每个形态的实测错误码/返回**（★ 让判据能报出「因为什么」）。
DOUBLE_OUT_DETAIL = {"by-ref VARIANT": "TypeError", "bare value": "(True, 0.0275, 0.0, 0.0)",
                     "omitted": "(True, 0.0275, 0.0, 0.0)"}
OBJECT_OUT_DETAIL = {"by-ref VARIANT": "ret=True", "bare value": "-2147352571 类型不匹配",
                     "omitted": "-2147352561 非选择性的参数"}

#: ★★ 仓库里 4 个 out 包装器的**形态**（★ 判据会**回源码核**，★ 不靠这里手抄）。
HELPERS = {
    "out_i4": ("sw_connect.py", "VT_I4"),
    "out_dispatch": ("sw_connect.py", "VT_DISPATCH"),
    "out_double": ("sw_sensor.py", "VT_R8"),
    "out_bstr": ("sw_sensor.py", "VT_BSTR"),
}
#: ★★★ **哪些包装器有真机证据**（★ `out_i4`/`out_dispatch` 有逐形态实测；
#:   ★★ **`out_double` 的证据在 287 找到**：★ `ICWMesh::GetDefaultElementSizeAndTolerance`
#:   的 `ByRef … As Double` 在 **2026-10-01 真机实测取回了值**（★ 见 `tests/test_double_out_cosworks_positive.py`））。
VERIFIED_ON_MACHINE = {"out_i4": True, "out_dispatch": True, "out_double": True, "out_bstr": False}
#: ★★★ **形态「按接口族分」的那些**（★ 287 精炼）：★ `Double&` **没有唯一形态** ——
#:   ★ cosworks（无类型信息）⇒ `VT_BYREF | VT_R8` ✓ · ★ sldworks.tlb（有类型信息）⇒ **裸值** ✓
#:   ⇒ ★★ **两张表都对**（★ 274 的「两表不同」结论**仍然成立**）。
INTERFACE_DEPENDENT_BY_287 = {"out_double"}


def _helper_variant(path: Path, fn: str, vt: str) -> bool:
    """★ 回源码核：`fn` 的返回式里**同时**有 `VT_BYREF` 与 `vt`（★ 不靠手抄）。"""
    src = path.read_text(encoding="utf-8")
    m = re.search(r"def %s\(.*?\n(.*?)(?=\ndef |\n#:|\Z)" % re.escape(fn), src, re.S)
    if not m:
        return False
    body = m.group(1)
    return ("VT_BYREF" in body) and (vt in body)


def _failures(double_forms, object_forms, helpers, verified, interface_dependent) -> list[str]:
    """★ 纯函数：① 两表必须**不同**；② 各表至少一种形态通；③ 登记自洽；④ 检查量非 0。"""
    bad: list[str] = []
    if double_forms == object_forms:
        bad.append("`Double&` 与 `Object&` 的形态表**相同** ⇒ 一刀切 ⇒ 与真机读数不符")
    for label, table in (("Double&", double_forms), ("Object&", object_forms)):
        if not any(table.values()):
            bad.append("%s 表里**没有**任何通过的形态 ⇒ 读数不可信" % label)
    if not interface_dependent:
        bad.append("`INTERFACE_DEPENDENT_BY_287` 为空 ⇒ 检查量为 0 ⇒ 不许通过")
    for name in sorted(interface_dependent):
        if name not in helpers:
            bad.append("登记了不存在的包装器 %r" % name)
        if not verified.get(name):
            bad.append("★ 形态「按接口族分」的 %r 应**有**真机证据（★ 287 已找到）" % name)
    if not helpers:
        bad.append("`HELPERS` 为空 ⇒ 检查量为 0")
    return bad


# ── ① ★★★ `Double&` **不吃** by-ref VARIANT ──────────────────────────
def test_double_out_does_not_take_a_byref_variant():
    """★★★ 真机（34.4.1）：`IBody2::GetExtremePoint` 的 3 个 `Double&` ⇒ by-ref VARIANT **抛 `TypeError`**；
    裸值 / 省略**通过**，★ 且出参**随返回元组回来**。
    """
    assert DOUBLE_OUT_FORMS["by-ref VARIANT"] is False, "★ 真机读数变了？"
    assert DOUBLE_OUT_FORMS["bare value"] is True
    assert DOUBLE_OUT_FORMS["omitted"] is True
    assert DOUBLE_OUT_DETAIL["bare value"].startswith("(True,"), "★ 出参应从返回元组取"


# ── ② ★★ `Object&` **必须** by-ref VARIANT（对照 253）────────────────
def test_object_out_takes_a_byref_variant():
    """★★ 真机（34.4.1）：`GetWhatsWrong` 的 3 个 `Object&` ⇒ **只有** by-ref VARIANT 通过；
    裸值 ⇒ `DISP_E_TYPEMISMATCH`；省略 ⇒ `DISP_E_PARAMNOTOPTIONAL`。
    """
    assert OBJECT_OUT_FORMS["by-ref VARIANT"] is True
    assert OBJECT_OUT_FORMS["bare value"] is False
    assert OBJECT_OUT_FORMS["omitted"] is False


# ── ③ ★★★ 两张表**必须不同** ⇒ 不能一刀切 ────────────────────────────
def test_two_tables_must_differ():
    """★★★ **本轮最值钱的一条**：★ `Double&` 与 `Object&` 的可用形态**正好相反**
    ⇒ ★★ **「出参一律 by-ref VARIANT」是错的** —— ★ 传法取决于**该形参怎么声明**。
    """
    assert DOUBLE_OUT_FORMS != OBJECT_OUT_FORMS, "两表相同 ⇒ 一刀切 ⇒ 空判据"


# ── ④ ★★★ 4 个包装器的形态**回源码核** + ★ **形态「按接口族分」的那些必须登记** ─────
def test_helper_forms_and_registered_risk():
    """★★★ 回源码核 4 个包装器的形态；★ 并断言 `out_double` **已登记为「按接口族分」**且**有**真机证据
    （★ 287 在 `ICWMesh::GetDefaultElementSizeAndTolerance` 上找到了 cosworks 的正例）。
    """
    for fn, (fname, vt) in sorted(HELPERS.items()):
        assert _helper_variant(SCRIPTS / fname, fn, vt), \
            "%s 的形态里找不到 `VT_BYREF` + `%s`（★ 回源码核失败）" % (fn, vt)
    assert VERIFIED_ON_MACHINE["out_double"], "★ 287 已在 cosworks 上找到 `Double&` 的正例"
    assert not VERIFIED_ON_MACHINE["out_bstr"], "★ `out_bstr` 至今**无**真机证据"
    assert VERIFIED_ON_MACHINE["out_i4"] and VERIFIED_ON_MACHINE["out_dispatch"], \
        "★ 这两个是逐形态实测过的 ⇒ 不该被标成未验"
    assert INTERFACE_DEPENDENT_BY_287 == {"out_double"}, "★ 287 精炼的是 `out_double`"


# ── ⑤ ★★ 判据必须能红 ───────────────────────────────────────────────
def test_pure_function_is_red_able():
    """★ 六组负例：① 两表合并；② 某表全 False；③ 接口相关表清空；
    ④ 登记了不存在的包装器；⑤ 接口相关的那个**没有**真机证据。"""
    assert not _failures(DOUBLE_OUT_FORMS, OBJECT_OUT_FORMS, HELPERS,
                         VERIFIED_ON_MACHINE, INTERFACE_DEPENDENT_BY_287), "正常读数被判红 ⇒ 判据过严"
    assert _failures(DOUBLE_OUT_FORMS, dict(DOUBLE_OUT_FORMS), HELPERS,
                     VERIFIED_ON_MACHINE, INTERFACE_DEPENDENT_BY_287), "两表相同却未判出 ⇒ 空判据"
    assert _failures({"a": False}, OBJECT_OUT_FORMS, HELPERS,
                     VERIFIED_ON_MACHINE, INTERFACE_DEPENDENT_BY_287), "全 False 却未判出 ⇒ 空判据"
    assert _failures(DOUBLE_OUT_FORMS, OBJECT_OUT_FORMS, HELPERS,
                     VERIFIED_ON_MACHINE, set()), "接口相关表清空却未判出 ⇒ 空判据"
    assert _failures(DOUBLE_OUT_FORMS, OBJECT_OUT_FORMS, HELPERS,
                     VERIFIED_ON_MACHINE, {"不存在的包装器"}), "登记了不存在的包装器却未判出"
    assert _failures(DOUBLE_OUT_FORMS, OBJECT_OUT_FORMS, HELPERS,
                     dict(VERIFIED_ON_MACHINE, out_double=False),
                     INTERFACE_DEPENDENT_BY_287), "接口相关的那个没真机证据却未判出"
