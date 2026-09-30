. "C:\Users\Zegel\solidpilot-mcp\tools\call.ps1"
# sketched_bend 修复后仍 COMPLETED —— 要确认面数到底变了没（可能是真弯了！）
Write-Output "=== 建钣金件 ==="
$null = Call 'open_new_part' @{}
$null = Call 'create_sketch' @{ plane='Front Plane' }
$null = Call 'add_sketch_entities' @{ segments=@(
  @{entity_type='line';x1=-0.08;y1=-0.01;x2=0.08;y2=-0.01},
  @{entity_type='line';x1= 0.08;y1=-0.01;x2=0.08;y2=0.01},
  @{entity_type='line';x1= 0.08;y1= 0.01;x2=-0.08;y2=0.01},
  @{entity_type='line';x1=-0.08;y1= 0.01;x2=-0.08;y2=-0.01}) }
$null = Call 'sheet_metal_feature' @{ feature_type='base_flange'; thickness=0.002; bend_radius=0.001 }

function Faces {
  $fa = Call 'analyze_model' @{ analysis_type='faces' }
  ($fa.cadState.features[0] | ConvertFrom-Json).faces.Count
}
$f0 = Faces
Write-Output "  折弯前面数 = $f0"

$fa = Call 'analyze_model' @{ analysis_type='faces' }
$top = -1
foreach($fc in ($fa.cadState.features[0]|ConvertFrom-Json).faces){
  $n = ([string]$fc.normal) -split '\s+'
  if([math]::Abs([double]$n[2]-1) -lt 1e-6){ $top=$fc.i; break }
}
$null = Call 'create_sketch' @{ on_face=$true; face_index=$top }
$null = Call 'add_sketch_entity' @{ entity_type='line'; x1=-0.05; y1=0; x2=0.05; y2=0 }
Write-Output "  在顶面(face=$top)画折弯线"

$r = Call 'sheet_metal_feature' @{ feature_type='sketched_bend'; angle=90; use_default_radius=$true } -TimeoutSec 90
Write-Output "  sketched_bend => $($r.status) $(if($r.status -ne 'COMPLETED'){$r.error.code})"
Write-Output "  特征 = $(if($r.status -eq 'COMPLETED'){($r.cadState.features[0] -replace '\s+',' ')})"

$f1 = Faces
Write-Output "  折弯后面数 = $f1"
Write-Output ""
if($f1 -gt $f0){
  Write-Output "  ★★ 面数增加了 $f0 → $f1 ⇒ 【真的弯了】！sketched_bend 是可用的"
} elseif($f1 -eq $f0){
  Write-Output "  ⚠ 面数未变 ⇒ 还是没弯（我的验证逻辑或服务端判定有问题）"
}
""
"=== 看服务端日志里的面数记录 ==="
$log = "C:\Users\Zegel\solidpilot-mcp\execution\solidworks\SolidworksExecution\bin\Debug\execution.log"
(Select-String -Path $log -Pattern 'sketched_bend: faces' | Select-Object -Last 3) | ForEach-Object { "  " + $_.Line.Trim() }
