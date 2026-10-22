"""★ 决定性对照：`FeatureFillet`（7 参，旧）与 `FeatureFillet3`（15 参，新）**谁真能建成倒角**。

★★ 官方依据（三源；★ 而**三源在这里给了三个不同的数** —— 铁律 4 的裁决场）：
  · `types/IFeatureManager/FeatureFillet.md`（8 参）⇒ 逐字
    「**Obsolete. Superseded by [[IFeatureManager::FeatureFillet2]].**」
  · `types/IFeatureManager/FeatureFillet2.md`（12 参）⇒ 「Superseded by FeatureFillet3」
  · `types/IFeatureManager/FeatureFillet3.md`（**15 参**）⇒ ★ **无废弃**
  · ★★ **反射（出厂类型库）里有两组**：
    ```
    ★ 组 A: Object FeatureFillet(Int32, Double, Int32, Int32, Object, Object, Object)         ← 7 参
            Object FeatureFillet3(Int32, Double, Double, Double, Int32, Int32, Int32, Obj…)   ← 15 参
    ★ 组 B: Void   FeatureFillet(Double, Boolean, Boolean, Boolean, Int32)                    ← 5 参
            Int32  FeatureFillet2(Double, Boolean, Boolean, Boolean, Int32, Int32, Object)    ← 7 参
            Int32  FeatureFillet3(Double, Boolean, Int32, Boolean, Int32, Int32, Obj…)        ← 9 参
    ```
  ⇒ ★★★ **「`FeatureFillet3` 有几参」有两个答案（15 或 9）** ——
    ★ 这正是**铁律 4 那条注记**说的：「`FeatureFillet3` 在本机类型库里有 14/15 个参数，官方文档写 7 个」✓

★★★ 判据（★ 跑之前写死）：★ **特征树出现新特征**才算"建成"（★ 只回对象不算 —— 事实 40 那一族）✓
"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（真机验证）。
# 文件:   tools/probe_fillet_generations.py
# 定位:   ★ 阶段 2：`scripts/sw_part.py` 的 `FeatureFillet`（★ 1 条）——
#   ★ 先判**该不该换**，★ 再决定改不改。
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

from scripts import sw_connect as c  # noqa: E402
from scripts import sw_part as p  # noqa: E402

OUT = REPO / "output" / "fillet-generations-evidence.json"


def _g(o, n, *a):
    return c.get_com_member(o, n, *a)


def _try(fn, *a):
    try:
        return {"ok": True, "ret": repr(fn(*a))[:90]}
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "err": "%s: %s" % (type(exc).__name__, str(exc)[:180])}


def _feat_names(doc) -> list:
    try:
        return [str(x) for x in (p.feature_names(doc) or [])]
    except Exception:  # noqa: BLE001
        return []


def _select_one_edge(doc) -> int:
    """★ 选一条边 —— ★ 用**本仓已验证的路**（`tool_specs_batch23._select_edge` 同款）。

    ★★★ 2026-10-03 修（★ **这正是本会话第 3 次撞"选不上"的根因**）：
      ★ 我上一版写的是 `resolve_selection(doc, spec, "EDGE", **append=True**)` ——
      ★★ 而它的真签名是 `(model, selector, kind, *, body_index=0)` ⇒ **没有 `append`**
      ⇒ ★★★ 于是抛 `TypeError`、★ **又被我的 `except Exception: pass` 吞掉**
      ⇒ ★★ 结果回读"选中数 = 0"，★ 看起来像"选不上"，★ **实际是我的调用姿势错了** ✓
      ★ 与**事实 48 定则②**同族：★ **`except: pass` 会把真因吞掉**（本次连吞 3 轮）✓
    """
    n = 0
    try:
        from sw_selection_spec import resolve_selection

        #: ★ 正确签名：★ 3 个位置参 + 关键字 `body_index`（★ **没有 `append`**）
        n = resolve_selection(doc, "index:0", "EDGE")
    except Exception as exc:  # noqa: BLE001
        #: ★★ **不再静默** —— 把真因记下来（★ 上一版就是这里吞掉的）
        return {"selected": -1, "err": "%s: %s" % (type(exc).__name__, str(exc)[:150])}
    return {"selected": n}


def main() -> int:
    started = time.time()
    R: dict = {"at": time.strftime("%Y-%m-%d %H:%M:%S")}
    sw, _ = c.connect_solidworks(wait_seconds=30)
    doc = None
    try:
        doc = c.new_document(sw, "part")
        p.start_sketch(doc, plane_name="Front Plane")
        _g(
            _g(doc, "SketchManager"),
            "CreateCornerRectangle",
            -0.04,
            -0.03,
            0.0,
            0.04,
            0.03,
            0.0,
        )
        p.end_sketch(doc)
        nm = [n for n in (p.feature_names(doc) or []) if n.startswith("草图")]
        p.extrude_boss(doc, (nm[-1] if nm else "草图1"), 20.0)
        R["★_基线特征数"] = len(_feat_names(doc))
        fm = _g(doc, "FeatureManager")

        #: ★★ 旧入口：★ 与我们生产代码**逐字相同的 7 参**
        _g(doc, "ClearSelection2", True)
        R["选中边数"] = _select_one_edge(doc)
        n0 = len(_feat_names(doc))
        R["旧_FeatureFillet(195, r, 0, 0, None, None, None)"] = _try(
            _g, fm, "FeatureFillet", 195, 0.005, 0, 0, None, None, None
        )
        n1 = len(_feat_names(doc))
        R["★_旧后特征数"] = n1
        R["★_旧建成"] = "★ 是（+%d）" % (n1 - n0) if n1 > n0 else "★★ 否（没变）"

        #: ★★ 新入口：★ 15 参（★ 组 A）。★ 后 8 个官方没给默认 ⇒ **本项目工程选择**（★
        #: 照旧值填）
        _g(doc, "ClearSelection2", True)
        R["选中边数2"] = _select_one_edge(doc)
        n2 = len(_feat_names(doc))
        R["新_FeatureFillet3(15 参)"] = _try(
            _g,
            fm,
            "FeatureFillet3",
            195,  # Options
            0.005,
            0.005,
            0.005,  # Radius / R1 / R2（★ 后两个是新参 ⇒ 本项目取同值）
            0,
            0,
            0,  # 三个 Int32（★ 新参 ⇒ 取 0）
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
        )  # 8 个 Object（★ 新参 ⇒ None）
        n3 = len(_feat_names(doc))
        R["★_新后特征数"] = n3
        R["★_新建成"] = "★ 是（+%d）" % (n3 - n2) if n3 > n2 else "★★ 否（没变）"
    except Exception as exc:  # noqa: BLE001
        R["err"] = "%s: %s" % (type(exc).__name__, str(exc)[:220])
    finally:
        try:
            if doc is not None:
                _g(sw, "CloseDoc", str(_g(doc, "GetTitle") or ""))
        except Exception:  # noqa: BLE001
            pass
    R["★★_结论"] = (
        "★ 旧的能建成 ⇒ 按上轮判据**没有换的必要**"
        if str(R.get("★_旧建成", "")).startswith("★ 是")
        else "★★ 旧的建不成 ⇒ 值得试新入口"
    )
    R["seconds"] = round(time.time() - started, 2)
    OUT.write_text(
        json.dumps(R, ensure_ascii=False, indent=1, default=str), encoding="utf-8"
    )
    print("wrote", OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
