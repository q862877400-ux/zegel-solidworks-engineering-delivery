. "C:\Users\Zegel\solidpilot-mcp\tools\call.ps1"
# create_rib 的关键：开放轮廓的【端点必须落在两侧壁上】。
# 4 轮前失败的原因：底板 x=±0.05，而筋线只画到 x=±0.04 —— 端点悬空在板内 10mm，
# SolidWorks 延伸不到任何壁 ⇒ InsertRib 建不出东西。
Write-Output "=== ① 底板：x/y ∈ ±0.05，z 0→0.02 ==="
$null = Call 'open_new_part' @{}
$null = Call 'create_sketch' @{ plane='Front Plane' }
$null = Call 'add_sketch_entities' @{ segments=@(
  @{entity_type='line';x1=-0.05;y1=-0.05;x2=0.05;y2=-0.05},
  @{entity_type='line';x1= 0.05;y1=-0.05;x2=0.05;y2=0.05},
  @{entity_type='line';x1= 0.05;y1= 0.05;x2=-0.05;y2=0.05},
  @{entity_type='line';x1=-0.05;y1= 0.05;x2=-0.05;y2=-0.05}) }
$e = Call 'extrude_feature' @{ feature_type='boss'; depth=0.02 }
Write-Output "  拉伸: $($e.status)  $(if($e.status -ne 'COMPLETED'){$e.error.code})"
(Call 'analyze_model' @{ analysis_type='mass_properties' }).cadState.features[0] | ForEach-Object { "  体积: $_" }

Write-Output ""
Write-Output "=== ② 筋轮廓：线端点【正好落在 x=±0.05 的壁面】 ==="
$null = Call 'create_sketch' @{ plane='Top Plane' }     # 偏移 0 即板顶面 z=0.02
$null = Call 'add_sketch_entity' @{ entity_type='line'; x1=-0.05; y1=0; x2=0.05; y2=0 }
$s = Call 'analyze_model' @{ analysis_type='sketch'; name='草图2' }
Write-Output "  草图2: $(($s.cadState.features[0] -replace '\s+',' ').Substring(0,[Math]::Min(190,($s.cadState.features[0] -replace '\s+',' ').Length)))"

Write-Output ""
Write-Output "=== ③ create_rib ==="
$r = Call 'create_rib' @{ thickness=0.003 } -TimeoutSec 90
Write-Output "  status = $($r.status)  $(if($r.status -ne 'COMPLETED'){$r.error.code})"
if ($r.status -eq 'COMPLETED') {
  Write-Output "  特征 = $(($r.cadState.features[0] -replace '\s+',' '))"
  (Call 'analyze_model' @{ analysis_type='geometry' }).cadState.features[0] | ForEach-Object { "  geo  = $_" }
  (Call 'analyze_model' @{ analysis_type='mass_properties' }).cadState.features[0] | ForEach-Object { "  mass = $_" }
  $expected = 0.10 * 0.10 * 0.02 + 0.10 * 0.003 * 0.02
  Write-Output "  理论体积 = $expected m³ (板 + 筋)"
} else {
  Write-Output "  msg = $($r.error.message)"
}
