. "C:\Users\Zegel\solidpilot-mcp\tools\call.ps1"
# 参数组合扫描 2：sheet_metal_feature 全部类型 + analyze_model 全部类型
# ★ 纪律（Round 13 教训）：每个用例前必须彻底清空文档，否则特征名累积、状态污染
$ErrorActionPreference='Continue'
$script:Res = New-Object System.Collections.ArrayList
function Rec { param($T,$C,$S,$M,$G)
  [void]$script:Res.Add([pscustomobject]@{Tool=$T;Combo=$C;Status=$S;Msg=$M;Geo=$G})
  $mk=switch($S){'OK'{'✅'};'SILENT'{'⚠静默'};'FAIL'{'❌'}else{'💥'}}
  "  $mk [$T] $C  $M $G"
}
function CleanDoc {
  for($i=0;$i -lt 30;$i++){ if((Call 'close_document' @{}).status -ne 'COMPLETED'){ break }; Start-Sleep -Milliseconds 120 }
  $null = Call 'open_new_part' @{}
}
function Num { param($t,$p) [regex]::Match($t,$p).Groups[1].Value }
function Vol { (Num (Call 'analyze_model' @{ analysis_type='mass_properties' }).cadState.features[0] 'volume=([0-9.E+-]+)') }
function GeoS { (Call 'analyze_model' @{ analysis_type='geometry' }).cadState.features[0] }
function FaceN { (Num (Call 'analyze_model' @{ analysis_type='geometry' }).cadState.features[0] 'bodies=(\d+)') }

# ═══ ① sheet_metal_feature 全部 6 种类型 ═══
Write-Output "=== ① sheet_metal_feature 全部类型 ==="
function NewSheet { param([double]$th=0.002)
  CleanDoc
  $null = Call 'create_sketch' @{ plane='Front Plane' }
  $null = Call 'add_sketch_entities' @{ segments=@(
    @{entity_type='line';x1=-0.08;y1=-0.01;x2=0.08;y2=-0.01},
    @{entity_type='line';x1= 0.08;y1=-0.01;x2=0.08;y2=0.01},
    @{entity_type='line';x1= 0.08;y1= 0.01;x2=-0.08;y2=0.01},
    @{entity_type='line';x1=-0.08;y1= 0.01;x2=-0.08;y2=-0.01}) }
  $null = Call 'sheet_metal_feature' @{ feature_type='base_flange'; thickness=$th; bend_radius=0.001 }
}
function Edge20 {
  $e = Call 'analyze_model' @{ analysis_type='edges' }
  $ej = $e.cadState.features[0]|ConvertFrom-Json
  for($i=0;$i -lt $ej.edges.Count;$i++){
    $ed=$ej.edges[$i]
    $sx=[double]$ed.start[0];$sy=[double]$ed.start[1];$sz=[double]$ed.start[2]
    $ex=[double]$ed.end[0];$ey=[double]$ed.end[1];$ez=[double]$ed.end[2]
    if([math]::Abs([math]::Sqrt([math]::Pow($ex-$sx,2)+[math]::Pow($ey-$sy,2)+[math]::Pow($ez-$sz,2))*1000 - 20) -lt 0.5){ return $ed.i }
  }
  return -1
}

