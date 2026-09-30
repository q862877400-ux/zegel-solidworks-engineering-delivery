# DimXpert 能否通过 slddimxpertclru.dll 激活？
# 背景（2026-09-28 实测）：
#   DimXpertPartClass CLSID = {a7af9c2d-52e5-40f1-9d6e-c2dfb4bcd204} 注册表【未注册】
#   本机没有任何 DimXpert 的 exe，只有 slddimxpertclru.dll（2MB，"cl"=command line 版）
#   唯一的选择：把该 DLL 当 InprocServer32 手动 LoadLibrary 后 CoCreateInstance
$ErrorActionPreference = 'Continue'

$sig = @'
using System;using System.Runtime.InteropServices;
public class DX {
  [DllImport("kernel32.dll", SetLastError=true, CharSet=CharSet.Unicode)]
  public static extern IntPtr LoadLibraryW(string p);
  [DllImport("ole32.dll")]
  public static extern int CoCreateInstance(ref Guid c, IntPtr o, uint ctx, ref Guid i, out IntPtr ppv);
}
'@
if(-not ("DX" -as [type])){ Add-Type -TypeDefinition $sig }

$clsid = [guid]'a7af9c2d-52e5-40f1-9d6e-c2dfb4bcd204'
$iid   = [guid]'a7af9c2d-52e5-40f1-9d6e-c2dfb4bcd203'   # IDimXpertPart

Write-Output "=== ① 裸 CoCreateInstance（不加载 DLL，注册表没有应失败）==="
$ppv = [IntPtr]::Zero
$hr = [DX]::CoCreateInstance([ref]$clsid,[IntPtr]::Zero,5,[ref]$iid,[ref]$ppv)
"  hr = 0x$($hr.ToString('X8'))  $(if($hr -eq 0){'✅'}else{'（预期 0x80040154 未注册）'})"

Write-Output ""
Write-Output "=== ② 手动 LoadLibrary slddimxpertclru.dll 后再试 ==="
$dll = "D:\Program Files\SOLIDWORKS Corp\SOLIDWORKS\slddimxpertclru.dll"
"  DLL 存在: $(Test-Path $dll)  ($([int]((Get-Item $dll).Length/1MB))MB)"
$h = [DX]::LoadLibraryW($dll)
"  LoadLibrary → 0x$($h.ToInt64().ToString('X'))  $(if($h -ne [IntPtr]::Zero){'✅ 已加载'}else{'❌ 失败 err=' + [Runtime.InteropServices.Marshal]::GetLastWin32Error()})"

if($h -ne [IntPtr]::Zero){
  $ppv2 = [IntPtr]::Zero
  $hr2 = [DX]::CoCreateInstance([ref]$clsid,[IntPtr]::Zero,5,[ref]$iid,[ref]$ppv2)
  "  CoCreateInstance → 0x$($hr2.ToString('X8'))"
  if($hr2 -eq 0 -and $ppv2 -ne [IntPtr]::Zero){
    "  ✅★ 成功拿到 IDimXpertPart！ptr=0x$($ppv2.ToInt64().ToString('X'))"
    # 反射调一个方法看看对象活着
    $redist = "D:\Program Files\SOLIDWORKS Corp\SOLIDWORKS\api\redist"
    $asm = [Reflection.Assembly]::LoadFrom("$redist\SolidWorks.Interop.swdimxpert.dll")
    $it = $asm.GetType('SolidWorks.Interop.swdimxpert.IDimXpertPart')
    $obj = [Runtime.InteropServices.Marshal]::GetTypedObjectForIUnknown($ppv2, $it)
    "  强类型对象: $($obj.GetType().FullName)"
    foreach($mn in 'GetFeatureCount','GetAnnotationCount','GetDimOption'){
      try{
        $mi = $it.GetMethod($mn)
        $v = $mi.Invoke($obj, $null)
        "    $mn() = $v"
      } catch { "    $mn threw $($_.Exception.GetType().Name)" }
    }
    [void][Runtime.InteropServices.Marshal]::Release($ppv2)
  } else {
    "  ❌ 仍失败。0x80040154=类未在注册表；0x80004002=接口不对"
    "  ⇒ 结论：slddimxpertclru.dll 里【没有】这个 CoClass（它只是命令行执行器，不是 COM 服务器）"
  }
}
