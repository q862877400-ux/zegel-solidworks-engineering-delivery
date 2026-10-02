r"""@brief 真机冒烟：`sw_assembly.get_interference_detection` —— ★★ **定量**（真造出干涉）。

## 为什么这样验
`159`（轮 159）查出它**两处成员名都错**（`InterferenceDetection` 少 `Manager`、
`GetInterference(index)` 不存在）⇒ ★ 两处都在 `try:` 里 ⇒ **此前静默降级**。
⇒ ★★ 那"修好了没有"就**必须用真机量**：
```
造一个装配，放**两个重叠**的块 ⇒ 干涉**必然存在**
⇒ 断言 `GetInterferenceCount() > 0` ⇒ ★ **定量**（空操作满足不了）
⇒ 且逐项要能拿到 `Name` / `Volume`（这两项本来就在代码里读）
```

## ⚠ 安全
**只在新装配 + 新零件上跑**；收尾**关件不保存** + **查模态框**。

# ── 来源 ──
# 仓库:   本项目自身（真机验收）
# 文件:   tools/verify_interference_smoke.py
# 定位:   给 Spec Kit `078` 取「干涉检查真能拿到数据」的证据。
# 官方依据: `IInterferenceDetectionMgr`（`C:\swapi\types\IInterferenceDetectionMgr\`）·
#          反射 `get_InterferenceDetectionManager()`
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

OUT = Path(r"D:\AI\SW\output\interference-smoke.json")
#: ⚠ 每次跑换一个子目录 —— 上一轮的文件被 SolidWorks **占着**（WinError 32），
#: 就地删会 `PermissionError`（**资源纪律**：别去删别人正拿着的文件）。
DIR = Path(r"D:\AI\SW\output\interference-smoke") / time.strftime("%H%M%S")
def main() -> int:
    ev: dict = {"started": time.strftime("%Y-%m-%d %H:%M:%S"), "checks": {}}
    checks: list = []

    def chk(name, ok, detail):
        checks.append(bool(ok))
        ev["checks"][name] = {"ok": bool(ok), "detail": str(detail)[:300]}
        print("   %s %-52s %s" % ("✓" if ok else "**✗**", name, str(detail)[:60]))

    sw = None
    part = None
    asm = None
    try:
        import sw_connect
        from scripts import sw_part, sw_assembly
        sw = sw_connect.connect_solidworks(wait_seconds=10)[0]
        try:
            sw.CommandInProgress = True
        except Exception:      # noqa: BLE001
            pass
        DIR.mkdir(parents=True, exist_ok=True)

        #: ① 造两个**重叠**的块（各 40x40x20，沿 X 偏 20mm ⇒ 重叠 20mm）
        paths = []
        for i in range(2):
            part = sw_connect.new_document(sw, "part")
            sw_part.start_sketch(part)
            sw_part.sketch_corner_rectangle(part, 0.0, 0.0, 40.0, 40.0)
            sw_part.end_sketch(part)
            sw_part.extrude_boss(part, "草图1", 20.0)
            p = DIR / ("block%d.sldprt" % i)
            if p.exists():
                p.unlink()
            sw_connect.save_document(part, str(p))
            paths.append(str(p))
        chk("造出 2 个 40x40x20 的块并保存", len(paths) == 2, "ok")

        #: ② 装配：第二个沿 X 偏 20mm ⇒ **重叠** ⇒ 干涉必然存在
        asm = sw_connect.new_document(sw, "assembly")
        sw_assembly.add_component(asm, paths[0], x=0, y=0, z=0)
        sw_assembly.add_component(asm, paths[1], x=20, y=0, z=0)
        chk("装配里放两个块（第二个偏 +20mm ⇒ **重叠**）", True, "ok")

        #: ③ ★★ 定量：干涉数应当 > 0
        rep = sw_assembly.get_interference_detection(asm)
        ev["report"] = {k: v for k, v in rep.items() if k != "items"}
        ev["items"] = rep.get("items")
        cnt = int(rep.get("interference_count") or rep.get("count") or 0)
        chk("★★ **定量**：`GetInterferenceCount() > 0`（真造出了干涉）", cnt > 0,
            "干涉数 = %s · 报告键 = %s" % (cnt, sorted(rep.keys())))
        items = rep.get("items") or []
        #: ★★★ **定量判据（最强的那个）**：两个 40×40×20 的块沿 X 偏 20mm
        #: ⇒ 重叠区 = **20 × 40 × 20 = 16000 mm³** ⇒ **算得出来、对得上**。
        vols = [it.get("volume") for it in items if isinstance(it.get("volume"), (int, float))]
        ev["volumes"] = vols
        chk("★★★ **定量**：干涉体积 ≈ **16000 mm³**（20×40×20，算得出来）",
            bool(vols) and abs(max(vols) - 16000.0) <= 2.0,
            "读回体积 = %s（期望 16000 ± 2）" % (vols,))
        cc = [it.get("component_count") for it in items]
        chk("★ 逐项能拿到 `GetComponentCount`（官方成员）", any(cc), "component_count = %s" % (cc,))
        if not vols and items:
            chk("⚠ 逐项的错误原文（**如实记**）", True, str(items[0])[:140])
    except Exception as exc:      # noqa: BLE001
        chk("整体冒烟", False, "%s: %s" % (type(exc).__name__, str(exc)[:180]))
    finally:
        try:
            if sw is not None:
                sw.CommandInProgress = False
        except Exception:      # noqa: BLE001
            pass
        for d in (asm, part):
            try:
                if d is not None and sw is not None:
                    t = str(sw_connect.safe_get_com_member(d, "GetTitle") or "")
                    if t:
                        sw.CloseDoc(t)
            except Exception:      # noqa: BLE001
                pass
        print("   （已关闭 scratch 文档，不保存）")

    import sw_connect as _sc
    dialogs, _点掉, scanned = _sc.settle_residual_dialogs()
    chk("★ 收尾无残留模态框（事实 64）", (not dialogs) and scanned > 0,
        "扫了 %d 个窗口 · %s" % (scanned, "无模态框" if not dialogs else dialogs))

    ev.update(passed=sum(1 for c in checks if c), total=len(checks),
              verdict="pass" if checks and all(checks) else "fail",
              finished=time.strftime("%Y-%m-%d %H:%M:%S"))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(ev, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print()
    print("  ── %d/%d · verdict: %s ──" % (ev["passed"], ev["total"], ev["verdict"]))
    return 0 if ev["verdict"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
