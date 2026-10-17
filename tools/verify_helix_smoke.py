r"""@brief 真机冒烟：`sw_helix` —— 验 `insert_helix` 那条路。

## 为什么挑它
`023`（轮 104）从「真缺」档补了螺旋线，**只有静态证据**。
★ 而且复查源码时发现一处**可疑**：`_newest_feature_name()` 读的是
`model.FirstFeature` —— 那是**特征树的第一个**，**不是最新的**
⇒ 它返回的"新建特征名"很可能是**错的**。本冒烟正好能验。

## 安全设计（轮 98 的模态框教训）
* **只在新零件上跑**，绝不碰用户文档；
* 前置**程序化造**：进草图 → 画一个圆 → 选中它（官方示例就是这样）；
* 先置 `CommandInProgress = True`；⚠ **事实 64**：压不住所有弹框 ⇒ **收尾查模态框**；
* 收尾：关掉自己建的件（**不保存**）。

## 判据
* `insert_helix` 能不能建成（返回什么）；
* ★ **返回的特征名到底是不是螺旋线**（用它验 `_newest_feature_name` 的疑点）；
* 任何一步抛 ⇒ **记下来**。

# ── 来源 ──
# 仓库:   本项目自身（真机验收）
# 文件:   tools/verify_helix_smoke.py
# 定位:   给 `scripts/sw_helix.py`（`023` 补的能力）取**真机**证据。
# 官方依据: `scripts/sw_helix.py` 的来源块（反射 + `C:\swapi`）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import ctypes
import ctypes.wintypes as w
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for p in (str(ROOT), str(ROOT / "scripts"), str(ROOT / "mcp-server")):
    if p not in sys.path:
        sys.path.insert(0, p)
sys.stdout.reconfigure(encoding="utf-8")

OUT = Path(Path(__file__).resolve().parents[1] / "output" / "helix-smoke-evidence.json")
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
def feature_names(model):
    """把特征树的名字逐个列出来（用于核对"新建的是哪一个"）。"""
    out = []
    try:
        f = __import__("sw_connect").get_com_member(model, "FirstFeature")
        while f is not None:
            out.append(str(__import__("sw_connect").get_com_member(f, "Name")))
            f = __import__("sw_connect").get_com_member(f, "GetNextFeature")
    except Exception:      # noqa: BLE001
        pass
    return out


def main() -> int:
    ev: dict = {"started": time.strftime("%Y-%m-%d %H:%M:%S"), "checks": {}}
    checks: list = []

    def chk(name, ok, detail):
        checks.append(bool(ok))
        ev["checks"][name] = {"ok": bool(ok), "detail": str(detail)[:300]}
        print("   %s %-44s %s" % ("✓" if ok else "**✗**", name, str(detail)[:72]))

    sw = None
    scratch = None
    try:
        import sw_connect
        sw = sw_connect.connect_solidworks(wait_seconds=10)[0]
        try:
            sw.CommandInProgress = True
        except Exception:      # noqa: BLE001
            pass
        scratch = sw_connect.new_document(sw, "part")
        chk("新建临时零件（不碰用户文档）", scratch is not None, "ok" if scratch else "建不出来")

        from scripts import sw_helix, sw_part, sw_selection_spec, sw_sketch

        def timed(fn):
            t0 = time.time()
            try:
                return True, fn(), time.time() - t0
            except Exception as exc:      # noqa: BLE001
                return False, "%s: %s" % (type(exc).__name__, str(exc)[:160]), time.time() - t0

        # ① 程序化造前置：进草图 → 画一个圆 → 选中它
        ok, r, _ = timed(lambda: sw_part.start_sketch(scratch))
        chk("start_sketch（进草图编辑态）", ok, "ok" if ok else r)
        ok2, r2, _ = timed(lambda: sw_part.sketch_circle(scratch, 0.0, 0.0, 20.0))
        chk("sketch_circle（画一个圆）", ok2, "ok" if ok2 else r2)

        skm = sw_connect.safe_get_com_member(scratch, "SketchManager")
        sketch = sw_connect.safe_get_com_member(skm, "ActiveSketch") if skm else None
        segs = []
        if sketch is not None:
            oks, rs, _ = timed(lambda: sw_sketch.get_sketch_segments(sketch))
            segs = rs if oks and isinstance(rs, list) else []
        chk("取到草图的线段（圆）", len(segs) >= 1, "%d 个线段" % len(segs))
        ev["segments"] = len(segs)

        sel = 0
        if segs:
            oksel, rsel, _ = timed(lambda: sw_selection_spec.select_object(scratch, segs[0]))
            sel = int(rsel) if oksel and isinstance(rsel, int) else 0
        chk("选中那个圆（官方示例的前置）", sel >= 1, "选区计数 = %d" % sel)

        before = feature_names(scratch)
        ev["features_before"] = before

        # ② ★ 本冒烟的核心
        okh, rh, dth = timed(lambda: sw_helix.insert_helix(
            scratch, height_mm=50.0, pitch_mm=10.0, revolution=5.0))
        chk("★ insert_helix(height=50mm, pitch=10mm, 5 圈)", okh,
            ("返回 %r · %.2fs" % (rh, dth)) if okh else rh)
        ev["returned"] = (rh if okh else None)

        after = feature_names(scratch)
        ev["features_after"] = after
        new = [f for f in after if f not in before]
        chk("★ 特征树**真的多了一个**特征", bool(new), "新增: %s" % new)

        # ★★ 验 `_newest_feature_name` 的疑点：返回的名字是不是**那个新特征**
        if okh and new:
            chk("★★ 返回的名字 == **新建的那个特征**（核 `FirstFeature` 疑点）",
                str(rh) in new,
                "返回 %r · 新增 %s · 树首 %r" % (rh, new, after[0] if after else None))
        # ★★★ 硬验证：把螺旋线的**定义读回来**，核单位换算
        #   官方：`Height` 单位是**米**、`Startangle` 是**弧度**
        #   ⇒ 传 50 mm 应当读回 0.05（而不是 50）
        if okh and new:
            def _read_def():
                feat = sw_connect.get_com_member(scratch, "FeatureByName", str(rh))
                if feat is None:
                    return None
                d = sw_connect.get_com_member(feat, "GetDefinition")
                if d is None:
                    return None
                return {
                    "height": sw_connect.safe_get_com_member(d, "Height"),
                    "pitch": sw_connect.safe_get_com_member(d, "Pitch"),
                    "revolution": sw_connect.safe_get_com_member(d, "Revolution"),
                }

            okd, rd, _ = timed(_read_def)
            ev["definition"] = rd if okd else str(rd)
            if okd and isinstance(rd, dict) and rd.get("height") is not None:
                h = float(rd["height"])
                chk("★★★ 读回 Height ≈ **0.05 米**（证明 mm→米 换算对）",
                    abs(h - 0.05) < 1e-6, "Height = %r 米（传的是 50 mm）" % h)
                p = rd.get("pitch")
                chk("★ 读回 Pitch ≈ **0.01 米**（10 mm）",
                    p is not None and abs(float(p) - 0.01) < 1e-6, "Pitch = %r" % p)
                rv = rd.get("revolution")
                chk("★ 读回 Revolution ≈ 5", rv is not None and abs(float(rv) - 5.0) < 1e-6,
                    "Revolution = %r" % rv)
            else:
                chk("读回螺旋线定义（拿不到就如实记）", False,
                    "取不到 GetDefinition / Height —— %s" % (rd,))

        ok, r, _ = timed(lambda: sw_part.end_sketch(scratch))
        chk("end_sketch（退出草图）", ok, "ok" if ok else r)
    except Exception as exc:      # noqa: BLE001
        chk("整体冒烟", False, "%s: %s" % (type(exc).__name__, str(exc)[:200]))
    finally:
        try:
            if sw is not None:
                sw.CommandInProgress = False
        except Exception:      # noqa: BLE001
            pass
        try:
            if scratch is not None and sw is not None:
                t = str(sw_connect.safe_get_com_member(scratch, "GetTitle") or "")
                if t:
                    sw.CloseDoc(t)
                    print("   （已关闭临时零件 %s，不保存）" % t)
        except Exception as exc:      # noqa: BLE001
            print("   ⚠ 收尾关文档失败（请人工确认）：%s" % str(exc)[:90])

    modals, _win_scanned = modal_dialogs()
    chk("★ 收尾无残留模态框（已知事实 64 的检查）", (not modals) and _win_scanned > 0,
        "扫了 %d 个窗口 · %s" % (_win_scanned, "无模态框" if not modals else "有 %d 个: %s" % (len(modals), modals)))

    ev.update(passed=sum(1 for c in checks if c), total=len(checks),
              verdict="pass" if checks and all(checks) else "fail",
              finished=time.strftime("%Y-%m-%d %H:%M:%S"))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(ev, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print()
    print("  ── %d/%d · verdict: %s ──" % (ev["passed"], ev["total"], ev["verdict"]))
    print("  ⚠ 只证「建成了 + 名字对得上」；**不证螺距/圈数/单位都正确**。")
    return 0 if ev["verdict"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
