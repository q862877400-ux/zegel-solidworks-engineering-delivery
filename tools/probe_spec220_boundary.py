"""★ 探针：边界特征（官方 `IFeatureManager::InsertNetBlend`）两个 Type 的建成与回读。"""

# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库 / 文件 / 定位 / 官方依据 / 许可 / 覆盖
# 仓库:   本项目自身（骨架照 tools/probe_spec211_scale.py 的先例）
# 文件:   tools/probe_spec220_boundary.py
# 定位:   ★ 规格 220 的 **T-220-01（还验证债）** —— ★ 把 `scripts/sw_net_blend.py` 的
#           两个
#         工具从 `stitched` 推向 `verified`（★ 或如实报"没验成"）✓
# 官方依据: ★ 三样读过（★ 见 `scripts/sw_net_blend.py` 来源块）：
# · 签名 `C:\swapi\types\IFeatureManager\InsertNetBlend.md`（20 参）⇒ `Type` 1=Boss / 2=
# Surface
#   · ★★ 调用序出自官方示例 `Insert_Boundary_Feature_Example_VB.htm` 第 67–74 行
#     （★ 例子里是**两个拉伸各选一个面** ⇒ ★ 本探针照它）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(Path(__file__).resolve().parents[1])
for _p in (str(ROOT), str(ROOT / "tools"), str(ROOT / "scripts")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import sw_connect  # noqa: E402
import tool_caller  # noqa: E402
from sw_net_blend import _feature_count as _fc  # noqa: E402

#: ★ 100 × 60 × 20 mm 板（★ 与既有探针同口径）
RECT = {"x1_mm": 0.0, "y1_mm": 0.0, "x2_mm": 100.0, "y2_mm": 60.0}
DEPTH = 20.0


def _build_plate(sw, tool_caller) -> object:
    """★ 建**两块**100×60×20 mm 的凸台（★ 同一草图两个不相交矩形 ⇒ 两个轮廓 ⇒ 各自的面独立）。

    ★★★ 为什么改（规格 220 续 · 第 37 轮）：★ 官方示例 `Postconditions` 逐字要求
      「② **Creates two boss-extrude features.** ③ **Selects a face on each boss-extrude feature.**」
      ⇒ ★ 边界特征要**两个轮廓**（★ 而不是同一块板上的两个面 ✗）✓
      ★ 本函数用**同一草图里的两个不相交矩形** ⇒ 一次拉伸出两块凸台 ⇒ 满足"两个轮廓" ✓
    """
    model = sw_connect.new_document(sw, "part")
    inj = {"model": model, "sw": sw}
    #: ★★★ 第 55 轮（规格 220 续）：★ **两块凸台改成"贴着"** ——
    #: ★ 依据官方 `InsertCosmeticWeldBead2` 第 12 行逐字：★「…also **fills the gap betwe
    #: en the
    #:     pre-selected part bodies**, if any.」✓
    #: ★★ 第 55 轮真机：★ 两块隔 30 mm 时（★ 中间**没有缝** ✗）⇒ 选面全对（★ 12 面 / 选
    #: 区 1→2 ✓）
    #:      ★ 而 `InsertCosmeticWeldBead(12.95)` **`returned: false`**、★ 树 **22 → 22** ✗
    #:   ⇒ ★ 改成 **x 从 100 起（与第一块共面贴合 ✓）** ⇒ ★ 两个面成为**真正的焊缝接头** ✓
    RECT2 = {"x1_mm": 100.0, "y1_mm": 0.0, "x2_mm": 200.0, "y2_mm": 60.0}
    #: ★★★ 第 38 轮：★ **两次拉伸**（★ 官方示例 `Postconditions` 逐字要"**两个 boss-extr
    #: ude 特征**" ✓）
    #: ★ 第 37 轮的教训：★ **同一草图里两个矩形只会拉出一块** ✗（★ 第二个把第一个挤掉了
    #: ✓）
    #:   ⇒ ★ 改成两轮：★ ① 草图1 + 矩形1 + 拉伸 ② **草图2 + 矩形2 + 拉伸** ✓
    rounds = (
        (
            ("solidworks_sketch_start", {}),
            ("solidworks_sketch_add_rectangle", RECT),
            ("solidworks_extrude_boss", {"sketch_name": "Sketch1", "depth_mm": DEPTH}),
        ),
        (
            ("solidworks_sketch_start", {}),
            ("solidworks_sketch_add_rectangle", RECT2),
            (
                "solidworks_extrude_boss",
                {
                    "sketch_name": "Sketch2",
                    "depth_mm": DEPTH,
                    #: ★★★ 第 56 轮：★ **关掉"合并结果"** ⇒ ★★
                    #: **两个体：贴合但不合并** ✓
                    #: ★ 依据第 55 轮真机：★ 隔 30 mm ⇒ 有体无"
                    #: 缝" ✗；
                    #: ★ 贴合但**默认合并** ⇒ 并成一个体（★ 6
                    #: 面 ✗）
                    #: ⇒ ★ 官方 `FeatureExtrusion3` 有 **`Merge
                    #: `** 形参 ✓
                    #: ★ 而本仓 `solidworks_extrude_boss` **就
                    #: 暴露了它** ✓
                    "merge": False,
                },
            ),
        ),
    )
    for rnd in rounds:
        for step, params in rnd:
            ok, note = tool_caller.call(step, inject_objects=inj, **params)
            if not ok:
                raise RuntimeError("★ 建板没成：%s ⇒ %s" % (step, str(note)[:100]))
    return model


def _run_one(sw, tool_caller, net, kind: str, fn_name: str) -> dict:
    """★ 跑一档（`surface` 或 `boss`），★ 回读特征树计数 + 逐步骤读数 ✓"""
    model = _build_plate(sw, tool_caller)
    before = _fc(model)
    fn = getattr(net, fn_name)
    try:
        #: ★★ 2026-10-07（规格 220 T-220-01）**swap test**：★ 交换两个面序号，★ 二分真因
        #:  ✓
        #: ★★★ 第 39 轮：★ **两个面取不同的体**（★ 官方示例逐字「a face on **each** boss
        #: -extrude」✓）
        #: ★ 第 38 轮真机：★ 两块凸台 = **两个独立的体** ⇒ ★ 0 号体 6 个面 ⇒ ★ 7 号面（i
        #: ndex 6）落在**第二块** ✓
        rep = fn(model, face_index_1=0, face_index_2=6)
    except Exception as exc:  # noqa: BLE001
        return {
            "kind": kind,
            "function": fn_name,
            "raised": str(exc)[:220],
            "feature_count_before": before,
            "feature_count_after": _fc(model),
        }
    rep = dict(rep or {})
    rep["kind"] = kind
    rep["function"] = fn_name
    return rep


def main() -> int:
    import sw_connect
    import tool_caller
    import sw_net_blend as net

    out = {
        "official": "IFeatureManager.InsertNetBlend",
        "plate_mm": [100.0, 60.0, DEPTH],
    }
    sw, _ = sw_connect.connect_solidworks(wait_seconds=20)
    if sw is None:
        print("★ 连不上 SolidWorks")
        return 2

    #: ── ① 纯 Python 层负例（★ 只测 blend_type 校验 ⇒ 不碰 COM、必然抛 ValueError ✓）──
    neg = {}
    for bad in (999, 7):
        try:
            net.insert_net_blend_report(None, blend_type=bad)
            neg["bad_type_%d" % bad] = "★★ 没抛 ⇒ 判据失效"
        except ValueError as exc:
            neg["bad_type_%d" % bad] = "✓ 抛 ValueError：%s" % str(exc)[:70]
    out["negatives"] = neg

    #: ── ①b 逐面盒中心（★ 只读诊断：确认 face_index 0/1 的点是否不同、是否落在面内）──
    try:
        import sw_selection_spec as _SS
        import sw_part as _sp

        _faces = list(
            _SS.entities_on_body(_build_plate(sw, tool_caller), "FACE", body_index=0)
            or []
        )
        centres = []
        for _i, _f in enumerate(_faces[:6]):
            _b = list(_sp.get_com_member(_f, "GetBox") or [])
            if len(_b) >= 6:
                centres.append(
                    {
                        "i": _i,
                        "centre": [
                            round((_b[0] + _b[3]) / 2.0, 4),
                            round((_b[1] + _b[4]) / 2.0, 4),
                            round((_b[2] + _b[5]) / 2.0, 4),
                        ],
                    }
                )
        out["face_centres"] = centres
        out["face_count"] = len(_faces)
        print(
            "★ 面数 = %d · 前几个面心 = %r"
            % (len(_faces), [c["centre"] for c in centres])
        )
    except Exception as _e:  # noqa: BLE001
        out["face_centres_error"] = str(_e)[:140]
        print("★ 面心诊断失败：%s" % str(_e)[:120])

    #: ── ② 真机两档：★ 曲面（Type=2）先跑，★ 凸台（Type=1）再跑 ─────────────
    results = []
    for kind, fn_name in (
        ("surface", "insert_boundary_surface_report"),
        ("boss", "insert_boundary_boss_report"),
    ):
        r = _run_one(sw, tool_caller, net, kind, fn_name)
        results.append(r)
        print(
            "★★ [%s] ok=%r · 特征树 %r → %r · feature=%r"
            % (
                kind,
                r.get("ok"),
                r.get("feature_count_before"),
                r.get("feature_count_after"),
                r.get("feature"),
            )
        )
        if r.get("raised"):
            print("   ★ 抛：%s" % r["raised"])
        for s in r.get("steps") or []:
            if s.get("error"):
                print("   ⚠ 步骤 %s 报：%s" % (s.get("step"), str(s["error"])[:110]))
    out["results"] = results

    #: ── ③ 收尾：★ 关掉自己开的文档（★ 纪律：用完关）────────────────────────
    try:
        sw.CloseAllDocuments(True)
        out["closed_documents"] = True
    except Exception as exc:  # noqa: BLE001
        out["closed_documents"] = "★ 关文档出错：%s" % str(exc)[:80]

    p = ROOT / "output" / "spec220-boundary.json"
    p.write_text(
        json.dumps(out, ensure_ascii=False, indent=1, default=str) + "\n",
        encoding="utf-8",
    )
    print("★ 证据：%s" % p)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
