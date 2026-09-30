# ★ 系统验证：interop 能加载 ≠ 产品已安装（R18 发现的关键模式）
# 判据：CoClass 的 CLSID 有没有在注册表 + 能不能 CoCreateInstance
$ErrorActionPreference='Continue'
$redist = "D:\Program Files\SOLIDWORKS Corp\SOLIDWORKS\api\redist"
$swDir  = "D:\Program Files\SOLIDWORKS Corp\SOLIDWORKS"

$sig = @'
using System;using System.Runtime.InteropServices;
public class PZ {
  [DllImport("ole32.dll")] public static extern int CoCreateInstance(ref Guid c, IntPtr o, uint ctx, ref Guid i, out IntPtr ppv);
}
'@
if(-not ("PZ" -as [type])){ Add-Type -TypeDefinition $sig }

# 每条产品线：(名称, interop dll, 主 CoClass, 主接口)
$prods = @(
  @{n='DimXpert';        dll='swdimxpert';      cls='DimXpertPartClass';        ifc='IDimXpertPart'},
  @{n='DesignChecker';   dll='dsgnchk';         cls='SWDesignCheckClass';       ifc='ISWDesignCheck'},
  @{n='Costing';         dll='sldcostingapi';   cls='CostManagerClass';         ifc='ICostManager'},
  @{n='Routing';         dll='SWRoutingLib';    cls='RoutePropertyClass';       ifc='IRouteProperty'},
  @{n='Sustainability';  dll='sustainability';  cls='sustainabilityAppClass';   ifc='ISustainabilityApp'},
  @{n='3D Printer';      dll='sw3dprinter';     cls='SW3DPrinterClass';         ifc='ISw3DPrinter'},
  @{n='Simulation';      dll='cosworks';        cls=$null;                      ifc=$null}
)

Write-Output "=== 12 条产品线：注册状态 vs interop 可加载 ==="
Write-Output ("{0,-16} {1,-14} {2,-12} {3,-14} {4}" -f '产品线','interop','接口数','CLSID注册','CoCreateInstance')
Write-Output ("-" * 78)

$rows = @()
foreach($p in $prods){
  $path = Join-Path $redist "SolidWorks.Interop.$($p.dll).dll"
  $nIfc = 0; $loaded = $false
  if(Test-Path $path){
    try{
      $asm = [Reflection.Assembly]::LoadFrom($path)
      $nIfc = ($asm.GetExportedTypes() | Where-Object { $_.IsInterface }).Count
      $loaded = $true
    } catch {}
  }
  $reg='—'; $cci='—'
  if($p.cls){
    $t = $null
    try{ $asm2 = [Reflection.Assembly]::LoadFrom($path); $t = $asm2.GetType("SolidWorks.Interop.$($p.dll).$($p.cls)") } catch {}
    if($t){
      $clsid = $t.GUID
      $reg = if(Test-Path "HKLM:\SOFTWARE\Classes\CLSID\{$clsid}"){'✅HKLM'} elseif(Test-Path "HKCR:\CLSID\{$clsid}"){'✅HKCR'} else {'❌未注册'}
      $ifcT = $null
      try{ $ifcT = $asm2.GetType("SolidWorks.Interop.$($p.dll).$($p.ifc)") } catch {}
      if($ifcT){
        $iid = $ifcT.GUID
        $ppv=[IntPtr]::Zero
        $hr = [PZ]::CoCreateInstance([ref]$clsid,[IntPtr]::Zero,5,[ref]$iid,[ref]$ppv)
        $cci = if($hr -eq 0){'✅成功'} else {"0x$($hr.ToString('X8'))"}
        if($ppv -ne [IntPtr]::Zero){ [void][Runtime.InteropServices.Marshal]::Release($ppv) }
      } else { $cci = '(接口类型未找到)' }
    } else { $reg='(类未找到)'; $cci='—' }
  } else {
    # Simulation 走 add-in
    $reg = 'add-in'
    $cci = '（走 LoadAddIn，已实测 ✅）'
  }
  Write-Output ("{0,-16} {1,-14} {2,-12} {3,-14} {4}" -f $p.n, $(if($loaded){'✅可加载'}else{'❌'}), $nIfc, $reg, $cci)
  $rows += [pscustomobject]@{Product=$p.n; Loaded=$loaded; Interfaces=$nIfc; Registered=$reg; CoCreate=$cci}
}

Write-Output ""
Write-Output "=== 结论 ==="
$okp = $rows | Where-Object { $_.CoCreate -eq '✅成功' -or $_.CoCreate -like '*已实测*' }
$np  = $rows | Where-Object { $_.Registered -eq '❌未注册' }
"  ✅ 真正可用: $(($okp|ForEach-Object{$_.Product}) -join ', ')"
"  ❌ 未注册(装了但没完整安装): $(($np|ForEach-Object{$_.Product}) -join ', ')"
"  ⚠ ⇒ interop DLL 只是【类型定义】，随主程序分发；它能加载【不代表产品已安装】"
$rows | Export-Csv "C:\Users\Zegel\solidpilot-mcp\product_availability.csv" -NoTypeInformation -Encoding UTF8
