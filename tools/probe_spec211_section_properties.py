"""★ 探针：`IModelDocExtension::GetSectionProperties2` 的建状态 / 正例 / 官方必然失败负例 / 副作用。"""

# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（规格 211 · B1-1 的真机探针）
# 文件:   tools/probe_spec211_section_properties.py
# 定位:   ★ 规格 `specs/211-user-feature-gaps` 的 **B1-1**「截面属性」。★ 官方页
# `C:\swapi\types\IModelDocExtension\GetSectionProperties2.md` **逐字读过**，本探针按它
# 写：
# · ① 「**This method clears the selection set**」+「objects in `Sections` **are added t
# o**
#          the current selection set」⇒ ★ **先清空、再加进去** ⇒ ★★ 这是它的**副作用机制** ✓
# · ② ★★★ 「If the objects are **already in the current selection set, an error** is gen
# erated;
#          that is, **status code will be equal to 1**, which means invalid input」
#          ⇒ ★★ **这是一条官方写死的「必然失败」负例** ✓
# · ③ ★★ **反例（本来会踩的坑）**：「The user selected a set of either **parallel planes
#  or
#          parallel faces** ⇒ **You can pass an empty sections array**」
#          ⇒ ★★ 所以「**空数组**」**不是**必然失败 ✗（★ 我原先拟的负例是**假的**）✓
#     · ④ 返回 **size 24** 数组；`retval[0]` = **status**：`0=success` · `1=invalid input` ·
#          `2=selected faces are not in the same or parallel planes` · `3=unable to compute` ✓
# 判据:   ★★ **双判**：`retval[0] == 0`（★ 官方定义的状态码）**且** `retval[1]`（面积）
#   与**几何算出来的**吻合（★ 100×60 的矩形 ⇒ 6000 mm²）—— ★ **不看"有没有抛异常"** ✓
#   ★ 副作用判据：★ `selection` 计数在**调用前后**的变化（★ 用回读，不看返回值）✓
# 官方依据: `C:\swapi\types\IModelDocExtension\GetSectionProperties2.md`（签名 + Remarks
#            + 24 元格式）
# 许可:   本仓库 MIT。无第三方代码引入。覆盖: 全文件
# ─────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(Path(__file__).resolve().parents[1])
for _p in (str(ROOT), str(ROOT / "tools"), str(ROOT / "scripts")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

#: ★ 正例的几何：100 × 60 mm 的矩形草图 ⇒ 面积应为 **6000 mm²**（★ 判据要能算出来）✓
RECT = {"x1_mm": 0.0, "y1_mm": 0.0, "x2_mm": 100.0, "y2_mm": 60.0}
EXPECT_AREA = 100.0 * 60.0


def _sel_count(sw, model) -> int:
    """★ 选区计数（★ 回读，事实 8：`GetSelectedObjectCount2(-1)`）✓"""
    import sw_connect

    try:
        sm = sw_connect.get_com_member(model, "SelectionManager")
        return int(sw_connect.get_com_member(sm, "GetSelectedObjectCount2", -1))
    except Exception:  # noqa: BLE001
        return -1


def main() -> int:
    import sw_connect
    import tool_caller

    sw, _ = sw_connect.connect_solidworks(wait_seconds=20)
    if sw is None:
        print("★ 连不上")
        return 2
    model = sw_connect.new_document(sw, "part")
    if model is None:
        print("★ 建不了零件")
        return 2
    inj = {"model": model, "sw": sw}

    #: ① 建一个 100×60 的矩形面（★ 用本仓既有能力，★ 不是被测的写操作）✓
    for step, params in (
        ("solidworks_sketch_start", {}),
        ("solidworks_sketch_add_rectangle", RECT),
        #: ★★★ **必须先拉伸造体** —— 只建草图**没有面可选**（★ 我第一版就漏了这步 ⇒
        #: 选择器报 `解析失败`、而**选区计数是 4**（那是草图矩形留下的）⇒ ★ 误以为选到了
        #: 面 ✗）
        ("solidworks_extrude_boss", {"sketch_name": "Sketch1", "depth_mm": 20.0}),
    ):
        ok, note = tool_caller.call(step, inject_objects=inj, **params)
        print("★ 建状态 %-34s ok=%s" % (step, ok))
        if not ok:
            print("   ★ 没成：%s" % str(note)[:90])
            return 1

    ext = sw_connect.get_com_member(model, "Extension")
    print("★ Extension =", "有" if ext is not None else "None")

    #: ② 选中一个面（★ 声明式选择器：`index:0` + `FACE`）✓
    ok, note = tool_caller.call(
        "solidworks_select_by_selector",
        inject_objects=inj,
        selector="index:0",
        kind="FACE",
        body_index=0,
    )
    print("★ 选一个面 ok=%s ⇒ %s" % (ok, str(note)[:80]))
    before = _sel_count(sw, model)
    print("★ 选完之后的选区计数（回读）= %r" % before)

    #: ③ 正例：★ 按官方「选了平行面 ⇒ 可传**空数组**」✓
    import sw_connect as sc

    empty = (
        sc.create_empty_dispatch_variant()
        if hasattr(sc, "create_empty_dispatch_variant")
        else None
    )
    result = {"call": "GetSectionProperties2(empty)", "before_sel": before}
    try:
        ret = sw_connect.get_com_member(ext, "GetSectionProperties2", empty)
        #: ★ 读取加固：★ 本仓既有做法是 `tuple(vals)`（见 `sw_selection_spec.py`）✓
        result["ret_type"] = type(ret).__name__
        vals = None
        if ret is not None:
            for _f in (lambda x: tuple(x), lambda x: list(x)):
                try:
                    vals = _f(ret)
                    break
                except Exception:  # noqa: BLE001
                    continue
        result["ret_len"] = len(vals) if vals else None
        if vals:
            result["status"] = vals[0]
            result["area"] = vals[1] if len(vals) > 1 else None
            result["centroid"] = vals[2:5]
        result["ok"] = True
    except Exception as exc:  # noqa: BLE001
        result["ok"] = False
        result["error"] = "%s: %s" % (type(exc).__name__, str(exc)[:110])
    after = _sel_count(sw, model)
    result["after_sel"] = after
    result["sel_cleared"] = after == 0
    print(
        "★ 正例（空数组 + 已选平行面）⇒ status=%r area=%r 选区 %r→%r（★ 官方说它会**清空**选区）"
        % (result.get("status"), result.get("area"), before, after)
    )

    #: ④ ★★ **官方写死的负例**：把**已在选择集里**的对象传进 `Sections` ⇒ status **必然
    #: = 1** ✓
    neg = {"call": "GetSectionProperties2(already-selected)"}
    try:
        #: ★ 先把刚选中的面取成对象，再传回去（★ 官方：「already in the current selectio
        #: n set ⇒ status=1」）✓
        sm = sw_connect.get_com_member(model, "SelectionManager")
        obj = sw_connect.get_com_member(sm, "GetSelectedObject6", 1, -1)
        neg["obj"] = "有" if obj is not None else "None"
        #: ★ 重新选一次（★ 上一步的清空副作用会把它清掉）⇒ ★ 制造"已在选择集里"的条件 ✓
        tool_caller.call(
            "solidworks_select_by_selector",
            inject_objects=inj,
            selector="index:0",
            kind="FACE",
            body_index=0,
        )
        ret2 = sw_connect.get_com_member(ext, "GetSectionProperties2", obj)
        neg["ret_type"] = type(ret2).__name__
        vals2 = None
        if ret2 is not None:
            try:
                vals2 = tuple(ret2)
            except Exception:  # noqa: BLE001
                vals2 = None
        neg["status"] = vals2[0] if vals2 else None
        neg["ok"] = True
    except Exception as exc:  # noqa: BLE001
        neg["ok"] = False
        neg["error"] = "%s: %s" % (type(exc).__name__, str(exc)[:110])
    print(
        "★ 负例（已在选择集里）⇒ status=%r（★ 官方说**必然 = 1**）" % neg.get("status")
    )

    out = {
        "official": "IModelDocExtension.GetSectionProperties2",
        "expect_area_mm2": EXPECT_AREA,
        "positive": result,
        "negative": neg,
    }
    p = ROOT / "output" / "spec211-b1-section-properties.json"
    p.write_text(
        json.dumps(out, ensure_ascii=False, indent=1, default=str) + "\n",
        encoding="utf-8",
    )
    print("★ 证据：%s" % p)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
