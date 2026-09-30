. "C:\Users\Zegel\solidpilot-mcp\tools\call.ps1"
# 上一轮失败的原因：主轴壳体是【回转体】，圆柱面与端面的交线是圆而非线段，
# 所以它【根本没有顶点实体】——SelectByID2("","VERTEX",…) 永远找不到。
# 正确测试对象：直线围成的多面体（矩形拉伸），有真顶点。
Write-Output "=== 建一个有真顶点的零件 ==="
$null = Call 'open_new_part' @{}
$null = Call 'create_sketch' @{ plane='Front Plane' }
$null = Call 'add_sketch_entities' @{ segments=@(
  @{entity_type='line';x1=-0.04;y1=-0.03;x2=0.04;y2=-0.03},
  @{entity_type='line';x1= 0.04;y1=-0.03;x2=0.04;y2=0.03},
  @{entity_type='line';x1= 0.04;y1= 0.03;x2=-0.04;y2=0.03},
  @{entity_type='line';x1=-0.04;y1= 0.03;x2=-0.04;y2=-0.03}) }
$null = Call 'extrude_feature' @{ feature_type='boss'; depth=0.05 }
(Call 'analyze_model' @{ analysis_type='geometry' }).cadState.features[0] | ForEach-Object { "  geo = $_" }

$e = Call 'analyze_model' @{ analysis_type='edges' }
$ej = $e.cadState.features[0] | ConvertFrom-Json
$pts = @{}
foreach($ed in $ej.edges){
  foreach($p in @($ed.start,$ed.end)){
    $k = "{0:F4},{1:F4},{2:F4}" -f [double]$p[0],[double]$p[1],[double]$p[2]
    if(-not $pts.ContainsKey($k)){ $pts[$k]=0 }
    $pts[$k]++
  }
}
$verts = $pts.GetEnumerator() | Where-Object { $_.Value -ge 2 } | Sort-Object { $_.Key }
Write-Output "  边数=$($ej.edge_count)  真顶点(被>=2边共享)=$($verts.Count) 个"
$verts | Select-Object -First 3 | ForEach-Object { "    $($_.Key) ×$($_.Value)" }

if($verts.Count -gt 0){
  $v = $verts[0].Key -split ','
  Write-Output ""
  Write-Output "=== add_ref(point) ==="
  $r = Call 'add_reference_geometry' @{ type='point'; px=[double]$v[0]; py=[double]$v[1]; pz=[double]$v[2] }
  Write-Output "  status = $($r.status)  $(if($r.status -ne 'COMPLETED'){$r.error.code})"
  if($r.status -eq 'COMPLETED'){
    Write-Output "  ★★ 成功 = $(($r.cadState.features[0] -replace '\s+',' '))"
    $f = Call 'analyze_model' @{ analysis_type='features' }
    (($f.cadState.features[0] | ConvertFrom-Json).features | Select-Object -Last 4) |
      ForEach-Object { "     $($_.name)  [$($_.type)]" }
  }
}
