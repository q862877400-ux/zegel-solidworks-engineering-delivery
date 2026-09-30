. "C:\Users\Zegel\solidpilot-mcp\tools\call.ps1"
# 上一轮 create_pattern FAILED 的原因：特征 type 是 'Extrusion'（不是 'Extrude'），
# 我用 -match 'Extrude' 匹配不到 ⇒ feature_name 取空 ⇒ 报 MISSING_PARAMETER。
# 修正：取名字里带 '拉伸'/'Extrusion' 的，且排除阵列/镜向本身。
$null = Call 'open_new_part' @{}
$null = Call 'create_sketch' @{ plane='Front Plane' }
$null = Call 'add_sketch_entities' @{ segments=@(
  @{entity_type='line';x1=-0.05;y1=-0.03;x2=0.05;y2=-0.03},
  @{entity_type='line';x1= 0.05;y1=-0.03;x2=0.05;y2=0.03},
  @{entity_type='line';x1= 0.05;y1= 0.03;x2=-0.05;y2=0.03},
  @{entity_type='line';x1=-0.05;y1= 0.03;x2=-0.05;y2=-0.03}) }
$null = Call 'extrude_feature' @{ feature_type='boss'; depth=0.01 }
$f = Call 'analyze_model' @{ analysis_type='features' }
$seed = ($f.cadState.features[0] | ConvertFrom-Json).features |
        Where-Object { $_.type -eq 'Extrusion' } | Select-Object -First 1
Write-Output "种子特征 = $($seed.name)  [type=$($seed.type)]"

$before = (Call 'analyze_model' @{ analysis_type='mass_properties' }).cadState.features[0]
$bg     = (Call 'analyze_model' @{ analysis_type='geometry' }).cadState.features[0]
Write-Output "前: $before | $bg"

Write-Output ""
Write-Output "=== create_pattern(linear, 3 实例, 间距 0.02) ==="
$r = Call 'create_pattern' @{ pattern_type='linear'; feature_name=$seed.name; spacing=0.02; count=3; direction='X' } -TimeoutSec 90
Write-Output "  status = $($r.status) $(if($r.status -ne 'COMPLETED'){$r.error.code})"
if($r.status -eq 'COMPLETED'){
  Write-Output "  特征 = $(($r.cadState.features[0] -replace '\s+',' '))"
  $after = (Call 'analyze_model' @{ analysis_type='mass_properties' }).cadState.features[0]
  $ag    = (Call 'analyze_model' @{ analysis_type='geometry' }).cadState.features[0]
  Write-Output "  后: $after | $ag"
  $v0 = [double]([regex]::Match($before,'volume=([0-9.E+-]+)').Groups[1].Value)
  $v1 = [double]([regex]::Match($after ,'volume=([0-9.E+-]+)').Groups[1].Value)
  Write-Output "  体积 $v0 → $v1   倍数 = $([math]::Round($v1/$v0,3))  (阵列 3 实例应 ≈ 2.333：种子被并入)"
  if([math]::Abs($v1 - $v0) -gt 1e-12){ Write-Output "  ★ 真实生效" } else { Write-Output "  ⚠ 几何没变（假成功）" }
}

Write-Output ""
Write-Output "=== 收尾：回收资源 ==="
