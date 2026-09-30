. "C:\Users\Zegel\solidpilot-mcp\tools\call.ps1"
# edge_flange 失败排查：看清边，选明确的直边，试不同参数
Write-Output "=== ① 建钣金：160×20 薄板 ==="
$null = Call 'open_new_part' @{}
$null = Call 'create_sketch' @{ plane='Front Plane' }
$null = Call 'add_sketch_entities' @{ segments=@(
  @{entity_type='line';x1=-0.08;y1=-0.01;x2=0.08;y2=-0.01},
  @{entity_type='line';x1= 0.08;y1=-0.01;x2=0.08;y2=0.01},
  @{entity_type='line';x1= 0.08;y1= 0.01;x2=-0.08;y2=0.01},
  @{entity_type='line';x1=-0.08;y1= 0.01;x2=-0.08;y2=-0.01}) }
$bf = Call 'sheet_metal_feature' @{ feature_type='base_flange'; thickness=0.002; bend_radius=0.001 }
Write-Output "  base_flange = $($bf.status)  $(if($bf.status -ne 'COMPLETED'){$bf.error.code})"
(Call 'analyze_model' @{ analysis_type='geometry' }).cadState.features[0] | ForEach-Object { "  geo = $_" }

Write-Output ""
Write-Output "=== ② 列出所有边（找直边）==="
$e = Call 'analyze_model' @{ analysis_type='edges' }
$ej = $e.cadState.features[0] | ConvertFrom-Json
Write-Output "  边数 = $($ej.edge_count)"
$lines = @()
for($i=0; $i -lt $ej.edges.Count; $i++){
  $ed = $ej.edges[$i]
  $sx = [double]$ed.start[0]; $sy = [double]$ed.start[1]; $sz = [double]$ed.start[2]
  $ex = [double]$ed.end[0];   $ey = [double]$ed.end[1];   $ez = [double]$ed.end[2]
  $len = [math]::Sqrt([math]::Pow($ex-$sx,2)+[math]::Pow($ey-$sy,2)+[math]::Pow($ez-$sz,2))
  $lines += [pscustomobject]@{ i=$ed.i; len_mm=[math]::Round($len*1000,2); start=($ed.start -join ',') }
}
$lines | Sort-Object len_mm | ForEach-Object { "    edge[$($_.i)] len=$($_.len_mm)mm start=($($_.start))" }

Write-Output ""
Write-Output "=== ③ 选最短的边试翻边（翻边宽度必须小于边长）==="
$shortest = $lines | Sort-Object len_mm | Select-Object -First 1
Write-Output "  用 edge[$($shortest.i)] (len=$($shortest.len_mm)mm)"
foreach($fl in 0.005, 0.010){
  $r = Call 'sheet_metal_feature' @{ feature_type='edge_flange'; edge_index=$shortest.i; flange_length=$fl; angle=90 } -TimeoutSec 90
  Write-Output "  flange_length=$fl m => $($r.status)  $(if($r.status -ne 'COMPLETED'){$r.error.code})"
  if($r.status -eq 'COMPLETED'){
    Write-Output "    ★ 特征 = $(($r.cadState.features[0] -replace '\s+',' '))"
    (Call 'analyze_model' @{ analysis_type='geometry' }).cadState.features[0] | ForEach-Object { "      geo = $_" }
    break
  }
}

Write-Output ""
Write-Output "=== ④ 服务端日志（看 InsertSketchForEdgeFlange 是否返回草图）==="
$log = "C:\Users\Zegel\solidpilot-mcp\execution\solidworks\SolidworksExecution\bin\Debug\execution.log"
Select-String -Path $log -Pattern 'edge_flange:' | Select-Object -Last 4 | ForEach-Object { "  " + $_.Line.Trim() }
