"""★ 探针：验 `scripts/` 里**新缝的三个装配/阵列模块函数**（B2b 的产出）—— ★ 不是重跑探针实现。"""
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（规格 213 · B2b 的**模块函数**真机验证）
# 文件:   tools/probe_spec213_b2b_modules.py
# 定位:   ★ 规格 213 的 **B2b**（B 类余下三项）。★ 与 B2 同一条纪律：
#   ★★ **验的是缝进模块之后那条路** ✗ —— ★ **不是**再跑一遍探针内部的实现 ✓
#   ★ 官方纪律逐字：「写探针验能力时，★ **按 `ToolSpec` 的契约调，别手调内部实现**」✓
#   ★★★ **为什么必须分开验**：★「探针能跑」与「模块函数能跑」**不是同一件事** ✗ ——
#     缝合会引入新错（★ 本次实测：★ 我第一版引用了模块里**不存在**的 `_feature_names` ✗ ✓）
# 判据:   ★★ 一律**回读**：
#     · ★ `explode_line` ⇒ ★ **特征树增量 + `ISketchManager::ActiveSketch`** ✓
#     · ★ `speedpak` ⇒ ★ **`IComponent2::IsSpeedPak` 前后对比** ✓（★ 顶层特征树看不见它 ✗）
#     · ★★ `curve_driven_pattern` ⇒ ★ 特征树增量 —— ★ **预期不建**（★ 官方 `Obsolete` ✓）⇒
#       ★ 本探针**如实记"不建"**、★ **不许把它写成建成**（★ A7 ✓）
# 官方依据: 见三个模块函数各自的来源块（`swapi` 签名 + mark 表 / 前置）✓
# 许可:   本仓库 MIT。★ 无第三方代码引入。★ 落盘一律在**仓库内 `output/`**（★ 非用户目录 ✓）。
# ─────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(Path(__file__).resolve().parents[1])
for _p in (str(ROOT), str(ROOT / "tools"), str(ROOT / "scripts")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

WORK = ROOT / "output" / "spec213-b2b-modules"


def _mk_part(sw, path: Path, w: float = 60.0, h: float = 40.0, d: float = 20.0):
    """★ 建一个**落盘**的零件 —— ★ `add_component` 要磁盘路径 ✗（零件名随工作表递增，★ 不假设）✓"""
    import sw_connect
    import sw_part
    m = sw_connect.new_document(sw, "part")
    sw_part.start_sketch(m, "Front Plane")
    sw_part.sketch_corner_rectangle(m, 0.0, 0.0, w, h)
    sk = sw_part.current_sketch_name(m)
    sw_part.end_sketch(m)
    sw_part.extrude_boss(m, sk, d)
    sw_connect.save_document(m, str(path))
    return m


def main() -> int:
    import sw_assembly
    import sw_assembly_doc as AD
    import sw_connect
    import sw_pattern as P
    import sw_part as PT

    out: dict = {"purpose": "★ 验 B2b 缝进 scripts/ 的三个模块函数（★ 走模块、不走探针实现）",
                 "cases": []}
    sw, _ = sw_connect.connect_solidworks(wait_seconds=20)
    if sw is None:
        print("★ 连不上")
        return 2
    WORK.mkdir(parents=True, exist_ok=True)

    #: ══════ ① 爆炸直线：★ 走 `sw_assembly_doc.insert_explode_line_sketch_report` ══════
    row1: dict = {"case": "explode_line_sketch（走模块函数）"}
    try:
        _mk_part(sw, WORK / "p1.sldprt")
        asm = sw_connect.new_document(sw, "assembly")
        row1["add_component"] = bool(sw_assembly.add_component(asm, str(WORK / "p1.sldprt"), 0.0, 0.0, 0.0))
        row1["exploded_view_created"] = bool(AD.create_exploded_view(asm))
        res = AD.insert_explode_line_sketch_report(asm)
        #: ★★ 记**前后**（★ 判据是**变化**、★ 不是"现在有" —— 见模块函数里的注释 ✓）
        row1.update({k: res.get(k) for k in ("explode_view_count", "added", "returned",
                                             "active_sketch_before", "active_sketch_after",
                                             "active_sketch_side_changed")})
        row1["ok"] = bool(res.get("ok"))
        print("★ ① 爆炸直线 ⇒ ok=%r · 新增=%r · ★ **侧变化 %r → %r** · bool 回 %r"
              % (row1["ok"], row1.get("added"), row1.get("active_sketch_before"),
                 row1.get("active_sketch_after"), row1.get("returned")))
    except Exception as e:                                              # noqa: BLE001
        row1["ok"] = False
        row1["exception"] = "%s: %s" % (type(e).__name__, str(e)[:180])
        print("★ ① 爆炸直线 ⇒ 抛 %s" % row1["exception"])
    out["cases"].append(row1)

    #: ══════ ② SpeedPak：★ 走 `sw_assembly_doc.create_speedpak_report` ══════
    row2: dict = {"case": "speedpak（走模块函数）"}
    try:
        _mk_part(sw, WORK / "pa.sldprt", 30.0, 20.0, 10.0)
        _mk_part(sw, WORK / "pb.sldprt", 30.0, 20.0, 10.0)
        sub = sw_connect.new_document(sw, "assembly")
        sw_assembly.add_component(sub, str(WORK / "pa.sldprt"), 0.0, 0.0, 0.0)
        sw_assembly.add_component(sub, str(WORK / "pb.sldprt"), 60.0, 0.0, 0.0)
        #: ★★ 子装配**本身也要落盘** —— ★ 顶层要 `add_component(<子装配路径>)` ✗
        row2["sub_saved"] = bool(sw_connect.save_document(sub, str(WORK / "sub.SLDASM")))
        top = sw_connect.new_document(sw, "assembly")
        row2["sub_inserted"] = bool(sw_assembly.add_component(top, str(WORK / "sub.SLDASM"), 0.0, 0.0, 0.0))
        res2 = AD.create_speedpak_report(top, speedpak_type=1)
        row2.update({k: res2.get(k) for k in ("component_count", "component_name", "selected",
                                              "is_speedpak_before", "is_speedpak_after", "returned")})
        row2["ok"] = bool(res2.get("ok"))
        print("★ ② SpeedPak ⇒ ok=%r · 组件=%r · 名=%r · 选中=%r · IsSpeedPak %r→%r"
              % (row2["ok"], row2["component_count"], row2["component_name"], row2["selected"],
                 row2["is_speedpak_before"], row2["is_speedpak_after"]))
    except Exception as e:                                              # noqa: BLE001
        row2["ok"] = False
        row2["exception"] = "%s: %s" % (type(e).__name__, str(e)[:180])
        print("★ ② SpeedPak ⇒ 抛 %s" % row2["exception"])
    out["cases"].append(row2)

    #: ══════ ③ 曲线驱动阵列：★ 走 `sw_pattern.insert_local_curve_driven_pattern_report` ══════
    row3: dict = {"case": "curve_driven_pattern（走模块函数 · ★ 预期不建 ⇒ stitched）"}
    try:
        m3 = sw_connect.new_document(sw, "part")
        PT.start_sketch(m3, "Front Plane")
        PT.sketch_corner_rectangle(m3, 0.0, 0.0, 40.0, 20.0)
        sk3 = PT.current_sketch_name(m3)
        PT.end_sketch(m3)
        PT.extrude_boss(m3, sk3, 10.0)
        #: ★ 方向 1 的曲线：★ 另画一条草图（★ 官方 mark 2 = Curve/edge/sketch ✓）
        PT.start_sketch(m3, "Front Plane")
        PT.sketch_corner_rectangle(m3, 0.0, 0.0, 120.0, 20.0)
        curve_sk = PT.current_sketch_name(m3)
        PT.end_sketch(m3)
        row3["seed_feature"] = sk3
        row3["curve_sketch"] = curve_sk
        #: ★★★★ **修过一处**：★ 第一版我把 `seed_feature` 传成**草图名** ✗ ⇒
        #:   ★★ 真机读数 `mark1=False · mark2=False` ⇒ **两处前置都没上** ⇒ **读数无效** ✗
        #:   ★ 而**原探针**用的是 `extrudes[0]` = **`凸台-拉伸1`**（★ **特征名**、★ 不是草图名 ✓）⇒
        #:     ★ `mark1=True · mark2=True · 选区=2` ✓
        #:   ⇒ ★★★ **正解：mark 1 = 「Components to pattern」⇒ 传**拉伸特征的名字**** ✓
        import sw_feature_readback as FR
        feat_names = FR.feature_names(m3)
        extrudes = [n for n in feat_names if "拉伸" in n or "Extrude" in str(n)]
        seed = extrudes[0] if extrudes else sk3
        row3["feature_names"] = feat_names
        row3["seed_used"] = seed
        res3 = P.insert_local_curve_driven_pattern_report(
            m3, seed_feature=seed, curve_sketch=curve_sk)
        row3.update({k: res3.get(k) for k in ("mark1_selected", "mark2_selected", "added",
                                              "returned_is_none")})
        row3["ok"] = bool(res3.get("ok"))
        print("★ ③ 曲线驱动阵列 ⇒ ok=%r（★ **预期 False** ✓）· mark1=%r · mark2=%r · 新增=%r · 回 None=%r"
              % (row3["ok"], row3["mark1_selected"], row3["mark2_selected"],
                 row3["added"], row3["returned_is_none"]))
    except Exception as e:                                              # noqa: BLE001
        row3["ok"] = False
        row3["exception"] = "%s: %s" % (type(e).__name__, str(e)[:180])
        print("★ ③ 曲线驱动阵列 ⇒ 抛 %s" % row3["exception"])
    out["cases"].append(row3)

    #: ★★★ 判定（★ **分档如实**，★ 不许把 `stitched` 写成 `verified` —— A7 ✓）
    ok1, ok2, ok3 = bool(row1.get("ok")), bool(row2.get("ok")), bool(row3.get("ok"))
    out["module_functions_verified"] = {"explode_line_sketch": ok1, "speedpak": ok2,
                                        "curve_driven_pattern": ok3}
    if ok1 and ok2 and not ok3:
        out["verdict"] = ("★★★★★ **两项 `verified` + 一项 `stitched`，全对** —— "
                          "★ 爆炸直线 ✓ · ★ SpeedPak ✓ · ★★ 曲线驱动阵列**如预期不建** ✓ "
                          "⇒ ★ **登记等级与真机读数一致** ✓（★ 这正是 A7 要的"
                          "「不许把 stitched 写成 verified」✓）")
    elif ok1 and ok2:
        out["verdict"] = ("★★★ 两项 `verified` 成立（爆炸直线 ✓ · SpeedPak ✓）；"
                          "★★ 而曲线驱动阵列**这次建了**（%）⇒ ★ **那与登记的 `stitched` 不一致** ✗ "
                          "⇒ ★ **要回头改登记**（★ 不许放着不管）✓" % ok3)
    else:
        out["verdict"] = ("★★ **未全过**（explode=%r · speedpak=%r · curve=%r）⇒ ★ **如实记、"
                          "★ 不许把 `stitched` 写成 `verified`** ✓" % (ok1, ok2, ok3))
    print("★★★ 判定 ⇒ %s" % out["verdict"])

    p = ROOT / "output" / "spec213-b2b-modules.json"
    p.write_text(json.dumps(out, ensure_ascii=False, indent=1, default=str) + "\n", encoding="utf-8")
    print("★ 证据：%s" % p)
    return 0


if __name__ == "__main__":
    import traceback
    try:
        raise SystemExit(main())
    except SystemExit:
        raise
    except BaseException:                                              # noqa: BLE001
        tb = traceback.format_exc()
        (ROOT / "output" / "spec213-b2b-modules-traceback.txt").write_text(tb, encoding="utf-8")
        print("★★ 异常已落盘：\n%s" % tb[-1200:])
        raise SystemExit(3)
