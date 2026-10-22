"""★ 决定性对照：`FeatureLinearPattern3` / `FeatureCircularPattern4`（旧）**真能建成阵列吗**。

★★ 官方依据（三源里的 `C:\\swapi`）：
  · `types/IFeatureManager/FeatureLinearPattern3.md`（10 参）⇒ 逐字
    「**Obsolete. Superseded by [[IFeatureManager::FeatureLinearPattern4]].**」
    ★★ 而 `FeatureLinearPattern4`（20 参）**自己也废弃** ⇒ `FeatureLinearPattern5`
    ⇒ ★★★ **后继链还有一代**（★ 与 `Get` 那族同形）✓
  · `types/IFeatureManager/FeatureCircularPattern4.md`（7 参）⇒
    「**Obsolete. Superseded by [[IFeatureManager::FeatureCircularPattern5]].**」
    ★★ 而 `FeatureCircularPattern5`（14 参）逐字
      「**Obsolete. See [[IFeatureManager::CreateFeature]] and the Remarks in …**」
    ⇒ ★★★ **那是"换范式"**（★ 同 `AddMate5` → `CreateMate`）✓

★★★ 判据（★ 跑之前写死）：★ **特征树出现新特征**才算"建成"（★ 事实 40 那一族）✓
  ★ 并**用同一个件分别测两条**（★ 但**每次都重新建件** —— 上一轮的教训：
    ★ 两条跑在同一个对象上会让第二次的读数**不可比**）✓
"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（真机验证）。
# 文件:   tools/probe_pattern_generations.py
# 定位:   ★ 阶段 2：`scripts/sw_part.py` 的 `FeatureLinearPattern3` 与 `FeatureCircula
#           rPattern4`。
#   许可:   本仓库 MIT。★ 无第三方代码引入。
#   覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

REPO = Path(Path(__file__).resolve().parents[1])
for _p in (str(REPO), str(REPO / "scripts"), str(REPO / "mcp-server")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from scripts import sw_connect as C                                       # noqa: E402
from scripts import sw_part as P                                          # noqa: E402

OUT = REPO / "output" / "pattern-generations-evidence.json"


def _g(o, n, *a):
    return C.get_com_member(o, n, *a)


def _try(fn, *a):
    try:
        return {"ok": True, "ret": repr(fn(*a))[:90]}
    except Exception as exc:                                              # noqa: BLE001
        return {"ok": False, "err": "%s: %s" % (type(exc).__name__, str(exc)[:180])}


def _names(doc) -> list:
    try:
        return [str(x) for x in (P.feature_names(doc) or [])]
    except Exception:                                                     # noqa: BLE001
        return []


def _make_part(sw, tag: str):
    """★ 建一个**新的**件（★ 每测一条都重来 —— 免得读数不可比）。"""
    doc = C.new_document(sw, "part")
    P.start_sketch(doc, plane_name="Front Plane")
    _g(_g(doc, "SketchManager"), "CreateCornerRectangle", -0.01, -0.01, 0.0, 0.01, 0.01, 0.0)
    P.end_sketch(doc)
    nm = [n for n in (P.feature_names(doc) or []) if n.startswith("草图")]
    P.extrude_boss(doc, (nm[-1] if nm else "草图1"), 10.0)
    return doc


def main() -> int:
    started = time.time()
    R: dict = {"at": time.strftime("%Y-%m-%d %H:%M:%S")}
    sw, _ = C.connect_solidworks(wait_seconds=30)

    #: ★★ ① 线性阵列（★ 旧入口，★ 与生产代码**逐字相同**的 10 实参）
    doc = None
    try:
        doc = _make_part(sw, "lp")
        R["★_LP基线特征数"] = len(_names(doc))
        #: ★ 前置：★ **选一个要阵列的特征**（★ 用本仓已验证的按名字选特征那条路）
        feat = None
        for n in _names(doc):
            if "拉伸" in n or "Extrude" in n or "凸台" in n:
                feat = n
                break
        R["选的被阵列特征"] = feat
        if feat:
            _try(P._ensure_sketch_selected if hasattr(P, "_ensure_sketch_selected") else _g,
                 doc, feat) if False else None
            try:
                _g(_g(doc, "Extension"), "SelectByID2", feat, "BODYFEATURE", 0, 0, 0, False, 0, None, 0)
            except Exception:                                             # noqa: BLE001
                pass
            try:
                R["回读选中数"] = int(_g(_g(doc, "SelectionManager"),
                                        "GetSelectedObjectCount2", -1) or 0)
            except Exception:                                             # noqa: BLE001
                R["回读选中数"] = -1
        fm = _g(doc, "FeatureManager")
        n0 = len(_names(doc))
        R["旧_FeatureLinearPattern3(10 参)"] = _try(
            _g, fm, "FeatureLinearPattern3",
            2, 0.03, 1, 0.0, False, False, "1 0 0", "0 1 0", False, False)
        n1 = len(_names(doc))
        R["★_LP后特征数"] = n1
        R["★_LP建成"] = "★ 是（+%d）" % (n1 - n0) if n1 > n0 else "★★ 否（没变）"
    except Exception as exc:                                              # noqa: BLE001
        R["LP_err"] = "%s: %s" % (type(exc).__name__, str(exc)[:200])
    finally:
        try:
            if doc is not None:
                _g(sw, "CloseDoc", str(_g(doc, "GetTitle") or ""))
        except Exception:                                                 # noqa: BLE001
            pass

    #: ★★ ② 圆形阵列（★ 旧入口，★ 与生产代码**逐字相同**的 7 实参）
    doc = None
    try:
        doc = _make_part(sw, "cp")
        R["★_CP基线特征数"] = len(_names(doc))
        #: ★ 前置：★ 先建一根**基准轴**（★ 用本仓 `part_axis` —— ★ 它会自己找圆柱面）
        R["建轴"] = _try(P.part_axis, doc, True)
        n0 = len(_names(doc))
        fm = _g(doc, "FeatureManager")
        R["旧_FeatureCircularPattern4(7 参)"] = _try(
            _g, fm, "FeatureCircularPattern4",
            4, 6.283185307179586, False, "None", False, True, False)
        n1 = len(_names(doc))
        R["★_CP后特征数"] = n1
        R["★_CP建成"] = "★ 是（+%d）" % (n1 - n0) if n1 > n0 else "★★ 否（没变）"
    except Exception as exc:                                              # noqa: BLE001
        R["CP_err"] = "%s: %s" % (type(exc).__name__, str(exc)[:200])
    finally:
        try:
            if doc is not None:
                _g(sw, "CloseDoc", str(_g(doc, "GetTitle") or ""))
        except Exception:                                                 # noqa: BLE001
            pass

    R["★★_结论"] = ("★ 至少一条旧的能建成 ⇒ 那一条**没有换的必要**"
                    if str(R.get("★_LP建成", "")).startswith("★ 是")
                    or str(R.get("★_CP建成", "")).startswith("★ 是")
                    else "★★ 两条都建不成 ⇒ 值得试新入口")
    R["seconds"] = round(time.time() - started, 2)
    OUT.write_text(json.dumps(R, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    print("wrote", OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
