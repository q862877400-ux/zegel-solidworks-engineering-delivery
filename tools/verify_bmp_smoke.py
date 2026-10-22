r"""@brief 真机冒烟：`sw_export.export_to_bmp` —— ★★ **读 BMP 头核对尺寸（定量往返）**。

## 为什么这条判据强
官方 `SaveBMP(FileName, WidthIn, HeightIn)` 把 **宽高当入参**
⇒ ★ 我可以**读回 BMP 文件头**（`BM` 魔数 + 位图信息头里的宽高）
⇒ 断言「**写进去的尺寸 == 读回来的尺寸**」——**空操作满足不了**（事实 40 那一族要的强证据）。

## 安全设计
**只在新零件上跑**、不改用户文档；`CommandInProgress`；收尾**关件不保存** + **查模态框**（事实 64）。
输出落在 `output/`（**已 gitignore** 的产物目录）。

# ── 来源 ──
# 仓库:   本项目自身（真机验收）
# 文件:   tools/verify_bmp_smoke.py
# 定位:   给 `scripts/sw_export.export_to_bmp`（轮 146 补的 `export_image`）取真机证据。
# 官方依据: `C:\swapi\types\IModelDoc2\SaveBMP.md`；BMP 头结构见微软 BMP 格式（小端）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

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

OUT = Path(Path(__file__).resolve().parents[1] / "output" / "bmp-smoke-evidence.json")
BMP = Path(Path(__file__).resolve().parents[1] / "output" / "smoke-view.bmp")
BMP2 = Path(Path(__file__).resolve().parents[1] / "output" / "smoke-view-window.bmp")
W, H, D = 100.0, 60.0, 20.0  #: 板（毫米）
BW, BH = 800, 600  #: ★ 请求的像素尺寸


def bmp_size(path: Path):
    """读 BMP 头里的宽高（`BITMAPINFOHEADER`：偏移 18/22，小端 int32）。

    ⚠ 只看头，**不解码像素** —— 头对不上就说明尺寸没按请求走。
    """
    b = path.read_bytes()[:26]
    if len(b) < 26 or b[:2] != b"BM":
        return None
    wid, hei = struct.unpack_from("<ii", b, 18)
    return abs(wid), abs(hei)


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
        print("   %s %-52s %s" % ("✓" if ok else "**✗**", name, str(detail)[:62]))

    sw = None
    doc = None
    try:
        import sw_connect

        from scripts import sw_export, sw_part

        sw = sw_connect.connect_solidworks(wait_seconds=10)[0]
        try:
            sw.CommandInProgress = True
        except Exception:  # noqa: BLE001
            pass
        doc = sw_connect.new_document(sw, "part")
        chk("新建临时零件（不碰用户文档）", doc is not None, "ok")
        sw_part.start_sketch(doc)
        sw_part.sketch_corner_rectangle(doc, 0.0, 0.0, W, H)
        sw_part.end_sketch(doc)
        sw_part.extrude_boss(doc, "草图1", D)
        chk("造出 %.0fx%.0fx%.0f 的板（有东西可拍）" % (W, H, D), True, "ok")

        #: ① 请求 800x600
        BMP.parent.mkdir(parents=True, exist_ok=True)
        for f in (BMP, BMP2):
            if f.exists():
                f.unlink()
        try:
            sw_export.export_to_bmp(doc, BMP, BW, BH)
            chk("export_to_bmp(%dx%d) 未抛异常" % (BW, BH), True, "ok")
        except Exception as exc:  # noqa: BLE001
            chk(
                "export_to_bmp(%dx%d)" % (BW, BH),
                False,
                "%s: %s" % (type(exc).__name__, str(exc)[:100]),
            )

        #: ② ★★ 定量往返：读回 BMP 头
        if BMP.exists():
            size = BMP.stat().st_size
            got = bmp_size(BMP)
            ev["bmp"] = {"path": str(BMP), "bytes": size, "size": got}
            chk("★ 文件存在且非空", size > 0, "%d 字节" % size)
            chk(
                "★★ **定量往返**：BMP 头里的尺寸 == 请求的 %dx%d" % (BW, BH),
                got == (BW, BH),
                "读回 %s（头 18/22 偏移，小端 int32）" % (got,),
            )
        else:
            chk("BMP 文件生成", False, "文件不存在")

        #: ③ 官方 Remarks：宽或高 ≤ 0 ⇒ 按**当前窗口**尺寸
        try:
            sw_export.export_to_bmp(doc, BMP2, 0, 0)
            got2 = bmp_size(BMP2) if BMP2.exists() else None
            ev["bmp_window"] = {"path": str(BMP2), "size": got2}
            chk(
                "★ 官方 Remarks：宽高 ≤ 0 ⇒ 按窗口尺寸（读回一个合理的正数）",
                bool(got2) and got2[0] > 0 and got2[1] > 0,
                "读回 %s" % (got2,),
            )
        except Exception as exc:  # noqa: BLE001
            chk(
                "宽高 ≤ 0 那条路", False, "%s: %s" % (type(exc).__name__, str(exc)[:90])
            )

        #: ④ 扩展名守卫
        try:
            sw_export.export_to_bmp(doc, Path(str(BMP).replace(".bmp", ".png")), BW, BH)
            chk("★ 扩展名不是 .bmp ⇒ 应当拒绝", False, "**没有拒绝**")
        except ValueError:
            chk("★ 扩展名不是 .bmp ⇒ 明确拒绝", True, "ValueError")
        except Exception as exc:  # noqa: BLE001
            chk("★ 扩展名不是 .bmp ⇒ 明确拒绝", False, "抛的是 %s" % type(exc).__name__)
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
    print("  ⚠ 只证「尺寸按请求走 + 文件合法」；**不证画面内容**（不比对像素）。")
    return 0 if ev["verdict"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
