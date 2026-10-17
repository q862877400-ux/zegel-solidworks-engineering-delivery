"""★ 探针：装饰焊缝（`InsertCosmeticWeldBead`）的真机建成与回读。"""
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库 / 文件 / 定位 / 官方依据 / 许可 / 覆盖
# 仓库:   本项目自身（建件器复用 tools/probe_spec220_boundary.py）
# 文件:   tools/probe_spec220_cosmetic_bead.py
# 定位:   ★ 规格 220（续）第 55 轮 —— ★ **装饰焊缝的真机验证**（★ 换路之后的第一次 ✓）
# 官方依据: ★ 见 `scripts/sw_cosmetic_weld_bead.py` 的来源块（★ 官方示例调用序逐字 ✓）
# 许可:   本仓库 MIT。★ 无第三方代码引入。覆盖: 全文件
# ★★ 判据：★ **特征树回读增量 ≥ 1**（★ 事实 8 ✓）
# ─────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(Path(__file__).resolve().parents[1])
for _p in (str(ROOT), str(ROOT / "tools"), str(ROOT / "scripts")):
    if _p not in sys.path:
        sys.path.insert(0, _p)


def main() -> int:
    import sw_connect
    import tool_caller
    import sw_cosmetic_weld_bead as cb
    import probe_spec220_boundary as bp                                   #: ★ 复用建件器（两块凸台 ✓）

    out = {"official": "IFeatureManager::InsertCosmeticWeldBead"}
    sw, _ = sw_connect.connect_solidworks(wait_seconds=20)
    if sw is None:
        print("★ 连不上")
        return 2

    model = bp._build_plate(sw, tool_caller)
    out["tries"] = []
    #: ★★★ 第 57 轮：★ **穷举所有面对**（★ 12 个面 ⇒ C(12,2) = 66 对 ✓）
    #:   ★ 依据第 56 轮：★ **夹具已对**（★ 12 面 = 两个体 + 贴合 + 不合并 ✓），★ 而"挑哪一对"是**机械活** ✗
    #:   ★ 判据是**特征树回读增量** ✓ ⇒ ★ **成功即停** ✓ ⇒ ★ 不必再猜"哪两个面是焊缝接头" ✓
    _n = len(cb._faces_all_bodies(model))
    _pairs = [(i, j) for i in range(_n) for j in range(i + 1, _n)]
    out["face_count"] = _n
    out["pair_count"] = len(_pairs)
    print("★ 面数 = %d ⇒ 试 %d 对（成功即停）" % (_n, len(_pairs)))
    for pair in _pairs:
        try:
            rep = cb.insert_cosmetic_weld_bead_report(model, face_index_1=pair[0],
                                                      face_index_2=pair[1],
                                                      weld_size_mm=12.95)
        except Exception as exc:                                                    # noqa: BLE001
            rep = {"ok": False, "raised": str(exc)[:220]}
        rep["faces"] = pair
        out["tries"].append(rep)
        print("★★ faces=%r ⇒ ok=%r · 特征树 %r → %r · 选区=%r"
              % (pair, rep.get("ok"), rep.get("feature_count_before"),
                 rep.get("feature_count_after"), rep.get("selection_count")))
        if rep.get("raised"):
            print("   ★ 抛：%s" % rep["raised"])
        if rep.get("error"):
            print("   ★ 拦：%s" % rep["error"])
        if rep.get("ok"):
            print("   ★★ 建成 ⇒ 停 ✓")
            break

    try:
        sw.CloseAllDocuments(True)
        out["closed"] = True
    except Exception:                                                              # noqa: BLE001
        pass
    p = ROOT / "output" / "spec220-cosmetic-bead.json"
    p.write_text(json.dumps(out, ensure_ascii=False, indent=1, default=str) + "\n",
                 encoding="utf-8")
    print("★ 证据：%s" % p)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