# base_flange 厚度组合
foreach($th in 0.001, 0.002, 0.005){
  NewSheet $th
  # 再建一个测变化
  $v0 = Vol
  $null = Call 'add_sketch_entities' @{ segments=@() }   # 占位
  $r = Call 'sheet_metal_feature' @{ feature_type='flat_pattern' } -TimeoutSec 90
  $g = if($r.status -eq 'COMPLETED'){ GeoS }else{''}
  $st = if($r.status -ne 'COMPLETED'){'FAIL'}else{'OK'}
  Rec 'sheet_metal' "base_flange(th=$th)+flat_pattern" $st $(if($r.status -ne 'COMPLETED'){$r.error.code}else{"v0=$v0"}) $g
}
# edge_flange 翻边宽度组合
foreach($fl in 0.005, 0.010, 0.015){
  NewSheet
  $ei = Edge20
  $v0 = Vol
  $r = Call 'sheet_metal_feature' @{ feature_type='edge_flange'; edge_index=$ei; flange_length=$fl; angle=90 } -TimeoutSec 90
  $v1 = if($r.status -eq 'COMPLETED'){ Vol }else{''}
  $g = if($r.status -eq 'COMPLETED'){ GeoS }else{''}
  $chg = ($r.status -eq 'COMPLETED' -and $v0 -ne $v1)
  $st = if($r.status -ne 'COMPLETED'){'FAIL'} elseif(-not $chg){'SILENT'} else {'OK'}
  Rec 'sheet_metal' "edge_flange(len=$fl)" $st $(if($r.status -ne 'COMPLETED'){$r.error.code}else{"$v0→$v1"}) $g
}
# edge_flange 角度组合
foreach($ang in 45, 90, 135){
  NewSheet
  $ei = Edge20
  $v0 = Vol
  $r = Call 'sheet_metal_feature' @{ feature_type='edge_flange'; edge_index=$ei; flange_length=0.010; angle=$ang } -TimeoutSec 90
  $v1 = if($r.status -eq 'COMPLETED'){ Vol }else{''}
  $chg = ($r.status -eq 'COMPLETED' -and $v0 -ne $v1)
  $st = if($r.status -ne 'COMPLETED'){'FAIL'} elseif(-not $chg){'SILENT'} else {'OK'}
  Rec 'sheet_metal' "edge_flange(angle=$ang)" $st $(if($r.status -ne 'COMPLETED'){$r.error.code}else{"$v0→$v1"}) ''
}

# ═══ ② analyze_model 全部 8 种类型 ═══
Write-Output ""
Write-Output "=== ② analyze_model 全部类型（建一个真零件）==="
CleanDoc
$null = Call 'create_sketch' @{ plane='Front Plane' }
$null = Call 'add_sketch_entities' @{ segments=@(
  @{entity_type='line';x1=-0.05;y1=-0.03;x2=0.05;y2=-0.03},
  @{entity_type='line';x1= 0.05;y1=-0.03;x2=0.05;y2=0.03},
  @{entity_type='line';x1= 0.05;y1= 0.03;x2=-0.05;y2=0.03},
  @{entity_type='line';x1=-0.05;y1= 0.03;x2=-0.05;y2=-0.03}) }
$null = Call 'extrude_feature' @{ feature_type='boss'; depth=0.01 }

foreach($t in 'features','geometry','mass_properties','bodies','edges','faces','feature_map'){
  $r = Call 'analyze_model' @{ analysis_type=$t } -TimeoutSec 90
  $g = if($r.status -eq 'COMPLETED'){ $s = $r.cadState.features[0]; $s.Substring(0,[Math]::Min(58,$s.Length)) } else {''}
  $st = if($r.status -ne 'COMPLETED'){'FAIL'}else{'OK'}
  Rec 'analyze' $t $st $(if($r.status -ne 'COMPLETED'){$r.error.code}else{''}) $g
}
# faces 的 near/k/axis 组合
foreach($c in @(
  @{n='faces near k=3'; p=@{analysis_type='faces'; near='[0,0,0.005]'; k=3}},
  @{n='faces near k=1'; p=@{analysis_type='faces'; near='[0.05,0,0.005]'; k=1}},
  @{n='faces near 无k';  p=@{analysis_type='faces'; near='[0,0,0]'}},
  @{n='faces axis=[0,0,1]';p=@{analysis_type='faces'; axis='[0,0,1]'}},
  @{n='edges near k=3'; p=@{analysis_type='edges'; near='[0,0,0.005]'; k=3}}
)){
  $r = Call 'analyze_model' $c.p
  $st = if($r.status -ne 'COMPLETED'){'FAIL'}else{'OK'}
  Rec 'analyze' $c.n $st $(if($r.status -ne 'COMPLETED'){$r.error.code}else{''}) ''
}

# ═══ 汇总 ═══
Write-Output ""
Write-Output "=== 汇总 ==="
$script:Res | Group-Object Status | ForEach-Object { "  {0,-8} {1}" -f $_.Name, $_.Count }
$bad = $script:Res | Where-Object { $_.Status -eq 'SILENT' }
Write-Output ""
if($bad){ "⚠ 静默失败:"; $bad | ForEach-Object { "   [$($_.Tool)] $($_.Combo)  $($_.Msg)" } }
else { "★ 无静默失败" }
$script:Res | Export-Csv -Path "C:\Users\Zegel\solidpilot-mcp\param_combos2.csv" -NoTypeInformation -Encoding UTF8

