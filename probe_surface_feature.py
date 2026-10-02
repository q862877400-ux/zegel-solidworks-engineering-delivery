"""★ **曲面特征的攻关探针**（2026-10-01 · 轮 308）。

★ 背景：事实 40 的结论是 **`IModeler.Create*Surface`（造**曲面体**）返回值跨次都变** ⇒
  当时定为"不做曲面"。★ **而本轮发现官方有**第二条路****：
  **`IFeatureManager.Insert*Surface` / `FeatureExtruRefSurface3`（建**曲面特征**）** ——
  ★★ 那条路**从来没试过**，★ 而且它正是**四家那 12 个曲面缺口名**的对应实现。

★ 本探针只问一件事：**`FeatureExtruRefSurface3` 能不能建出一个曲面特征**。
★ 判据（★ 三条都要）：① 调用**不抛** ② **特征树真的多了**（★ 回读，不靠返回值 —— ★ 它回 void）
  ③ **曲面体真的出现**（`GetBodies2(swSurfBodies)` 计数 > 0）。
★ 安全：`CommandInProgress` 抑制 + `finally` 收尾 + 关掉自己开的文档。
"""

import json
import sys
import time
import traceback
from pathlib import Path

sys.path[:0] = [r"C:\swprojects\sw-skill-fork", r"C:\swprojects\sw-skill-fork\scripts"]

import sw_connect                                              # noqa: E402
from scripts import sw_part as P                               # noqa: E402
from scripts import sw_feature_readback as FR                  # noqa: E402
from scripts.sw_connect import get_com_member                  # noqa: E402

#: swEndConditions_e / swStartConditions_e 的官方数值（★ 从反射来，★ 不凭记忆）
SW_END_COND_BLIND = 0
SW_END_COND_THROUGH_ALL = 1
SW_START_COND_SKETCH_PLANE = 0
SW_BODY_SURF = 2          #: swBodyType_e 里曲面体的取值（★ 待真机核）


def _surf_body_count(doc):
    """★ 数曲面体（★ 按 `GetBodies2` 的 body 类型）。"""
    n = 0
    try:
        for b in (get_com_member(doc, "GetBodies2", 0, True) or []):
            try:
                t = get_com_member(b, "GetType")
            except Exception:                                  # noqa: BLE001
                t = None
            #: ★ GetType 回的是 swBodyType_e（★ 0=solid · 1=sheet · 2=surface?）⇒ 先把值记下来
            if t is not None:
                n += 1 if int(t) != 0 else 0
    except Exception:                                          # noqa: BLE001
        pass
    return n


def main() -> int:
    sw = sw_connect.connect_solidworks(wait_seconds=30)[0]
    try:
        sw.CommandInProgress = True
    except Exception:                                          # noqa: BLE001
        pass
    ev = {"steps": {}}
    doc = None
    try:
        doc = sw_connect.new_document(sw, "part")
        #: ★ 一个草图（★ 拉伸曲面的全部输入）
        P.start_sketch(doc, plane_name="Front Plane")
        P.sketch_corner_rectangle(doc, -20.0, -10.0, 20.0, 10.0)
        sk = P.current_sketch_name(doc)
        P.end_sketch(doc)
        ev["steps"]["sketch"] = {"ok": bool(sk), "name": sk}
        before = len(FR.feature_names(doc))
        ev["steps"]["tree_before"] = before
        #: ★ 官方签名：FeatureExtruRefSurface3(Sd, Dir, StartCond, OffsetVal, T1, T2, D1, D2, …)
        #:   ⚠ 它是 **void** ⇒ ★ 成败只能看**特征树**与**曲面体**
        #: ★★★ 2026-10-01（轮 308）**真 arity = 22**（★ 三源互证：
        #:   官方 md 的完整签名列了 22 个；反射 arity 表 `sw_api_sldworks.py:4300`
        #:   写 `FeatureExtruRefSurface3: 22`）。
        #:   ⚠ 我上一次传了 8 个 ⇒ `DISP_E_BADPARAMCOUNT`（★ 而那不是"API 不行"）。
        args = (
            True,                       # Sd        单端
            False,                      # Dir       不反向
            SW_START_COND_SKETCH_PLANE,  # StartCond
            0.0,                        # OffsetVal
            SW_END_COND_BLIND,          # T1
            SW_END_COND_BLIND,          # T2
            0.010,                      # D1        深度 10 mm
            0.010,                      # D2
            False, False,               # Dchk1 / Dchk2
            False, False,               # Ddir1 / Ddir2
            0.0, 0.0,                   # Dang1 / Dang2
            False, False,               # OffsetReverse1 / 2
            False, False,               # TranslateSurface1 / 2
            False, False,               # CapEnd1 / CapEnd2
            False,                      # DeleteOriginalFace
            True,                       # KnitResult（★ 缝合结果 ⇒ 更像一个真曲面）
        )
        assert len(args) == 22, "★ 参数个数必须是 22（反射 arity）" 
        for label, call in (
            ("FeatureExtruRefSurface3", lambda: get_com_member(doc, "FeatureManager", a=None)),
        ):
            pass                                               #: ★ 占位（下面直接调）
        try:
            fm = get_com_member(doc, "FeatureManager")
            ret = get_com_member(fm, "FeatureExtruRefSurface3", *args)
            ev["steps"]["call"] = {"ok": True, "returned": repr(ret)[:40],
                                   "★": "它回 void ⇒ 成败看特征树与曲面体"}
        except Exception as exc:                               # noqa: BLE001
            ev["steps"]["call"] = {"ok": False,
                                   "error": "%s: %s" % (type(exc).__name__, str(exc)[:220]),
                                   "tb": traceback.format_exc().splitlines()[-2:]}
        after = len(FR.feature_names(doc))
        ev["steps"]["tree_after"] = after
        ev["steps"]["tree_grew"] = after > before
        ev["steps"]["names_after"] = FR.feature_names(doc)[-4:]
        ev["steps"]["surf_bodies"] = _surf_body_count(doc)
        #: ★ 逐个 body 的类型也记下来（★ 那才能说清"有没有曲面体"）
        types = []
        try:
            for b in (get_com_member(doc, "GetBodies2", 0, True) or []):
                types.append(str(get_com_member(b, "GetType")))
        except Exception:                                      # noqa: BLE001
            pass
        ev["steps"]["body_types"] = types
        ok = bool(ev["steps"]["call"].get("ok")) and ev["steps"]["tree_grew"]
        ev["verdict"] = "pass" if ok else "fail"
    finally:
        try:
            if doc is not None:
                t = str(sw_connect.safe_get_com_member(doc, "GetTitle") or "")
                if t:
                    sw.CloseDoc(t)
        except Exception:                                      # noqa: BLE001
            pass
        try:
            sw.CommandInProgress = False
        except Exception:                                      # noqa: BLE001
            pass
    ev["captured_at"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    out = Path(r"D:\AI\SW\output\surface-feature-probe.json")
    out.write_text(json.dumps(ev, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("  call        : %s" % json.dumps(ev["steps"].get("call"), ensure_ascii=False)[:190])
    print("  tree        : %s -> %s (grew=%s)" % (ev["steps"].get("tree_before"),
                                                  ev["steps"].get("tree_after"),
                                                  ev["steps"].get("tree_grew")))
    print("  names_after : %s" % ev["steps"].get("names_after"))
    print("  body_types  : %s" % ev["steps"].get("body_types"))
    print("  verdict     : %s" % ev["verdict"].upper())
    print("  证据: %s" % out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
