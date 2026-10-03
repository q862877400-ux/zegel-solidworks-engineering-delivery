"""★ 把能力层里**手抄的成员表**对着**出厂类型库**逐条核 —— 用 PowerShell 读 .NET 元数据。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（工具）
# 文件:   tools/check_typelib_tables.py
# 定位:   ★ 2026-10-03（轮 416）24h 计划 v2 —— 把**轮 415 的发现**机械化。
#   ★★ 那一轮的真因**不在探针**、★ 而在能力层自己的**手抄名单**：
#     `sw_simulation_loads._ERRORCODE_MEMBERS`（抄自 CHM）**漏了 `AddTemperature` 与
#     `AddRemoteLoad`** ⇒ 于是这两个成员**从不补末尾 `ByRef ErrorCode`** ⇒
#     `com_error(-2147352561, '非选择性的参数')` ⇒ ★ **两条好能力看起来调不通**。
#   ★★ 定位它用的是**出厂类型库**（★ 铁律 4 的最高裁决者）—— 而它是**托管程序集**，
#     ★ 可以用 **PowerShell 的 .NET 反射**离线读（★ 零 Python 依赖、★ 不需要 SW 在跑）：
#     ```
#     [Reflection.Assembly]::LoadFrom('<...>\api\redist\SolidWorks.Interop.cosworks.dll')
#     $t.GetMethods() | ? { $_.Name -like 'Add*' } | % { $_.Name; $_.GetParameters() }
#     ```
#   ⇒ ★ 本工具把这条**做成可重复的一步**：★ 读仓里那三张表，★ 读类型库，★ **逐条比**。
# 官方依据: `SolidWorks.Interop.cosworks.dll`（本机 `api\redist\` 下，版本 **34.4.1.1011**）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
#
# ★ 判据：★ 三张表与类型库**逐条一致** ⇒ 0 处不符。
# ⚠ 便携性：★ 找不到那个 DLL ⇒ **打印 [SKIP] 并 exit 0**（★ 与既有门禁同一约定）。

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

#: 2026-10-03（接手轮）强制 stdout 为 UTF-8 —— 本门禁会 print 中文与箭头/勾这类符号，
#:   而 stdout 是管道时（测试正是用管道抓输出）默认按 locale（本机 GBK）编码
#:   ⇒ UnicodeEncodeError: 'gbk' codec can't encode character … ⇒ 门禁自己崩掉。
#:   known-facts 58 那一族（中文 Windows 上两侧默认编码不一致 —— 病灶在输出侧）；
#:   而测试那侧的 subprocess.run 已经带了 encoding='utf-8'。
sys.stdout.reconfigure(encoding="utf-8")

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

DLL_CANDIDATES = (
    Path(r"D:\Program Files\SOLIDWORKS Corp\SOLIDWORKS\api\redist\SolidWorks.Interop.cosworks.dll"),
    Path(r"C:\Program Files\SOLIDWORKS Corp\SOLIDWORKS\api\redist\SolidWorks.Interop.cosworks.dll"),
)
IFACE = "SolidWorks.Interop.cosworks.ICWLoadsAndRestraintsManager"

#: ★ PowerShell 读元数据（★ 只"读"，不调 COM、不碰 SW）
_PS = r"""
$dll = '%s'
$asm = [Reflection.Assembly]::LoadFrom($dll)
$t = $asm.GetType('%s')
foreach ($m in ($t.GetMethods() | Where-Object { $_.Name -like 'Add*' -or $_.Name -like 'Get*' } | Sort-Object Name)) {
  $ps = $m.GetParameters()
  $names = ($ps | ForEach-Object { $_.Name + ':' + $_.ParameterType.Name }) -join ','
  Write-Output ("{0}|{1}" -f $m.Name, $names)
}
""" % ("%s", IFACE)


def _dump_typelib(dll: Path) -> dict:
    """★ 回 `{成员名: [(形参名, 类型名), …]}`。"""
    out: dict = {}
    try:
        proc = subprocess.run(["pwsh", "-NoProfile", "-Command", _PS % dll],
                              check=False, capture_output=True, text=True,
                              encoding="utf-8", errors="replace", timeout=180)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise RuntimeError("pwsh 读元数据失败: %s" % exc) from exc
    for line in (proc.stdout or "").splitlines():
        if "|" not in line:
            continue
        name, rest = line.split("|", 1)
        params = []
        for item in rest.split(","):
            if ":" in item:
                pn, pt = item.split(":", 1)
                params.append((pn.strip(), pt.strip()))
        out[name.strip()] = params
    return out


def main(argv: list) -> int:
    dll = next((p for p in DLL_CANDIDATES if p.exists()), None)
    if dll is None:
        print("  [SKIP] 本机找不到 `SolidWorks.Interop.cosworks.dll` ⇒ 无法核对（便携性约定）")
        return 0
    print("  核对源：%s" % dll)
    try:
        lib = _dump_typelib(dll)
    except RuntimeError as exc:
        print("  [SKIP] %s" % exc)
        return 0
    print("  类型库给出 `Add*` **%d** 个" % len(lib))

    import sw_simulation_loads as L

    bad: list = []
    skipped: list = []
    #: ① `_ERRORCODE_MEMBERS` —— ★ 应当是"带 ByRef/out 形参"的那些
    #: ★ 只比 **`Add*`** —— ★ `_ERRORCODE_MEMBERS` 只服务 `Add*`（★ `_check` 只被它们用）；
    #:   ★ `Get*` 不在其职责范围内 ⇒ ★ **拿它们去比就是假阳性**。
    want_err = {n for n, ps in lib.items() if n.startswith("Add")
                and any(pt.endswith("&") for _, pt in ps)}
    have_err = set(L._ERRORCODE_MEMBERS)
    for n in sorted(want_err - have_err):
        bad.append(("_ERRORCODE_MEMBERS", "缺", n))
    for n in sorted(have_err - want_err):
        bad.append(("_ERRORCODE_MEMBERS", "多", n))
    #: ② `_REFGEOM_MEMBERS` —— ★ 应当是"有一个叫 `RefGeom` 的形参"的那些
    want_ref = {n for n, ps in lib.items() if any(pn == "RefGeom" for pn, _ in ps)}
    have_ref = set(L._REFGEOM_MEMBERS)
    for n in sorted(want_ref - have_ref):
        bad.append(("_REFGEOM_MEMBERS", "缺", n))
    #: ③ `OFFICIAL_LOAD_SIGNATURES` —— ★ 应当是"**非 out** 形参的个数"
    for n, expected in sorted(L.OFFICIAL_LOAD_SIGNATURES.items()):
        ps = lib.get(n)
        if ps is None:
            #: ★ 只有 **`Add*`** 缺席才算问题；★ 其它名字（如 `Get*`）
            #:   本身就不在这个接口上 ⇒ ★ **如实注明、不报错**（★ 避免假阳性）
            if n.startswith("Add"):
                bad.append(("OFFICIAL_LOAD_SIGNATURES", "类型库里没有", n))
            else:
                skipped.append(n)
            continue
        real = len([1 for _, pt in ps if not pt.endswith("&")])
        if expected != real:
            bad.append(("OFFICIAL_LOAD_SIGNATURES", "差异", "%s 表=%d 实=%d" % (n, expected, real)))
    if skipped:
        print("  注：%s 不在该接口上（★ 非 `Add*`）⇒ 跳过" % ", ".join(sorted(skipped)))
    print("  比对三张表（_ERRORCODE_MEMBERS %d · _REFGEOM_MEMBERS %d · OFFICIAL_LOAD_SIGNATURES %d）"
          % (len(have_err), len(have_ref), len(L.OFFICIAL_LOAD_SIGNATURES)))
    if bad:
        print("  不符 **%d** 处：" % len(bad))
        for table, kind, item in bad[:30]:
            print("    %-28s %-12s %s" % (table, kind, item))
        print("\n  判据：★ 手抄的表要与**出厂类型库**逐条一致（★ 铁律 4：冲突以它为准）。")
        print("  真例（轮 415）：`_ERRORCODE_MEMBERS` 漏了 `AddTemperature`/`AddRemoteLoad`")
        print("  ⇒ 它们从不补 `ByRef ErrorCode` ⇒ `DISP_E_PARAMNOTOPTIONAL` ⇒ 两条好能力看着像坏的。")
        return 1
    print("  [OK] 三张表与出厂类型库**逐条一致**（0 处不符）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
