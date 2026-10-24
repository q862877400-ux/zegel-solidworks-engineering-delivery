"""★ 诊断：交付件里每张草图的段，以及圆心能不能读出来。

## 为什么要单独诊断

`s3-acceptance.md` 第一次跑出 `孔心位移=[]` ⇒
**E2 判 fail 可能是「读数失败」而不是「孔真的没动」**。
这两件事必须分清，否则我会记下一个错结论（第 13 轮就差点犯过）。

## 量什么

对每一张草图特征：

1. `GetSpecificFeature2()` 回的是不是 `ISketch`
2. `GetSketchSegments` 有几段
3. 每段 `GetCenterPoint2` 能不能取到；能取到就打印 X/Y（毫米）

★ 只读，不改任何东西。
"""

from __future__ import annotations

import json
import shutil
import sys
import time
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
R = Path(Path(__file__).resolve().parents[1])
sys.path.insert(0, str(R))
sys.path.insert(0, str(R / "scripts"))

from scripts import sw_connect as c_  # noqa: E402
from scripts.sw_connect import (  # noqa: E402
    get_com_member,
    open_doc_count,  # noqa: E402
)
from scripts.sw_connect import try_call as _try  # noqa: E402
from scripts.sw_connect import try_member as _member  # noqa: E402
from scripts.sw_feature_readback import (  # noqa: E402
    feature_names,  # noqa: E402
    )

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库 / 文件 / 定位 / 官方依据 / 许可 / 覆盖
# 仓库:   本项目自身（工具 · 诊断）
# 文件:   tools/probe_s3_hole_center_diagnose.py
# 定位:   S3 验收里 E2 的「孔心位移」读成空列表 —— 先分清是「读数失败」还是
#          「孔真的没动」。本探针只量每张草图的段与圆心可读性。
# 官方依据: IFeature.GetSpecificFeature2 · ISketch.GetSketchSegments ·
#          ISketchArc.GetCenterPoint2 · ISketchPoint.X / .Y（米）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

SRC = R / "output" / "stage2" / "板1_rev-1.SLDPRT"
WORK = R / "output" / "s3-acceptance"


def main() -> int:
    ev: dict = {"probe": "s3-hole-center-diagnose", "sketches": []}
    sw = doc = None
    try:
        WORK.mkdir(parents=True, exist_ok=True)
        copy = WORK / "diag.SLDPRT"
        shutil.copy2(SRC, copy)
        conn = c_.connect_solidworks(wait_seconds=30)
        sw = conn[0] if isinstance(conn, tuple) else conn
        try:
            sw.CommandInProgress = True
        except Exception:  # noqa: BLE001
            pass
        ok_o, doc = _try(c_.open_document, sw, str(copy))
        if not ok_o or doc is None:
            print("★ 打不开：%s" % str(doc)[:120])
            return 2

        names = [n for n in (feature_names(doc) or [])
                 if n.startswith("草图") or n.lower().startswith("sketch")]
        print("草图形状数：%d → %s" % (len(names), names))

        for nm in names:
            row: dict = {"name": nm}
            ok_f, feat = _try(get_com_member, doc, "FeatureByName", nm)
            if not ok_f or feat is None:
                row["error"] = "取不到特征"
                ev["sketches"].append(row)
                continue
            ok_s, sk = _try(get_com_member, feat, "GetSpecificFeature2")
            row["specific_ok"] = ok_s and sk is not None
            if not row["specific_ok"]:
                row["specific_err"] = str(sk)[:100]
                ev["sketches"].append(row)
                continue
            ok_seg, segs = _try(get_com_member, sk, "GetSketchSegments")
            segs = list(segs) if ok_seg and segs else []
            row["segments"] = len(segs)
            centers = []
            for s in segs:
                pt = _member(s, "GetCenterPoint2")
                if pt is None:
                    continue
                x, y = _member(pt, "X"), _member(pt, "Y")
                if x is not None and y is not None:
                    centers.append([round(float(x) * 1000.0, 3),
                                    round(float(y) * 1000.0, 3)])
            row["centers_mm"] = centers
            ev["sketches"].append(row)
            print("  %-10s 段=%-3s 圆心=%s" % (nm, len(segs), centers))

        #: 顺带：不在编辑态时活动草图是什么
        ok_a, act = _try(get_com_member, doc, "SketchManager")
        ev["sketch_manager_ok"] = bool(ok_a and act is not None)
        print("SketchManager 可读：%s" % ev["sketch_manager_ok"])
        return 0
    finally:
        if sw is not None:
            if doc is not None:
                ok_t, title = _try(get_com_member, doc, "GetTitle")
                if ok_t and title:
                    _try(sw.CloseDoc, str(title))
            print("收尾后剩余文档数：%s" % open_doc_count(sw))
            try:
                sw.CommandInProgress = False
            except Exception:  # noqa: BLE001
                pass
        ev["finished_at"] = time.strftime("%Y-%m-%dT%H:%M:%S")
        dest = R / "output" / "s3-hole-center-diagnose.json"
        dest.write_text(json.dumps(ev, ensure_ascii=False, indent=2), encoding="utf-8")
        print("证据已写：%s" % dest)


if __name__ == "__main__":
    raise SystemExit(main())
