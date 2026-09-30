. "C:\Users\Zegel\solidpilot-mcp\tools\call.ps1"
# ★ 关键发现：open_new_part 没有真正新建文档 —— 特征名在累积
#   （阵列(线性)1,2,3,4 …）说明我的所有测试都叠在同一个零件上，状态被污染。
# 正确做法：每次测试前先 close_document 彻底清空。
function Num { param($t,$p) [regex]::Match($t,$p).Groups[1].Value }
function Vol { (Num (Call 'analyze_model' @{ analysis_type='mass_properties' }).cadState.features[0] 'volume=([0-9.E+-]+)') }
function GeoS { (Call 'analyze_model' @{ analysis_type='geometry' }).cadState.features[0] }
function DocName { (Call 'verify_state' @{}).cadState.activeDocument }
function FeatureList {
  $r = Call 'analyze_model' @{ analysis_type='features' }
  if(-not $r.cadState.features -or $r.cadState.features.Count -eq 0){ return '(空)' }
  (($r.cadState.features[0]|ConvertFrom-Json).features | ForEach-Object { $_.name }) -join '|'
}

function CleanPart {
  # ★ 彻底清理：先关掉所有文档，再新建
  for($i=0;$i -lt 30;$i++){ if((Call 'close_document' @{}).status -ne 'COMPLETED'){ break } ; Start-Sleep -Milliseconds 150 }
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

Write-Output "=== 干净状态下的阵列验证（每次先 close_document）==="
foreach($c in @(
  @{d='X'; sp=0.02}, @{d='X'; sp=0.2}, @{d='Y'; sp=0.2}, @{d='Z'; sp=0.02}, @{d='Z'; sp=0.05})){
  $s = CleanPart
  $doc0 = DocName
  $v0 = Vol; $g0 = GeoS
  $r = Call 'create_pattern' @{ pattern_type='linear'; feature_name=$s.name; spacing=$c.sp; count=3; direction=$c.d }
  $v1 = Vol; $g1 = GeoS
  $fl = FeatureList
  $ratio = if([double]$v0 -gt 0){ [math]::Round([double]$v1/[double]$v0,3) } else { 0 }
  $mark = if($v0 -ne $v1){ '★ 生效' } else { '⚠ 体积没变' }
  Write-Output ("dir={0,-2} sp={1,-5} 文档={2,-10} 体积 {3}→{4} (×{5})  {6}→{7}  {8}" -f `
     $c.d,$c.sp,$doc0,$v0,$v1,$ratio,$g0,$g1,$mark)
  Write-Output ("        特征树: {0}" -f $fl)
}
