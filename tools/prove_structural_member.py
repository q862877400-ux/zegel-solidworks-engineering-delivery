"""★ 真机：**结构构件**（焊件族）—— ★ 判据是**特征树**（不是 `Count`）。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（工具）
# 文件:   tools/prove_structural_member.py
# 定位:   ★ 2026-10-03（轮 428）`plan-200r-v3` **段 2（焊件族）**；★ 承段 1 的收口。
#   ★★ **而本轮先做了一件侦察**（★ 按 AGENTS.md 的顺序：dead-ends → limitations → facts → 动手）：
#     ★ 而 `capabilities.yaml` 的 `weldment_cut_list` 条目**早就写明**了卡点：
#       「**2026-10-02（轮 364）真因查明：本机没装「焊件轮廓库」（Weldment Profiles）** ⇒
#         所以报「没有可写入切割清单的结构构件实体」**不是代码问题**，而是**建不出结构构件**」
#     ★★★ **而本轮的侦察**推翻**了它**：
#       ```
#       ✓ 在：C:\ProgramData\SOLIDWORKS\SOLIDWORKS 2026\weldment profiles
#       ⇒ 111 个 .sldlfp（ansi / **GB** / iso / DIN / JIS …）
#         · …\GB\square-rods.sldlfp · …\GB\l-e.sldlfp · …\GB\round-rods.sldlfp …
#       ```
#     ⇒ ★★ **即：★ 前置现在是**齐的****（★ 而轮 364 那条结论**要更新**）✓
#   ★★ **而其余两件都是"先找后搓"找到的现成物**（★ 我差点自己写）：
#     · ★ `sw_sketch.get_sketch_segments(sketch)` —— ★ **取草图线段**（★ `ISketch.GetSketchSegments`）✓
#     · ★ `sw_part` 里那条现成的取 `ISketch` 的路：`FeatureByName` → `GetSpecificFeature2` ✓
#   ★★ **判据**：★ 这条用的是**特征树**（★ 与段 1 的 `Count` 完全不同的一条判据家族）——
#     ★ 收集前后**特征类型名集合**，★ 判「多了 `WeldmentFeature` 与结构构件」✓
#   ⚠ 只新建、**不保存**（★ 硬约束⑦；★ 轮廓是**已在盘上的**外部文件，★ 零件在内存里）。
# 官方依据: `IFeatureManager.InsertStructuralWeldment5`（★ `sw_weldment.create_structura
#           l_member` 已在用）·
#   `ISketch.GetSketchSegments()`（★ 出厂类型库反射：**0 参** → Object）· `IFeature.GetSpecificFeature2`
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
#
# ★ 判据：★ 特征树里**多了** `WeldmentFeature`（★ 与/或结构构件那类的类型名）。

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "scripts"))

OUT = Path(Path(__file__).resolve().parents[1] / "output" / "structural-member-evidence.json")
PROFILE = Path(r"C:\ProgramData\SOLIDWORKS\SOLIDWORKS 2026\weldment profiles\GB\square-rods.sldlfp")


def _type_names(model) -> set:
    """★ 特征树里全部特征的**类型名**（★ 判据用）—— ★ 照 `sw_weldment` 里既有的遍历写法。"""
    from sw_connect import get_com_member, safe_get_com_member
    names, feature, guard = set(), safe_get_com_member(model, "FirstFeature"), 0
    while feature is not None and guard < 500:
        names.add(str(safe_get_com_member(feature, "GetTypeName2") or ""))
        feature = safe_get_com_member(feature, "GetNextFeature")
        guard += 1
    return names


def main() -> int:
    import sw_connect
    from sw_connect import get_com_member, safe_get_com_member
    from scripts.sw_part import current_sketch_name, end_sketch, sketch_line, start_sketch
    from scripts.sw_sketch import get_sketch_segments
    from scripts.sw_weldment import create_structural_member_from_sketch

    ev: dict = {"steps": {}, "at": time.strftime("%Y-%m-%dT%H:%M:%S"),
                "profile": str(PROFILE), "profile_exists": PROFILE.is_file()}
    sw = sw_connect.connect_solidworks(wait_seconds=30)[0]
    doc = None
    try:
        doc = sw_connect.new_document(sw, "part")
        #: ★ 结构构件的**路径草图**：前视基准面上一段直线
        start_sketch(doc, plane_name="Front Plane")
        sketch_line(doc, 0.0, 0.0, 100.0, 0.0)
        sk = current_sketch_name(doc, "")
        end_sketch(doc)
        ev["steps"]["path_sketch"] = {"ok": bool(sk), "sketch": sk}

        #: ★ **先验入口**：★ 能不能从草图特征拿到线段对象
        segs = []
        try:
            feature = get_com_member(doc, "FeatureByName", sk)
            sketch = get_com_member(feature, "GetSpecificFeature2")
            segs = list(get_sketch_segments(sketch))
            ev["steps"]["entry_check"] = {"ok": len(segs) >= 1, "segment_count": len(segs),
                                          "first_type": type(segs[0]).__name__ if segs else None}
        except Exception as exc:                               # noqa: BLE001
            ev["steps"]["entry_check"] = {"ok": False,
                                          "err": "%s: %s" % (type(exc).__name__, str(exc)[:130])}
        before = _type_names(doc)
        if (ev["steps"].get("entry_check") or {}).get("ok"):
            try:
                rep2 = create_structural_member_from_sketch(doc, sk, str(PROFILE))
                ev["steps"]["structural_member"] = {
                    "ok": bool(rep2.get("ok") and rep2.get("new_type_names")),
                    "feature": str(rep2.get("feature"))[:60],
                    "segments": rep2.get("segments"),
                    "new_type_names": rep2.get("new_type_names"),
                    "note": "★ 判据：★ 特征树里**多了**新类型名（如 `WeldmentFeature`）"}
            except Exception as exc:                           # noqa: BLE001
                ev["steps"]["structural_member"] = {
                    "ok": False, "err": "%s: %s" % (type(exc).__name__, str(exc)[:150])}
        else:
            ev["steps"]["structural_member"] = {"ok": False, "skipped": "★ 入口没验过 ⇒ 不施加"}
        v = ev["steps"].get("structural_member") or {}
        ev["verdict"] = "pass" if (v.get("ok") and v.get("new_type_names")) else "partial"
        ev["note"] = ("★ 结构构件（焊件族）—— ★ 判据是**特征树**（★ 不是 `Count`）。"
                      "★ 前置：★ 本机的**焊件轮廓库**在（★ 111 个 `.sldlfp`，★ 用 GB 的方管）—— "
                      "★ 而那**推翻了** `capabilities.yaml` 里轮 364 那条「本机没装轮廓库」。")
        OUT.write_text(json.dumps(ev, ensure_ascii=False, indent=1, default=str) + "\n", encoding="utf-8")
        print(json.dumps(ev, ensure_ascii=False, indent=1, default=str)[:1500])
        print("  产物: %s ⇒ %s" % (OUT, str(ev["verdict"]).upper()))
    finally:
        try:
            sw.CommandInProgress = False
        except Exception:                                      # noqa: BLE001
            pass
        try:
            if doc is not None:
                t = str(sw_connect.safe_get_com_member(doc, "GetTitle") or "")
                if t:
                    sw.CloseDoc(t)
        except Exception:                                      # noqa: BLE001
            pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
