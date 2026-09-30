. "C:\Users\Zegel\solidpilot-mcp\tools\call.ps1"
$parts = "D:\AI\SW\AI Solidworks\模型"
# add_reference_geometry type=point 内部用 SelectByID2("", "VERTEX", x,y,z)
# ⇒ 坐标必须精确落在【顶点实体】上。边端点不是顶点实体。
# 做法：取多���【相交的边】的公共端点 —— 那是真正的顶点。
$null = Call 'open_document' @{ file_path = "$parts\主轴壳体_Housing.sldprt" }
$e = Call 'analyze_model' @{ analysis_type='edges' }
$ej = $e.cadState.features[0] | ConvertFrom-Json
Write-Output "边数 = $($ej.edge_count)"

# 统计各端点出现的次数：出现 >=2 次的就是真顶点
$pts = @{}
foreach($ed in $ej.edges){
  foreach($p in @($ed.start, $ed.end)){
    $k = "{0:F4},{1:F4},{2:F4}" -f [double]$p[0], [double]$p[1], [double]$p[2]
    if(-not $pts.ContainsKey($k)){ $pts[$k] = 0 }
    $pts[$k]++
  }
}
$verts = $pts.GetEnumerator() | Where-Object { $_.Value -ge 2 } | Sort-Object { $_.Key }
Write-Output "被 >=2 条边共享的端点（真顶点）= $($verts.Count) 个"
$verts | Select-Object -First 5 | ForEach-Object { "   $($_.Key)  ×$($_.Value)" }

if($verts.Count -gt 0){
  $v = $verts[0].Key -split ','
  Write-Output ""
  Write-Output "=== add_ref(point) 用真顶点 ($($verts[0].Key)) ==="
  $r = Call 'add_reference_geometry' @{ type='point'; px=[double]$v[0]; py=[double]$v[1]; pz=[double]$v[2] }
  Write-Output "  status = $($r.status)  $(if($r.status -ne 'COMPLETED'){$r.error.code})"
  if($r.status -eq 'COMPLETED'){
    Write-Output "  ★★ 成功 = $(($r.cadState.features[0] -replace '\s+',' '))"
    $f = Call 'analyze_model' @{ analysis_type='features' }
    (($f.cadState.features[0] | ConvertFrom-Json).features | Where-Object { $_.name -match '点|Point' }) |
      ForEach-Object { "     树里: $($_.name)  [$($_.type)]" }
  }
} else {
  Write-Output "  没有共享端点 —— 该零件的边都是独立端点（回转体），换测试对象"
}
