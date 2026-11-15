"""隔离：普通方形 + 拉伸。判断是「拉伸 API 坏了」还是「草图的问题」。

# ── 来源 ─────────────────────────────────────────────────────────────
# 业主 2026-11-07 指令：「你新建一个普通方形，拉伸试试，看看是拉伸 API 坏了
#   还是草图的问题」
# 判据：方形能拉伸 ⇒ API 正常，问题在齿轮草图；方形也失败 ⇒ API 调用路径坏了。
# 做法：最小正方形（4 条真直线，10×10 mm），`P.sketch` 上下文 + `extrude_boss`。
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
from scripts import sw_part as P  # noqa: E402
import scripts.sw_feature_readback as f_  # noqa: E402


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:  # noqa: BLE001
        pass

    sw, _ = c.connect_solidworks(wait_seconds=20)
    doc = c.new_document(sw, "part")
    title = str(c.get_com_member(doc, "GetTitle") or "?")
    print("文档 =", title)

    # 正方形：10 × 10 mm，四角 (0,0)-(10,0)-(10,10)-(0,10)
    with P.sketch(doc, "Front Plane") as sk:
        P.sketch_line(doc, 0.0, 0.0, 10.0, 0.0)
        P.sketch_line(doc, 10.0, 0.0, 10.0, 10.0)
        P.sketch_line(doc, 10.0, 10.0, 0.0, 10.0)
        P.sketch_line(doc, 0.0, 10.0, 0.0, 0.0)
        print("草图名 =", sk)
    print("活动草图存在 =", bool(c.get_com_member(doc, "GetActiveSketch2")))
    print("特征树（拉伸前）=", list(f_.feature_names(doc) or []))

    feat = P.extrude_boss(doc, sk, 0.010)     # 10 mm
    print("extrude_boss 返回 =", "Feature" if feat is not None else "None")
    time.sleep(0.4)
    try:
        c.get_com_member(doc, "ForceRebuild3", False)
    except Exception:  # noqa: BLE001
        pass
    print("特征树（拉伸后）=", list(f_.feature_names(doc) or []))
    vol = 0.0
    try:
        ext = c.get_com_member(doc, "Extension")
        mp = c.get_com_member(ext, "CreateMassProperty")
        vol = float(c.get_com_member(mp, "Volume")) * 1e9
    except Exception:  # noqa: BLE001
        pass
    print(f"体积 = {vol:.3f} mm³（期望 1000）")
    ok = feat is not None and abs(vol - 1000.0) < 1.0
    print("判定:", "✓ 方形能拉伸 ⇒ 拉伸 API 正常，问题在齿轮草图"
          if ok else "✗ 方形也失败 ⇒ 拉伸 API 调用路径坏了")
    try:
        c.get_com_member(doc, "ViewZoomtofit2")
    except Exception:  # noqa: BLE001
        pass
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
