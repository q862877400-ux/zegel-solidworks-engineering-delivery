#!/usr/bin/env python3
"""从本机 SolidWorks 安装目录的 interop DLL 反射出 API 签名清单，供 arity 审计用。

用途
----
``scripts/audit_call_arity.py`` 需要一份「成员名 → 宿主接口 + 参数类型序列」的
清单才能判断某个 COM 调用的实参个数对不对。此前该清单是**仓库外**的
``D:\\AI\\SW\\_raw\\reflect\\*.txt``，换机器就失效。本脚本把它变成**可复现的**：
只要本机装了 SolidWorks，一条命令即可重新生成。

    python scripts/refresh_api_signatures.py
    python scripts/refresh_api_signatures.py --out D:/somewhere

⚠ **产物不提交进仓库**（见 ``.gitignore`` 的 ``.api-signatures/``）。
   理由：清单是从达索 interop 程序集派生的内容，虽属事实性签名而非创作性表达，
   但把大体积派生件塞进 MIT 仓库是不必要的分发风险。
   **工具进仓库、产物留在本地**——这样既可复现，又不外发。

⚠ 本脚本**只读程序集元数据**：不加载 COM 对象、不实例化、不连接 SolidWorks，
   符合 AGENTS.md 铁律 2。

⚠ 反射需要能枚举 .NET 程序集。标准库做不到这一点，故本脚本**生成并调用一段
   PowerShell**（.NET 运行时自带反射能力），而不是自己解析二进制。
   若本机 PowerShell 为 ConstrainedLanguage 模式且禁止 Add-Type，
   脚本会给出明确提示而不是静默产出空清单。
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import tempfile
from pathlib import Path

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（本任务的工具层）
# 文件:   scripts/refresh_api_signatures.py —— 本文件自身
# 定位:   本文件的模块常量、PS_TEMPLATE 反射脚本与 main() 全部单元。
# 依据:   PS_TEMPLATE 里的反射写法（纯 .NET API + 重入保护）来自
#         D:\AI\SW\tools\reflect-interop.ps1 —— 那是本任务为 cosworks
#         域清单写的同一段代码。本脚本把它内联，以**避免依赖仓库外的
#         D:\ 路径**（否则本工具换机器就失效）。
#         ⚠ 该 handler 内只能用纯 .NET：任何 cmdlet / New-Object 都会
#         触发 PowerShell 模块自动加载 → 重入 → 无限递归（本任务踩过）。
# ⚑ 初稿的路径 bug: 传给子进程的 -OutFile 是相对路径，而子进程 cwd 被设为
#   输出目录，导致生成 `.api-signatures/.api-signatures/iface_*.txt`。
#   现已改传绝对路径（见 main 里的 out_file_abs）。
# 覆盖:   全文件 —— 本模块是一个内聚的工具单元。
# ⚠ 本脚本只读程序集元数据，不加载/实例化任何 COM 对象（见 AGENTS.md 铁律 2）
# ⚠ 本工具的行为已**真实跑过**：生成 iface_sldworks.txt（17,766 行）
#   与 iface_cosworks.txt（2,690 行），并被 audit_call_arity 端到端消费。
# ────────────────────────────────────────────────────────────────────

for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
    except Exception:  # noqa: BLE001
        pass

DEFAULT_DLL_DIRS = (
    r"D:\Program Files\SOLIDWORKS Corp\SOLIDWORKS\api\redist",
    r"C:\Program Files\SOLIDWORKS Corp\SOLIDWORKS\api\redist",
)

#: 目标程序集。sldworks 是主程序集；cosworks 是 Simulation（域 13）。
DEFAULT_ASSEMBLIES = ("sldworks", "cosworks")

#: PowerShell 反射脚本。⚠ handler 内**只能用纯 .NET API**：
#: 任何 cmdlet / New-Object 都会触发 PowerShell 模块自动加载 → 重入 handler
#: → 无限递归（本项目已踩过一次，见 D:\AI\SW\tools\reflect-interop.ps1 的说明）。
PS_TEMPLATE = r"""
param([string]$DllDir, [string]$Assembly, [string]$OutFile)
$ErrorActionPreference = 'Stop'
$script:inHandler = $false
$handler = [System.ResolveEventHandler]{
  param($s, $e)
  if ($script:inHandler) { return $null }
  $script:inHandler = $true
  try {
    $n = ([System.Reflection.AssemblyName]::new($e.Name)).Name
    $p = [System.IO.Path]::Combine($DllDir, "SolidWorks.Interop.$n.dll")
    if ([System.IO.File]::Exists($p)) { return [System.Reflection.Assembly]::LoadFrom($p) }
    return $null
  } finally { $script:inHandler = $false }
}
[System.AppDomain]::CurrentDomain.add_AssemblyResolve($handler)
try {
  $dll = [System.IO.Path]::Combine($DllDir, "SolidWorks.Interop.$Assembly.dll")
  if (-not [System.IO.File]::Exists($dll)) { Write-Host "NO_DLL $Assembly"; exit 2 }
  $asm = [System.Reflection.Assembly]::LoadFrom($dll)
  $sb = [System.Text.StringBuilder]::new()
  [void]$sb.AppendLine("# reflection of SolidWorks.Interop.$Assembly.dll")
  [void]$sb.AppendLine("# format: ## <Interface> then '  <Ret> <Name>(<ParamTypes>)'")
  foreach ($t in ($asm.GetTypes() | Where-Object { $_.IsInterface -and $_.IsPublic } | Sort-Object Name)) {
    [void]$sb.AppendLine("## " + $t.Name)
    foreach ($m in ($t.GetMethods() | Sort-Object Name)) {
      $ps = ($m.GetParameters() | ForEach-Object { $_.ParameterType.Name }) -join ', '
      [void]$sb.AppendLine("  " + $m.ReturnType.Name + " " + $m.Name + "(" + $ps + ")")
    }
  }
  [System.IO.File]::WriteAllText($OutFile, $sb.ToString(), [System.Text.UTF8Encoding]::new($false))
  Write-Host "OK $Assembly -> $OutFile"
} finally {
  [System.AppDomain]::CurrentDomain.remove_AssemblyResolve($handler)
}
"""


def find_dll_dir(explicit: str | None) -> str:
    if explicit:
        if not Path(explicit).is_dir():
            raise SystemExit(f"[FATAL] 指定的 DLL 目录不存在: {explicit}")
        return explicit
    for candidate in DEFAULT_DLL_DIRS:
        if Path(candidate).is_dir():
            return candidate
    raise SystemExit(
        "[FATAL] 找不到 SolidWorks interop 目录。请确认已安装 SolidWorks，\n"
        f"       或用 --dll-dir 指定。已尝试: {', '.join(DEFAULT_DLL_DIRS)}"
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="从本机 interop DLL 反射出 API 签名清单（供 arity 审计用）"
    )
    parser.add_argument("--dll-dir", default=None, help="interop 目录（默认自动探测）")
    parser.add_argument("--out", default=".api-signatures", help="输出目录")
    parser.add_argument(
        "--assemblies",
        default=",".join(DEFAULT_ASSEMBLIES),
        help="目标程序集名，逗号分隔",
    )
    args = parser.parse_args()

    dll_dir = find_dll_dir(args.dll_dir)
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    print(f"interop 目录: {dll_dir}")
    print(f"输出目录    : {out_dir.resolve()}")

    failures: list[str] = []
    for assembly in [a.strip() for a in args.assemblies.split(",") if a.strip()]:
        with tempfile.TemporaryDirectory() as tmp:
            script = Path(tmp) / "reflect.ps1"
            script.write_text(PS_TEMPLATE, encoding="utf-8")
            out_file = out_dir / f"iface_{assembly}.txt"
            # ⚑ 必须传**绝对路径**：子进程的 cwd 被设为 out_dir，
            # 相对 OutFile 会在输出目录里再拼一次，生成
            # `.api-signatures/.api-signatures/iface_*.txt`（本脚本初版就栽在这）。
            out_file_abs = str(out_file.resolve())
            proc = subprocess.run(
                [
                    "pwsh",
                    "-NoProfile",
                    "-File",
                    str(script),
                    "-DllDir",
                    dll_dir,
                    "-Assembly",
                    assembly,
                    "-OutFile",
                    out_file_abs,
                ],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=900,
                cwd=str(out_dir),
            )
            sys.stdout.write(proc.stdout or "")
            if proc.returncode != 0 or not out_file.is_file():
                failures.append(assembly)
                sys.stderr.write(proc.stderr or "")
            else:
                size = out_file.stat().st_size
                lines = out_file.read_text(encoding="utf-8").count("\n")
                print(f"  iface_{assembly}.txt  {size} 字节 / {lines} 行")

    print()
    if failures:
        print(f"[WARN] 未能生成: {', '.join(failures)}")
        print("       arity 审计对这几个程序集会不可用。")
        return 1
    print(f"[OK] 全部生成。接下来可跑：")
    print(
        f"       python scripts\\audit_call_arity.py <文件> {out_dir.resolve()}/iface_sldworks.txt"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
