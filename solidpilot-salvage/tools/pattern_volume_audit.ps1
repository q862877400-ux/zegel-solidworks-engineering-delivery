. "C:\Users\Zegel\solidpilot-mcp\tools\call.ps1"
# 判据改进：bodies=0 抓不到"体积没变"的静默失败。
# 阵列的正确判据 = 体积必须变（阵列必然增加材料，除非实例完全融合在原体内）
function V { (Call 'analyze_model' @{ analysis_type='mass_properties' }).cadState.features[0] }
function B { (Call 'analyze_model' @{ analysis_type='geometry' }).cadState.features[0] }
function Seed {
  $null = Call 'open_new_part' @{}
  $null = Call 'create_sketch' @{ plane='Front Plane' }
  $null = Call 'add_sketch_entities' @{ segments=@(
    @{entity_type='line';x1=-0.05;y1=-0.03;x2=0.05;y2=-0.03},
    @{entity_type='line';x1= 0.05;y1=-0.03;x2=0.05;y2=0.03},
    @{entity_type='line';x1= 0.05;y1= 0.03;x2=-0.05;y2=0.03},
    @{entity_type='line';x1=-0.05;y1= 0.03;x2=-0.05;y2=-0.03}) }
  $null = Call 'extrude_feature' @{ feature_type='boss'; depth=0.01 }
  $f = Call 'analyze_model' @{ analysis_type='features' }
  return ($f.cadState.features[0]|ConvertFrom-Json).features | Where-Object { $_.type -eq 'Extrusion' } | Select-Object -First 1
}

Write-Output "=== 阵列：体积判据（每种方向/间距都必须让体积变化）==="
$rows = @()
foreach($d in 'X','Y','Z'){
  foreach($sp in 0.02, 0.005, 0.2){
    $s = Seed
    $v0 = [double]([regex]::Match((V),'volume=([0-9.E+-]+)').Groups[1].Value)
    $r = Call 'create_pattern' @{ pattern_type='linear'; feature_name=$s.name; spacing=$sp; count=3; direction=$d }
    if($r.status -ne 'COMPLETED'){
      $rows += [pscustomobject]@{Dir=$d;Sp=$sp;V0=$v0;V1=0;Ratio=0;Status='FAIL';Note=$r.error.code}
      continue
    }
    $v1 = [double]([regex]::Match((V),'volume=([0-9.E+-]+)').Groups[1].Value)
    $ratio = if($v0 -gt 0){ [math]::Round($v1/$v0,3) } else { 0 }
    $st = if([math]::Abs($v1-$v0) -lt 1e-12){ 'SILENT(体积没变)' } else { 'OK' }
    $rows += [pscustomobject]@{Dir=$d;Sp=$sp;V0=$v0;V1=$v1;Ratio=$ratio;Status=$st;Note=''}
  }
}
""
$rows | Format-Table -AutoSize | Out-String -Width 130 | ForEach-Object { $_.TrimEnd() } | Write-Output
Write-Output ""
Write-Output "=== 静默失败（体积完全没变）的组合 ==="
$bad = $rows | Where-Object { $_.Status -like 'SILENT*' }
if($bad){ $bad | ForEach-Object { "  ⚠ 方向=$($_.Dir) 间距=$($_.Sp) 体积 $($_.V0) → $($_.V1)（完全没变）" } }
else { "  （无）" }
