. "C:\Users\Zegel\solidpilot-mcp\tools\call.ps1"
# sweep 正确用法：
#   ① 先建【路径草图】并退出
#   ② 再建【轮廓草图】并【保持激活】← 它会被当作 profile
#   ③ 立刻调 extrude(sweep, path_sketch=<路径草图名>)
Write-Output "=== ① 路径草图（Top 平面，开放线）==="
$null = Call 'open_new_part' @{}
$null = Call 'create_sketch' @{ plane='Top Plane' }
$null = Call 'add_sketch_entity' @{ entity_type='line'; x1=-0.06; y1=0; x2=0.06; y2=0 }

# 退出这个草图，让下一个能激活
$null = Call 'edit_feature' @{ feature_name='草图1'; action='delete' }   # 删掉重来更干净
$null = Call 'open_new_part' @{}

Write-Output "=== 重来：先路径 ==="
$null = Call 'create_sketch' @{ plane='Top Plane' }
$null = Call 'add_sketch_entity' @{ entity_type='line'; x1=-0.06; y1=0; x2=0.06; y2=0 }
# 不退出：直接建第二个草图会自动退出第一个？先看特征树
$f = Call 'analyze_model' @{ analysis_type='features' }
$names = ($f.cadState.features[0] | ConvertFrom-Json).features |
         Where-Object { $_.type -eq 'ProfileFeature' } | ForEach-Object { $_.name }
Write-Output "  当前草图: $($names -join ', ')"

Write-Output "=== ② 轮廓草图（Front 平面，圆），保持激活 ==="
$null = Call 'create_sketch' @{ plane='Front Plane' }
$null = Call 'add_sketch_entity' @{ entity_type='circle'; cx=-0.06; cy=0; radius=0.008 }

$f2 = Call 'analyze_model' @{ analysis_type='features' }
$names2 = ($f2.cadState.features[0] | ConvertFrom-Json).features |
          Where-Object { $_.type -eq 'ProfileFeature' } | ForEach-Object { $_.name }
Write-Output "  草图列表: $($names2 -join ', ')"
$path = $names2 | Select-Object -First 1
Write-Output "  路径草图名 = $path"

Write-Output "=== ③ 调 sweep（轮廓草图此刻应仍激活）==="
$r = Call 'extrude_feature' @{ feature_type='sweep'; path_sketch=$path } -TimeoutSec 120
Write-Output "  status = $($r.status)  $(if($r.status -ne 'COMPLETED'){$r.error.code})"
if ($r.status -eq 'COMPLETED') {
  Write-Output "  特征 = $(($r.cadState.features[0] -replace '\s+',' '))"
  (Call 'analyze_model' @{ analysis_type='geometry' }).cadState.features[0] | ForEach-Object { "  geo  = $_" }
  (Call 'analyze_model' @{ analysis_type='mass_properties' }).cadState.features[0] | ForEach-Object { "  mass = $_" }
} else {
  Write-Output "  msg = $($r.error.message)"
}
