. "C:\Users\Zegel\solidpilot-mcp\tools\call.ps1"
$tmp = "$env:TEMP\apisc"
$parts = "D:\AI\SW\AI Solidworks\模型"

Write-Output "=== 验证1: IGES 是否需要 .igs 扩展名 ==="
$null = Call 'open_document' @{ file_path = "$parts\主轴壳体_Housing.sldprt" }
foreach ($ext in 'igs','iges') {
  $r = Call 'save_document' @{ file_path = "$tmp\test1.$ext" } -TimeoutSec 60
  Write-Output "  .$ext => $($r.status) $(if($r.status -ne 'COMPLETED'){$r.error.code})"
}

Write-Output ""
Write-Output "=== 验证2: suppress 是否真生效（体积应变化）==="
$null = Call 'open_new_part' @{}
$null = Call 'create_sketch' @{ plane='Front Plane' }
$null = Call 'add_sketch_entities' @{ segments=@(
  @{entity_type='line';x1=-0.05;y1=-0.05;x2=0.05;y2=-0.05},
  @{entity_type='line';x1= 0.05;y1=-0.05;x2=0.05;y2=0.05},
  @{entity_type='line';x1= 0.05;y1= 0.05;x2=-0.05;y2=0.05},
  @{entity_type='line';x1=-0.05;y1= 0.05;x2=-0.05;y2=-0.05}) }
$null = Call 'extrude_feature' @{ feature_type='boss'; depth=0.02 }   # 大凸台
$null = Call 'create_sketch' @{ plane='Front Plane'; offset=0.02 }
$null = Call 'add_sketch_entity' @{ entity_type='circle'; cx=0; cy=0; radius=0.03 }
$null = Call 'extrude_feature' @{ feature_type='boss'; depth=0.01 }   # 上面加个凸台

$v0 = (Call 'analyze_model' @{ analysis_type='mass_properties' }).cadState.features[0]
Write-Output "  初始      $v0"

$s = Call 'edit_feature' @{ feature_name='凸台-拉伸2'; action='suppress' }
Write-Output "  suppress => $($s.status)"
$v1 = (Call 'analyze_model' @{ analysis_type='mass_properties' }).cadState.features[0]
Write-Output "  抑制后    $v1"

$u = Call 'edit_feature' @{ feature_name='凸台-拉伸2'; action='unsuppress' }
Write-Output "  unsuppress => $($u.status)"
$v2 = (Call 'analyze_model' @{ analysis_type='mass_properties' }).cadState.features[0]
Write-Output "  恢复后    $v2"

$d = Call 'edit_feature' @{ feature_name='凸台-拉伸2'; action='delete' }
Write-Output "  delete   => $($d.status)"
$v3 = (Call 'analyze_model' @{ analysis_type='mass_properties' }).cadState.features[0]
Write-Output "  删除后    $v3"

Write-Output ""
Write-Output "  判定："
Write-Output "    抑制生效 = $($v0 -ne $v1)   (初始 vs 抑制后)"
Write-Output "    恢复生效 = $($v1 -ne $v2)"
Write-Output "    删除生效 = $($v2 -ne $v3)"
