. "C:\Users\Zegel\solidpilot-mcp\tools\call.ps1"
# 上一轮两个错：
#  ① edge_flange_finish 要 ex/ey/ez（边坐标），不是 edge_index
#  ② 钣金顶面在 z=0（face[5] n=(0,0,1) p=(0,0,0)）——我按 z>0.019 筛，全不满足
function NewSheet {
  $null = Call 'open_new_part' @{}
  $null = Call 'create_sketch' @{ plane='Front Plane' }
  $null = Call 'add_sketch_entities' @{ segments=@(
    @{entity_type='line';x1=-0.08;y1=-0.01;x2=0.08;y2=-0.01},
    @{entity_type='line';x1= 0.08;y1=-0.01;x2=0.08;y2=0.01},
    @{entity_type='line';x1= 0.08;y1= 0.01;x2=-0.08;y2=0.01},
    @{entity_type='line';x1=-0.08;y1= 0.01;x2=-0.08;y2=-0.01}) }
  $null = Call 'sheet_metal_feature' @{ feature_type='base_flange'; thickness=0.002; bend_radius=0.001 }
}

Write-Output "=== ① sketched_bend：在【真实顶面】建折弯线草图 ==="
NewSheet
$fa = Call 'analyze_model' @{ analysis_type='faces' }
$fj = $fa.cadState.features[0] | ConvertFrom-Json
$top = -1
foreach($fc in $fj.faces){
  $n = ([string]$fc.normal) -split '\s+'
  if([math]::Abs([double]$n[2] - 1) -lt 1e-6){ $top = $fc.i; break }
}
Write-Output "  顶面 face_index = $top  (n=+Z, z=0)"
if($top -ge 0){
  $null = Call 'create_sketch' @{ on_face=$true; face_index=$top }
  $null = Call 'add_sketch_entity' @{ entity_type='line'; x1=-0.05; y1=0; x2=0.05; y2=0 }
  $r = Call 'sheet_metal_feature' @{ feature_type='sketched_bend'; angle=90; use_default_radius=$true
                                      bend_position='centerline' } -TimeoutSec 90
  Write-Output "  sketched_bend => $($r.status) $(if($r.status -ne 'COMPLETED'){$r.error.code})"
  if($r.status -eq 'COMPLETED'){
    Write-Output "    ★★ $(($r.cadState.features[0] -replace '\s+',' '))"
    (Call 'analyze_model' @{ analysis_type='mass_properties' }).cadState.features[0] | ForEach-Object { "       mass = $_" }
  } else {
    # 试另一种 bend_position
    $r2 = Call 'sheet_metal_feature' @{ feature_type='sketched_bend'; angle=90; use_default_radius=$true
                                        bend_position='material-inside' } -TimeoutSec 90
    Write-Output "  bend_position=material-inside => $($r2.status) $(if($r2.status -ne 'COMPLETED'){$r2.error.code})"
  }
}

Write-Output ""
Write-Output "=== ② edge_flange_sketch → finish（finish 用 ex/ey/ez）==="
NewSheet
$e = Call 'analyze_model' @{ analysis_type='edges' }
$ej = $e.cadState.features[0] | ConvertFrom-Json
$pick=-1; $mid=@(0.0,0.0,0.0)
for($i=0;$i -lt $ej.edges.Count;$i++){
  $ed=$ej.edges[$i]
  $sx=[double]$ed.start[0];$sy=[double]$ed.start[1];$sz=[double]$ed.start[2]
  $ex=[double]$ed.end[0];  $ey=[double]$ed.end[1];  $ez=[double]$ed.end[2]
  $len=[math]::Sqrt([math]::Pow($ex-$sx,2)+[math]::Pow($ey-$sy,2)+[math]::Pow($ez-$sz,2))*1000
  if([math]::Abs($len-20) -lt 0.5){ $pick=$ed.i; $mid=@(($sx+$ex)/2,($sy+$ey)/2,($sz+$ez)/2); break }
}
Write-Output "  选 edge_index=$pick (20mm) 中点=($($mid -join ','))"

if($pick -ge 0){
  $r1 = Call 'sheet_metal_feature' @{ feature_type='edge_flange_sketch'; edge_index=$pick; angle=90; clear_profile=$true } -TimeoutSec 90
  Write-Output "  第1步 edge_flange_sketch => $($r1.status)"
  if($r1.status -eq 'COMPLETED'){
    $null = Call 'add_sketch_entity' @{ entity_type='line'; x1=0; y1=0; x2=0.012; y2=0 }
    $r2 = Call 'sheet_metal_feature' @{ feature_type='edge_flange_finish'
                                        ex=$mid[0]; ey=$mid[1]; ez=$mid[2]
                                        angle=90; use_default_radius=$true } -TimeoutSec 90
    Write-Output "  第2步 edge_flange_finish => $($r2.status) $(if($r2.status -ne 'COMPLETED'){$r2.error.code})"
    if($r2.status -eq 'COMPLETED'){
      Write-Output "    ★★★ 成功 = $(($r2.cadState.features[0] -replace '\s+',' '))"
      (Call 'analyze_model' @{ analysis_type='mass_properties' }).cadState.features[0] | ForEach-Object { "         mass = $_" }
    }
  }
}
