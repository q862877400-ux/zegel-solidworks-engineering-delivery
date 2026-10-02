r"""@brief 探针：`geometric_tolerance` 的**另一半**能不能通 —— 试**正确的顺序**。

## 背景（轮 120 的结论与它自己列的「未查证」）
轮 120 量到：
```
GetFrameCount()（新建后） = 1
AddFrame()               -> False
GetFrame(0)/(1)/(2)      -> 全 None
CanConvertFormat() -> True
ConvertFormat()    -> 0（成功）
ConvertFormat 后 GetFrameCount() = 0（从 1 掉到 0）
ConvertFormat 后 GetFrame(1)/(2) -> 仍全 None
⇒ 判「2022 格式的帧路径取不到帧」，按事实 53 停手
```

## ★★★ 本探针的假设（读官方 Remarks 读出来的）
```
官方 `IGtol.AddFrame` 的 Remarks（`C:\swapi\types\IGtol\AddFrame.md`）**原文**：
  > This method is valid only if this Gtol was created in SOLIDWORKS **2022 or later**.
⇒ ★★ 实测 `AddFrame() -> False` 恰恰说明：**那个 Gtol 在调用时还不是「2022 或更新」建的**
   （新建的 GTol 默认是旧格式）
⇒ ★★★ **正确顺序应当是**：**先 `ConvertFormat()`（升级到 2022 格式）→ 再 `AddFrame()` → 再 `GetFrame(n)`**
   —— 而轮 120 的顺序是 `AddFrame()` **先于** `ConvertFormat()` ⇒ **必然失败**
```

## 判据（能被空操作证伪）
```
① `ConvertFormat()` 返回 0（成功）
② **转换后** `AddFrame()` 返回 **True**（空操作/错序时为 False）
③ **转换后** `GetFrame(n)` 拿到**非 None** 的 frame 对象
④ 若 ③ 成就 ⇒ 再试 `IGtolFrame.AddIndicator(Int32, Int32, String)` ⇒ 真机 **add_gtol_indicator 那半通了**
```

## ⚠ 安全
**只在新零件上跑**；收尾**关件不保存** + **查模态框**。

# ── 来源 ──
# 仓库:   本项目自身（真机探针）
# 文件:   tools/probe_gtol_frame_order.py
# 定位:   给 Spec Kit `085` 验证「2022 格式帧路径」是**顺序问题**还是**真到不了**。
# 官方依据: `C:\swapi\types\IGtol\AddFrame.md`（Remarks：**2022 or later**）·
#          `IGtol\ConvertFormat.md` / `CanConvertFormat.md` · `IGtolFrame\AddIndicator.md` ·
#          出厂反射 `Object GetFrame(Int32)` / `Boolean AddFrame()` / `Int32 ConvertFormat()`
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import json
import sys
import time
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for p in (str(ROOT), str(ROOT / "scripts"), str(ROOT / "mcp-server")):
    if p not in sys.path:
        sys.path.insert(0, p)
sys.stdout.reconfigure(encoding="utf-8")

OUT = Path(r"D:\AI\SW\output\gtol-frame-order.json")
def main() -> int:
    ev: dict = {"steps": []}
    sw = None
    doc = None
    try:
        import sw_connect
        from scripts import sw_gtol
        sw = sw_connect.connect_solidworks(wait_seconds=10)[0]
        try:
            sw.CommandInProgress = True
        except Exception:      # noqa: BLE001
            pass
        doc = sw_connect.new_document(sw, "part")

        gtol = sw_gtol.insert_gtol(doc)
        print("  ① `insert_gtol()` ⇒ %s" % ("有对象" if gtol is not None else "**None**"))
        ev["insert_gtol_ok"] = gtol is not None
        if gtol is None:
            return 1

        def rd(name):
            try:
                return sw_connect.safe_get_com_member(gtol, name)
            except Exception as exc:      # noqa: BLE001
                return "EXC:%s" % str(exc)[:40]

        def rec(tag, **kw):
            ev["steps"].append({"step": tag, **kw})
            print("     %-30s %s" % (tag, {k: str(v)[:26] for k, v in kw.items()}))

        rec("新建后 GetFrameCount", count=rd("GetFrameCount"))
        rec("新建后 AddFrame()【旧顺序】", ret=rd("AddFrame"))
        rec("新建后 GetFrame(0)", got=type(rd("GetFrame", )).__name__ if False else "（见下）")

        #: ★ 关键：**先转换，再加帧**
        rec("CanConvertFormat()", ret=rd("CanConvertFormat"))
        try:
            conv = sw_connect.safe_get_com_member(gtol, "ConvertFormat")
            rec("★ ConvertFormat()【先转换】", ret=conv)
        except Exception as exc:      # noqa: BLE001
            rec("★ ConvertFormat()", exc="%s: %s" % (type(exc).__name__, str(exc)[:40]))
        rec("转换后 GetFrameCount", count=rd("GetFrameCount"))

        #: ★★ 转换**之后**再加帧
        try:
            add = sw_connect.safe_get_com_member(gtol, "AddFrame")
            rec("★★ AddFrame()【转换之后】", ret=add)
        except Exception as exc:      # noqa: BLE001
            rec("★★ AddFrame()【转换之后】", exc="%s: %s" % (type(exc).__name__, str(exc)[:40]))
        rec("加帧后 GetFrameCount", count=rd("GetFrameCount"))

        #: ③ 取帧
        frames = []
        for idx in (0, 1, 2, 3):
            try:
                f = sw_connect.safe_get_com_member(gtol, "GetFrame", idx)
            except Exception as exc:      # noqa: BLE001
                f = "EXC:%s" % str(exc)[:30]
            frames.append("有" if (f is not None and not str(f).startswith("EXC")) else str(f)[:14])
        rec("★★ GetFrame(0..3)", frames=frames)
        ev["frames"] = frames

        #: ④ 若拿到 frame ⇒ 试加指示符
        got_frame = None
        for idx in (0, 1, 2, 3):
            try:
                f = sw_connect.safe_get_com_member(gtol, "GetFrame", idx)
                if f is not None and not isinstance(f, str):
                    got_frame = f
                    break
            except Exception:      # noqa: BLE001
                pass
        if got_frame is not None:
            try:
                r = sw_connect.safe_get_com_member(got_frame, "AddIndicator", 0, 0, "A")
                rec("★★★ IGtolFrame.AddIndicator(0,0,'A')", ret=r)
                ev["add_indicator_ok"] = bool(r)
            except Exception as exc:      # noqa: BLE001
                rec("★★★ AddIndicator", exc="%s: %s" % (type(exc).__name__, str(exc)[:50]))
                ev["add_indicator_tb"] = traceback.format_exc().strip().splitlines()[-2:]
        else:
            rec("★★★ AddIndicator", skipped="**没拿到 frame**")
    except Exception as exc:      # noqa: BLE001
        ev["error"] = "%s: %s" % (type(exc).__name__, str(exc)[:160])
        print("  ⚠ 探针出错: %s" % ev["error"])
    finally:
        try:
            if sw is not None:
                sw.CommandInProgress = False
        except Exception:      # noqa: BLE001
            pass
        try:
            if doc is not None and sw is not None:
                t = str(sw_connect.safe_get_com_member(doc, "GetTitle") or "")
                if t:
                    sw.CloseDoc(t)
        except Exception:      # noqa: BLE001
            pass

    import sw_connect as _sc
    dialogs, _点掉, scanned = _sc.settle_residual_dialogs()
    print("  收尾：扫了 %d 个窗口 · %s" % (scanned, "无模态框" if not dialogs else dialogs))
    ev["modal_dialogs"] = dialogs
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(ev, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("  证据: %s" % OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
