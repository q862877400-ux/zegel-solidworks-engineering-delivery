"""★ 探针：圆角焊缝（`InsertFilletBeadFeature2`）的真机建成与回读。"""
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库 / 文件 / 定位 / 官方依据 / 许可 / 覆盖
# 仓库:   本项目自身（建件器复用 tools/probe_spec220_boundary.py）
# 文件:   tools/probe_spec220_bead.py
# 定位:   ★ 规格 220（续）第 49 轮 —— ★ **焊件/圆角焊缝的真机验证** ✓
# 官方依据: ★ 签名与语义见 `scripts/sw_weld_bead.py` 的来源块（★ 官方 16 参逐字 ✓）
# 许可:   本仓库 MIT。★ 无第三方代码引入。覆盖: 全文件
# ★★ 判据：★ **特征树回读增量 ≥ 1**（★ 事实 8：★ 返回值不可信 ✓）
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
    import sw_weld_bead as wb
    import probe_spec220_boundary as bp                                   #: ★ 复用建件器 ✓

    out = {"official": "IFeatureManager::InsertFilletBeadFeature2"}
    sw, _ = sw_connect.connect_solidworks(wait_seconds=20)
    if sw is None:
        print("★ 连不上")
        return 2

    model = bp._build_plate(sw, tool_caller)                               #: ★ 两块凸台 ✔
    before = wb._feature_count(model)
    out["tries"] = []
    for pair in ((0, 1), (2, 3), (0, 6)):
        try:
            rep = wb.insert_fillet_bead_report(model, edge_index_1=pair[0],
                                               edge_index_2=pair[1], size_mm=5.0)
        except Exception as exc:                                                    # noqa: BLE001
            rep = {"ok": False, "raised": str(exc)[:200]}
        rep["edges"] = pair
        out["tries"].append(rep)
        print("★★ edges=%r ⇒ ok=%r · 特征树 %r → %r"
              % (pair, rep.get("ok"), rep.get("feature_count_before"),
                 rep.get("feature_count_after")))
        if rep.get("raised"):
            print("   ★ 抛：%s" % rep["raised"])
        for s in (rep.get("steps") or []):
            if s.get("step", "").startswith("select"):
                print("   %s ⇒ ok=%r · 选区计数=%r · 边数=%r"
                      % (s.get("step"), s.get("ok"), s.get("selection_count"),
                         s.get("edge_count")))
        if rep.get("ok"):
            print("   ★★ 建成 ⇒ 停止后续尝试 ✓")
            break

    try:
        sw.CloseAllDocuments(True)
        out["closed"] = True
    except Exception:                                                              # noqa: BLE001
        pass
    p = ROOT / "output" / "spec220-bead.json"
    p.write_text(json.dumps(out, ensure_ascii=False, indent=1, default=str) + "\n",
                 encoding="utf-8")
    print("★ 证据：%s" % p)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
