. "C:\Users\Zegel\solidpilot-mcp\tools\call.ps1"
# 验证 4 个静默失败修复：它们现在必须【明确报失败】，而不是假装成功
$std = "D:\Program Files\SOLIDWORKS Corp\SOLIDWORKS\spiop\files\resources\standard"
$rpt = "$env:TEMP\dc_verify"; New-Item -ItemType Directory -Force -Path $rpt | Out-Null

Write-Output "=== ① auto_dimension_drawing（修复前：COMPLETED + count=0）==="
$null = Call 'open_document' @{ file_path="D:\AI\SW\AI Solidworks\模型\主轴壳体_Housing.sldprt" }
$null = Call 'create_drawing' @{ }
$r1 = Call 'auto_dimension_drawing' @{ all_views=$true } -TimeoutSec 90
Write-Output "  => $($r1.status)  $(if($r1.status -ne 'COMPLETED'){$r1.error.code})"
if($r1.status -ne 'COMPLETED'){ Write-Output "     $($r1.error.message -replace '\s+',' ')" }

Write-Output ""
Write-Output "=== ② auto_center_marks（修复前：COMPLETED + viewsMarked=0）==="
$r2 = Call 'auto_center_marks' @{ } -TimeoutSec 90
Write-Output "  => $($r2.status)  $(if($r2.status -ne 'COMPLETED'){$r2.error.code})"
if($r2.status -ne 'COMPLETED'){ Write-Output "     $($r2.error.message -replace '\s+',' ')" }

Write-Output ""
Write-Output "=== ③ design_check（修复前：rc=0 + 零报告）==="
$null = Call 'open_document' @{ file_path="D:\AI\SW\AI Solidworks\模型\主轴壳体_Housing.sldprt" }
$r3 = Call 'design_check' @{ standard_file="$std\SheetMetalDesign.xml"; report_dir=$rpt; overwrite=$true } -TimeoutSec 120
Write-Output "  => $($r3.status)  $(if($r3.status -ne 'COMPLETED'){$r3.error.code})"
if($r3.status -ne 'COMPLETED'){
  $m = $r3.error.message -replace '\s+',' '
  Write-Output "     $($m.Substring(0,[Math]::Min(200,$m.Length)))"
}

Write-Output ""
Write-Output "=== ④ sketched_bend（修复前：特征建出但几何没弯）==="
$null = Call 'open_new_part' @{}
$null = Call 'create_sketch' @{ plane='Front Plane' }
$null = Call 'add_sketch_entities' @{ segments=@(
  @{entity_type='line';x1=-0.08;y1=-0.01;x2=0.08;y2=-0.01},
  @{entity_type='line';x1= 0.08;y1=-0.01;x2=0.08;y2=0.01},
  @{entity_type='line';x1= 0.08;y1= 0.01;x2=-0.08;y2=0.01},
  @{entity_type='line';x1=-0.08;y1= 0.01;x2=-0.08;y2=-0.01}) }
$null = Call 'sheet_metal_feature' @{ feature_type='base_flange'; thickness=0.002; bend_radius=0.001 }
$g0 = Call 'analyze_model' @{ analysis_type='geometry' }
Write-Output "  折弯前面数: $($g0.cadState.features[0])"
# 在顶面建折弯线草图
$fa = Call 'analyze_model' @{ analysis_type='faces' }
$top = -1
foreach($fc in ($fa.cadState.features[0]|ConvertFrom-Json).faces){
  $n = ([string]$fc.normal) -split '\s+'
  if([math]::Abs([double]$n[2]-1) -lt 1e-6){ $top=$fc.i; break }
}
$null = Call 'create_sketch' @{ on_face=$true; face_index=$top }
$null = Call 'add_sketch_entity' @{ entity_type='line'; x1=-0.05; y1=0; x2=0.05; y2=0 }
$r4 = Call 'sheet_metal_feature' @{ feature_type='sketched_bend'; angle=90; use_default_radius=$true } -TimeoutSec 90
Write-Output "  => $($r4.status)  $(if($r4.status -ne 'COMPLETED'){$r4.error.code})"
if($r4.status -ne 'COMPLETED'){
  Write-Output "     $($r4.error.message -replace '\s+',' ')"
  $g1 = Call 'analyze_model' @{ analysis_type='geometry' }
  Write-Output "     实际面数: $($g1.cadState.features[0])  ← 与折弯前对比，应完全相同（证明确实没弯）"
}
