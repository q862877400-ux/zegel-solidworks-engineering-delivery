r"""@brief 诊断：`InsertDome` 到底该怎么调？（轮 143，第 3 次终于对了之前先诊断）

## 已知
* 官方签名 `void IModelDoc2.InsertDome(double Height, bool ReverseDir, bool DoEllipticSurface)`
* 官方 Remarks：**选面必须用 mark=1**
* 实测：mark=1 选面**成功**（`SelectByID2` 返回 True），但 `InsertDome` 仍报
  **`0x8002000F` = `DISP_E_PARAMNOTOPTIONAL`（"非选择性的参数"）**

## 本探针做**四个**对照（一次把可能性排开）
1. `get_com_member(model,"InsertDome")` 得到的对象**是什么**（类型/来源）；
2. **直接** `model.InsertDome(8.0, False, False)`（不经 `get_com_member`）；
3. 传 **3 个** vs **4 个** 实参（看错误变不变）；
4. ★ 顺带修掉**特征树遍历**（`GetFeatureCount` 那条也返回 0）：
   试 `model.GetFeatureCount(True)` / `(False)` / 用 `IFeature` 走 `FirstFeature`。

# ── 来源 ──
# 仓库:   本项目自身（真机诊断）
# 文件:   tools/diag_insert_dome.py
# 定位:   给 Spec Kit `062` 定位 `InsertDome` 的正确调用形态。
# 官方依据: `C:\swapi\types\IModelDoc2\InsertDome.md`；`examples\...Dome...CSharp.md`
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

OUT = Path(Path(__file__).resolve().parents[1] / "output" / "diag-insert-dome.json")
W, H, D = 100.0, 60.0, 20.0


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


def main() -> int:
    ev: dict = {"started": time.strftime("%Y-%m-%d %H:%M:%S"), "probes": {}}
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
        sw_part.start_sketch(doc)
        sw_part.sketch_corner_rectangle(doc, 0.0, 0.0, W, H)
        sw_part.end_sketch(doc)
        sw_part.extrude_boss(doc, "草图1", D)

        #: ── ⓪ 先修清"特征树怎么数" ──────────────────────────────
        print("  ── ⓪ 特征树计数法对照 ──")
        for label, fn in (
            ("GetFeatureCount(True)", lambda: doc.GetFeatureCount(True)),
            ("GetFeatureCount(False)", lambda: doc.GetFeatureCount(False)),
        ):
            try:
                v = fn()
                print("     %-24s ⇒ %r" % (label, v))
                ev["probes"][label] = str(v)
            except Exception as exc:  # noqa: BLE001
                print("     %-24s ⇒ EXC: %s" % (label, str(exc)[:60]))
                ev["probes"][label] = "EXC: %s" % str(exc)[:60]
        try:
            f = doc.FirstFeature()
            names = []
            while f is not None and len(names) < 12:
                names.append(str(f.Name))
                f = f.GetNextFeature()
            print("     FirstFeature 走链           ⇒ %r" % (names,))
            ev["probes"]["firstfeature_chain"] = names
        except Exception as exc:  # noqa: BLE001
            print("     FirstFeature 走链           ⇒ EXC: %s" % str(exc)[:60])

        #: ── ① 选面（mark=1）────────────────────────────────────
        callout = sw_part._empty_callout()
        doc.Extension.SelectByID2("", "FACE", W / 2, H / 2, D, True, 0, callout, 0)
        doc.ClearSelection2(True)
        ok = doc.Extension.SelectByID2(
            "", "FACE", W / 2, H / 2, D, False, 1, callout, 0
        )
        print()
        print("  ── ① 选面 mark=1 ⇒ %s ──" % ok)
        ev["probes"]["select_mark1"] = bool(ok)

        #: ── ② `get_com_member` 拿到的是什么 ─────────────────────
        print()
        print("  ── ② 成员解析对照 ──")
        gm = (
            sw_connect.safe_get_com_member(doc, "InsertDome")
            if hasattr(sw_connect, "safe_get_com_member")
            else getattr(doc, "InsertDome", None)
        )
        print("     get_com_member → %r" % (type(gm).__name__,))
        ev["probes"]["get_com_member_type"] = type(gm).__name__
        raw = getattr(doc, "InsertDome", None)
        print("     getattr(doc) → %r" % (type(raw).__name__,))
        ev["probes"]["getattr_type"] = type(raw).__name__

        #: ── ③ 三种调法对照 ─────────────────────────────────────
        print()
        print("  ── ③ 调法对照（每次都重选一次面）──")
        for label, caller in (
            ("get_com_member(3 参)", lambda: gm(DOME_H, False, False)),
            ("getattr 直调(3 参)", lambda: raw(DOME_H, False, False)),
            ("getattr 直调(4 参)", lambda: raw(DOME_H, False, False, False)),
        ):
            doc.Extension.SelectByID2("", "FACE", W / 2, H / 2, D, True, 0, callout, 0)
            doc.ClearSelection2(True)
            doc.Extension.SelectByID2("", "FACE", W / 2, H / 2, D, False, 1, callout, 0)
            try:
                r = caller()
                print("     %-24s ⇒ 返回 %r ✓" % (label, r))
                ev["probes"]["call_" + label] = "ok: %r" % (r,)
            except Exception as exc:  # noqa: BLE001
                print(
                    "     %-24s ⇒ %s: %s" % (label, type(exc).__name__, str(exc)[:66])
                )
                ev["probes"]["call_" + label] = "EXC: %s" % str(exc)[:70]
    except Exception as exc:  # noqa: BLE001
        print("  ⚠ 诊断出错：%s: %s" % (type(exc).__name__, str(exc)[:160]))
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
        except Exception:  # noqa: BLE001
            pass
        print()
        print("   （临时零件已关闭，不保存）")

    modals, _win_scanned = modal_dialogs()
    print(
        "   收尾模态框: %s（扫了 %d 个窗口）"
        % ("无" if not modals else modals, _win_scanned)
    )
    ev["modal_dialogs"] = modals
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(
        json.dumps(ev, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return 0


DOME_H = 8.0

if __name__ == "__main__":
    raise SystemExit(main())
