# 套件：其它产品线的 API 可达性探测
# 依据：api\redist 下每个 interop DLL = 一个可编程产品。目标范围②要求全部实测。
$ErrorActionPreference='Continue'
$redist = "D:\Program Files\SOLIDWORKS Corp\SOLIDWORKS\api\redist"
$out = New-Object System.Collections.ArrayList

# ── 1. 列出所有 interop DLL 并尝试加载 ──
Write-Output "=== 全部 interop DLL 加载测试 ==="
Get-ChildItem $redist -Filter "*.dll" | ForEach-Object {
  $n = $_.Name
  try {
    $asm = [Reflection.Assembly]::LoadFrom($_.FullName)
    $types = $asm.GetExportedTypes()
    [void]$out.Add([pscustomobject]@{Dll=$n;Loaded=$true;Types=$types.Count})
    Write-Output "  ✅ {0,-42} {1,4} 个类型" -f $n, $types.Count
  } catch {
    [void]$out.Add([pscustomobject]@{Dll=$n;Loaded=$false;Types=0})
    Write-Output "  ❌ {0,-42} {1}" -f $n, $_.Exception.Message.Substring(0,[Math]::Min(50,$_.Exception.Message.Length))
  }
}

# ── 2. 重点：几个从未碰过的产品，关键接口清单 ──
Write-Output ""
Write-Output "=== 未测产品的关键接口 ==="
$targets = @{
  'SolidWorks.Interop.dsgnchk.dll'   = 'Design Checker'
  'SolidWorks.Interop.fworks.dll'    = 'Flow Simulation'
  'SolidWorks.Interop.sldcostingapi.dll' = 'Costing'
  'SolidWorks.Interop.sustainability.dll' = 'Sustainability'
  'SolidWorks.Interop.sw3dprinter.dll' = '3D Printer'
  'SolidWorks.Interop.swdimxpert.dll' = 'DimXpert'
  'SolidWorks.Interop.SWRoutingLib.dll' = 'Routing'
}
foreach($dll in $targets.Keys){
  $p = Join-Path $redist $dll
  if(-not (Test-Path $p)){ Write-Output "  [缺] $dll"; continue }
  try{
    $asm = [Reflection.Assembly]::LoadFrom($p)
    $its = $asm.GetExportedTypes() | Where-Object { $_.IsInterface -and $_.Name -like 'I*' }
    $main = $its | Select-Object -First 6 | ForEach-Object { $_.Name }
    Write-Output "  【$($targets[$dll])】 $($its.Count) 个接口；主要：$($main -join ', ')"
  } catch { Write-Output "  ❌ $dll : $($_.Exception.Message.Substring(0,[Math]::Min(60,$_.Exception.Message.Length)))" }
}

$out | Export-Csv -Path "C:\Users\Zegel\solidpilot-mcp\api_products.csv" -NoTypeInformation -Encoding UTF8
