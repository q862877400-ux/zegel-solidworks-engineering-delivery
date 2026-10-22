"""★ 问真机：一个 COM 对象**能用哪些成员** —— 并与程序集里的名单对差。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（工具）
# 文件:   tools/com_member_probe.py
# 定位:   ★ 2026-10-03（轮 447）承**事实 361** —— ★ 那轮查明：★ 「**接口在文档里**」**
#           ≠**
# 「**这个对象能用它**」，★ 而**真正的判据**是 ★ `getattr(obj, 名字, None) is not None`
# 。
#   ★★★ **本工具就是那条判据的自动化**：
#     ```
#     ① ★ 从出厂 interop 程序集读**某个接口的成员名单**（★ 纯元数据反射，★ 零依赖）
#     ② ★ 逐个问真机上的对象：★ `getattr(obj, 名, None)`
#     ③ ★★ **两者的差**就是「**程序集/文档里有、而这个对象用不了**」的那些 ——
#        ★ 而★ 那**正是本阶段要找的东西**（★ 事实 361 的 `CreateStructureSystem`）✓
#     ```
#   ★ 真机依据（事实 361）：★ `getattr(ext, "SelectByID2")` **有**（★ 而它能用）；
#     ★★ `getattr(ext, "CreateStructureSystem")` **回 `None`**（★ 而文档里明明有）✓
# 官方依据: 出厂程序集 `SolidWorks.Interop.sldworks.dll` 的公开成员（★ 反射可得）·
#   pywin32 迟到绑定只认 `DispInterface`（★ `IDispatch::GetIDsOfNames`）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
#
# ★ 判据：★ 分类三态 —— **取得到且可调 / 取得到但不可调 / 取不到（None）**；
#    ★★ 而"取不到"**不**等于"接口里没有"（★ 它可能只是**不在 dispinterface 里**）✓

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

INTEROP = Path(
    os.environ.get(
        "DSL_INTEROP",
        r"D:\Program Files\SOLIDWORKS Corp\SOLIDWORKS\api\redist\SolidWorks.Interop.sldworks.dll",
    )
)

PS_MEMBERS = r"""
$ErrorActionPreference = "Stop"
$asm = [Reflection.Assembly]::LoadFrom($env:DSL_INTEROP)
#: ★★ 真机第一版用**短名** ⇒ `GetType` 回 **null**（★ 而它需要**全名**）。
#:   ★ 故这里自动补命名空间：★ 先试原名，再试三个常用命名空间。
$t = $asm.GetType($env:DSL_TYPE)
if ($null -eq $t) {
  foreach ($ns in @("SolidWorks.Interop.sldworks", "SolidWorks.Interop.cosworks", "SolidWorks.Interop.swconst")) {
    $t = $asm.GetType($ns + "." + $env:DSL_TYPE)
    if ($null -ne $t) { break }
  }
}
if ($null -eq $t) { Write-Error ("type not found: " + $env:DSL_TYPE); exit 2 }
foreach ($m in $t.GetMembers()) { Write-Output ($m.MemberType.ToString() + "|" + $m.Name) }
"""


def interface_members(type_name: str, dll: Path | None = None) -> dict:
    """★ 回 `{成员名: 种类}`（★ 种类如 `Method` / `Property`）。

    ★ 走 **PowerShell 的 .NET 元数据反射**（★ 与 `typelib_iids.py` 同一路，★ 零依赖）。
    ⚠ 一个名字可能既是属性又有方法（★ 同名重载）⇒ ★ 本函数**保留先到的那个**并记账。
    """
    dll = Path(dll or INTEROP)
    if not dll.is_file():
        raise FileNotFoundError("出厂程序集不在：%s" % dll)
    env = dict(os.environ)
    env["DSL_INTEROP"] = str(dll)
    env["DSL_TYPE"] = type_name
    #: ★★ 第一版用 `-Command` 传**多行脚本** ⇒ 真机报了**一串脚本原文**（★ 即它没当脚本
    #: 执行）。
    #: ★★ **正解是 `-EncodedCommand`**（base64 / UTF-16LE）—— ★ 那是传多行脚本**最稳**的
    #: 方式 ✓
    import base64

    enc = base64.b64encode(PS_MEMBERS.encode("utf-16-le")).decode("ascii")
    r = subprocess.run(
        ["powershell", "-NoProfile", "-EncodedCommand", enc],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=env,
        timeout=300,
    )
    if r.returncode != 0 or not (r.stdout or "").strip():
        raise RuntimeError(
            "反射失败（%s）：%s" % (type_name, (r.stderr or r.stdout or "")[:160])
        )
    out: dict = {}
    for line in r.stdout.splitlines():
        if "|" in line:
            kind, _, nm = line.partition("|")
            nm = nm.strip()
            if nm and nm not in out:
                out[nm] = kind.strip()
    return out


def probe_members(obj, names) -> dict:
    """★ 逐个问真机：★ 回 `{名字: "callable" | "value" | "missing"}`。

    ★★ **判据**：★ `getattr(obj, 名, None)` ——
      ```
      ★ `None`        ⇒ **取不到**（★ 而★ 不一定是"接口里没有" —— ★ 可能只是不在 dispinterface 里）
      ★ 可调          ⇒ 方法
      ★ 其它          ⇒ 属性（★ 取值）
      ```
    ⚠ 一律**不调用**（★ "取或调"的坑见事实 227）—— ★ 只 `getattr`。
    """
    out: dict = {}
    for n in names:
        try:
            v = getattr(obj, n, None)
        except Exception:  # noqa: BLE001
            out[n] = "missing"
            continue
        out[n] = "missing" if v is None else ("callable" if callable(v) else "value")
    return out


# ⚑ 2026-10-03（轮 470）：这里曾有一个 `diff_against_interface(obj, type_name, *, limit)
# ` ——
#   它把「程序集成员名单」与「真机探测结果」对成三组（`on_object` / `unusable` /
#   `missing_from_assembly`），是**建库阶段的一次性分析助手**；那一阶段的结论已经写进
# `docs/known-facts.md` 与能力条目的 `limitations` ⇒ **它没被取代，而是**任务结束了****
# ，
#   从此全仓**没有任何调用点**（★ 实测：全仓出现 **1** 次 = 就只有这一处定义）。
#   ★ 删掉它、留这段墓碑 —— 依据是本仓自己的先例（`tools/propose_capability_sources.py`
#   L136-137 对 `match_modules` 的处理）★ 以及门禁 `tests/test_no_uncalled_helpers.py`
#   的判据：「门禁/工具里**不该有**定义了却全仓库没人调的函数」。
#   ⚠ 若将来又要做"程序集 vs 真机"对账：★ **别凭记忆重写** —— 上面那三组的语义
#   （尤其 `unusable` = 程序集里有而真机取不到）在 `docs/known-facts.md` 里有更详的记载。


def main(argv: list) -> int:
    args = [a for a in argv if not a.startswith("--")]
    if len(args) < 2:
        print(
            "  用法：python tools/com_member_probe.py <\u63a5\u53e3\u540d> <\u6a21\u5f0f>"
        )
        print("        ★ 模式：`members` 只列程序集里的名单（★ 不需要 SW）")
        print("        ★★ 而**问真机**的用法见 `tools/prove_member_availability.py`")
        return 2
    name, mode = args[0], args[1]
    if mode == "members":
        try:
            m = interface_members(name)
        except Exception as exc:  # noqa: BLE001
            print("  [SKIP] %s" % str(exc)[:120])
            return 0
        print("  %s：程序集里 **%d** 个成员" % (name, len(m)))
        for n in sorted(m)[:40]:
            print("    %-46s %s" % (n, m[n]))
        return 0
    print("  ★ 未知模式：%s" % mode)
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
