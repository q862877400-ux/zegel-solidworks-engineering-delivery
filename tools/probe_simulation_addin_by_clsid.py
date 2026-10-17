r"""@brief 纯读探针：用 **CLSID 的 `{GUID}`** 取 Simulation 加载项对象（**不加载任何 DLL**）。

## 为什么（2026-10-01）
轮 179 起 `capture_topology_evidence.py` 报
`GetAddInObject('SldWorks.Simulation') 返回 None ⇒ 加载项未加载或未安装（需许可）`。
本轮实测把它的**归因**推翻了一半：
```
· `swLoadAddinError_e`: swSuccess=0 · swAddinAlreadyLoaded=2 · **swFileNotFound=3** · **swLicenseError=7**
· 旧探针 `LoadAddIn("SldWorks.Simulation")` ⇒ **3** ⇒ ★ 那是「**文件没找到**」（传名字当路径了），
  **不是**许可问题（许可问题应该是 **7**）
· `SldWorks.Simulation` 这个 **ProgID 存在**（HKLM\SOFTWARE\Classes\SldWorks.Simulation）
  → CLSID `{C8F79410-CD71-4061-A2E4-B6BF17CCB27F}` → InprocServer32 = `…\Simulation\cosworks.dll`（存在）
· ★ 但 `HKLM\SOFTWARE\SolidWorks\Addins` 下**没有**它 ⇒ **没注册成加载项**
```

## 判据（可证伪）
```
① `GetAddInObject('{C8F79410-CD71-4061-A2E4-B6BF17CCB27F}')`
   · 非 None ⇒ ★ **ProgID 那条路才是错的**，用 GUID 就能拿到 ⇒ 拓扑/仿真**当下可用**
   · None 且无异常 ⇒ COM 类在、但**没被 SOLIDWORKS 当加载项启动** ⇒ 属"注册/启用"问题
   · 抛异常 ⇒ ★ 把**异常码**记下来（它才可能是许可问题）
② **不调用 `LoadAddIn`**（那会加载一个 40 MB 的进程内 COM 服务器 ⇒ 有风险；
   本探针只回答"现在拿不拿得到"，**不动环境**）
```

## ⚠ 安全
**纯读**：只调 `GetAddInObject`（+ 一次 `GetAddInObject` 对照组用 `SldWorks.Simulation`）。
`CommandInProgress` 开→关 · 收尾**轮询点掉**残留弹窗 · **不启动新实例**（复用已有的）· 不写任何配置。

# ── 来源 ──
# 仓库:   本项目自身（真机探针）
# 文件:   tools/probe_simulation_addin_by_clsid.py
# 定位:   复核「仿真加载项取不到」的**归因**（轮 179 归为许可，本轮发现归因错了）。
# 官方依据: `ISldWorks.GetAddInObject(String Clsid)` 的 Remarks ——
#         「a GUID, use curly brackets as in "{GUID}", or the string is interpreted as a ProgID」
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

OUT = Path(Path(__file__).resolve().parents[1] / "output" / "simulation-addin-by-clsid.json")
#: 实测从注册表读出（只读）：`SldWorks.Simulation` 的 CLSID
CLSID = "{C8F79410-CD71-4061-A2E4-B6BF17CCB27F}"


def main() -> int:
    ev: dict = {"clsid": CLSID}
    import sw_connect
    sw = sw_connect.connect_solidworks(wait_seconds=10)[0]     #: 复用已有实例，不新建
    try:
        sw.CommandInProgress = True
    except Exception:      # noqa: BLE001
        pass

    for label, key in (("① CLSID 的 {GUID}", CLSID),
                       ("② 对照：ProgID `SldWorks.Simulation`", "SldWorks.Simulation")):
        try:
            got = sw_connect.safe_get_com_member(sw, "GetAddInObject", key)
            kind = None if got is None else type(got).__name__
            ev[label] = kind
            print("  %-38s ⇒ **%s**" % (label, "None" if got is None else kind))
        except Exception as exc:      # noqa: BLE001
            ev[label] = "EXC:%s:%s" % (type(exc).__name__, str(exc)[:120])
            print("  %-38s ⇒ %s" % (label, ev[label]))

    sw.CommandInProgress = False
    found, dismissed, scanned = sw_connect.settle_residual_dialogs(settle_seconds=1.0)
    ev["cleanup"] = {"found": found, "dismissed": dismissed, "scanned": scanned}
    print("  收尾：发现 %d · 点掉 %d · 扫了 %d 个窗口" % (found, dismissed, scanned))

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(ev, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("  证据: %s" % OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
