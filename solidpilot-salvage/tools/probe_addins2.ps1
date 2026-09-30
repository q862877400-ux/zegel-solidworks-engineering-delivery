# 通用 add-in 探测（强类型版）
# 关键教训：New-Object -ComObject 得到的是裸 IDispatch，GetAddInObject 解析不出来
#   （TYPE_E_ELEMENTNOTFOUND 0x8002802B）——必须加载 interop DLL 转成强类型 ISldWorks。
# 这与我在 Simulation 上踩过的坑完全一致。
$ErrorActionPreference = 'Continue'
$redist = "D:\Program Files\SOLIDWORKS Corp\SOLIDWORKS\api\redist"

# 1) 加载强类型 interop
Add-Type -Path "$redist\SolidWorks.Interop.swconst.dll" -EA SilentlyContinue
$asm = [Reflection.Assembly]::LoadFrom("$redist\SolidWorks.Interop.sldworks.dll")
$ISldWorks = $asm.GetType('SolidWorks.Interop.sldworks.ISldWorks')
Write-Output "已加载 ISldWorks 类型: $($null -ne $ISldWorks)"

# 2) 拿到 COM 对象并转强类型
$raw = New-Object -ComObject SldWorks.Application
$sw = [Runtime.InteropServices.Marshal]::GetTypedObjectForIUnknown(
        [Runtime.InteropServices.Marshal]::GetIUnknownForObject($raw), $ISldWorks)
Write-Output "强类型 ISldWorks: $($null -ne $sw)"
Write-Output "  RevisionNumber = $($sw.RevisionNumber())"
Write-Output ""

# 3) 找各产品的 add-in：先扫安装目录里所有可能的 addin dll
$swDir = "D:\Program Files\SOLIDWORKS Corp\SOLIDWORKS"
Write-Output "=== 安装目录里的 addin 型 dll（候选）==="
$cands = Get-ChildItem $swDir -Recurse -Filter "*.dll" -EA SilentlyContinue |
         Where-Object { $_.Name -match 'cosworks|Electrical|Flow|Cost|Sustain|3DPrint|DimXpert|DesignCheck|Routing' } |
         Select-Object -First 14
$cands | ForEach-Object { "  $($_.Name)  ←  $(Split-Path $_.DirectoryName -Leaf)" }

Write-Output ""
Write-Output "=== LoadAddIn + GetAddInObject 逐个试 ==="
$names = 'SldWorks.Simulation','CosmosWorks.CosmosWorks','SldWorks.Electrical',
         'SldWorks.FlowSimulation','SldWorks.Costing','SldWorks.Sustainability',
         'SldWorks.3DPrinter','SldWorks.DimXpert','SldWorks.DesignChecker','SldWorks.Routing'
foreach($n in $names){
  $r = 'n/a'; $o = $null
  try { $o = $sw.GetAddInObject($n); $r = if($o){'obj'}else{'null'} }
  catch { $r = "EX:$($_.Exception.GetType().Name)" }
  "  {0,-28} GetAddInObject => {1}" -f $n, $r
}

Write-Output ""
Write-Output "=== 扫所有已加载的 addin 名字（AddInStack）==="
try {
  $st = $sw.GetAddInStack()   # 返回已加载的 addin 名列表
  if($st){ $st | ForEach-Object { "  $_" } } else { "  (空/不支持)" }
} catch { "  GetAddInStack 不支持: $($_.Exception.Message.Substring(0,[Math]::Min(60,$_.Exception.Message.Length)))" }
