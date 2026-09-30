. "C:\Users\Zegel\solidpilot-mcp\tools\call.ps1"
# rib 5 轮失败的根因链（本轮定位）：
#   ① create_sketch【没有 offset 参数】⇒ 筋草图一直建在基准面 z=0（板底面），不是板中面/顶面
#   ② 用 on_face=true + face_index 直接在【板顶面】建草图（绕开没有 offset 的限制）
$null = Call 'open_new_part' @{}
$null = Call 'create_sketch' @{ plane='Front Plane' }
$null = Call 'add_sketch_entities' @{ segments=@(
  @{entity_type='line';x1=-0.05;y1=-0.05;x2=0.05;y2=-0.05},
  @{entity_type='line';x1= 0.05;y1=-0.05;x2=0.05;y2=0.05},
  @{entity_type='line';x1= 0.05;y1= 0.05;x2=-0.05;y2=0.05},
  @{entity_type='line';x1=-0.05;y1= 0.05;x2=-0.05;y2=-0.05}) }
$null = Call 'extrude_feature' @{ feature_type='boss'; depth=0.02 }
Write-Output "底板: $((Call 'analyze_model' @{ analysis_type='mass_properties' }).cadState.features[0])"

# 找顶面：法向 z=+1 且 z 坐标最大
$f = Call 'analyze_model' @{ analysis_type='faces' }
$fj = $f.cadState.features[0] | ConvertFrom-Json
$top = $null; $topI = -1
foreach($fc in $fj.faces){
  $n = ([string]$fc.normal) -split '\s+'
  if($n.Count -ge 3 -and [math]::Abs([double]$n[2] - 1) -lt 1e-6){
    $p = ([string]$fc.point) -split '\s+'
    if($p.Count -ge 3 -and [double]$p[2] -gt 0.019){ $top = $fc; $topI = $fc.i }
  }
}
Write-Output "顶面 face_index = $topI  (法向+Z, z=0.02)"

if($topI -ge 0){
  Write-Output ""
  Write-Output "=== 在顶面建筋草图 ==="
  $sk = Call 'create_sketch' @{ on_face=$true; face_index=$topI }
  Write-Output "  create_sketch(on_face) = $($sk.status)"
  $null = Call 'add_sketch_entity' @{ entity_type='line'; x1=-0.05; y1=0; x2=0.05; y2=0 }
  $s2 = Call 'analyze_model' @{ analysis_type='sketch'; name='草图2' }
  Write-Output "  草图2: $(($s2.cadState.features[0] -replace '\s+',' ').Substring(0,[Math]::Min(210,($s2.cadState.features[0] -replace '\s+',' ').Length)))"

  Write-Output ""
  Write-Output "=== create_rib ==="
  $r = Call 'create_rib' @{ thickness=0.003 } -TimeoutSec 90
  Write-Output "  status = $($r.status)  $(if($r.status -ne 'COMPLETED'){$r.error.code})"
  if($r.status -eq 'COMPLETED'){
    Write-Output "  特征 = $(($r.cadState.features[0] -replace '\s+',' '))"
    (Call 'analyze_model' @{ analysis_type='mass_properties' }).cadState.features[0] | ForEach-Object { "  mass = $_" }
    Write-Output "  理论(板+筋) = $([math]::Round(0.1*0.1*0.02 + 0.1*0.003*0.02, 8)) m³"
  } else { Write-Output "  msg = $($r.error.message)" }
}
