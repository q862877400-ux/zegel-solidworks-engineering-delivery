"""★ 探针：`InsertWeldmentTrimFeature2` —— ★ 先"查行为" + ★★ 两个数组形参的**形态判定**。"""
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（规格 211 · B3-1 的真机探针）
# 文件:   tools/probe_spec211_weldtrim.py
# 定位:   ★ 规格 `specs/211-user-feature-gaps` 的 **B3-1**「裁剪/延伸焊件」。
#   ★ 官方页三样已读（★ `C:\swapi\types\IFeatureManager\InsertWeldmentTrimFeature2.md`）✓：
#     `Feature InsertWeldmentTrimFeature2( int EndCond, int Options, double GapValue,
#      object BodiesToTrim, object BodiesOrFaces )`
#     ★★ `## Remarks` **给了完整 mark 表**：★ **1 = Body or bodies to trim** ·
#       ★ **2 = Trimming boundaries (body or face)** ✓
# 判据:   ★★★ **两步，★ 与"扫描曲面"那条路同型**（★ 那是成功案例，★ 照它走 ✓）：
#     ★ **第一步（本探针）＝ 只"查行为"** —— ★ 不建复杂几何（★ 焊件体要 `create_structural_member`，
#       ★ 那本身有前置）⇒ ★★ **先量它的三种行为**：
#       · ★ **抛异常** ⇒ 记下来（★ 形态被拒 ✓）
#       · ★ **静默回 `None`** ⇒ ★★ **但这**还不算试死**（★ 因为前置没上 ✓ ——
#         ★★ 这条是扫描曲面那轮定下的**定则**：★「读到静默」≠「判定试死」✓）
#       · ★ **建成** ⇒ ★ 大发现 ✓
#     ★★ **另做一件本探针特有的事：两个 `object` 数组形参的形态判定** ✓
#       —— ★ 它是 `System.object`（★ 不是 `System.object[]`）⇒
#         ★ 按**事实 12 / 33**：★ **空数组不能传 Python `None`** ✗ ⇒
#         ★★ 故本探针**两种形态都试**：★ ① 传 `None` · ② 传**空 `VARIANT(VT_DISPATCH, None)`** ✓
#         ★ 并**分开记**（★ 哪个形态不报"类型不匹配"⇒ 那就是对的形态 ✓）
# 官方依据: `C:\swapi\types\IFeatureManager\InsertWeldmentTrimFeature2.md`（签名 + Param
#           eters + Remarks）
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


def _classify(rep: dict) -> str:
    if rep.get("ok"):
        return "★★★★ **建成** ⇒ ★ 大发现 ✓"
    if rep.get("returned_is_none"):
        err = str(rep.get("error") or "")
        if "类型不匹配" in err or "0x80028CA0" in err:
            return "★★ **类型不匹配**（★ `0x80028CA0`）⇒ ★★ **数组形参的形态不对** ✗"
        return ("★★ **静默回 `None`** ⇒ ★ **但还不算试死**（★ 前置没上 —— "
                "★ 定则：「读到静默」≠「判定试死」）✓")
    err = str(rep.get("error") or "")
    if err.startswith(("TypeError", "com_error", "AttributeError", "RuntimeError")):
        return "★★ **抛异常** ⇒ ★ %s" % err[:110]
    return "★ 其它：%s" % err[:110]


def main() -> int:
    import sw_connect
    import sw_weldment as W

    out: dict = {"official": "IFeatureManager.InsertWeldmentTrimFeature2",
                 "step": "第一步：只查行为 + 数组形参的形态判定",
                 "marks": dict(W.WELDMENT_TRIM_MARKS)}

    sw, _ = sw_connect.connect_solidworks(wait_seconds=20)
    if sw is None:
        print("★ 连不上")
        return 2
    model = sw_connect.new_document(sw, "part")
    if model is None:
        print("★ 建不了零件")
        return 2

    #: ★ ① 库层包装（★ 它内部传 `None` ✓）
    rep_none = W.insert_weldment_trim_report(model, gap_mm=0.0)
    out["form_A_none"] = {k: rep_none.get(k) for k in
                          ("ok", "returned_is_none", "selection_count_before",
                           "feature_count_before", "feature_count_after", "error")}
    out["form_A_verdict"] = _classify(rep_none)
    print("★ 形态 ①（库层传 `None`）⇒ %s" % out["form_A_verdict"])

    #: ★ ② **绕开库层**、直接传**空 VARIANT**（★ 事实 12/33 的形态 ✓）
    form_b: dict = {}
    try:
        empty = sw_connect.create_empty_dispatch_variant()
        fm = sw_connect.get_com_member(model, "FeatureManager")
        feat = sw_connect.get_com_member(fm, "InsertWeldmentTrimFeature2",
                                         0, 0, 0.0, empty, empty)
        form_b = {"ok": True, "returned_is_none": feat is None,
                  "returned_name": getattr(feat, "Name", None) if feat is not None else None}
        form_b["verdict"] = ("★ 调用完成、★ 回 `%s`" % ("None" if feat is None else "对象"))
    except Exception as exc:                                            # noqa: BLE001
        form_b = {"ok": False, "error": "%s: %s" % (type(exc).__name__, str(exc)[:150]),
                  "verdict": "★★ 抛 ⇒ 空 VARIANT 这个形态也不成"}
    out["form_B_empty_variant"] = form_b
    print("★ 形态 ②（空 VARIANT）⇒ %s" % form_b.get("verdict"))

    p = ROOT / "output" / "spec211-b3-weldtrim.json"
    p.write_text(json.dumps(out, ensure_ascii=False, indent=1, default=str) + "\n", encoding="utf-8")
    print("★ 证据：%s" % p)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
