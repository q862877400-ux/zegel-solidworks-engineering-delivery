# 套件：Motion / Electrical / 钣金细节 / 标准件
$ErrorActionPreference='Continue'
. "C:\Users\Zegel\solidpilot-mcp\tools\call.ps1"
$script:Res = New-Object System.Collections.ArrayList
function T { param([string]$N,[scriptblock]$A)
  $sw=[Diagnostics.Stopwatch]::StartNew(); $st='ERR'; $m=''
  try{ $r=&$A; $sw.Stop(); $st=$r.status
       if($st -ne 'COMPLETED'){ $m="$($r.error.code)" }
       else { $f=$r.cadState.features; $m=if($f -and $f.Count){ (($f[0] -replace '\s+',' ').Substring(0,[Math]::Min(90,($f[0] -replace '\s+',' ').Length))) }else{'ok'} } }
  catch{ $sw.Stop(); $st='THROW'; $m=($_.Exception.Message -replace '\s+',' ') }
  [void]$script:Res.Add([pscustomobject]@{Suite='misc';Name=$N;Status=$st;Ms=[int]$sw.ElapsedMilliseconds;Msg=$m})
  $mk=switch($st){'COMPLETED'{'✅'}'THROW'{'💥'}default{'❌'}}
  "  $mk $N  $m"
}

$partsDir = "D:\AI\SW\AI Solidworks\模型"
$stdDir   = "D:\AI\SW\AI Solidworks\设计\标准件"

"── 组1: Motion 运动分析 ──"
T 'open_document(装配)'    { Call 'open_document' @{ file_path="$partsDir\换刀主轴装配_BT30_ATC_Assembly.SLDASM" } }
T 'motion_study(explode)'  { Call 'motion_study' @{ action='explode' } }
T 'analyze(运动后)'        { Call 'analyze_assembly' @{} }
T 'motion_study(rotation)' { Call 'motion_study' @{ action='rotation' } }
T 'motion_study(probe)'    { Call 'motion_study' @{ action='probe' } }

"── 组2: Electrical ──"
T 'electrical' { Call 'electrical' @{ } }

"── 组3: 钣金细节（edge_flange / bend）──"
T 'open_new_part'  { Call 'open_new_part' @{} }
T 'sketch(Front)'  { Call 'create_sketch' @{ plane='Front Plane' } }
T '细长矩形' { Call 'add_sketch_entities' @{ segments=@(
    @{entity_type='line';x1=-0.08;y1=-0.01;x2=0.08;y2=-0.01},
    @{entity_type='line';x1= 0.08;y1=-0.01;x2=0.08;y2=0.01},
    @{entity_type='line';x1= 0.08;y1= 0.01;x2=-0.08;y2=0.01},
    @{entity_type='line';x1=-0.08;y1= 0.01;x2=-0.08;y2=-0.01}) } }
T 'base_flange'    { Call 'sheet_metal_feature' @{ feature_type='base_flange'; thickness=0.002; bend_radius=0.001 } }
T 'verify(钣金)'   { Call 'analyze_model' @{ analysis_type='geometry' } }
$e = Call 'analyze_model' @{ analysis_type='edges' }
$edgeN = 0
if($e.status -eq 'COMPLETED'){ try{ $edgeN = (($e.cadState.features[0]|ConvertFrom-Json).edge_count) }catch{} }
"     边数 = $edgeN"
if($edgeN -gt 0){
  T 'edge_flange' { Call 'sheet_metal_feature' @{ feature_type='edge_flange'; edge_index=0; flange_length=0.01; angle=90 } }
  T 'verify(翻边)' { Call 'analyze_model' @{ analysis_type='geometry' } }
  T 'flat_pattern' { Call 'sheet_metal_feature' @{ feature_type='flat_pattern' } }
} else { "  ⚠ 无边，跳过翻边/展开" }

"── 组4: 标准件（三种转换件已在库里）──"
foreach($n in '六角螺母_M12_ISO4032','平垫圈_M12_ISO7089','内六角螺钉_M12x40_ISO4762'){
  T "打开标准件 $n" { Call 'open_document' @{ file_path="$stdDir\$n.sldprt" } }
  T "  质量 $n"    { Call 'analyze_model' @{ analysis_type='mass_properties' } }
}

"── 组5: 批量插入到装配 ──"
T 'open_new_assembly2' { Call 'open_new_assembly' @{} }
foreach($n in '六角螺母_M12_ISO4032','平垫圈_M12_ISO7089'){
  T "  插入 $n" { Call 'insert_standard_part' @{ file="$stdDir\$n.sldprt" } }
}
T 'verify(装配)' { Call 'analyze_assembly' @{} }

"`n=== 汇总 ==="
$script:Res | Group-Object Status | ForEach-Object { "  {0,-10} {1}/{2}" -f $_.Name,$_.Count,$script:Res.Count }
$ok=($script:Res|Where-Object{$_.Status -eq 'COMPLETED'}).Count
"  通过率 $ok / $($script:Res.Count)"
$script:Res | Export-Csv -Path "C:\Users\Zegel\solidpilot-mcp\api_scan_results.csv" -NoTypeInformation -Encoding UTF8
