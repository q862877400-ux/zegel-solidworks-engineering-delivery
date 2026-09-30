# 通用 add-in 探测：绕开我的服务端，直接用 COM 探测各产品
# 依据：Simulation 当初的突破路径是 LoadAddIn -> GetAddInObject，
#      且【不依赖 AddinsStartup 注册】（注册表里全空，Simulation 照样能跑）。
$ErrorActionPreference = 'Continue'
$swDir = "D:\Program Files\SOLIDWORKS Corp\SOLIDWORKS"

# 挂到已在运行的 SolidWorks 上
# 注意：pwsh(.NET Core) 没有 Marshal.GetActiveObject（.NET Framework 独有，已移除）。
# SolidWorks 是单实例并注册在 ROT，New-Object -ComObject 会连到已运行的那个。
$sw = New-Object -ComObject SldWorks.Application
if(-not $sw){ Write-Output "拿不到 SldWorks.Application"; exit 1 }
Write-Output "已连上 SldWorks.Application"
Write-Output ""

# 候选：各产品的 add-in 名 + 可能的 dll
$cands = @(
  @{n='SldWorks.Simulation';    dll='Simulation\cosworks.dll'},
  @{n='SldWorks.Electrical';    dll='Electrical\SwElectrical.dll'},
  @{n='SldWorks.FlowSimulation';dll='Flow Simulation\FlowSimulation.dll'},
  @{n='SldWorks.Costing';       dll=$null},
  @{n='SldWorks.Sustainability';dll=$null},
  @{n='SldWorks.3DPrinter';     dll=$null},
  @{n='SldWorks.DimXpert';      dll=$null},
  @{n='SldWorks.DesignChecker'; dll=$null}
)

Write-Output "=== 逐个 LoadAddIn + GetAddInObject ==="
foreach($c in $cands){
  $status = ''
  try {
    if($c.dll -and (Test-Path (Join-Path $swDir $c.dll))){
      $r = $sw.LoadAddIn((Join-Path $swDir $c.dll))
      $status = "LoadAddIn=$r"
    } else { $status = "无dll路径, 直接试" }
    $obj = $sw.GetAddInObject($c.n)
    if($obj){
      $t = $obj.GetType().Name
      # 试着取一个属性证明真的活着
      $probe = ''
      try { $v = $obj.GetType().InvokeMember('RevisionNumber','GetProperty',$null,$obj,$null); $probe = " RevisionNumber=$v" } catch {}
      Write-Output "  ✅ {0,-26} {1,-22} obj={2}{3}" -f $c.n, $status, $t, $probe
    } else {
      Write-Output "  ❌ {0,-26} {1,-22} GetAddInObject=null" -f $c.n, $status
    }
  } catch {
    Write-Output "  💥 {0,-26} {1}" -f $c.n, $_.Exception.Message.Substring(0,[Math]::Min(70,$_.Exception.Message.Length))
  }
}
