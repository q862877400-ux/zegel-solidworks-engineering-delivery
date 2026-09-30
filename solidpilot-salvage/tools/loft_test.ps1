. "C:\Users\Zegel\solidpilot-mcp\tools\call.ps1"
# profiles 必须是【扁平 JSON 数组】，不是嵌套数组
$p = '["草图1","草图2","草图3"]'
Write-Output "  传入 profiles = $p"
$r = Call 'extrude_feature' @{ feature_type='loft'; profiles=$p } -TimeoutSec 90
Write-Output "  loft status = $($r.status)  $(if($r.status -ne 'COMPLETED'){$r.error.code})"
if ($r.status -eq 'COMPLETED') {
  ($r.cadState.features | ForEach-Object { $_.Trim().Trim('"') }) | Select-Object -First 1 | ForEach-Object { "  特征: $_" }
  (Call 'analyze_model' @{ analysis_type='geometry' }).cadState.features[0] | ForEach-Object { "  geo : $_" }
  (Call 'analyze_model' @{ analysis_type='mass_properties' }).cadState.features[0] | ForEach-Object { "  mass: $_" }
}
