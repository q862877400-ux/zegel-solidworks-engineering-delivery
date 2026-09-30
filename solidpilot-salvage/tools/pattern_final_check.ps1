. "C:\Users\Zegel\solidpilot-mcp\tools\call.ps1"
# 边数是【拓扑】量，不可能被缓存 —— 用它做最终判定
function Num { param($txt,$pat) [regex]::Match($txt,$pat).Groups[1].Value }
function Vol { (Num (Call 'analyze_model' @{ analysis_type='mass_properties' }).cadState.features[0] 'volume=([0-9.E+-]+)') }
function EdgeN { (Num (Call 'analyze_model' @{ analysis_type='edges' }).cadState.features[0] 'edge_count=(\d+)') }
function BodyN { (Num (Call 'analyze_model' @{ analysis_type='geometry' }).cadState.features[0] 'bodies=(\d+)') }
function PatNames {
  $r = Call 'analyze_model' @{ analysis_type='features' }
  if(-not $r.cadState.features -or $r.cadState.features.Count -eq 0){ return '(读不到)' }
  (($r.cadState.features[0]|ConvertFrom-Json).features | Where-Object { $_.type -match 'Pattern|Mirror' } | ForEach-Object { $_.name }) -join ','
}
function Seed {
  $null = Call 'open_new_part' @{}
  $null = Call 'create_sketch' @{ plane='Front Plane' }
  $null = Call 'add_sketch_entities' @{ segments=@(
    @{entity_type='line';x1=-0.05;y1=-0.03;x2=0.05;y2=-0.03},
    @{entity_type='line';x1= 0.05;y1=-0.03;x2=0.05;y2=0.03},
    @{entity_type='line';x1= 0.05;y1= 0.03;x2=-0.05;y2=0.03},
    @{entity_type='line';x1=-0.05;y1= 0.03;x2=-0.05;y2=-0.03}) }
  $null = Call 'extrude_feature' @{ feature_type='boss'; depth=0.01 }
  $r = Call 'analyze_model' @{ analysis_type='features' }
  return ($r.cadState.features[0]|ConvertFrom-Json).features | Where-Object { $_.type -eq 'Extrusion' } | Select-Object -First 1
}

foreach($c in @(
  @{d='X'; sp=0.02}, @{d='X'; sp=0.2}, @{d='Y'; sp=0.2}, @{d='Z'; sp=0.02}, @{d='Z'; sp=0.2}, @{d='Z'; sp=0.05})){
  $s = Seed
  $v0 = Vol; $e0 = EdgeN; $b0 = BodyN
  $r = Call 'create_pattern' @{ pattern_type='linear'; feature_name=$s.name; spacing=$c.sp; count=3; direction=$c.d }
  $v1 = Vol; $e1 = EdgeN; $b1 = BodyN; $pat = PatNames
  $real = ($v0 -ne $v1) -and ($e0 -ne $e1)
  $partial = ($v0 -ne $v1) -or ($e0 -ne $e1)
  $mark = if($real){'★★ 确实阵列了'} elseif($partial){'★ 部分变化(融合)'} else {'⚠ 静默失败'}
  Write-Output ("dir={0,-2} sp={1,-5} 体积 {2}→{3}  边 {4}→{5}  体 {6}→{7}  阵列='{8}'  {9}" -f `
     $c.d,$c.sp,$v0,$v1,$e0,$e1,$b0,$b1,$pat,$mark)
}
