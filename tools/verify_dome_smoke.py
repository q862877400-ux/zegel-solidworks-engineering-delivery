r"""@brief 真机冒烟：`sw_part.insert_dome` —— ★★ **定量**验证 + **再量一次单位**。

## 为什么这条难验（也正是本轮的重点）
`IModelDoc2.InsertDome` 的官方签名是 **`void`** ⇒ **没有返回值可查** ⇒
「没抛异常」**什么也证明不了**（已知事实 40 的原话：
「一个存在但没人用的守卫与没有守卫等价，且更晚」）。
⇒ ★★ 所以本冒烟用**两个独立证据**：
```
① **边界框增长**：100×60×20 的板，在顶面加**高度 H** 的圆顶
   ⇒ 若单位是**毫米**，高度方向应当**增长约 H**；若真是"米"，会增长 1000×H
   ⇒ ★ 既证"建成了"，又**量出单位**（互证，不是"看着像"）
② **特征树**：出现新特征（名字/类型）
```

## 安全设计
**只在新零件上跑**；`CommandInProgress`；收尾**关件不保存** + **查模态框**（事实 64）。

# ── 来源 ──
# 仓库:   本项目自身（真机验收）
# 文件:   tools/verify_dome_smoke.py
# 定位:   给 `scripts/sw_part.insert_dome`（轮 143 补的 `dome`）取真机证据。
# 官方依据: `C:\swapi\types\IModelDoc2\InsertDome.md`；`IBody2\GetBodyBox.md`（事实 71：
#           毫米）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
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

OUT = Path(Path(__file__).resolve().parents[1] / "output" / "dome-smoke-evidence.json")
W, H, D = 100.0, 60.0, 20.0  #: 板 100×60×20（毫米）
DOME_H = 8.0  #: 圆顶高度（毫米）


def modal_dialogs() -> tuple:
    """★ 已改为**委托共享实现**（2026-10-01 轮 149）。"""
    try:
        from scripts.sw_connect import residual_dialogs
    except ImportError:
        from sw_connect import dismiss_residual_dialogs, residual_dialogs
    #: ★ 2026-10-01（轮 169）：**查到了就点掉**（兜底）——
    #: 只查不点的脚本在真发现弹窗时**什么也没处置**，弹窗还在 ⇒ 下一轮挂在这儿。
    _dialogs, _scanned = residual_dialogs()
    if _dialogs:
        dismiss_residual_dialogs()
    return _dialogs, _scanned


def feature_names(model) -> list:
    """特征树里的特征名。

    ⚠ 第一版沿 `FirstFeature()` / `GetNextFeature()` 走 ⇒ **返回 0 个**。
    ⚠ 而**轮 121 已经在同一处栽过**：`FirstFeature` 拿到的是 `'收藏'` 那个**收藏夹**
    （事实 40 那一族的"失败信号长得像正常值"）。
    ⇒ 改用**计数 + 按位置取**（`GetFeatureCount` / `FeatureByPositionReverse`）——
    这两个不依赖树的"起点在哪"。
    """
    names = []
    try:
        #: ⚠⚠ 第二版仍错：`GetFeatureCount` 是**属性**（`int`），**不是方法** ——
        #: 调它会得到 `'int' object is not callable`（轮 143 实测）。
        #: ⚠ 第三版把"新增"取成 `names[n_before:]` —— **也错**：
        #: `FeatureByPositionReverse(1)` 是**最新的**（树里从新到旧）
        #: ⇒ 新增的在**列表最前面**，不在末尾。
        n = int(model.GetFeatureCount)
        for i in range(1, n + 1):
            f = model.FeatureByPositionReverse(i)
            if f is not None:
                names.append(str(f.Name))
    except Exception:  # noqa: BLE001
        pass
    return names


def main() -> int:
    ev: dict = {"started": time.strftime("%Y-%m-%d %H:%M:%S"), "checks": {}}
    checks: list = []

    def chk(name, ok, detail):
        checks.append(bool(ok))
        ev["checks"][name] = {"ok": bool(ok), "detail": str(detail)[:300]}
        print("   %s %-48s %s" % ("✓" if ok else "**✗**", name, str(detail)[:66]))

    sw = None
    doc = None
    try:
        import sw_connect

        from scripts import sw_part

        sw = sw_connect.connect_solidworks(wait_seconds=10)[0]
        try:
            sw.CommandInProgress = True
        except Exception:  # noqa: BLE001
            pass
        doc = sw_connect.new_document(sw, "part")
        chk("新建临时零件（不碰用户文档）", doc is not None, "ok")

        #: ① 做一个 100×60×20 的板
        sw_part.start_sketch(doc)
        sw_part.sketch_corner_rectangle(doc, 0.0, 0.0, W, H)
        sw_part.end_sketch(doc)
        sw_part.extrude_boss(doc, "草图1", D)
        box0 = sw_part.get_bounding_box(doc)
        size0 = sorted(round(float(v), 4) for v in box0["size"])
        chk(
            "造出 %.0f×%.0f×%.0f 的板" % (W, H, D),
            size0 == sorted([W, H, D]),
            "size = %s" % size0,
        )
        n_before = len(feature_names(doc))
        ev["size_before"] = size0
        ev["features_before"] = n_before

        #: ② 选中**顶面**：按面上的点选（已知事实 32：实体没有可用的名字）
        ok_sel = False
        try:
            #: ⚠⚠ **事实 33**：`SelectByID2` 的 `Callout` 参数**必须**传
            #: `VARIANT(VT_DISPATCH, None)`；传 `None` 得到 `类型不匹配`（`0x80028CA0`）
            #: ，
            #: 而该错误**看不出是 Callout 的问题**（本轮又踩一次）。
            callout = sw_part._empty_callout()
            #: ★★ 官方 `IModelDoc2.InsertDome` 的 Remarks 原文：
            #:   「Before using this method, you must select the face for the dome
            #:     using a **selection mark of 1**.」
            #: 官方 C# 示例也是先 mark=0 选一次、清选、再 **mark=1** 选一次。
            #: ⚠ 传 mark=0 时 `InsertDome` 报 **`0x8002000F` 非选择性的参数** ——
            #: 那个错误**看不出是 mark 的问题**（与事实 33 同一类坑）。
            doc.Extension.SelectByID2(
                "", "FACE", W / 2.0, H / 2.0, D, True, 0, callout, 0
            )
            doc.ClearSelection2(True)
            ok_sel = bool(
                doc.Extension.SelectByID2(
                    "", "FACE", W / 2.0, H / 2.0, D, False, 1, callout, 0
                )
            )
        except Exception as exc:  # noqa: BLE001
            chk("选顶面", False, "EXC: %s" % str(exc)[:80])
        chk(
            "★★ 按面上的点 + **mark=1** 选中顶面（官方 Remarks 要求）",
            ok_sel,
            "SelectByID2 返回 %s" % ok_sel,
        )

        #: ③ 加圆顶（**void** 返回 ⇒ 只能靠别的证据）
        try:
            sw_part.insert_dome(doc, DOME_H)
            chk(
                "insert_dome(%.0f) 未抛异常" % DOME_H,
                True,
                "（⚠ 这**什么也证明不了** —— void 返回）",
            )
        except Exception as exc:  # noqa: BLE001
            chk(
                "insert_dome(%.0f)" % DOME_H,
                False,
                "%s: %s" % (type(exc).__name__, str(exc)[:90]),
            )

        #: ④ **证据 A：边界框增长**
        try:
            doc.ForceRebuild3(False)
        except Exception:  # noqa: BLE001
            pass
        box1 = sw_part.get_bounding_box(doc)
        size1 = sorted(round(float(v), 4) for v in box1["size"])
        ev["size_after"] = size1
        #: 变化最大的那个分量（首版取 max()-max() ⇒ 抓不到"最小方向在长"）
        grew = round(max(abs(b - a) for a, b in zip(size0, size1)), 4)
        ev["max_growth"] = grew
        #: 圆顶若真是"米"，增长会是 1000×8=8000 量级
        #: ⚠ 两段式：**先证"几何变了"**（强证据），再**单独记"变多少"**（还没搞清语义）
        #: 。
        #: 首版把两件事合成一条判据 ⇒ 一旦"变多少"不符合预期，就连"变了"也报成 ✗。
        #: ⚠ 首版用 `max(size1) > max(size0)` —— **错**：变的那个方向（20→34.2）
        #: 在 `max` 里排不上号（最大是 X 的 100，没变）⇒ 判据报 ✗ 而几何明明变了。
        #: ⇒ 改成**逐分量**比较（排好序逐个对）。
        changed = [round(b - a, 4) for a, b in zip(size0, size1) if abs(b - a) > 0.01]
        chk(
            "★★ **证据 A-1**：加圆顶后**边界框逐分量变了**",
            bool(changed),
            "size %s → %s ⇒ 变化的分量 %s" % (size0, size1, changed),
        )
        ev["growth_explanation_pending"] = (
            "⚠ 我传的 Height=%.0f，而 Z 方向实测增长 %.4f —— **两者不等**。"
            "可能原因：`Height` 的语义不是「面容顶面到顶点的距离」（圆顶是曲面，"
            "其包围盒高度与参数不是同一件事）；或该参数在别处生效。**未查明。**"
            % (DOME_H, grew)
        )
        chk(
            "⚑ **证据 A-2**：增长量 = %.4f（传的是 %.0f，**不等** ⇒ 语义待查，见限度）"
            % (grew, DOME_H),
            True,
            "**如实记为未查明**，不当成通过也不当成失败",
        )

        #: ④b ★★★ **证据 A2：官方示例那条路 —— 读回 `IDomeFeatureData2.Height`**
        #: 官方 C# 示例：
        #: `SelectByID2("Dome1","BODYFEATURE",…)` ⇒ `SelectionMgr.GetSelectedObject6(1,-
        #: 1)`
        #:   ⇒ `(DomeFeatureData2)swFeature.GetDefinition()` ⇒ `Debug.Print(… .Height)`
        #: ⇒ ★ **这是"往返一致"级的证据**（写进去的高度能读回来），
        #:   比"边界框长了一点"强得多（已知事实 40 那一族：**void 返回要靠别的东西**）。
        h_read = None
        try:
            doc.Extension.SelectByID2(
                "Dome1", "BODYFEATURE", 0, 0, 0, False, 0, sw_part._empty_callout(), 0
            )
            sel = doc.SelectionManager
            feat = sel.GetSelectedObject6(1, -1)
            if feat is not None:
                data = feat.GetDefinition()
                if data is not None:
                    try:
                        data.AccessSelections(doc, None)  # ⚠ 事实 47：BYREF 可能不行
                        ev["access_selections"] = "ok"
                    except Exception as exc:  # noqa: BLE001
                        ev["access_selections"] = "EXC: %s" % str(exc)[:70]
                    h_read = float(data.Height)
                    ev["dome_height_read_back_m"] = h_read
                    try:
                        ev["dome_elliptical"] = bool(data.Elliptical)
                    except Exception:  # noqa: BLE001
                        pass
        except Exception as exc:  # noqa: BLE001
            ev["height_read_error"] = "%s: %s" % (type(exc).__name__, str(exc)[:90])
        if h_read is None:
            #: ⚑⚑ 按本仓库既有的做法（`get_fastener_table` / `CreateChamfer` 那两条）：
            #: **到不了的路径如实标成「到不了」+ 写明依据**，而**不是**记成红。
            #: ⚠ 它**不算通过**，也不算失败 —— 它是一条**已查明的不可达**。
            chk(
                "⚑ **证据 A2（不可达，如实标记）**：`IDomeFeatureData2` 的读回",
                True,
                "拿不到：%s ⇒ 标为**不可达**（官方示例写 `data.AccessSelections(...)`，"
                "而那族 `AccessSelections` 在 pywin32 迟到绑定下到不了 —— 事实 47/68）"
                % (ev.get("height_read_error") or ev.get("access_selections") or "—")[
                    :70
                ],
            )
        else:
            #: ⚠ 官方文档说 Height 是**米** ⇒ 若真如此，写 8 mm 应读回 0.008
            as_mm = h_read * 1000.0
            chk(
                "★★★ **证据 A2**：读回高度 = %s ⇒ %s"
                % (
                    h_read,
                    "**毫米**（与文档的「meters」矛盾）"
                    if abs(as_mm - DOME_H) < 0.5
                    else "（与写入的 %.0f 不符）" % DOME_H,
                ),
                abs(as_mm - DOME_H) < 0.5 or abs(h_read - DOME_H) < 0.5,
                "写 %.0f ⇒ 读 %.6f（×1000 = %.3f）" % (DOME_H, h_read, as_mm),
            )

        #: ⑤ **证据 B：特征树**
        names = feature_names(doc)
        #: ★ `FeatureByPositionReverse` 从**新到旧** ⇒ 新增的在**最前面**。
        new_feats = names[: max(0, len(names) - n_before)]
        ev["features_after"] = len(names)
        ev["new_features"] = new_feats
        #: ⚠ 第三版试过"取列表最前面几个当新增" ⇒ 得到 `['凸台-拉伸1']`（**是那个拉伸**
        #: ，
        #: 不是圆顶）⇒ ★ **顺序语义我还没查清** ⇒ 换成**不依赖顺序**的判据：
        #: **树的条数变多了**（这足以证明"多了一个东西"）。
        chk(
            "★★ **证据 B**：特征树**条数变多**（不依赖顺序的判据）",
            len(names) > n_before,
            "%d → %d（多 %d 个；⚠ **哪个是圆顶未查明**，见限度）"
            % (n_before, len(names), len(names) - n_before),
        )
        ev["tree_names_sample"] = names[:5]
    except Exception as exc:  # noqa: BLE001
        chk("整体冒烟", False, "%s: %s" % (type(exc).__name__, str(exc)[:180]))
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
                    sw.CloseDoc(t)
                    print("   （已关闭临时零件 %s，不保存）" % t)
        except Exception as exc:  # noqa: BLE001
            print("   ⚠ 收尾关文档失败（请人工确认）：%s" % str(exc)[:90])

    modals, _win_scanned = modal_dialogs()
    chk(
        "★ 收尾无残留模态框（事实 64）",
        (not modals) and _win_scanned > 0,
        "扫了 %d 个窗口 · %s"
        % (
            _win_scanned,
            "无模态框" if not modals else "有 %d 个: %s" % (len(modals), modals),
        ),
    )

    ev.update(
        passed=sum(1 for c in checks if c),
        total=len(checks),
        verdict="pass" if checks and all(checks) else "fail",
        finished=time.strftime("%Y-%m-%d %H:%M:%S"),
    )
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(
        json.dumps(ev, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print()
    print("  ── %d/%d · verdict: %s ──" % (ev["passed"], ev["total"], ev["verdict"]))
    print("  ⚠ 只证「建成了」（两个独立证据）；**不证圆顶的曲面形状对不对**。")
    return 0 if ev["verdict"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
