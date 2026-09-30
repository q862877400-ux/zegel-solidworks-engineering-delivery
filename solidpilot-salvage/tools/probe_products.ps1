. "C:\Users\Zegel\solidpilot-mcp\tools\call.ps1"
# 真实探测各产品 add-in 的可达性（目标要求"必须真实调用一次"）
# 方法：LoadAddIn → GetAddInObject → 报对象类型。这与 Simulation 当初的突破路径相同。

$redist = "D:\Program Files\SOLIDWORKS Corp\SOLIDWORKS\api\redist"
$swDir  = "D:\Program Files\SOLIDWORKS Corp\SOLIDWORKS"

Write-Output "=== 各产品 add-in 的注册位置 ==="
foreach($k in 'SldWorks.Simulation.19','SldWorks.Electrical','SldWorks.FlowSimulation',
              'SldWorks.DesignChecker','SldWorks.Costing','SldWorks.Sustainability',
              'SldWorks.3DPrinter','SldWorks.DimXpert','SldWorks.Routing'){
  $v = (Get-ItemProperty "HKCU:\Software\SolidWorks\AddinsStartup\$k" -EA SilentlyContinue).'(default)'
  $v2 = (Get-ItemProperty "HKLM:\SOFTWARE\SolidWorks\AddinsStartup\$k" -EA SilentlyContinue).'(default)'
  $s = if($null -ne $v){"HKCU=$v"} elseif($null -ne $v2){"HKLM=$v2"} else {'未注册'}
  "  {0,-30} {1}" -f $k, $s
}

Write-Output ""
Write-Output "=== 服务端现有哪些产品探测入口 ==="
$svc = "C:\Users\Zegel\solidpilot-mcp\execution\solidworks\SolidworksExecution"
Get-ChildItem $svc -Recurse -Filter *.cs | ForEach-Object {
  $h = Select-String -Path $_.FullName -Pattern 'GetAddInObject\("([^"]+)"' -AllMatches
  if($h){
    $names = $h | ForEach-Object { $_.Matches } | ForEach-Object { $_.Groups[1].Value } | Sort-Object -Unique
    "  $($_.Name): $($names -join ', ')"
  }
}

Write-Output ""
Write-Output "=== 独立 exe 形态的产品（可直接起进程）==="
Get-ChildItem $swDir -Recurse -Filter "*.exe" -EA SilentlyContinue |
  Where-Object { $_.Name -match 'DesignChecker|dcw|swcost|Costing|3DPrint|InspectTool' } |
  Select-Object -First 8 | ForEach-Object { "  $($_.Name)  →  $($_.DirectoryName)" }
