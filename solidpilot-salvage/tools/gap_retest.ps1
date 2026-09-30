. "C:\Users\Zegel\solidpilot-mcp\tools\call.ps1"
$parts = "D:\AI\SW\AI Solidworks\模型"

Write-Output "=== ① lcsc_fetch_step：用 keyword 参数 ==="
$r = Call 'lcsc_fetch_step' @{ keyword = "R0603"; limit = 3 } -TimeoutSec 120
Write-Output "  status = $($r.status)  $(if($r.status -ne 'COMPLETED'){$r.error.code})"
if ($r.status -eq 'COMPLETED') {
  Write-Output "  $(($r.cadState.features[0] -replace '\s+',' ').Substring(0,[Math]::Min(220,($r.cadState.features[0] -replace '\s+',' ').Length)))"
} else { Write-Output "  msg = $($r.error.message)" }

Write-Output ""
Write-Output "=== ② add_ref(point)：用【真实顶点】坐标 ==="
$null = Call 'open_document' @{ file_path = "$parts\主轴壳体_Housing.sldprt" }
$e = Call 'analyze_model' @{ analysis_type='edges' }
$ej = $e.cadState.features[0] | ConvertFrom-Json
Write-Output "  该零件边数 = $($ej.edge_count)"
if ($ej.edges -and $ej.edges.Count -gt 0) {
  $v0 = $ej.edges[0].start      # 第一个边的起点 = 一个真实顶点
  Write-Output "  取真实顶点 = $($v0 -join ', ')"
  $r2 = Call 'add_reference_geometry' @{ type='point'; px=$v0[0]; py=$v0[1]; pz=$v0[2] }
  Write-Output "  add_ref(point) = $($r2.status)  $(if($r2.status -ne 'COMPLETED'){$r2.error.code})"
  if ($r2.status -eq 'COMPLETED') {
    Write-Output "  → $($r2.cadState.features[0])"
  }
}

Write-Output ""
Write-Output "=== ③ topology_optimize(probe) 为什么 NO_STUDY ==="
$null = Call 'open_document' @{ file_path = "$parts\换刀主轴装配_BT30_ATC_Assembly.SLDASM" }
$r3 = Call 'topology_optimize' @{ action='probe' } -TimeoutSec 120
Write-Output "  装配文档下 probe = $($r3.status)  $(if($r3.status -ne 'COMPLETED'){$r3.error.code})"
if ($r3.status -eq 'COMPLETED') {
  Write-Output "  $(($r3.cadState.features[0] -replace '\s+',' ').Substring(0,[Math]::Min(200,($r3.cadState.features[0] -replace '\s+',' ').Length)))"
} else { Write-Output "  msg = $($r3.error.message)" }
