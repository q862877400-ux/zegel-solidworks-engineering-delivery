. "C:\Users\Zegel\solidpilot-mcp\tools\call.ps1"
# ★ 第一个真正跑起来的"其它产品线"能力：Design Checker
# 已知（实测）：
#   CoCreateInstance(SWDesignCheckClass) => 成功（CLSID df1ad3b3-… 在 HKLM 注册）
#   官方标准检查文件在 SOLIDWORKS\spiop\files\resources\standard\*.xml
$parts = "D:\AI\SW\AI Solidworks\模型"
$std   = "D:\Program Files\SOLIDWORKS Corp\SOLIDWORKS\spiop\files\resources\standard"
$rpt   = "$env:TEMP\dc_report"
New-Item -ItemType Directory -Force -Path $rpt | Out-Null

Write-Output "=== 标准检查文件清单 ==="
Get-ChildItem $std -Filter "*.xml" -EA SilentlyContinue | Select-Object -First 8 |
  ForEach-Object { "  $($_.Name)  ($([int]$_.Length/1KB)KB)" }

Write-Output ""
Write-Output "=== 打开一个零件（DesignChecker 需要活动文档）==="
$null = Call 'open_document' @{ file_path="$parts\主轴壳体_Housing.sldprt" }
Write-Output "  当前文档: $((Call 'verify_state' @{}).cadState.activeDocument)"

# 通过服务端调 DesignChecker（必须在 STA + 持有正确实例）
Write-Output ""
Write-Output "=== 用服务端跑 DesignChecker ==="
$pick = (Get-ChildItem $std -Filter "*.xml" -EA SilentlyContinue | Select-Object -First 1).FullName
Write-Output "  用标准文件: $(Split-Path $pick -Leaf)"
$r = Call 'design_check' @{ standard_file=$pick; report_dir=$rpt; overwrite=$true } -TimeoutSec 180
Write-Output "  status = $($r.status)  $(if($r.status -ne 'COMPLETED'){$r.error.code})"
if($r.status -eq 'COMPLETED'){
  Write-Output "  $(($r.cadState.features[0] -replace '\s+',' ').Substring(0,[Math]::Min(400,($r.cadState.features[0] -replace '\s+',' ').Length)))"
} else {
  Write-Output "  msg = $($r.error.message)"
}
