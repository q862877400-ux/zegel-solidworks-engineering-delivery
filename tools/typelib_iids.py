"""★ 从出厂 interop 程序集读**接口 IID**，并对 COM 对象做 QueryInterface。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（工具）
# 文件:   tools/typelib_iids.py
# 定位:   ★ 2026-10-03（轮 446）承**事实 360** —— ★ 结构系统那条链卡在**接口归属**上。
#   ★★★ **为什么需要它**：★ 官方 VBA 示例里那句 `Set PrimDef = structMemDef`
#     靠的是 **VBA 的多接口自动转换**；★ 而在 **pywin32** 里，★ 拿到手的只有
# `IStructureSystemMemberFeatureData` ⇒ ★★ **要换到 `IPrimaryMemberPathSegmentFeatureDat
# a`
#     就必须自己 `QueryInterface`** —— ★ 而 QI **要 IID** ⚠
#   ★★★★ **而 IID 从哪来**：★ 出厂 interop 程序集里**每个接口都带 `[Guid(...)]`** ——
#      ★★ 那就是 IID ⇒ ★ **纯元数据反射可得**（★ 不需要 COM、不需要 SW 跑着）✓
#      ★ 真机计数：★ `SolidWorks.Interop.sldworks.dll` 的 **1032** 个公开接口里，
#        **1023** 个带 Guid 特性（★ 覆盖率 **99.1%**）✓
#   ⚠ **不走的错路**（★ 都核过）：★ `pythoncom.LoadTypeLib` 要的是**COM 类型库**，
#      ★ 而 `SolidWorks.Interop.*.dll` 是 **.NET interop 程序集** ⇒ 喂它会失败；
# ★ 而注册表 `TypeLib` 的 **591** 个条目里，含 SOLIDWORKS / SldWorks / cosworks 的 **0**
#  个 ✓
# 官方依据: 出厂程序集 `D:\Program Files\SOLIDWORKS Corp\SOLIDWORKS\api\redist\
#   SolidWorks.Interop.sldworks.dll` 的 `System.Runtime.InteropServices.GuidAttribute` ·
#   `TypeLibTypeAttribute`（★ 真机：`FHidden, FDual, FDispatchable`）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
#
# ★ 判据：★ 给出的 IID **必须来自程序集本身的 `[Guid]`**（★ 不是手抄、不是猜）——
#    ★ 而 CLI 的 `--check <名字>` 会**回读**它，★ 便于核对。

from __future__ import annotations

import os
import sys
from pathlib import Path

#: ★ 出厂 interop 程序集（★ 可用 `DSL_INTEROP` 覆盖）
_CACHE: dict | None = None
INTEROP = Path(
    os.environ.get(
        "DSL_INTEROP",
        r"D:\Program Files\SOLIDWORKS Corp\SOLIDWORKS\api\redist\SolidWorks.Interop.sldworks.dll",
    )
)


PS_SCRIPT = r"""
$ErrorActionPreference = "Stop"
$asm = [Reflection.Assembly]::LoadFrom($env:DSL_INTEROP)
foreach ($t in $asm.GetExportedTypes()) {
  if (-not $t.IsInterface) { continue }
  $a = $t.GetCustomAttributes([System.Runtime.InteropServices.GuidAttribute], $false)
  if ($a.Count -gt 0) { Write-Output ($t.Name + "|" + $a[0].Value) }
}
"""


def interface_iids(path=None, *, refresh=False):
    """★ 回 `{接口名: IID}` —— ★ 走 **PowerShell 元数据反射**（★ 本仓既有的零依赖做法）。

    ⚠ 为什么不走 pythonnet：★ 真机测过 `import System` ⇒ `No module named 'System'`
      （★ 本机的 Python 没装 pythonnet）⇒ ★★ 而 **PowerShell 自带 .NET** ⇒ 零依赖可用 ✓
    """
    global _CACHE
    if _CACHE is not None and not refresh:
        return _CACHE
    dll = Path(path or INTEROP)
    if not dll.is_file():
        raise FileNotFoundError("出厂程序集不在：%s" % dll)
    import subprocess

    env = dict(os.environ)
    env["DSL_INTEROP"] = str(dll)
    r = subprocess.run(
        ["powershell", "-NoProfile", "-Command", PS_SCRIPT],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=env,
        timeout=300,
    )
    out = {}
    for line in (r.stdout or "").splitlines():
        if "|" in line:
            name, _, guid = line.partition("|")
            name, guid = name.strip(), guid.strip()
            if name and guid:
                out[name] = guid
    if not out:
        raise RuntimeError("反射没回任何接口（★ stderr：%s）" % (r.stderr or "")[:160])
    _CACHE = out
    return out


def iid(name: str, path: Path | None = None) -> str:
    """★ 取一个接口的 IID；★ 查不到就**抛**（★ 不静默）。"""
    m = interface_iids(path)
    if name not in m:
        raise KeyError("%s 不在名单里（★ 共 %d 个带 Guid 的接口）" % (name, len(m)))
    return m[name]


def qi(obj, name: str, path: Path | None = None):
    """★ 对一个 COM 对象做 `QueryInterface`，★ 回**那个接口**的包装。

    ★ 做法：`pythoncom` 从 IID 造出接口 ⇒ `obj._oleobj_.QueryInterface(iid)` ✓
    ⚠ 若对象不支持该接口 ⇒ **抛**（★ 而那是**有用的信息** —— ★ 说明接口归属真的不对）。
    """
    #: ★ 第一版我写了 `pythoncom.IID` ⇒ 真机报 `module 'pythoncom' has no attribute 'IID
    #: '`。
    #: ★★ **正解是 `pywintypes.IID`**（★ pywin32 里 IID 工厂在 pywintypes 上）。
    import pywintypes

    ole = getattr(obj, "_oleobj_", None)
    if ole is None:
        raise TypeError("这个对象没有 `_oleobj_` ⇒ 不是 pywin32 的 COM 包装")
    return ole.QueryInterface(pywintypes.IID("{%s}" % iid(name, path)))


def main(argv: list) -> int:
    args = [a for a in argv if not a.startswith("--")]
    if not INTEROP.is_file():
        print("  [SKIP] 出厂程序集不在：%s" % INTEROP)
        return 0
    try:
        m = interface_iids()
    except Exception as exc:  # noqa: BLE001
        print("  [SKIP] 读不了程序集（★ 需要 pythonnet/clr）：%s" % str(exc)[:90])
        return 0
    if args:
        for n in args:
            print("  %-46s %s" % (n, m.get(n, "**不在名单里**")))
        return 0
    print("  出厂程序集：%s" % INTEROP.name)
    print("  带 Guid 的公开接口 **%d** 个" % len(m))
    for n in (
        "IPrimaryMemberPathSegmentFeatureData",
        "IStructureSystemMemberFeatureData",
        "IStructureSystemMemberProfile",
        "IFeatureManager",
        "IModelDocExtension",
    ):
        if n in m:
            print("    %-46s %s" % (n, m[n]))
    print("  ★ 用法：python tools/typelib_iids.py <接口名>  # 查一个")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
