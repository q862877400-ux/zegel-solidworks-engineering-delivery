"""只读勘察：这块板的**孔位草图**与**板宽尺寸**分别是什么。

## 为什么要先勘察

E2.rebuild 要的是「改板宽 ⇒ 四个孔心跟着动」。要做成这件事，必须先知道：

① 四个孔心在哪个草图里（孔心是**草图点**，事实 32：草图段没有名字）
② 板宽是不是一个**已有尺寸**（若不是，改板宽就得先给它建尺寸）
③ 那个草图里有没有可以当"基准"的线段（孔心要与它建尺寸才可能联动）

★ 本脚本**只读**：不建尺寸、不改模型、不保存。勘察结论决定下一步怎么做。

## 输出

- 特征树里草图/孔特征的名字与类型
- 每个草图：段数、点数、每条线段的端点坐标
- 模型里的显示尺寸清单（名字 + 数值）
- 包围盒（板宽从这儿读）
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
R = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(R))
sys.path.insert(0, str(R / "scripts"))
sys.path.insert(0, str(R / "tools"))


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库 / 文件 / 定位 / 官方依据 / 许可 / 覆盖
# 仓库:   本项目自身（工具 · E2 联动勘察）
# 文件:   tools/probe_e2_hole_sketch_survey.py
# 定位:   只读勘察首件板件的孔位草图与板宽尺寸，决定「孔心接尺寸」该怎么做。
#          E2.rebuild 的硬前置（孔心必须是尺寸）现在**可达**（事实 567，
#          `IModelDocExtension.AddDimension` 可用），本脚本是动手前的地形。
# 官方依据: ISketch::GetSketchSegments / GetSketchPoints2 · IFeature::GetFirstDisplayDimension ·
#          IModelDoc2::GetBox（包围盒）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

SRC = R / "output" / "stage2" / "板1_rev-1.SLDPRT"
DEST = R / "output" / "e2-hole-sketch-survey.json"

import sw_connect as c_  # noqa: E402


def _sketch_info(sk) -> dict:
    segs, pts = [], []
    try:
        for s in list(c_.get_com_member(sk, "GetSketchSegments") or ()):
            segs.append(
                {
                    "type": c_.get_com_member(s, "GetType"),
                    "start": list(c_.get_com_member(s, "GetStartPoint2").x) or [],
                }
            )
    except Exception:  # noqa: BLE001
        pass
    try:
        for p in list(c_.get_com_member(sk, "GetSketchPoints2") or ()):
            pts.append(
                {
                    "x": round(float(c_.get_com_member(p, "X")) * 1000.0, 3),
                    "y": round(float(c_.get_com_member(p, "Y")) * 1000.0, 3),
                }
            )
    except Exception:  # noqa: BLE001
        pass
    return {"segments": len(segs), "points": pts}


def main() -> int:
    ev: dict = {"probe": "e2-hole-sketch-survey"}
    sw = conn = doc = None
    try:
        conn = c_.connect_solidworks(wait_seconds=30)
        sw = conn[0] if isinstance(conn, tuple) else conn
        try:
            sw.CommandInProgress = True
        except Exception:  # noqa: BLE001
            pass

        import shutil

        work = R / "output" / "survey53"
        work.mkdir(parents=True, exist_ok=True)
        copy = work / "板1_survey.SLDPRT"
        shutil.copy2(SRC, copy)
        ok_o, doc = c_.try_call(c_.open_document, sw, str(copy))
        ev["open"] = {"ok": bool(ok_o), "title": str(c_.get_com_member(doc, "GetTitle") or "")}

        #: ① 包围盒 —— ★ 用仓库既有的 solid_body_extent_mm
        #:   （IModelDoc2.GetBox **不存在**，实测 AttributeError；
        #:     本机要按实体取，仓库那个函数已经封装好）
        from scripts.sw_feature_readback import solid_body_extent_mm

        ev["box"] = solid_body_extent_mm(doc)
        print("① 包围盒(mm)：%s" % ev["box"])

        #: ② 特征树里的草图与孔特征 —— ★ 用仓库既有的 eature_names
        #:   （自己走 GetFeatureTreeRootItem2 实测返回 0 个，别手搓）
        from scripts.sw_feature_readback import feature_names

        names = list(feature_names(doc) or ())
        ev["features"] = names
        print("② 特征 %d 个：%s" % (len(names), names))

        #: ③ 每个草图的段数与点坐标（孔心是草图点）
        sketches = {}
        for nm in names:
            if not (nm.startswith("草图") or nm.lower().startswith("sketch")):
                continue
            try:
                c_.get_com_member(
                    c_.get_com_member(doc, "Extension"),
                    "SelectByID2", nm, "SKETCH", 0.0, 0.0, 0.0, False, 0, None, 0,
                )
                doc.EditSketch()
                sk2 = c_.get_com_member(doc, "GetActiveSketch2")
                sketches[nm] = _sketch_info(sk2) if sk2 is not None else {"err": "无活动草图"}
                c_.get_com_member(doc, "SketchManager").InsertSketch(True)
            except Exception as exc:  # noqa: BLE001
                sketches[nm] = {"err": "%s" % (type(exc).__name__,)}

        #: ④ 每个孔特征的**子特征**（定位草图藏在子特征里）
        #:   ★ 照仓库 `feature_names` 的方式平铺遍历（`FirstFeature` + `GetNextFeature`）；
        #:     上一版用 `SelectByID2` 取特征对象拿到 None ⇒ "子特征 0 个"是**假读数**。
        holes = {}
        try:
            f0 = c_.get_com_member(doc, "FirstFeature")
        except Exception:  # noqa: BLE001
            f0 = None
        f = f0
        while f is not None:
            try:
                fname = str(c_.get_com_member(f, "Name") or "")
                ftype = str(c_.get_com_member(f, "GetTypeName2") or "")
            except Exception:  # noqa: BLE001
                break
            if ftype == "HoleWzd" or "孔" in fname:
                subs = []
                try:
                    sf = c_.get_com_member(f, "GetFirstSubFeature")
                except Exception:  # noqa: BLE001
                    sf = None
                while sf is not None:
                    try:
                        subs.append(
                            {
                                "name": str(c_.get_com_member(sf, "Name") or ""),
                                "type": str(c_.get_com_member(sf, "GetTypeName2") or ""),
                            }
                        )
                    except Exception:  # noqa: BLE001
                        pass
                    try:
                        sf = c_.get_com_member(sf, "GetNextSubFeature")
                    except Exception:  # noqa: BLE001
                        break
                holes[fname] = {"type": ftype, "subfeatures": subs}
                print("   %-16s type=%-10s 子特征 %d 个 %s"
                      % (fname[:16], ftype, len(subs),
                         [(s["name"], s["type"]) for s in subs][:4]))
            try:
                f = c_.get_com_member(f, "GetNextFeature")
            except Exception:  # noqa: BLE001
                break

        ev["holes"] = holes

        ev["sketches"] = sketches
        print("③ 草图勘察：")
        for k, v in sketches.items():
            print("   %-16s %s" % (k[:16], str(v)[:120]))

        ev["ok"] = True
        return 0
    except Exception as exc:  # noqa: BLE001
        import traceback

        ev["err"] = "%s: %s" % (type(exc).__name__, str(exc)[:200])
        ev["traceback"] = traceback.format_exc()[-800:]
        print("★ 失败：", ev["err"])
        return 1
    finally:
        if doc is not None:
            try:
                ttl = str(c_.get_com_member(doc, "GetTitle") or "")
                if ttl:
                    sw.CloseDoc(ttl)
            except Exception:  # noqa: BLE001
                pass
        if sw is not None:
            try:
                sw.CommandInProgress = False
            except Exception:  # noqa: BLE001
                pass
            try:
                ev["docs_left"] = c_.open_doc_count(sw)
            except Exception:  # noqa: BLE001
                pass
        DEST.write_text(json.dumps(ev, ensure_ascii=False, indent=2), encoding="utf-8")
        print("   证据已写：%s" % DEST)


if __name__ == "__main__":
    raise SystemExit(main())
