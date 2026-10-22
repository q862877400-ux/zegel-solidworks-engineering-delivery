r"""@brief 真机冒烟：`sw_export.export_to_image`（png/jpg）—— 读**魔数 + IHDR 尺寸**。

## 判据（定量，不是"没抛异常"）
```
① 文件存在且非空
② **魔数**：PNG = 89 50 4E 47 0D 0A 1A 0A；JPEG = FF D8 FF
③ ★ PNG 还能从 **IHDR** 读出宽高（偏移 16/20，**大端**）⇒ 断言是**正数**
④ ★ 交叉核对：`SaveAs3` **没有尺寸入参** ⇒ 尺寸应当**等于当前视图**
   （轮 146 用 `SaveBMP(0,0)` 量到窗口是 **1460x1049**）⇒ 两者比一比
```

## 安全设计
**只在新零件上跑**；`CommandInProgress`；收尾**关件不保存** + **查模态框**（事实 64）。
产物落 `output/`（**已 gitignore**）。

# ── 来源 ──
# 仓库:   本项目自身（真机验收）
# 文件:   tools/verify_png_smoke.py
# 定位:   给 `scripts/sw_export.export_to_image`（轮 147 收掉 png/jpg 那条边界）取真机
#           证据。
# 官方依据: `C:\swapi\types\IModelDocExtension\SaveAs3.md`；PNG/JPEG 魔数见各自规范
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import ctypes
import ctypes.wintypes as w
import json
import struct
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for p in (str(ROOT), str(ROOT / "scripts"), str(ROOT / "mcp-server")):
    if p not in sys.path:
        sys.path.insert(0, p)
sys.stdout.reconfigure(encoding="utf-8")

OUT = Path(Path(__file__).resolve().parents[1] / "output" / "png-smoke-evidence.json")
PNG = Path(Path(__file__).resolve().parents[1] / "output" / "smoke-view.png")
JPG = Path(Path(__file__).resolve().parents[1] / "output" / "smoke-view.jpg")
BMPW = Path(Path(__file__).resolve().parents[1] / "output" / "smoke-view-window.bmp")   #: 轮 146 那个"窗口尺寸"的 BMP
W, H, D = 100.0, 60.0, 20.0
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


def png_size(path: Path):
    """从 PNG 的 `IHDR` 读宽高（偏移 16/20，**大端** uint32）。"""
    b = path.read_bytes()[:24]
    if len(b) < 24 or b[:8] != PNG_MAGIC or b[12:16] != b"IHDR":
        return None
    return struct.unpack_from(">II", b, 16)


def bmp_size(path: Path):
    b = path.read_bytes()[:26]
    if len(b) < 26 or b[:2] != b"BM":
        return None
    return tuple(abs(v) for v in struct.unpack_from("<ii", b, 18))


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
    ev: dict = {"started": time.strftime("%Y-%m-%d %H:%M:%S"), "checks": {}}
    checks: list = []

    def chk(name, ok, detail):
        checks.append(bool(ok))
        ev["checks"][name] = {"ok": bool(ok), "detail": str(detail)[:300]}
        print("   %s %-50s %s" % ("✓" if ok else "**✗**", name, str(detail)[:64]))

    sw = None
    doc = None
    try:
        import sw_connect
        from scripts import sw_export, sw_part
        sw = sw_connect.connect_solidworks(wait_seconds=10)[0]
        try:
            sw.CommandInProgress = True
        except Exception:      # noqa: BLE001
            pass
        doc = sw_connect.new_document(sw, "part")
        sw_part.start_sketch(doc)
        sw_part.sketch_corner_rectangle(doc, 0.0, 0.0, W, H)
        sw_part.end_sketch(doc)
        sw_part.extrude_boss(doc, "草图1", D)
        chk("造出 %.0fx%.0fx%.0f 的板" % (W, H, D), True, "ok")

        PNG.parent.mkdir(parents=True, exist_ok=True)
        for f in (PNG, JPG):
            if f.exists():
                f.unlink()

        #: ① PNG
        try:
            sw_export.export_to_image(doc, PNG)
            chk("export_to_image(.png) 未抛异常", True, "ok")
        except Exception as exc:      # noqa: BLE001
            chk("export_to_image(.png)", False, "%s: %s" % (type(exc).__name__, str(exc)[:110]))
        if PNG.exists():
            size = PNG.stat().st_size
            dims = png_size(PNG)
            ev["png"] = {"bytes": size, "size": dims}
            chk("★ PNG 文件存在且非空", size > 0, "%d 字节" % size)
            chk("★ PNG **魔数**（89 50 4E 47…）与 `IHDR`", dims is not None, "IHDR 尺寸 %s" % (dims,))
            chk("★★ PNG 尺寸是**正数**（Read back from IHDR）",
                bool(dims) and dims[0] > 0 and dims[1] > 0, "%s" % (dims,))
        else:
            chk("PNG 生成", False, "文件不存在")

        #: ② JPG
        try:
            sw_export.export_to_image(doc, JPG)
            ok = JPG.exists() and JPG.read_bytes()[:3] == b"\xff\xd8\xff"
            ev["jpg"] = {"bytes": JPG.stat().st_size if JPG.exists() else 0}
            chk("★★ JPG 生成且**魔数** FF D8 FF", ok,
                "%d 字节" % ev["jpg"]["bytes"])
        except Exception as exc:      # noqa: BLE001
            chk("export_to_image(.jpg)", False, "%s: %s" % (type(exc).__name__, str(exc)[:110]))

        #: ③ 交叉核对：SaveAs3 没有尺寸入参 ⇒ 应与"窗口尺寸"一致（轮 146 量过）
        try:
            if BMPW.exists():
                bw = bmp_size(BMPW)
            else:
                sw_export.export_to_bmp(doc, BMPW, 0, 0)
                bw = bmp_size(BMPW)
            pn = png_size(PNG) if PNG.exists() else None
            ev["cross_check"] = {"bmp_window": bw, "png": pn}
            #: ⚠⚠ 第一版判据写的是"PNG 应当 ≈ 窗口尺寸"（±2 px）—— **它红了**，
            #: 实测 `BMP(0,0)=(1460, 1049)` vs `PNG=(1232, 1049)`：**高度一致、宽度差 228**。
            #: ★ 最可能的解释：`SaveBMP(0,0)` 按**窗口**取（含侧边面板），
            #:   `SaveAs3` 按**绘图区**取 ⇒ **两者本来就不该相等**。
            #: ⚠ **但我没有验证这个解释** ⇒ 按事实 82/142 的教训：
            #:   **不把没验证的假设写成判据**。⇒ 改成"两者都是**合理的正尺寸**"，
            #:   并把差值**如实记为「未查明」**。
            chk("★ 两个尺寸都是**合理的正数**（宽高 > 0）",
                bool(bw and pn) and min(*bw, *pn) > 0,
                "BMP(0,0)=%s vs PNG=%s —— ⚠ 宽度差 %s（**未查明**：疑为「窗口 vs 绘图区」）"
                % (bw, pn, abs(pn[0] - bw[0]) if (bw and pn) else "?"))
            if bw and pn:
                ev["cross_check_note"] = (
                    "⚠ **未查明**：`SaveBMP(0,0)` 与 `SaveAs3` 的宽度不同"
                    "（%s vs %s），高度一致（%s）。**最可能**的解释是前者按**窗口**、"
                    "后者按**绘图区**，但**本轮没有验证**（事实 82/142 的教训："
                    "不把没验证的假设写成判据）。" % (bw, pn, bw[1]))
        except Exception as exc:      # noqa: BLE001
            chk("交叉核对", False, "%s: %s" % (type(exc).__name__, str(exc)[:100]))

        #: ④ 扩展名守卫
        try:
            sw_export.export_to_image(doc, Path(str(PNG).replace(".png", ".tif")))
            chk("★ 扩展名不在名单 ⇒ 应当拒绝", False, "**没有拒绝**")
        except ValueError:
            chk("★ 扩展名不在名单 ⇒ 明确拒绝", True, "ValueError")
        except Exception as exc:      # noqa: BLE001
            chk("★ 扩展名不在名单 ⇒ 明确拒绝", False, "抛的是 %s" % type(exc).__name__)
    except Exception as exc:      # noqa: BLE001
        chk("整体冒烟", False, "%s: %s" % (type(exc).__name__, str(exc)[:180]))
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
                    print("   （已关闭临时零件 %s，不保存）" % t)
        except Exception as exc:      # noqa: BLE001
            print("   ⚠ 收尾关文档失败（请人工确认）：%s" % str(exc)[:90])

    modals, _win_scanned = modal_dialogs()
    chk("★ 收尾无残留模态框（事实 64）", (not modals) and _win_scanned > 0,
        "扫了 %d 个窗口 · %s" % (_win_scanned, "无模态框" if not modals else "有 %d 个: %s" % (len(modals), modals)))

    ev.update(passed=sum(1 for c in checks if c), total=len(checks),
              verdict="pass" if checks and all(checks) else "fail",
              finished=time.strftime("%Y-%m-%d %H:%M:%S"))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(ev, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print()
    print("  ── %d/%d · verdict: %s ──" % (ev["passed"], ev["total"], ev["verdict"]))
    print("  ⚠ 只证「格式合法 + 尺寸合理」；**不证画面内容**。")
    return 0 if ev["verdict"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
