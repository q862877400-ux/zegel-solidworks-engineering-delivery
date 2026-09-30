# ─────────────────────────────────────────────────────────────────────
# 用途：对指定 interop 程序集里的枚举做纯元数据反射，产出「名称 = 数值」清单。
# 为什么需要：C:\swapi 的部分枚举 md（例如 swFeatureNameID_e）只有名称列、
#   没有数值列，而 AGENTS.md 铁律 4 要求「枚举值必须查，不许猜」。
#   故以托管程序集元数据作为取值真源（读官方程序集，不是实测）。
#
# ⚠ 踩坑记录（重要，勿删）：
#   解析程序集的 AssemblyResolve handler 里**绝对不能用 PowerShell cmdlet
#   或 New-Object**。它们会触发 PowerShell 的模块自动加载，而模块加载又会
#   调用 ResourceManager → 再次进入同一个 handler，形成无限递归，
#   最终以栈溢出 + 数百行递归栈文本收场。handler 内部只能用纯 .NET API，
#   并配合 $script:inHandler 重入保护兜底。
#
# 用法：pwsh -NoProfile -File reflect-enum.ps1 -Assembly swconst -Enum swFeatureNameID_e
# ─────────────────────────────────────────────────────────────────────
param(
  [Parameter(Mandatory = $true)][string]$Assembly,
  [Parameter(Mandatory = $true)][string]$Enum
)
$ErrorActionPreference = 'Stop'
$redist = 'D:\Program Files\SOLIDWORKS Corp\SOLIDWORKS\api\redist'
$script:inHandler = $false

$handler = [System.ResolveEventHandler]{
  param($s, $e)
  if ($script:inHandler) { return $null }          # 重入保护
  $script:inHandler = $true
  try {
    # 纯 .NET：不得使用 cmdlet / New-Object
    $n = ([System.Reflection.AssemblyName]::new($e.Name)).Name
    $p = [System.IO.Path]::Combine($redist, "SolidWorks.Interop.$n.dll")
    if ([System.IO.File]::Exists($p)) {
      return [System.Reflection.Assembly]::LoadFrom($p)
    }
    return $null
  } finally {
    $script:inHandler = $false
  }
}
[System.AppDomain]::CurrentDomain.add_AssemblyResolve($handler)

try {
  $dll = [System.IO.Path]::Combine($redist, "SolidWorks.Interop.$Assembly.dll")
  if (-not [System.IO.File]::Exists($dll)) { Write-Host "NO_DLL $Assembly"; exit 2 }

  $asm = [System.Reflection.Assembly]::LoadFrom($dll)
  $type = $asm.GetType("SolidWorks.Interop.swconst.$Enum")
  if ($null -eq $type) {
    Write-Host "NO_ENUM $Enum in $Assembly"
    $prefix = $Enum.Substring(0, [Math]::Min(8, $Enum.Length))
    foreach ($t in $asm.GetTypes()) {
      if ($t.IsEnum -and $t.Name.Contains($prefix)) { Write-Host "  CANDIDATE $($t.Name)" }
    }
    exit 3
  }

  Write-Host "# $($type.FullName)  ($($asm.GetName().Name) $($asm.GetName().Version))"
  foreach ($name in [System.Enum]::GetNames($type)) {
    $val = [System.Convert]::ToInt64([System.Enum]::Parse($type, $name))
    Write-Host "$name = $val"
  }
} finally {
  [System.AppDomain]::CurrentDomain.remove_AssemblyResolve($handler)
}
