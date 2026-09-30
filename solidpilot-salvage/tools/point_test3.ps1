. "C:\Users\Zegel\solidpilot-mcp\tools\call.ps1"
# 上一轮的 bug：我用 "{0:F4}" 格式化坐标再 split 解析，
# 这会把 0.0399999999 截断成 0.04 —— 顶点命中容差极小，截断就错位。
# 修正：直接用边的 start 数组【原始浮点】，不经任何字符串格式化。
$null = Call 'open_new_part' @{}
$null = Call 'create_sketch' @{ plane='Front Plane' }
$null = Call 'add_sketch_entities' @{ segments=@(
  @{entity_type='line';x1=-0.04;y1=-0.03;x2=0.04;y2=-0.03},
  @{entity_type='line';x1= 0.04;y1=-0.03;x2=0.04;y2=0.03},
  @{entity_type='line';x1= 0.04;y1= 0.03;x2=-0.04;y2=0.03},
  @{entity_type='line';x1=-0.04;y1= 0.03;x2=-0.04;y2=-0.03}) }
$null = Call 'extrude_feature' @{ feature_type='boss'; depth=0.05 }

$e = Call 'analyze_model' @{ analysis_type='edges' }
$ej = $e.cadState.features[0] | ConvertFrom-Json

# ★ 不用字符串做 key —— 用原始 double 的位模式分组
$groups = @{}
for($i=0; $i -lt $ej.edges.Count; $i++){
  foreach($which in 'start','end'){
    $p = $ej.edges[$i].$which
    $k = "$([double]$p[0].ToString('R'))|$([double]$p[1].ToString('R'))|$([double]$p[2].ToString('R'))"
    if(-not $groups.ContainsKey($k)){ $groups[$k] = @() }
    $groups[$k] += $i
  }
}
# 找被 >=2 条边共享的点 = 真顶点
$hit = $null
foreach($g in $groups.GetEnumerator()){
  if($g.Value.Count -ge 2){
    $parts = $g.Key -split '\|'
    $hit = @{ x=[double]$parts[0]; y=[double]$parts[1]; z=[double]$parts[2]; n=$g.Value.Count }
    break
  }
}
if($hit){
  Write-Output "真顶点(R 精度，无截断) = $($hit.x), $($hit.y), $($hit.z)   被 $($hit.n) 条边共享"
  $r = Call 'add_reference_geometry' @{ type='point'; px=$hit.x; py=$hit.y; pz=$hit.z }
  Write-Output "  status = $($r.status)  $(if($r.status -ne 'COMPLETED'){$r.error.code})"
  if($r.status -eq 'COMPLETED'){
    Write-Output "  ★★ 成功 = $(($r.cadState.features[0] -replace '\s+',' '))"
    $f = Call 'analyze_model' @{ analysis_type='features' }
    (($f.cadState.features[0] | ConvertFrom-Json).features | Select-Object -Last 3) |
      ForEach-Object { "     $($_.name)  [$($_.type)]" }
  }
} else { Write-Output "没找到共享端点" }
