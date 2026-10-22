r"""@brief 探针：`ISketchManager.CreateSpline` 的**实参形态**（官方要求**扁平一维 double 数组**）。

## 为什么（轮 183）
轮 141/182 记录「样条建不出来（`CreateSpline2` 返回 None）」—— 但那时**没读官方 Remarks**。
★ 官方 `CreateSpline` / `CreateSpline2` 的 Remarks **写明**：
```
"PointData: Array of X,Y,Z point coordinates … **(see Remarks)**"
"The PointData array is a set of, at least, **two X, Y, Z values**.
 X 起点 = PointData[0]，Y = [1]，Z = [2]；下一点 X = [3] …"
```
⇒ ★★★ **即：一个**扁平的一维数组** `[x0,y0,z0, x1,y1,z1, …]`** ——
⚠ 而仓库传的是 **list of tuples** `[(x,y,z), …]` ⇒ **形态不对**（★ 与轮 167 `AddRelation` 同一族）。

## 判据（能被空操作证伪）
```
★ **回读草图段数**（`ISketch.GetSketchSegments`）—— 与轮 167 同一手法：
  · 建样条**前**段数 = N；建**后**段数 **> N** ⇒ **成了**
  · 段数不变 ⇒ 没成（**空操作不变**）
逐个形态试（**每次新零件**，避状态污染）：
  ① 扁平 list   ② 扁平 tuple   ③ VARIANT(VT_ARRAY|VT_R8)   ④ list of tuples（现状，做对照）
```

## ⚠ 安全
只在新零件上；`CommandInProgress` 复位；收尾**轮询 + 查到就点掉**；关件不保存。

# ── 来源 ──
# 仓库:   本项目自身（真机探针）
# 文件:   tools/probe_spline_forms.py
# 定位:   给 Spec Kit `103` 判定「样条建不出来」是**实参形态**问题还是**后端到不了**。
# 官方依据: `C:/swapi/types/ISketchManager/CreateSpline.md`（Remarks：**扁平的 X,Y,Z 序
#           列**）·
#          `CreateSpline2.md`（同 Remarks + `SimulateNaturalEnds`）· 出厂反射
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

import json
import sys
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for p in (str(ROOT), str(ROOT / "scripts"), str(ROOT / "mcp-server")):
    if p not in sys.path:
        sys.path.insert(0, p)
sys.stdout.reconfigure(encoding="utf-8")

OUT = Path(Path(__file__).resolve().parents[1] / "output" / "spline-forms.json")
PTS3 = [(0.0, 0.0, 0.0), (0.005, 0.001, 0.0), (0.010, -0.001, 0.0), (0.015, 0.0, 0.0)]


def flat(pts):
    out = []
    for p in pts:
        out.extend([float(v) for v in p])
    return out


def main() -> int:
    import pythoncom
    import win32com.client

    ev: dict = {"trials": []}
    sw = None
    try:
        import sw_connect
        from scripts import sw_part

        sw = sw_connect.connect_solidworks(wait_seconds=10)[0]
        try:
            sw.CommandInProgress = True
        except Exception:  # noqa: BLE001
            pass

        forms = [
            ("① 扁平 list", flat(PTS3)),
            ("② 扁平 tuple", tuple(flat(PTS3))),
            (
                "③ VARIANT(VT_ARRAY|VT_R8)",
                win32com.client.VARIANT(
                    pythoncom.VT_ARRAY | pythoncom.VT_R8, flat(PTS3)
                ),
            ),
            ("④ list of tuples（现状对照）", PTS3),
        ]
        for label, data in forms:
            doc = sw_connect.new_document(sw, "part")
            rec = {"form": label}
            try:
                #: 进草图
                sw_part.start_sketch(doc)
                skm = sw_connect.safe_get_com_member(doc, "SketchManager")
                sk = sw_connect.safe_get_com_member(skm, "ActiveSketch")

                def segs():
                    try:
                        v = sw_connect.safe_get_com_member(sk, "GetSketchSegments")
                        return len(list(v)) if v else 0
                    except Exception:  # noqa: BLE001
                        return -1

                before = segs()
                try:
                    r = sw_connect.call_com_member(skm, "CreateSpline2", data, False)
                    rec["raised"] = None
                    rec["ret"] = type(r).__name__ if r is not None else "None"
                except Exception as exc:  # noqa: BLE001
                    rec["raised"] = "%s: %s" % (type(exc).__name__, str(exc)[:70])
                    rec["tb"] = traceback.format_exc().strip().splitlines()[-2:]
                after = segs()
                rec["before"], rec["after"] = before, after
                rec["changed"] = after > before >= 0
                print(
                    "  %-30s 段数 %s → %s ⇒ **%s**  %s"
                    % (
                        label,
                        before,
                        after,
                        "变了 ✚" if rec["changed"] else "没变",
                        (rec["raised"] or rec.get("ret", ""))[:44],
                    )
                )
                if rec["changed"]:
                    print("     ★★ **这个形态可行**")
            except Exception as exc:  # noqa: BLE001
                rec["outer"] = "%s: %s" % (type(exc).__name__, str(exc)[:70])
                print("  %-30s ⚠ 外层异常: %s" % (label, rec["outer"][:50]))
            ev["trials"].append(rec)
            try:
                t = str(sw_connect.safe_get_com_member(doc, "GetTitle") or "")
                if t:
                    sw.CloseDoc(t)
            except Exception:  # noqa: BLE001
                pass
    except Exception as exc:  # noqa: BLE001
        ev["error"] = "%s: %s" % (type(exc).__name__, str(exc)[:160])
        print("  ⚠ 探针出错: %s" % ev["error"])
    finally:
        try:
            if sw is not None:
                sw.CommandInProgress = False
        except Exception:  # noqa: BLE001
            pass

    import sw_connect as _sc

    found, dismissed, scanned = _sc.settle_residual_dialogs(settle_seconds=1.0)
    print("  收尾：发现 %d · 点掉 %d · 扫了 %d 个窗口" % (found, dismissed, scanned))
    ev["cleanup"] = {"found": found, "scanned": scanned}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(
        json.dumps(ev, ensure_ascii=False, indent=2, default=str) + "\n",
        encoding="utf-8",
    )
    print("  证据: %s" % OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
