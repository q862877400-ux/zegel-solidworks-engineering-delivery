"""★ 照**官方例子**走 `InsertEndCapFeature2`（★ 7 参 · 面**当参数传** · 不需要预选）。"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（真机验证）。规格 `specs/202-user-coverage-gaps` 的 **R3 收口**。
# 文件:   tools/probe_endcap_feature2.py
# 定位:   ★★★ 事实 504 记着：`InsertEndCapFeature3`（**预选**那条）在本仓 setup 上静默回 `None`，
#   ★ 四类原因已排除 ⇒ ★ **换一条路**（这正是事实 53 说的"回退换做法"）。
#   ★ 官方 `InsertEndCapFeature2` 的 Remarks 逐字：
#     「Call `InsertEndCapFeature3` if you want to **pre-select** the faces to end-cap in the
#      graphics area.」⇒ ★ **`2` 把面当参数收** ⇒ ★ 正好绕开事实 503（预选活不下来）。
#   ★★ 官方例子的**逐字配方**（`C:\\swapi\\examples\\Insert_Weldment_Features_Example_VB.md`）：
#     ```
#     face = selMgr.GetSelectedObject6(1, -1)        ' 取选中的面对象
#     Set faceECObj1(0) = face                       ' 装进数组
#     endCapFeature = fm.InsertEndCapFeature2(0.005, False, True, 0.003, 0.5, 0.003, y)
#     ```
#     ★ 注意与事实 504 里那条 3 参路线的差异：`BIsChamfer=**True**` · `WallThicknessRatio=**0.5**`。
#   ★ 选面用**按点**（`SelectByID2("", "FACE", x, y, z, …)`）—— ★ 本仓事实 32 明写这是**可行路径**
#     （按名字不行、按对象可行、**按面上的点可行**）。
#   官方依据: `C:\\swapi\\types\\IFeatureManager\\InsertEndCapFeature2.md` 的签名与 Remarks + 上面那份例子
#   许可:   本仓库 MIT。★ 无第三方代码引入。
#   覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import pythoncom                                                    # noqa: E402
import win32com.client as w32                                       # noqa: E402

REPO = Path(Path(__file__).resolve().parents[1])
for _p in (str(REPO), str(REPO / "scripts"), str(REPO / "mcp-server")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from scripts import sw_connect as C                                  # noqa: E402
from scripts import sw_part as P                                     # noqa: E402

OUT = REPO / "output" / "endcap-feature2-evidence.json"


def _g(o, n, *a):
    return C.get_com_member(o, n, *a)


def _profile():
    pref = ("tube rectangular", "tube square", "pipe", "tube")
    found = []
    for root in (r"C:\ProgramData\SOLIDWORKS", r"C:\ProgramData\SolidWorks"):
        for h in sorted(Path(root).rglob("*.sldlfp")):
            s = str(h)
            if "weldment profiles" not in s.lower():
                continue
            found.append(s)
            if any(k in s.lower() for k in pref):
                return s
        if found:
            return found[0]
    return ""


def _face_center(face):
    """★ 取一张面**面上的一个点**（★ 供 `SelectByID2("", "FACE", x, y, z, …)` 用）。

    ★★ 2026-10-03 修（★ 这是**我自己器械的 bug**，不是"再猜一个变量"）：
      上一版用 `IFace2.GetBox` 的**包围盒中心** —— ★ 而**空心管（管/方通）的端面是"环"**，
      ★ 它的包围盒中心**落在孔里** ⇒ ★ 那个点**根本不在面上**。
    ★ 正确做法：取**面自己的曲面**（`IFace2.GetSurface()`）在参数域中点 `Evaluate(0.5, 0.5)`
      —— ★ 对本例的平面（含环形平面）一定落在面上。
    """
    try:
        surf = _g(face, "GetSurface")
        if surf is not None:
            pt = list(_g(surf, "Evaluate", 0.5, 0.5) or [])
            if len(pt) >= 3:
                return (float(pt[0]), float(pt[1]), float(pt[2]))
    except Exception:                                                 # noqa: BLE001
        pass
    try:
        box = list(_g(face, "GetBox") or [])                          #: ★ 兜底（并注明它可能不在面上）
        if len(box) >= 6:
            return ((box[0] + box[3]) / 2.0, (box[1] + box[4]) / 2.0, (box[2] + box[5]) / 2.0)
    except Exception:                                                 # noqa: BLE001
        pass
    return None


def main() -> int:
    started = time.time()
    R: dict = {"at": time.strftime("%Y-%m-%d %H:%M:%S"), "cases": []}
    sw, _ = C.connect_solidworks(wait_seconds=30)
    prof = _profile()
    R["profile"] = prof
    for idx in range(4):                       #: ★ 试前 4 张面（每张单独一个案例）
        row: dict = {"face_index": idx}
        doc = None
        try:
            doc = C.new_document(sw, "part")
            P.start_sketch(doc, plane_name="Front Plane")
            _g(_g(doc, "SketchManager"), "CreateLine", -0.08, 0.0, 0.0, 0.08, 0.0, 0.0)
            P.end_sketch(doc)
            names = [n for n in (P.feature_names(doc) or [])
                     if n.startswith("草图") or n.lower().startswith("sketch")]
            from scripts.sw_weldment import create_structural_member_from_sketch
            sm = create_structural_member_from_sketch(
                doc, sketch_name=(names[-1] if names else "草图1"), profile_path=prof)
            row["weldment_ok"] = bool(isinstance(sm, dict) and sm.get("ok"))
            faces = []
            for b in list(_g(doc, "GetBodies2", 0, True) or []):
                faces.extend(list(_g(b, "GetFaces") or []))
            row["face_count"] = len(faces)
            if idx >= len(faces):
                row["skip"] = "★ 没有第 %d 张面" % idx
                R["cases"].append(row)
                continue
            face = faces[idx]
            pt = _face_center(face)
            row["point"] = [round(v, 5) for v in pt] if pt else None
            #: ★ 按**面上的点**选（★ 事实 32 的可行路径）
            ext = _g(doc, "Extension")
#: ★★ **事实 33 逐字**：`SelectByID2` 的 Callout **必须**传 `VARIANT(VT_DISPATCH, None)`
#:   （`sw_part._empty_callout()`）—— ★ 传 `None` 得到 `类型不匹配`，
#:   ★★ 而**那个错误看不出是 Callout 的问题**（★ 本轮又踩一次）。
            ok_sel = False
            if pt:
                ok_sel = bool(_g(ext, "SelectByID2", "", "FACE", pt[0], pt[1], pt[2],
                                 False, 0, P._empty_callout(), 0))
            row["select_returned"] = ok_sel
            row["sel_count"] = int(_g(_g(doc, "SelectionManager"),
                                      "GetSelectedObjectCount2", -1) or 0)
            if row["sel_count"] < 1:
                row["skip"] = "★ 按点没选上面"
                R["cases"].append(row)
                continue
            #: ★ 官方：用 `GetSelectedObject6(1, -1)` 取回**面对象**（不是用我们自己的索引）
            got = _g(_g(doc, "SelectionManager"), "GetSelectedObject6", 1, -1)
            row["got_type"] = type(got).__name__
            arr = w32.VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_DISPATCH, [got])
            before = list(P.feature_names(doc) or [])
            #: ★★ 官方例子逐字配方
            ret = _g(_g(doc, "FeatureManager"), "InsertEndCapFeature2",
                     0.005, False, True, 0.003, 0.5, 0.003, arr)
            row["returned_is_none"] = ret is None
            if ret is not None:
                for k, m in (("ret_name", "Name"), ("ret_type", "GetTypeName2")):
                    try:
                        row[k] = str(_g(ret, m))
                    except Exception:                                 # noqa: BLE001
                        pass
            after = list(P.feature_names(doc) or [])
            row["new_features"] = [n for n in after if n not in before]
            row["ok"] = bool(row["new_features"])
        except Exception as exc:                                      # noqa: BLE001
            row["ok"] = False
            row["err"] = "%s: %s" % (type(exc).__name__, str(exc)[:200])
        finally:
            try:
                if doc is not None:
                    _g(sw, "CloseDoc", str(_g(doc, "GetTitle") or ""))
            except Exception:                                         # noqa: BLE001
                pass
        R["cases"].append(row)
        if row.get("ok"):
            break                             #: ★ 建成一张就够了（判据是"能不能建成"）
    R["passed"] = sum(1 for r in R["cases"] if r.get("ok"))
    R["seconds"] = round(time.time() - started, 2)
    OUT.write_text(json.dumps(R, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    print("wrote", OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
