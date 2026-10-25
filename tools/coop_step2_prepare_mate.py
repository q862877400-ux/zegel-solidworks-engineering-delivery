"""人工验收 · 第 2 步「准备」：摆好两块板，**保持打开**给业主看。

## 这一步的产出

装配体里两块板（同一零件的两个实例）：

```
组件1  原点        x −50…+50mm   z 10…30mm
组件2  右移 30mm    x −20…+80mm   z 60…80mm   ← 抬高 50mm
```

★ 业主应当看到：**两块板，上面那块比下面那块高出一截、还往右错开一点**。

## 为什么不做配合

第 3 步才做。这一步只摆位，让业主确认「初始状态确实是这样」。
"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库 / 文件 / 定位 / 官方依据 / 许可 / 覆盖
# 仓库:   本项目自身（人工验收 · 第 2 步「准备」）
# 文件:   tools/coop_step2_prepare_mate.py
# 定位:   把配合演示摆成**可观察的初始状态**并保持文档打开，等业主确认。
#          起因：业主 2026-10-26「很多操作你还是做一遍给我看，然后我人工确认一下，
#          免得你机器判据问题，你以为验收了实际上不对」⇒ 见
#          docs/human-acceptance-protocol.md 阶段 2。
# 官方依据: IAssemblyDoc::AddComponent5（文件须已在内存）·
#          IModelDocExtension::SaveAs（6 参）·
#          IModelDoc2::ShowNamedView2 / ViewZoomtofit2
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
R = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(R))
sys.path.insert(0, str(R / "scripts"))

PART = R / "output" / "stage2" / "板1_rev-1.SLDPRT"
DEST = R / "output" / "coop" / "配合演示_初始.SLDASM"

import sw_assembly as asm_  # noqa: E402
import sw_connect as c_  # noqa: E402
from sw_connect import get_com_member  # noqa: E402


def main() -> int:
    conn = c_.connect_solidworks(wait_seconds=30)
    sw = conn[0] if isinstance(conn, tuple) else conn
    try:
        sw.CommandInProgress = True
    except Exception:  # noqa: BLE001
        pass

    #: 清场
    try:
        for d in list(get_com_member(sw, "GetDocuments") or ()):
            sw.CloseDoc(str(get_com_member(d, "GetTitle") or ""))
    except Exception:  # noqa: BLE001
        pass

    c_.open_document(sw, str(PART))
    ok, asm = c_.try_call(c_.new_document, sw, "assembly")
    if not ok or asm is None:
        print("★ 建不了装配体")
        return 1
    try:
        sw.ActivateDoc3(str(get_com_member(asm, "GetTitle") or ""), 0, False)
    except Exception:  # noqa: BLE001
        pass
    cand = get_com_member(sw, "ActiveDoc")
    if cand is not None and int(get_com_member(cand, "GetType") or 0) == 2:
        asm = cand

    asm_.add_component(asm, str(PART), x_m=0.0, y_m=0.0, z_m=0.0, sw=sw)
    asm_.add_component(asm, str(PART), x_m=0.030, y_m=0.0, z_m=0.050, sw=sw)

    n = len(list(get_com_member(asm, "GetComponents", False) or ()))
    print("① 组件数：%d" % n)

    #: 存到 output/coop 便于业主看到文件名
    DEST.parent.mkdir(parents=True, exist_ok=True)
    ok_s, s_ret = c_.try_call(
        c_.get_com_member,
        c_.get_com_member(asm, "Extension"),
        "SaveAs",
        str(DEST),
        0,
        5,
        c_.create_empty_dispatch_variant(),
        c_.out_i4(),
        c_.out_i4(),
    )
    print("② 存盘：%s（%s）" % (ok_s, str(s_ret)[:40]))

    #: 等轴测 + 缩放适应，让业主一眼看到两块板
    try:
        asm.ShowNamedView2("*等轴测", 7)
    except Exception:  # noqa: BLE001
        pass
    try:
        asm.ViewZoomtofit2()
    except Exception:  # noqa: BLE001
        pass

    #: 把 SolidWorks 窗口置前
    try:
        import ctypes
        import time

        u = ctypes.windll.user32
        hwnd = u.FindWindowW(None, "SOLIDWORKS Design Premium 2026 SP4.1")
        if not hwnd:
            for cls in ("SW_AppFrame",):
                hwnd = u.FindWindowW(cls, None)
        if hwnd:
            u.ShowWindow(hwnd, 3)
            time.sleep(0.4)
            u.SetForegroundWindow(hwnd)
    except Exception:  # noqa: BLE001
        pass

    #: 读数（给业主对照）
    for i, cp in enumerate(list(get_com_member(asm, "GetComponents", False) or ()), 1):
        tr = get_com_member(cp, "Transform2")
        d = list(get_com_member(tr, "ArrayData") or ())
        if len(d) >= 12:
            print(
                "   组件%d 平移(mm) = (%.1f, %.1f, %.1f)"
                % (i, d[9] * 1000, d[10] * 1000, d[11] * 1000)
            )
    print("★ 文档**保持打开**，等业主人工确认初始状态")
    try:
        sw.CommandInProgress = False
    except Exception:  # noqa: BLE001
        pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
