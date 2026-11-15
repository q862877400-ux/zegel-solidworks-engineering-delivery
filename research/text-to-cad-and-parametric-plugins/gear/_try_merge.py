"""试 `MergePoints` 修补 + 用 CheckFeatureUse 复核 + 拉伸（业主指令「先试试」）。

# ── 来源 ─────────────────────────────────────────────────────────────
# 业主 2026-11-07：「我手动拉伸选齿轮内部是可以拉伸的，所以我猜测按理应该是某种线
#   交叉的情况，而且合法性检查出来那个连接点，我再怎么放大也看不出问题，
#   我怀疑是某种系统BUG，而不是单纯简单的没接上。如果是真的没接上那我手动拉伸
#   也应该失败的，反正你先试试吧」
# 官方依据（`C:\\swapi\\types\\ISketch\\MergePoints.md` 的 Remarks 逐字）：
#   「This method requires that **only one open contour** exists in the sketch.」
#   ⇒ 现在这条轮廓正好是「一条带小缺口的开放链」，正是 MergePoints 的适用场景。
# 流程：检查(前) → 进草图 → MergePoints(1e-5 m = 10 µm) → 检查(后) → 退出 → 拉伸
# 判据：检查 status 应为 0（OK）且 closed_count = 1；拉伸后体积应 ≈ 3092 mm³
# ────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from scripts import sw_connect as c  # noqa: E402
from scripts import sw_sketch as ck  # noqa: E402
from scripts import sw_sketch_check as sc  # noqa: E402
import scripts.sw_feature_readback as f_  # noqa: E402

TARGET = "零件46"


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:  # noqa: BLE001
        pass

    sw, _ = c.connect_solidworks(wait_seconds=15)
    doc = None
    for d in list(c.get_com_member(sw, "GetDocuments") or []):
        if str(c.get_com_member(d, "GetTitle")) == TARGET:
            doc = d
            break
    if doc is None:
        print(f"✗ 找不到 {TARGET}")
        return 1
    print("文档 =", c.get_com_member(doc, "GetTitle"))

    sk_name = next((n for n in (f_.feature_names(doc) or []) if "草图" in n), None)
    sk = sc.sketch_of(doc, sk_name)
    if sk is None:
        print("✗ 取不到草图")
        return 1
    ft = sc.FEATURE_TYPES["BOSSEXTRUDE"]
    before = sc.check_sketch(sk, ft)
    print("检查(修补前) =", before.report())

    # MergePoints 要求草图处于活动状态
    try:
        c.get_com_member(doc, "EditSketch")
    except Exception:  # noqa: BLE001
        pass
    time.sleep(0.3)
    sk_act = c.get_com_member(doc, "GetActiveSketch2")
    print("活动草图 =", bool(sk_act))
    target_sk = sk_act if sk_act is not None else sk

    merged = None
    for tol in (1e-6, 1e-5, 1e-4):
        try:
            r = ck.merge_points(target_sk, tol)
            print(f"  MergePoints({tol:g} m) = {r}")
            if r:
                merged = tol
                break
        except Exception as exc:  # noqa: BLE001
            print(f"  MergePoints({tol:g} m) 异常 {str(exc)[:90]}")

    after = sc.check_sketch(target_sk, ft)
    print("检查(修补后) =", after.report())

    try:
        c.get_com_member(doc, "InsertSketch", True)   # 退出草图
    except Exception:  # noqa: BLE001
        pass
    time.sleep(0.3)
    print("活动草图(退出后) =", bool(c.get_com_member(doc, "GetActiveSketch2")))

    if not after.ok:
        print("⇒ 修补后检查仍不通过，不拉伸")
        return 1

    # 选轮廓 + 拉伸
    sk2 = sc.sketch_of(doc, sk_name)
    cts = list(c.get_com_member(sk2, "GetSketchContours") or [])
    doc.ClearSelection2(True)
    sm = c.get_com_member(doc, "SelectionManager")
    sd = c.get_com_member(sm, "CreateSelectData")
    if sd is not None:
        c.set_com_member(sd, "Mark", 0)
    sel = 0
    for ct in cts:
        try:
            if bool(c.get_com_member(ct, "Select2", True, sd)):
                sel += 1
        except Exception:  # noqa: BLE001
            pass
    print(f"选中轮廓 {sel}/{len(cts)}")
    feat = c.get_com_member(
        c.get_com_member(doc, "FeatureManager"), "FeatureExtrusion3",
        True, False, False, 0, 0, 0.010, 0.0,
        False, False, False, False, 0.0, 0.0,
        False, False, False, False, True, False, True, 0, 0.0, False)
    print("FeatureExtrusion3 返回 =", "Feature" if feat is not None else "None")
    time.sleep(0.4)
    try:
        c.get_com_member(doc, "ForceRebuild3", False)
    except Exception:  # noqa: BLE001
        pass
    print("特征树 =", list(f_.feature_names(doc) or []))
    vol = 0.0
    try:
        mp = c.get_com_member(c.get_com_member(doc, "Extension"),
                              "CreateMassProperty")
        vol = float(c.get_com_member(mp, "Volume")) * 1e9
    except Exception:  # noqa: BLE001
        pass
    print(f"体积 = {vol:.3f} mm³")
    print("判定:", "✓ 建成" if vol > 1 else "✗ 未建成")
    try:
        c.get_com_member(doc, "ViewZoomtofit2")
    except Exception:  # noqa: BLE001
        pass
    return 0 if vol > 1 else 1


if __name__ == "__main__":
    raise SystemExit(main())
