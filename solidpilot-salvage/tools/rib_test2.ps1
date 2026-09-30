. "C:\Users\Zegel\solidpilot-mcp\tools\call.ps1"
# 坐标系错误：Top Plane 是 XZ 平面（法向 Y），不是 XY。
# 底板是 Front Plane(XY) 沿 Z 拉伸的，所以筋草图必须用 Front Plane + offset=板厚的一半。
Write-Output "=== ① 底板：Front Plane 拉伸 20mm（z: 0→0.02）==="
$null = Call 'open_new_part' @{}
$null = Call 'create_sketch' @{ plane='Front Plane' }
$null = Call 'add_sketch_entities' @{ segments=@(
  @{entity_type='line';x1=-0.05;y1=-0.05;x2=0.05;y2=-0.05},
  @{entity_type='line';x1= 0.05;y1=-0.05;x2=0.05;y2=0.05},
  @{entity_type='line';x1= 0.05;y1= 0.05;x2=-0.05;y2=0.05},
  @{entity_type='line';x1=-0.05;y1= 0.05;x2=-0.05;y2=-0.05}) }
$null = Call 'extrude_feature' @{ feature_type='boss'; depth=0.02 }
$plate = (Call 'analyze_model' @{ analysis_type='mass_properties' }).cadState.features[0]
Write-Output "  底板 $plate   (理论 0.1*0.1*0.02 = 2e-4)"

Write-Output ""
Write-Output "=== ② 筋草图：Front Plane + offset=0.01（板中面 z=0.01）==="
$null = Call 'create_sketch' @{ plane='Front Plane'; offset=0.01 }
$null = Call 'add_sketch_entity' @{ entity_type='line'; x1=-0.05; y1=0; x2=0.05; y2=0 }
$s = Call 'analyze_model' @{ analysis_type='sketch'; name='草图2' }
Write-Output "  草图2 plane: $(($s.cadState.features[0] -replace '\s+',' ').Substring(0,[Math]::Min(230,($s.cadState.features[0] -replace '\s+',' ').Length)))"

Write-Output ""
Write-Output "=== ③ create_rib ==="
$r = Call 'create_rib' @{ thickness=0.003 } -TimeoutSec 90
Write-Output "  status = $($r.status)  $(if($r.status -ne 'COMPLETED'){$r.error.code})"
if ($r.status -eq 'COMPLETED') {
  Write-Output "  特征 = $(($r.cadState.features[0] -replace '\s+',' '))"
  (Call 'analyze_model' @{ analysis_type='geometry' }).cadState.features[0] | ForEach-Object { "  geo  = $_" }
  (Call 'analyze_model' @{ analysis_type='mass_properties' }).cadState.features[0] | ForEach-Object { "  mass = $_" }
  Write-Output "  理论(板+筋) = $([math]::Round(0.1*0.1*0.02 + 0.1*0.003*0.02, 8)) m³"
} else {
  Write-Output "  msg = $($r.error.message)"
}
