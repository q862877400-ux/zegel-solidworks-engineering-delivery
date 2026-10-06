"""★ 真机：unfold 的**选择契约**（固定面 mark 1 + 折弯 mark 4）—— 判据是**逐条回读 mark**。"""
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（工具）
# 文件:   tools/probe_spec209_unfold_contract.py
# 定位:   ★ 规格 `specs/209-union-adopt-18/` 的 **B2-1（idx 336 unfold）**：裁决书逐字要求
#   「官方**没给 mark** ⇒ 必须先真机定出"可建对象"，**且前置判据用回读**
#    `GetSelectedObjectCount2(-1)`（事实 8），**不许信返回值**」✓
#   ★★ 本探针**只验"选择契约"**（能不能把 mark 摆对），**不假装验了"特征建成"** ——
#     因为正面案例的前置（**带折弯的钣金件**）在本机拿不到（见 hem 那两轮的负结论）。
#   ★ 判据：① 选区计数 == 1 + 折弯条数；② 第 1 条 mark == **1**；③ 其余每条 mark == **4**
#     —— ★ **三条全是 `ISelectionMgr::GetSelectedObjectMark` 的回读值** ✓
# 官方依据: `C:\swapi\examples\Insert_and_Access_Fold_Feature_Example_VB.md`（★ mark 的唯一出处）·
#   `C:\swapi\types\ISelectionMgr\{SetSelectedObjectMark,GetSelectedObjectMark}.md` ·
#   `C:\swapi\enums\swSelectionMarkAction_e.md`（★ 第 3 参 = `swSelectionMarkSet`(0)）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────────

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

R = Path(r"D:\AI\SW")
sys.path.insert(0, str(R / "scripts"))
OUT = R / "output" / "spec209-unfold-contract.json"


def main() -> int:
    import sw_connect
    import sw_part as P
    import sw_sheet_metal as SM
    from sw_connect import safe_get_com_member

    sw, _ = sw_connect.connect_solidworks(wait_seconds=30)
    ev = {"at": time.strftime("%Y-%m-%dT%H:%M:%S"),
          "_": "unfold 的选择契约（★ 回读 mark；★ 不假装验了特征建成）",
          "judge": "GetSelectedObjectMark 的逐条回读 + 选区计数"}
    opened = []

    def _close(doc):
        try:
            t = str(safe_get_com_member(doc, "GetTitle") or "")
            if t:
                sw.CloseDoc(t)
        except Exception:                                      # noqa: BLE001
            pass

    doc = sw_connect.new_document(sw, "part")
    opened.append(doc)
    with P.sketch(doc, "Front Plane") as sk:
        P.sketch_corner_rectangle(doc, -30.0, -20.0, 30.0, 20.0)
    #: ★ 用**真厚度（2 mm = 文档单位）** —— 见 `probe_spec209_hem_units.py` 的单位定案
    SM.create_base_flange(doc, sk, SM.BaseFlangeSpec(thickness=2.0, bend_radius=1.0, depth=50.0))
    names = [str(safe_get_com_member(f, "Name") or "") for f in SM.iter_features(doc)]
    ev["feature_names"] = names
    #: ★ 拿一个**真实存在的特征名**当"折弯"—— ★ 本格**只验选择契约**，不声称它是折弯 ✓
    fake_bend = "基体-法兰1" if "基体-法兰1" in names else (names[-1] if names else "")
    ev["bend_feature_name_used"] = fake_bend
    r = SM.create_unfold(doc, [fake_bend], face_index=0)
    ev["selection"] = r.get("selection")
    ev["tree"] = [r.get("tree_before"), r.get("tree_after")]
    ev["new_features"] = r.get("new_features")
    ev["flat_pattern_count"] = [r.get("flat_pattern_count_before"),
                                r.get("flat_pattern_count_after")]
    ev["feature_built"] = bool(r.get("ok"))
    ev["error"] = r.get("error")
    c = r.get("selection") or {}
    ev["★_contract_verdict"] = (
        "★ 选择契约**成立**（计数 %r · mark 逐条 %r）" % (c.get("total_count"),
                                                       c.get("marks_readback"))
        if c.get("contract_ok") else
        "★ 选择契约**不成立**（计数 %r · mark %r · errors %r）"
        % (c.get("total_count"), c.get("marks_readback"), c.get("errors")))
    ev["★_feature_verdict"] = (
        "★★ 特征**建成了**（新特征 %r）" % (r.get("new_features"),) if r.get("ok") else
        "★★ 特征**没建成**（★ 如实记：树 %r→%r · 平展型式 %r→%r）—— ★ 正面案例需要"
        "**带折弯的钣金件**当夹具，而本机造不出折弯（见 hem 两轮的负结论）"
        % (r.get("tree_before"), r.get("tree_after"), r.get("flat_pattern_count_before"),
           r.get("flat_pattern_count_after")))
    print("  selection =", json.dumps(c, ensure_ascii=False)[:400])
    print("  " + ev["★_contract_verdict"])
    print("  " + ev["★_feature_verdict"])

    for d in opened:
        _close(d)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(ev, ensure_ascii=False, indent=1, default=str) + "\n",
                   encoding="utf-8")
    print("  产物：%s" % OUT)
    try:
        sw.CommandInProgress = False
    except Exception:                                          # noqa: BLE001
        pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
