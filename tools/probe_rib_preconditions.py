r"""@brief 探针：`InsertRib` 的**前置形态** —— 三个变体一次试掉（`rib` 真机失败的收敛）。

## ★★★ 为什么这三个变体（★ 每条都有依据）
```
★ 官方 `IFeatureManager.InsertRib` 的 `ReferenceEdgeIndex` 说明是
  「**Edge in the sketch** to use to determine the **material direction**」——
  ★★ 即「**草图里的一条边**」，那是**实体**（不是草图特征）。
★ 而本项目 `sw_selection_spec.py` 记着：★ **实体没有名字**（按名字选对实体不成立）·
  `edge.Select4(False, callout)` 能选（计数 1）· `__current_selection__`「对 AI 驱动最自然」。
⇒ ★ 变体（★ 三个，各改一个量）：
    A. **草图特征被选** + `ReferenceEdgeIndex = 0`     ← ★ 当前能力层的行为（已知失败）
    B. **草图特征被选** + `ReferenceEdgeIndex = 1`     ← ★ 试"索引从 1 起"
    C. **`__current_selection__`**（先把草图层/边选上，mark=1）+ `ReferenceEdgeIndex = 0`
⇒ ★★ 判据（★ 事先规定 —— 事实 165 第 12 条）：★ **看特征树里有没有多出一个"筋"**
   （★ 用**条数**与**名字**两个独立证据，照 `verify_dome_smoke.py` 的写法）。
```

## ⚠ 安全
只在新零件上跑 · `CommandInProgress` 抑制弹窗 · 关件不保存 · **不跑仿真** ·
★ 每个变体用**一个新零件**（★ 免得前一个的失败影响后一个）。

# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（真机探针）
# 文件:   tools/probe_rib_preconditions.py
# 定位:   收敛 `rib` 的真机失败（24h 段 3 续）；产物 `output/rib-preconditions.json`。
# 官方依据: `C:\swapi\types\IFeatureManager\InsertRib.md`（10 参数说明）·
#          `C:\swapi\types\IModelDoc2\InsertRib.md`（Obsolete）
# 许可:   本仓库 MIT。无第三方代码引入。
# ⚠ 真机脚本：跑之前确认只有一个 SolidWorks 实例（已知事实 24）。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for p in (str(ROOT), str(ROOT / "scripts"), str(ROOT / "mcp-server")):
    if p not in sys.path:
        sys.path.insert(0, p)
sys.stdout.reconfigure(encoding="utf-8")

OUT = Path(Path(__file__).resolve().parents[1] / "output" / "rib-preconditions.json")


def main() -> int:
    ev: dict = {
        "captured_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "question": "InsertRib 的真机前置形态（草图特征 vs 草图里的边 / 索引 0 vs 1）",
        "variants": {},
    }
    sw = None
    try:
        import sw_connect
        from scripts import sw_part as P, sw_feature_readback as FR

        sw = sw_connect.connect_solidworks(wait_seconds=30)[0]
        try:
            sw.CommandInProgress = True
        except Exception:  # noqa: BLE001
            pass

        def _plate_and_sketch():
            """建板 + 一个**含一条线**的草图（★ 筋的典型轮廓）⇒ 回 (doc, 草图名)。"""
            d = sw_connect.new_document(sw, "part")
            P.start_sketch(d, plane_name="Front Plane")
            P.sketch_corner_rectangle(d, -50.0, -30.0, 50.0, 30.0)
            sk = P.current_sketch_name(d)
            P.end_sketch(d)
            P.extrude_boss(d, sk, 20.0)
            #: ★ 筋的轮廓草图：在右视基准面上画一条**开放线**（典型用法）
            P.start_sketch(d, plane_name="Right Plane")
            try:
                P.sketch_centerline(d, 0.0, 0.0, 0.0, 30.0)  #: 参考中心线
            except Exception:  # noqa: BLE001
                pass
            sk2 = P.current_sketch_name(d)
            P.end_sketch(d)
            return d, sk2

        def _run(label: str, ref_index: int, use_current_selection: bool) -> dict:
            d = None
            try:
                d, sk2 = _plate_and_sketch()
                before = FR.feature_names(d)
                #: ★ 选法：A/B = 传草图名（能力层自己选草图特征）；C = 先选好再传 __curr
                #: ent_selection__
                name_arg = "__current_selection__" if use_current_selection else sk2
                if use_current_selection:
                    sw_connect.safe_get_com_member(d, "ClearSelection2", True)
                    try:
                        from scripts.sw_selection_spec import resolve_selection

                        resolve_selection(d, "index:0", "SKETCH")  #: ★ 选中那个草图
                    except Exception as exc:  # noqa: BLE001
                        ev["variants"].setdefault(label, {})["select_error"] = str(exc)[
                            :120
                        ]
                #: ★ 直接调 COM（★ 绕过能力层，好把 ref_index 换掉）
                from scripts.sw_connect import get_com_member

                fm = get_com_member(d, "FeatureManager")
                try:
                    get_com_member(
                        fm,
                        "InsertRib",
                        True,
                        False,
                        2.0,
                        int(ref_index),
                        False,
                        False,
                        False,
                        0.0,
                        True,
                        False,
                    )
                    err = None
                except Exception as exc:  # noqa: BLE001
                    err = "%s: %s" % (type(exc).__name__, str(exc)[:160])
                after = FR.feature_names(d)
                rb = FR.feature_readback(d, "筋1")
                out = {
                    "name_arg": name_arg,
                    "ref_index": int(ref_index),
                    "call_error": err,
                    "features_before": before,
                    "features_after": after,
                    "count_delta": len(after) - len(before),
                    "rib_present": rb.get("present"),
                    "ok": err is None and (len(after) > len(before)),
                }
                ev["variants"][label] = out
                print(
                    "  [%s] ref_index=%d · 调用错误=%s · 特征 %d→%d · 筋在=%s"
                    % (
                        label,
                        ref_index,
                        (err or "无")[:40],
                        len(before),
                        len(after),
                        rb.get("present"),
                    )
                )
                return out
            except Exception as exc:  # noqa: BLE001
                ev["variants"][label] = {
                    "ok": False,
                    "error": "%s: %s" % (type(exc).__name__, str(exc)[:180]),
                }
                print("  [%s] ★ 异常: %s" % (label, str(exc)[:70]))
                return ev["variants"][label]
            finally:
                try:
                    if d is not None:
                        t = str(sw_connect.safe_get_com_member(d, "GetTitle") or "")
                        if t:
                            sw.CloseDoc(t)
                except Exception:  # noqa: BLE001
                    pass

        _run("A_sketch_feature_index0", 0, False)
        _run("B_sketch_feature_index1", 1, False)
        _run("C_current_selection_index0", 0, True)

        ok = [k for k, v in ev["variants"].items() if v.get("ok")]
        ev["verdict"] = {
            "variants_tried": list(ev["variants"]),
            "variants_that_built_a_feature": ok,
            "★": (
                "★ 若有任一变体建出了特征 ⇒ **那就是正确的前置形态**；"
                "★ 若全失败 ⇒ 三个候选都排除，★ **如实记下并停手**（事实 53）"
            ),
        }
        print("  ── 判读 ──")
        print("     %s" % json.dumps(ev["verdict"], ensure_ascii=False)[:260])
    except Exception as exc:  # noqa: BLE001
        ev["error"] = "%s: %s" % (type(exc).__name__, str(exc)[:240])
    finally:
        try:
            if sw is not None:
                sw.CommandInProgress = False
        except Exception:  # noqa: BLE001
            pass

    if ev.get("error"):
        print("  ⚠ error: %s" % ev["error"])
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(
        json.dumps(ev, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print("  证据: %s" % OUT)
    return 0 if not ev.get("error") else 1


if __name__ == "__main__":
    raise SystemExit(main())
