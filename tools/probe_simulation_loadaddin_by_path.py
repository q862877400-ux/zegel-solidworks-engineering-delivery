r"""@brief 决定性探针：用**正确的参数形态**调 `LoadAddIn`，让返回码回答「是不是许可问题」。

## 为什么（2026-10-01）
官方文档（`C:\swapi\types\ISldWorks\LoadAddIn.md`）写明：
```
FileName = **"Fully qualified file name of the add-in"** ⇒ 要**完整文件路径**
Returns  = "Status of loading the add-in as defined in swLoadAddinError_e"
```
而**旧探针传的是名字**（`"SldWorks.Simulation"`）⇒ 返回 **3 = swFileNotFound** ⇒
★ 那是「**文件没找到**」，**不是**许可问题（许可错是 **7 = swLicenseError**）。
```
swSuccess=0 · swAddinNotLoaded=1 · swAddinAlreadyLoaded=2 · swFileNotFound=3 ·
swAddinsDisabled=4 · swLoadConflict=5 · swRegistrationError=6 · **swLicenseError=7** · swUnknownError=-1
```
本机实测（只读注册表）：`SldWorks.Simulation` → CLSID `{C8F79410-CD71-4061-A2E4-B6BF17CCB27F}`
→ `InprocServer32` = `D:\Program Files\SOLIDWORKS Corp\SOLIDWORKS\Simulation\cosworks.dll`（文件存在）。

## 判据（可证伪，**返回码就是判据**）
```
· 返回 **0 或 2** ⇒ ★ **能加载** ⇒ 「取不到」的真因是**加载项没启用**，不是许可
· 返回 **7**      ⇒ ★ **许可问题**（用户装了许可但没生效 / 类型不对）
· 返回 **3**      ⇒ 路径形态仍不对（本探针的主要假说被否）
· 返回 **4**      ⇒ 加载项被**禁用**（Tools > Add-Ins 里没勾）
· 抛异常         ⇒ 记异常码；★ 与事实 47/28 的 `0x80010105` 类比时**不猜**
```

## ⚠ 安全（这条会**加载一个 40 MB 的进程内 COM 服务器**，风险高于纯读探针）
* **只调一次** `LoadAddIn`（不重试 —— COM 是 STA，调用开始后无法中止）；
* `CommandInProgress` 开 → **关**（`finally`）；
* 收尾 `settle_residual_dialogs()` **轮询点掉**残留弹窗；
* **不启动新实例**（复用已有）；
* **不改**注册表 / 不改全局配置 / 不写任何启动项 ⇒ 本次加载**不持久**
  （`LoadAddIn` 只影响当前会话；下次启动是否自动加载由 `AddInsStartup` 决定，本探针**不碰**）。

# ── 来源 ──
# 仓库:   本项目自身（真机探针）
# 文件:   tools/probe_simulation_loadaddin_by_path.py
# 定位:   给「仿真加载项取不到」**定因**（许可 vs 未启用 vs 参数形态）。
# 官方依据: `C:\swapi\types\ISldWorks\LoadAddIn.md`（参数与返回值）+ `C:\swapi\enums\swLoadAddinError_e.md`
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for p in (str(ROOT), str(ROOT / "scripts"), str(ROOT / "mcp-server")):
    if p not in sys.path:
        sys.path.insert(0, p)
sys.stdout.reconfigure(encoding="utf-8")

OUT = Path(Path(__file__).resolve().parents[1] / "output" / "simulation-loadaddin-by-path.json")
#: 实测自注册表（只读）：`SldWorks.Simulation` 的 InprocServer32
DLL = Path(r"D:\Program Files\SOLIDWORKS Corp\SOLIDWORKS\Simulation\cosworks.dll")
CLSID = "{C8F79410-CD71-4061-A2E4-B6BF17CCB27F}"
#: 官方 `swLoadAddinError_e` 的**全部 9 个成员**（读 `C:\swapi\enums\swLoadAddinError_e.md`）
CODES = {0: "swSuccess", 1: "swAddinNotLoaded", 2: "swAddinAlreadyLoaded", 3: "swFileNotFound",
         4: "swAddinsDisabled", 5: "swLoadConflict", 6: "swRegistrationError",
         7: "swLicenseError", -1: "swUnknownError"}


def main() -> int:
    ev: dict = {"dll": str(DLL), "dll_exists": DLL.is_file(), "clsid": CLSID}
    if not DLL.is_file():
        print("  ✗ 路径不存在 ⇒ 判据失效（先查路径）")
        return 2
    import sw_connect
    sw = sw_connect.connect_solidworks(wait_seconds=10)[0]      #: 复用已有实例
    try:
        sw.CommandInProgress = True
        try:
            rc = sw_connect.safe_get_com_member(sw, "LoadAddIn", str(DLL))
            ev["load_addin_rc"] = rc
            print("  `LoadAddIn(<完整路径>)` ⇒ **%s = %s**"
                  % (rc, CODES.get(rc, "（不在枚举里）")))
        except Exception as exc:      # noqa: BLE001
            ev["load_addin_exc"] = "%s: %s" % (type(exc).__name__, str(exc)[:160])
            print("  `LoadAddIn(<路径>)` ⇒ 抛异常 %s" % ev["load_addin_exc"])
        #: 加载后再取（两种形态都试，纯读）
        for label, key in (("by_clsid", CLSID), ("by_progid", "SldWorks.Simulation")):
            try:
                got = sw_connect.safe_get_com_member(sw, "GetAddInObject", key)
                ev[label] = None if got is None else type(got).__name__
            except Exception as exc:      # noqa: BLE001
                ev[label] = "EXC:%s" % type(exc).__name__
            print("  加载后 GetAddInObject(%s) ⇒ **%s**" % (label, ev[label]))
    finally:
        try:
            sw.CommandInProgress = False
        except Exception:      # noqa: BLE001
            pass

    found, dismissed, scanned = sw_connect.settle_residual_dialogs(settle_seconds=1.0)
    ev["cleanup"] = {"found": found, "dismissed": dismissed, "scanned": scanned}
    print("  收尾：发现 %d · 点掉 %d · 扫了 %d 个窗口" % (found, dismissed, scanned))

    rc = ev.get("load_addin_rc")
    if rc in (0, 2):
        ev["conclusion"] = "**能加载** ⇒ 取不到的真因是「加载项没启用」，**不是许可**"
    elif rc == 7:
        ev["conclusion"] = "**许可问题**（swLicenseError）"
    elif rc == 3:
        ev["conclusion"] = "路径形态仍不对（主假说被否）"
    elif rc == 4:
        ev["conclusion"] = "加载项被**禁用**（Tools > Add-Ins 里没勾）"
    else:
        ev["conclusion"] = "见 rc / 异常（不猜）"
    print("  ⇒ 结论：%s" % ev["conclusion"])
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(ev, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("  证据: %s" % OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
