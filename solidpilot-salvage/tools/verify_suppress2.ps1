. "C:\Users\Zegel\solidpilot-mcp\tools\call.ps1"
# suppress 的正确测法：必须有【下游依赖】。
# 建 凸台A(大) → 切除B(在 A 上) → 抑制 A，看 B 是否失效（体积大变）
Write-Output "=== 建依赖链：大凸台 + 在它上面切除 ==="
$null = Call 'open_new_part' @{}
$null = Call 'create_sketch' @{ plane='Front Plane' }
$null = Call 'add_sketch_entity' @{ entity_type='circle'; cx=0; cy=0; radius=0.05 }
$null = Call 'extrude_feature' @{ feature_type='boss'; depth=0.03 }
Write-Output "  凸台1 圆柱 R50 x 30"

$null = Call 'create_sketch' @{ plane='Top Plane'; offset=0.03 }
$null = Call 'add_sketch_entity' @{ entity_type='circle'; cx=0; cy=0; radius=0.02 }
$null = Call 'extrude_feature' @{ feature_type='cut'; through=$true }
Write-Output "  切除1 通孔 R20（依赖凸台1）"

$null = Call 'create_sketch' @{ plane='Top Plane' }
$null = Call 'add_sketch_entity' @{ entity_type='circle'; cx=0; cy=0; radius=0.01 }
$null = Call 'extrude_feature' @{ feature_type='boss'; depth=0.05 }
Write-Output "  凸台2 凸柱 R10（依赖切除1）"

$f = Call 'analyze_model' @{ analysis_type='features' }
$names = ($f.cadState.features[0] | ConvertFrom-Json).features |
         Where-Object { $_.type -match 'Extrude|Revolve' } | ForEach-Object { $_.name }
Write-Output "  特征: $($names -join ', ')"

$v0 = (Call 'analyze_model' @{ analysis_type='mass_properties' }).cadState.features[0]
Write-Output ""
Write-Output "  初始体积   $v0"

# 抑制最下游的凸台2 —— 它是"叶子"，抑制后应该消失
Write-Output ""
Write-Output "=== 试1: 抑制 凸台2（叶子特征）==="
$s = Call 'edit_feature' @{ feature_name='凸台-拉伸2'; action='suppress' }
Write-Output "  => $($s.status) $(if($s.status -ne 'COMPLETED'){$s.error.code})"
$v1 = (Call 'analyze_model' @{ analysis_type='mass_properties' }).cadState.features[0]
Write-Output "  体积 $v1   变化: $($v0 -ne $v1)"

# 抑制最上游的凸台1 —— 它有 2 个下游依赖，抑制应该让模型重建失败或体积大变
Write-Output ""
Write-Output "=== 试2: 抑制 凸台1（被 2 个特征依赖）==="
$s2 = Call 'edit_feature' @{ feature_name='凸台-拉伸1'; action='suppress' }
Write-Output "  => $($s2.status) $(if($s2.status -ne 'COMPLETED'){$s2.error.code})"
if ($s2.status -eq 'COMPLETED') {
  $v2 = (Call 'analyze_model' @{ analysis_type='mass_properties' }).cadState.features[0]
  Write-Output "  体积 $v2   变化: $($v1 -ne $v2)"
}
