. "C:\Users\Zegel\solidpilot-mcp\tools\call.ps1"
# R19：① Toolbox 实证（目标明确要求，我从未测过）② 标准件库真实内容
Write-Output "=== ① list_standard_parts：读真实的标准件库 ==="
foreach($lib in $null,'C:\ProgramData\SOLIDWORKS\SOLIDWORKS 2026\design library','C:\ProgramData\SOLIDWORKS\SOLIDWORKS 2026\design library\parts'){
  $p = @{}
  $tag = '(默认)'
  if($lib){ $p = @{folder=$lib}; $tag = (Split-Path $lib -Leaf) }
  $r = Call 'list_standard_parts' $p -TimeoutSec 120
  if($r.status -eq 'COMPLETED'){
    $t = $r.cadState.features[0]
    Write-Output ("  folder='{0}'" -f $tag)
    Write-Output "    $($t.Substring(0,[Math]::Min(230,$t.Length)))"
  } else {
    Write-Output ("  folder='{0}' => FAILED {1}" -f $tag, $r.error.code)
  }
}

Write-Output ""
Write-Output "=== ② Toolbox：注册表里的 CLSID 能否实例化 ==="
$sig = @'
using System;using System.Runtime.InteropServices;
public class TB { [DllImport("ole32.dll")] public static extern int CoCreateInstance(ref Guid c, IntPtr o, uint ctx, ref Guid i, out IntPtr ppv); }
'@
if(-not ("TB" -as [type])){ Add-Type -TypeDefinition $sig }
$redist = "D:\Program Files\SOLIDWORKS Corp\SOLIDWORKS\api\redist"
# Toolbox 的 interop 类型
if(Test-Path "$redist\SolidWorks.Interop.sldtoolboxconfigureaddin.dll"){
  try{
    $asm = [Reflection.Assembly]::LoadFrom("$redist\SolidWorks.Interop.sldtoolboxconfigureaddin.dll")
    $ifs = $asm.GetExportedTypes() | Where-Object { $_.IsInterface }
    Write-Output "  interop 接口: $($ifs.Count) 个 → $(($ifs | Select-Object -First 6 | ForEach-Object { $_.Name }) -join ', ')"
  } catch { Write-Output "  interop 加载失败: $($_.Exception.Message)" }
}
# 逐个试注册表里的 toolboxdata CLSID
$clsids = @(
  @{g='{02383289-21B5-31D7-BDD9-FE51E1426516}'; n='sldtoolboxdata.AppUtils'},
  @{g='{159ED2DC-59D4-4BB7-90FF-6DA31FA76371}'; n='sldtoolboxdata.ToolboxSolver'}
)
foreach($c in $clsids){
  $k = "HKLM:\SOFTWARE\Classes\CLSID\$($c.g)"
  $dll = ''
  if(Test-Path "$k\InprocServer32"){ $dll = (Get-ItemProperty "$k\InprocServer32" -EA SilentlyContinue).'(default)' }
  $iid = [guid]'00000000-0000-0000-C000-000000000046'   # IUnknown
  $cls = [guid]($c.g -replace '^\{|\}$','')
  $ppv = [IntPtr]::Zero
  $hr = [TB]::CoCreateInstance([ref]$cls,[IntPtr]::Zero,5,[ref]$iid,[ref]$ppv)
  $mark = if($hr -eq 0){'✅'}else{'❌'}
  Write-Output ("  {0} {1,-32} 0x{2}" -f $mark, $c.n, $hr.ToString('X8'))
  if($ppv -ne [IntPtr]::Zero){ [void][Runtime.InteropServices.Marshal]::Release($ppv) }
  if($dll){ Write-Output "       实现 = $dll" }
}

Write-Output ""
Write-Output "=== ③ routing 库有 216 个文件但 CLSID 未注册 —— 看这些文件是什么 ==="
$r = Get-ChildItem "C:\ProgramData\SOLIDWORKS\SOLIDWORKS 2026\design library\routing" -Recurse -File -EA SilentlyContinue
$r | Group-Object Extension | ForEach-Object { "  $($_.Name) × $($_.Count)" }
$r | Select-Object -First 4 | ForEach-Object { "    $($_.Name)  $([int]$_.Length/1KB)KB" }

