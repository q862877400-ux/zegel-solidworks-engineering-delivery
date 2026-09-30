. "C:\Users\Zegel\solidpilot-mcp\tools\call.ps1"
# 上一轮的错误：选了 edge[0]（长度 2mm = 板厚方向），翻边长度 5/10mm 反而比边还长。
# 正确：选 20mm 或 160mm 的边，翻边长度必须 < 边长。
Write-Output "=== 建钣金 160×20×2 ==="
$null = Call 'open_new_part' @{}
$null = Call 'create_sketch' @{ plane='Front Plane' }
$null = Call 'add_sketch_entities' @{ segments=@(
  @{entity_type='line';x1=-0.08;y1=-0.01;x2=0.08;y2=-0.01},
  @{entity_type='line';x1= 0.08;y1=-0.01;x2=0.08;y2=0.01},
  @{entity_type='line';x1= 0.08;y1= 0.01;x2=-0.08;y2=0.01},
  @{entity_type='line';x1=-0.08;y1= 0.01;x2=-0.08;y2=-0.01}) }
$null = Call 'sheet_metal_feature' @{ feature_type='base_flange'; thickness=0.002; bend_radius=0.001 }
Write-Output "  base_flange OK"

$e = Call 'analyze_model' @{ analysis_type='edges' }
$ej = $e.cadState.features[0] | ConvertFrom-Json

# 分类边长，选 20mm 的（翻边 10mm < 20mm 可行）
$byLen = @{}
for($i=0; $i -lt $ej.edges.Count; $i++){
  $ed = $ej.edges[$i]
  $sx=[double]$ed.start[0];$sy=[double]$ed.start[1];$sz=[double]$ed.start[2]
  $ex=[double]$ed.end[0];  $ey=[double]$ed.end[1];  $ez=[double]$ed.end[2]
  $len=[math]::Round([math]::Sqrt([math]::Pow($ex-$sx,2)+[math]::Pow($ey-$sy,2)+[math]::Pow($ez-$sz,2))*1000,2)
  if(-not $byLen.ContainsKey($len)){ $byLen[$len] = @() }
  $byLen[$len] += $ed.i
}
Write-Output "  边长分类: " + (($byLen.Keys | Sort-Object | ForEach-Object { "$($_)mm×$($byLen[$_].Count)" }) -join ', ')

$candidates = @()
foreach($len in ($byLen.Keys | Sort-Object)){ if($len -ge 20){ $candidates += $byLen[$len][0] } }
Write-Output "  候选边(≥20mm): $($candidates -join ', ')"

$log = "C:\Users\Zegel\solidpilot-mcp\execution\solidworks\SolidworksExecution\bin\Debug\execution.log"
foreach($ei in $candidates){
  # 这条边的实际长度
  $edgeLen = 0
  foreach($k in $byLen.Keys){ if($byLen[$k] -contains $ei){ $edgeLen = [double]$k; break } }
  foreach($fl in 0.010, 0.005, 0.015){
    if(($fl*1000) -ge $edgeLen){ continue }   # 翻边宽必须小于边长
    $r = Call 'sheet_metal_feature' @{ feature_type='edge_flange'; edge_index=$ei; flange_length=$fl; angle=90 } -TimeoutSec 90
    Write-Output "  edge[$ei]($($edgeLen)mm) flange=$fl m => $($r.status) $(if($r.status -ne 'COMPLETED'){$r.error.code})"
    if($r.status -eq 'COMPLETED'){
      Write-Output "  ★★ 成功: $(($r.cadState.features[0] -replace '\s+',' '))"
      (Call 'analyze_model' @{ analysis_type='geometry' }).cadState.features[0] | ForEach-Object { "     geo = $_" }
      (Call 'analyze_model' @{ analysis_type='mass_properties' }).cadState.features[0] | ForEach-Object { "     mass = $_" }
      (Select-String -Path $log -Pattern 'edge_flange:' | Select-Object -Last 1) | ForEach-Object { "     $($_.Line.Trim())" }
      exit 0
    }
  }
}
Write-Output ""
Write-Output "  服务端日志:"
(Select-String -Path $log -Pattern 'edge_flange:' | Select-Object -Last 5) | ForEach-Object { "    " + $_.Line.Trim() }
