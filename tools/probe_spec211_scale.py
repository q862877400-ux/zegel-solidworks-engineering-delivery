"""★ 探针：`InsertScale` 的建成 / 体积 `x³` 判据 / 官方必然失败负例 / 我方工程选择。"""
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（规格 211 · B1-2 的真机探针）
# 文件:   tools/probe_spec211_scale.py
# 定位:   ★ 规格 `specs/211-user-feature-gaps` 的 **B1-2**「缩放/变形」。
#   ★ 官方页三样**逐字读过**（★ 见 `scripts/sw_part.py` 的 `insert_scale` 来源块）：
# · `C:\swapi\types\IFeatureManager\InsertScale.md`（签名 + Uniform 表 + Returns 的两种
# 情形）
#     · `C:\swapi\enums\swScaleType_e.md`（★ **只有 3 个成员**）
#     · ★★ `C:\swapi\examples\Insert_Scale_Feature_Example_VB.md`（★ **给了完整调用序** +
#       ★ `GetErrorCode`）✓
# 判据:   ★★★ 主判据 = **体积按 `x³` 变化** —— ★ 缩放因子**无量纲** ⇒
#     ★★ **这条判据不受长度单位影响**（★ 与 B1-1 那个"单位未确证"的坑相对照）✓
#   ★ 辅助：★ 特征树里出现"缩放"特征（★ **用 `_feature_report` 的"建之前/之后"对比**）✓
#   ★★ **负例（两条，都要不碰 COM 就能证）**：
#     · ★ `Type=999` ⇒ ★ 不在官方 `swScaleType_e` 里 ⇒ **必然非法** ✓（★ 官方定义集合）
#     · ★ `x=0` ⇒ ★ **我方工程选择**（★ 官方没说 0 会怎样，★ **如实标注不是官方要求**）✓
#   ⚠ 另有一条**官方写明的**："缩放**图形体**"时** `Returns` = `Null` 且**不建特征** ⇒
#     ★ 那是**另一条路**，★ 本探针**不走**（★ 本探针要的是**建缩放特征**）✓
# 官方依据: 见上（三样）
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

#: ★ 100 × 60 × 20 mm ⇒ 体积 **120000 mm³**（★ 真值可算）✓
RECT = {"x1_mm": 0.0, "y1_mm": 0.0, "x2_mm": 100.0, "y2_mm": 60.0}
DEPTH = 20.0
FACTOR = 3.0                                  #: ★ 官方示例用的就是 3 ✓
EXPECT_BEFORE = 100.0 * 60.0 * DEPTH          #: 120000 mm³
EXPECT_AFTER = EXPECT_BEFORE * FACTOR ** 3    #: ★ ×27 = 3240000 ✓


def main() -> int:
    import sw_connect
    import tool_caller
    import sw_part
    from sw_mass_property import mass_properties

    out = {"official": "IFeatureManager.InsertScale",
           "expect_volume_before_mm3": EXPECT_BEFORE,
           "expect_volume_after_mm3": EXPECT_AFTER,
           "factor": FACTOR}

    #: ── ① 两条负例（★ 不碰 COM，纯 Python 层 ⇒ 必然失败 ✓）────────────────
    neg = {}
    try:
        sw_part.insert_scale(None, scale_type=999)
        neg["type_999"] = "★★ 没抛 ⇒ 判据失效"
    except ValueError as exc:
        neg["type_999"] = "✓ 抛 ValueError：%s" % str(exc)[:80]
    try:
        sw_part.insert_scale(None, x=0.0)
        neg["x_zero"] = "★★ 没抛 ⇒ 判据失效"
    except ValueError as exc:
        neg["x_zero"] = "✓ 抛 ValueError：%s" % str(exc)[:80]
    out["negatives"] = neg
    print("★ 负例 Type=999 ⇒ %s" % neg["type_999"])
    print("★ 负例 x=0      ⇒ %s" % neg["x_zero"])

    #: ── ② 真机：建板 ⇒ 读体积 ⇒ 缩放 ⇒ 再读体积 ⇒ 比 `x³` ────────────────
    sw, _ = sw_connect.connect_solidworks(wait_seconds=20)
    if sw is None:
        print("★ 连不上")
        return 2
    model = sw_connect.new_document(sw, "part")
    inj = {"model": model, "sw": sw}
    for step, params in (("solidworks_sketch_start", {}),
                         ("solidworks_sketch_add_rectangle", RECT),
                         ("solidworks_extrude_boss",
                          {"sketch_name": "Sketch1", "depth_mm": DEPTH})):
        ok, note = tool_caller.call(step, inject_objects=inj, **params)
        if not ok:
            print("★ 建状态没成：%s ⇒ %s" % (step, str(note)[:80]))
            return 1
    v0 = mass_properties(model).get("volume")
    out["volume_before"] = v0
    print("★ 缩放前体积（★ 回读）= %r（★ 期望 %r mm³）" % (v0, EXPECT_BEFORE))

    rep = sw_part.insert_scale_report(model, scale_type=1, uniform=True,
                                      x=FACTOR, volume_before=v0)
    out["report"] = rep
    print("★★ 缩放报告 ⇒ volume_ratio=%r（★ 期望 %r）· volume_ok=%r"
          % (rep.get("volume_ratio"), rep.get("volume_ratio_expected"), rep.get("volume_ok")))
    print("★★ 特征树：presence_before=%r → presence_after=%r"
          % (rep.get("present_before"), rep.get("present_after")))

    p = ROOT / "output" / "spec211-b1-scale.json"
    p.write_text(json.dumps(out, ensure_ascii=False, indent=1, default=str) + "\n",
                 encoding="utf-8")
    print("★ 证据：%s" % p)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
