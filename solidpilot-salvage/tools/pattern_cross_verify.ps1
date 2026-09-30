. "C:\Users\Zegel\solidpilot-mcp\tools\call.ps1"
# 上轮我判"4 个静默失败"，但要先确认判据本身对不对（我刚犯过"判据选错"的错）。
# 阵列分离 ⇒ 体积×N 且 边数×N；阵列融合 ⇒ 体积增、边数可能不变。
# 所以【边数】是更硬的判据。两个一起看。
function V { (Call 'analyze_model' @{ analysis_type='mass_properties' }).cadState.features[0] }
function E { (Call 'analyze_model' @{ analysis_type='edges' }).cadState.features[0] }
function F { Call 'analyze_model' @{ analysis_type='features' }
            (($_.cadState.features[0]|ConvertFrom-Json).features | Where-Object { $_.type -match 'Pattern|Mirror' } | ForEach-Object { $_.name }) -join ',' }
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

foreach($case in @(
  @{d='X'; sp=0.02}, @{d='X'; sp=0.2}, @{d='Y'; sp=0.2}, @{d='Z'; sp=0.02}, @{d='Z'; sp=0.2})){
  $s = Seed
  $v0 = [regex]::Match((V),'volume=([0-9.E+-]+)').Groups[1].Value
  $e0 = [regex]::Match((E),'edge_count=(\d+)').Groups[1].Value
  $r = Call 'create_pattern' @{ pattern_type='linear'; feature_name=$s.name; spacing=$case.sp; count=3; direction=$case.d }
  $v1 = [regex]::Match((V),'volume=([0-9.E+-]+)').Groups[1].Value
  $e1 = [regex]::Match((E),'edge_count=(\d+)').Groups[1].Value
  $pat = F
  $changed = ($v0 -ne $v1) -or ($e0 -ne $e1)
  Write-Output ("dir={0} sp={1}  体积 {2}→{3}   边数 {4}→{5}   阵列特征='{6}'   {7}" -f `
    $case.d, $case.sp, $v0, $v1, $e0, $e1, $pat, $(if($changed){'★ 真生效'}else{'⚠ 无变化'}))
}
