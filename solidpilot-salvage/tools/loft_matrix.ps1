. "C:\Users\Zegel\solidpilot-mcp\tools\call.ps1"
# 建两个截面：矩形(前视) + 圆(上视)，形状不同避免退化
$null = Call 'open_new_part' @{}
$null = Call 'create_sketch' @{ plane='Front Plane' }
$null = Call 'add_sketch_entities' @{ segments=@(
  @{entity_type='line';x1=-0.03;y1=-0.03;x2=0.03;y2=-0.03},
  @{entity_type='line';x1= 0.03;y1=-0.03;x2=0.03;y2=0.03},
  @{entity_type='line';x1= 0.03;y1= 0.03;x2=-0.03;y2=0.03},
  @{entity_type='line';x1=-0.03;y1= 0.03;x2=-0.03;y2=-0.03}) }
$null = Call 'create_sketch' @{ plane='Top Plane' }
$null = Call 'add_sketch_entity' @{ entity_type='circle'; cx=0; cy=0; radius=0.02 }

$f = Call 'analyze_model' @{ analysis_type='features' }
$names = ($f.cadState.features[0] | ConvertFrom-Json).features |
         Where-Object { $_.type -eq 'ProfileFeature' } | ForEach-Object { $_.name }
Write-Output "截面草图: $($names -join ', ')"
$p = '["' + $names[0] + '","' + $names[1] + '"]'

Write-Output ""
Write-Output "=== 一次跑 9 种（选面策略 × 插入 API）组合 ==="
$r = Call 'extrude_feature' @{ feature_type='loft'; profiles=$p } -TimeoutSec 300
Write-Output "  status = $($r.status)"
if ($r.status -eq 'COMPLETED') {
  Write-Output "  特征 = $(($r.cadState.features[0] -replace '\s+',' '))"
  (Call 'analyze_model' @{ analysis_type='geometry' }).cadState.features[0] | ForEach-Object { "  geo  = $_" }
  (Call 'analyze_model' @{ analysis_type='mass_properties' }).cadState.features[0] | ForEach-Object { "  mass = $_" }
} else {
  # 逐条打印每个策略的结果
  $msg = $r.error.message
  Write-Output "  错误 = $($r.error.code)"
  Write-Output "  ── 各策略结果 ──"
  ($msg -split '\|') | ForEach-Object { Write-Output "    $($_.Trim())" }
}
