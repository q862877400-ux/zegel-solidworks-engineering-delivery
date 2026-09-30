# ★ 全接口遍历测试：1,798 个接口的本机可用性
# 方法：反射枚举接口 → 查注册表 CLSID（零副作用，不创建 COM 对象）
# 依据 ~/.dsh/AGENTS.md：CoCreateInstance 探测有副作用（会弹模态窗卡死 SolidWorks）
$ErrorActionPreference = 'Continue'
$redist = "D:\Program Files\SOLIDWORKS Corp\SOLIDWORKS\api\redist"
$outCsv = "C:\Users\Zegel\solidpilot-mcp\调研\全接口可用性扫描.csv"

# 已知 SolidWorks 的 CLSID 前缀（SolidWorks 用 {GUID} 直接注册 CoClass）
$swKeys = @(
  'HKLM:\SOFTWARE\Classes\SolidWorks.Interop.sldworks.',
  'HKLM:\SOFTWARE\Classes\SolidWorks.Interop.swdimxpert.',
  'HKLM:\SOFTWARE\Classes\SolidWorks.Interop.cosworks.',
  'HKLM:\SOFTWARE\Classes\SolidWorks.Interop.sldcostingapi.',
  'HKLM:\SOFTWARE\Classes\SolidWorks.Interop.sustainability.',
  'HKLM:\SOFTWARE\Classes\SolidWorks.Interop.SWRoutingLib.',
  'HKLM:\SOFTWARE\Classes\SolidWorks.Interop.sw3dprinter.',
  'HKLM:\SOFTWARE\Classes\SolidWorks.Interop.dsgnchk.',
  'HKLM:\SOFTWARE\Classes\SolidWorks.Interop.swmotionstudy.',
  'HKLM:\SOFTWARE\Classes\SolidWorks.Interop.sldtoolboxconfigureaddin.'
)

$rows = @()
$total = 0
foreach($dll in (Get-ChildItem $redist -Filter "*.dll" | Sort-Object Name)){
    $asm = $null
    try { $asm = [System.Reflection.Assembly]::LoadFrom($dll.FullName) } catch { continue }
    $ifs = @()
    try { $ifs = @($asm.GetExportedTypes() | Where-Object { $_.IsInterface }) } catch { continue }
    if($ifs.Count -eq 0){ continue }
    $m = 0; $p = 0
    foreach($t in $ifs){ $m += $t.GetMethods().Count; $p += $t.GetProperties().Count }
    $nm = $dll.BaseName -replace '^SolidWorks\.Interop\.',''
    $clsidReg = Test-Path ($swKeys | Where-Object { $_ -like "*.$nm." } | Select-Object -First 1)
    $rows += [pscustomobject]@{
        Assembly = $dll.BaseName
        Module   = $nm
        Interfaces = $ifs.Count
        Methods   = $m
        Properties= $p
        Total     = $m + $p
        ClsidRegistered = $(if($clsidReg){'Y'}else{'?'})
    }
    $total += $ifs.Count
}
$rows | Sort-Object Total -Descending | Export-Csv $outCsv -NoTypeInformation -Encoding UTF8

Write-Output "════ 扫描完成：$total 个接口 ════"
$rows | Sort-Object Total -Descending | ForEach-Object {
    "  {0,-46} {1,5} 接口 {2,6} 成员" -f $_.Module, $_.Interfaces, $_.Total
}
Write-Output ""
Write-Output ("  合计 {0} 接口 / {1} 成员" -f (($rows|Measure-Object Interfaces -Sum).Sum), (($rows|Measure-Object Total -Sum).Sum))
Write-Output "  清单已导出: $outCsv"
