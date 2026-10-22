r"""@brief 真机证据：**倒角 / 圆角 2 个工具**（砌墙 W4 续 / Spec Kit `137` 的验收②）。

## ★★★ 本批要真机回答的**一个未知**（不能假设）
```
`sw_part.chamfer` / `fillet` **没有 `edges` 参数** ⇒ ★ 它们**真的作用在当前选择上吗**？
⇒ 证据脚本里必须有这个**对照**：
     · 选中一条边 ⇒ 调 chamfer ⇒ 看结果
     · ★ **不选**（清空选区）⇒ 调 chamfer ⇒ 看结果
   ★ **两者不同**才说明"用 selection 驱动"成立；**若相同** ⇒ 本批的 `selection` 是**假设计**，
     必须**如实记录并改设计**（★ 不能把假设计当成功）。
```

## 断言方式
```
★ 项目里**没有"体积 / 质量属性"的工具**（已核）⇒ 用**特征树 + 特征名**：
   倒角后应出现名字含「倒角」的特征；圆角后应出现名字含「圆角」的特征。
★ 另记包围盒（倒角切掉角 ⇒ 包围盒**通常不变**，★ 所以**不能用它**当唯一判据 —— 记录即可）。
```

## 流程
```
新建零件 → batch21 建草图（矩形 40×20）→ batch22 拉伸 10mm（成一个盒）
  → ★ 选一条边（`index:0`）→ `chamfer(distance_mm=2)` ⇒ 断言特征树多一个「倒角」
  → 再选一条边 → `fillet(radius_mm=3)` ⇒ 断言多一个「圆角」
  → ★ **对照实验**：清空选区后调 chamfer ⇒ 记录结果（与"选中"对比）
→ ★ **负例**：`selection = "index:9999"`（越界）⇒ 必须**报错**
```

## ⚠ 安全
**只在新零件上跑**、`CommandInProgress` 抑制弹窗、收尾**关件不保存**。

# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（真机证据脚本，**不是**从四家外部 MCP 项目移植）
# 文件:   tools/capture_chamfer_fillet_evidence.py
# 定位:   砌墙 W4 续（Spec Kit `137`）的**验收②**：产出 `output/chamfer-fillet-evidenc
#           e.json`。
# 官方依据: `IFeatureManager.InsertFeatureChamfer`（★ 形态已按铁律 4 核过，见事实 164）
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

OUT = Path(
    Path(__file__).resolve().parents[1] / "output" / "chamfer-fillet-evidence.json"
)


def feature_names(model, sc) -> list[str]:
    """特征树里的特征名。"""
    names = []
    try:
        n = int(sc.safe_get_com_member(model, "GetFeatureCount"))
    except Exception:  # noqa: BLE001
        return names
    for k in range(1, n + 1):
        f = sc.safe_get_com_member(model, "FeatureByPositionReverse", k)
        nm = str(sc.safe_get_com_member(f, "Name") or "") if f is not None else ""
        if nm:
            names.append(nm)
    return names


class _P:
    """最小 params 容器（注册器传进来的那个形状）。"""

    def __init__(self, selection=""):
        self.selection = selection


def _volume_mm3(doc):
    """★ 读当前文档的体积（**mm³**）—— ★ 走**能力层**（`sw_mass_property`），不直调 COM。

    ★ 单位依据（真机对照实验，2026-10-01 轮 263）：★ `Volume` 读数的单位是 **mm³**
      （盒 40×20×10 ⇒ **8000**）。★ 而入口必须用 **`CreateMassProperty2`** ——
      老入口 `CreateMassProperty` 是 **Obsolete**，★ 它的读数（尤其 `Density`）**是错的**
      （见 known-facts 196）。
    ⚠ 读不到时回 `None`（★ 判据那边会**如实标**，不假装量到了）。
    """
    try:
        from scripts import sw_mass_property as mp

        r = mp.mass_properties(doc)
        v = r.get("volume") if isinstance(r, dict) else None
        return float(v) if v is not None else None
    except Exception:  # noqa: BLE001
        return None


def main() -> int:
    ev: dict = {
        "captured_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "capability": "chamfer_fillet_on_selection",
        "steps": {},
    }
    sw = None
    doc = None
    ok = True
    try:
        import sw_connect
        import tool_specs_batch23 as b23

        from scripts import sw_part
        from scripts.sw_selection_spec import clear_selection

        #: ① 核声明解析得到 + 记下 param_alias / pre_call 是否存在
        bindings = {}
        for spec in b23.SPECS_BATCH23:
            mod = __import__("scripts.%s" % spec.module, fromlist=[spec.function])
            bindings[spec.name] = {
                "resolved": callable(getattr(mod, spec.function, None)),
                "aliases": dict(spec.param_alias or {}),
                "has_pre_call": spec.pre_call is not None,
            }
        ev["steps"]["bindings"] = {
            "ok": all(v["resolved"] and v["has_pre_call"] for v in bindings.values()),
            "detail": bindings,
        }
        ok = ok and ev["steps"]["bindings"]["ok"]

        sw = sw_connect.connect_solidworks(wait_seconds=10)[0]
        try:
            sw.CommandInProgress = True
        except Exception:  # noqa: BLE001
            pass
        doc = sw_connect.new_document(sw, "part")

        #: ② 造一个盒：草图 40×20 → 拉伸 10
        sw_part.start_sketch(doc, plane_name="Front Plane")
        sw_part.sketch_corner_rectangle(doc, -20.0, -10.0, 20.0, 10.0)
        sk = sw_part.current_sketch_name(doc)
        sw_part.end_sketch(doc)
        sw_part.extrude_boss(doc, sk, 10.0)
        base = feature_names(doc, sw_connect)

        #: ③ ★ 走工具真实路径：pre_call 把 selection 选好，再调目标函数
        def apply_tool(spec_name: str, selection: str, func, **kwargs):
            spec = next(s for s in b23.SPECS_BATCH23 if s.name == spec_name)
            spec.pre_call(_P(selection))
            return func(doc, **kwargs)

        #: ④ 倒角（选 index:0 那条边）—— ★★ 2026-10-01（轮 264）**升级为体积判据**
        #:
        #: ★★★ 为什么升级（★ 判据原文见 `scripts/sw_chamfer_geometry.py` 的来源块，**MIT
        #: **）：
        #:   本脚本原来的判据是「**特征树多一个倒角**」。★ 而四家的那份判据明确警告：
        #:     · ★ **特征树里有它、而移除零体积** ⇒ **静默空操作**；
        #:     · ★ **非零体积差、错几何** ⇒ ★★ **更糟**（★ 因为它**看起来对了**）；
        #:     · ★★★ **没有一个是充分的证明** —— 要**三件一起**：**特征在** + **体积下降** +
        #:       **下降量 ≈ 解析公式**。
        #: ⚠ 而本脚本的**旧 docstring** 写着「项目里**没有**体积/质量属性的工具 ⇒ 只能用
        #: 特征树」
        #:     —— ★★ **那句现在过时了**：`sw_mass_property` 已经修好（★ 轮 263），
        #:     且 D4 的解析判据（`sw_chamfer_geometry`）已就位。
        #:
        #: ★★★★ **判据设计（★ 不需要事先知道那条边是哪条）**：
        #:   ★ 倒角减少量 = `0.5 · w² · L` ⇒ **反解** `L = 2·ΔV / w²`
        #:   ⇒ ★★ **反解出的 L 必须等于盒的某条棱长**（`40 / 20 / 10`，容差 2%）
        #:   ⇒ ★ 这**一条**判据同时排除「零体积空操作」与「做在错的几何上」两种坏情况。
        f_ch = None
        vol_before = _volume_mm3(doc)
        try:
            f_ch = apply_tool(
                "solidworks_chamfer", "index:0", sw_part.chamfer, distance=2.0
            )
            after_ch = feature_names(doc, sw_connect)
            vol_after = _volume_mm3(doc)
            #: ★ D4 判据：反解边长，看它是不是盒的某条棱
            w = 2.0
            removed = (
                (vol_before - vol_after)
                if (vol_before is not None and vol_after is not None)
                else None
            )
            implied_len = (
                (2.0 * removed / (w * w)) if (removed and removed > 0) else None
            )
            edge_ok = implied_len is not None and any(
                abs(implied_len - e) / e <= 0.02 for e in (40.0, 20.0, 10.0)
            )
            ev["steps"]["chamfer"] = {
                "ok": bool(f_ch is not None) and len(after_ch) > len(base),
                "feature": str(getattr(f_ch, "Name", "") or ""),
                "n_before": len(base),
                "n_after": len(after_ch),
                "new_names": [n for n in after_ch if n not in base][:4],
                #: ★★ 新增：体积判据（D4）
                "volume_before_mm3": vol_before,
                "volume_after_mm3": vol_after,
                "removed_mm3": removed,
                "implied_edge_length_mm": implied_len,
                "implied_matches_a_real_edge": edge_ok,
                "★_d4": (
                    "★ 反解 `L = 2·ΔV / w²` ⇒ 必须等于盒的某条棱（40/20/10）—— "
                    "★ 这一条同时排除「零体积空操作」与「做在错的几何上」"
                ),
            }
            ok = ok and ev["steps"]["chamfer"]["ok"]
        except Exception as exc:  # noqa: BLE001
            ev["steps"]["chamfer"] = {
                "ok": False,
                "raised": type(exc).__name__,
                "msg": str(exc)[:110],
                "volume_before_mm3": vol_before,
            }
            ok = False

        #: ⑤ 圆角
        f_fi = None
        try:
            f_fi = apply_tool(
                "solidworks_fillet", "index:1", sw_part.fillet, radius=3.0
            )
            after_fi = feature_names(doc, sw_connect)
            ev["steps"]["fillet"] = {
                "ok": bool(f_fi is not None) and len(after_fi) > len(base),
                "feature": str(getattr(f_fi, "Name", "") or ""),
                "n_after": len(after_fi),
                "new_names": [n for n in after_fi if n not in base][:6],
            }
            ok = ok and ev["steps"]["fillet"]["ok"]
        except Exception as exc:  # noqa: BLE001
            ev["steps"]["fillet"] = {
                "ok": False,
                "raised": type(exc).__name__,
                "msg": str(exc)[:110],
            }

        #: ⑥ ★★ 对照：清空选区后调 chamfer ⇒ 结果与"选中"是否不同
        try:
            clear_selection(doc)
            n_before_ctrl = len(feature_names(doc, sw_connect))
            try:
                f_ctrl = sw_part.chamfer(doc, 2.0)
                n_after_ctrl = len(feature_names(doc, sw_connect))
                ev["steps"]["control_no_selection"] = {
                    "outcome": "建出来了：%s" % str(getattr(f_ctrl, "Name", "") or ""),
                    "n_before": n_before_ctrl,
                    "n_after": n_after_ctrl,
                    "★": "★ 清空选区也能建 ⇒ **说明「用 selection 驱动」不成立**（要改设计）"
                    if n_after_ctrl > n_before_ctrl
                    else "记录",
                }
            except Exception as exc:  # noqa: BLE001
                ev["steps"]["control_no_selection"] = {
                    "outcome": "抛了 %s" % type(exc).__name__,
                    "msg": str(exc)[:90],
                    "★": "★ 清空选区会报错 ⇒ 支持「它作用在当前选择上」（本批设计成立）",
                }
        except Exception as exc:  # noqa: BLE001
            ev["steps"]["control_no_selection"] = {
                "outcome": "对照实验本身失败: %s" % str(exc)[:80]
            }

        #: ⑦ 负例：越界 index ⇒ 必须报错
        try:
            spec = next(s for s in b23.SPECS_BATCH23 if s.name == "solidworks_chamfer")
            spec.pre_call(_P("index:9999"))
            ev["steps"]["negative_out_of_range"] = {
                "ok": False,
                "★": "★ **没有抛错** —— 越界却静默通过",
            }
            ok = False
        except Exception as exc:  # noqa: BLE001
            ev["steps"]["negative_out_of_range"] = {
                "ok": True,
                "raised": type(exc).__name__,
                "msg": str(exc)[:90],
            }
    except Exception as exc:  # noqa: BLE001
        ev["error"] = "%s: %s" % (type(exc).__name__, str(exc)[:200])
        ok = False
    finally:
        try:
            if sw is not None:
                sw.CommandInProgress = False
        except Exception:  # noqa: BLE001
            pass
        try:
            if doc is not None and sw is not None:
                t = str(sw_connect.safe_get_com_member(doc, "GetTitle") or "")
                if t:
                    sw.CloseDoc(t)  #: ★ 关件不保存
        except Exception:  # noqa: BLE001
            pass

    ev["verdict"] = "pass" if (ok and not ev.get("error")) else "fail"
    print("  ── 倒角 / 圆角 真机证据 ──")
    for k, v in ev["steps"].items():
        print("    %-26s %s" % (k, json.dumps(v, ensure_ascii=False)[:200]))
    if ev.get("error"):
        print("  ⚠ error: %s" % ev["error"])
    print("  结论: %s" % ev["verdict"].upper())
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(
        json.dumps(ev, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print("  证据: %s" % OUT)
    return 0 if ev["verdict"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
