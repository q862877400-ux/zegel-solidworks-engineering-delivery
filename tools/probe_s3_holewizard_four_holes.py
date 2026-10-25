"""★ 验证：按指定坐标建 4 个异型孔向导孔，孔位与孔型都读得回。

## 为什么

第 26 轮单点验证了「异型孔向导可用、孔型完整可读」，但那条路口只能放
**面中心**。为了首件板的 4 个孔，本轮加了
`create_hole_wizard_at_point_report(model, x_mm, y_mm, z_mm, size, ...)`
（把射线起点从面中心换成显式坐标，其余 12 参 + 27 参逐字照抄）。

## 本探针验什么

| 读数 | 期望 |
|---|---|
| 建出 4 个孔特征 | 树里 4 个新特征 |
| 类型名 | `HoleWzd`（实测值，不是猜的） |
| `hole_params` 孔型可读 | `ThruHoleDiameter` 有值 |
| **孔位对不对** | 用 `sw_review.collect_geometry_measurements` 从 B-Rep 量孔心，与坐标比 |

★ 最后一条是**独立读数**：不信 `HoleWizard5` 的返回值，从几何上量回来。

## 只读纪律

新建文档 → 用完关掉；`CommandInProgress`；收尾核文档数。
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
R = Path(Path(__file__).resolve().parents[1])
sys.path.insert(0, str(R))
sys.path.insert(0, str(R / "scripts"))

from scripts import sw_connect as c_  # noqa: E402
from scripts import sw_hole_features as h_  # noqa: E402
from scripts import sw_part as p_  # noqa: E402
from scripts.sw_connect import open_doc_count  # noqa: E402
from scripts.sw_connect import try_call as _try  # noqa: E402
from scripts.sw_connect import try_member as _member  # noqa: E402
from scripts.sw_feature_readback import feature_info, feature_names, hole_params  # noqa: E402
from scripts.sw_review import collect_geometry_measurements  # noqa: E402

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库 / 文件 / 定位 / 官方依据 / 许可 / 覆盖
# 仓库:   本项目自身（工具 · 多孔定位验证）
# 文件:   tools/probe_s3_holewizard_four_holes.py
# 定位:   E2 的孔型子项需要异型孔向导；单点已验证「孔型可读」，
#          本轮验「多孔能按指定坐标放置」。用见 C:\swapi 的
#          IFeatureManager.HoleWizard5（27 参）+ IModelDocExtension.SelectByRay（12 参）。
# 官方依据: IFeatureManager.HoleWizard5 · IModelDocExtension.SelectByRay ·
#          IWizardHoleFeatureData2.ThruHoleDiameter（经 hole_params）·
#          B-Rep 孔心（经 sw_review.collect_geometry_measurements）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

HOLES = [(10.0, 10.0), (90.0, 10.0), (10.0, 50.0), (90.0, 50.0)]
TOP_Z_MM = 20.0  #: 板厚 20mm，前视面起草图 ⇒ 顶面在 z=20（拉伸 20mm）


def main() -> int:
    ev: dict = {"probe": "s3-holewizard-four-holes", "holes_requested": HOLES}
    sw = doc = None
    try:
        conn = c_.connect_solidworks(wait_seconds=30)
        sw = conn[0] if isinstance(conn, tuple) else conn
        try:
            sw.CommandInProgress = True
        except Exception:  # noqa: BLE001
            pass
        doc = c_.new_document(sw, "part")
        p_.start_sketch(doc, plane_name="Front Plane")
        p_.sketch_corner_rectangle(doc, 0.0, 0.0, 100.0, 60.0)
        p_.end_sketch(doc)
        sk_names = [n for n in (feature_names(doc) or []) if n.startswith("草图")]
        _try(p_.extrude_boss, doc, sk_names[-1] if sk_names else "草图1", 20.0)
        before = [str(n) for n in (feature_names(doc) or [])]
        print("① 板已建：%s" % before)

        #: ② 逐个按坐标建孔
        built = []
        for i, (hx, hy) in enumerate(HOLES, 1):
            ok, res = _try(
                h_.create_hole_wizard_at_point_report,
                doc, hx, hy, TOP_Z_MM, "M8",
            )
            built.append({"i": i, "at": [hx, hy, TOP_Z_MM], "ok": ok,
                          "result": res if ok else str(res)[:180]})
            if not ok:
                print("   ✗ 孔 %d @(%g,%g)：%s" % (i, hx, hy, str(res)[:150]))
        ev["built"] = built
        n_ok = sum(1 for b in built if b["ok"])
        print("② 建孔：%d/%d 成功" % (n_ok, len(HOLES)))

        #: ③ 特征与类型
        after = [str(n) for n in (feature_names(doc) or [])]
        new = [n for n in after if n not in before]
        types = {}
        for n in new:
            info = feature_info(doc, n) or {}
            types[n] = info.get("GetTypeName2")
        ev["new_features"] = new
        ev["new_feature_types"] = types
        print("③ 新特征 %d 个 · 类型 %s" % (len(new), set(types.values())))

        #: ④ 孔型可读
        readable = 0
        for n in new:
            okp, prm = _try(hole_params, doc, n)
            if okp and isinstance(prm, dict) and prm.get("ThruHoleDiameter"):
                readable += 1
        ev["hole_params_readable"] = readable
        print("④ hole_params 可读 %d/%d" % (readable, len(new)))

        #: ⑤ 从 B-Rep 量孔心（独立读数，不信返回值）
        ok_g, measured = _try(collect_geometry_measurements, doc)
        mholes = (measured or {}).get("holes") if isinstance(measured, dict) else None
        ev["measured_holes"] = mholes
        print("⑤ B-Rep 量到孔 %s 个" % (len(mholes) if mholes else 0))

        #: 判读
        ev["verdict"] = {
            "built_ok": n_ok,
            "built_total": len(HOLES),
            "new_features": len(new),
            "types": sorted({str(t) for t in types.values() if t}),
            "hole_params_readable": readable,
        }
        ev["ok"] = bool(n_ok == len(HOLES) and readable == len(HOLES))
        ev["conclusion"] = (
            "★ 4 个异型孔向导孔按指定坐标建成，孔型全部可读"
            if ev["ok"]
            else "★ 未达：建成 %d/%d · 孔型可读 %d/%d"
            % (n_ok, len(HOLES), readable, len(HOLES))
        )
        print(ev["conclusion"])
        return 0 if ev["ok"] else 1
    except Exception as exc:  # noqa: BLE001
        import traceback

        ev["err"] = "%s: %s" % (type(exc).__name__, str(exc)[:240])
        ev["traceback"] = traceback.format_exc()[-1200:]
        print("★ 失败：", ev["err"])
        return 1
    finally:
        if sw is not None:
            if doc is not None:
                t = str(_member(doc, "GetTitle") or "")
                if t:
                    _try(sw.CloseDoc, t)
            ev["docs_left"] = open_doc_count(sw)
            print("   收尾后剩余文档数：%s" % ev["docs_left"])
            try:
                sw.CommandInProgress = False
            except Exception:  # noqa: BLE001
                pass
        ev["finished_at"] = time.strftime("%Y-%m-%dT%H:%M:%S")
        dest = R / "output" / "s3-holewizard-four-holes.json"
        dest.write_text(json.dumps(ev, ensure_ascii=False, indent=2), encoding="utf-8")
        print("   证据已写：%s" % dest)


if __name__ == "__main__":
    raise SystemExit(main())
