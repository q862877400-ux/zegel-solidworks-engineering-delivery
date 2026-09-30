# 套件：放样(loft) / 扫描(sweep) / 旋转(revolve) / 筋(rib)
# 规则：同一问题连续 5 轮不通就跳过。
$ErrorActionPreference='Continue'
. "C:\Users\Zegel\solidpilot-mcp\tools\call.ps1"
$script:Res = New-Object System.Collections.ArrayList
function T { param([string]$N,[scriptblock]$A)
  $sw=[Diagnostics.Stopwatch]::StartNew(); $st='ERR'; $m=''
  try{ $r=&$A; $sw.Stop(); $st=$r.status
       if($st -ne 'COMPLETED'){ $m="$($r.error.code)" }
       else { $f=$r.cadState.features; $m=if($f -and $f.Count){ (($f[0] -replace '\s+',' ').Substring(0,[Math]::Min(80,($f[0] -replace '\s+',' ').Length))) }else{'ok'} } }
  catch{ $sw.Stop(); $st='THROW'; $m=($_.Exception.Message -replace '\s+',' ') }
  [void]$script:Res.Add([pscustomobject]@{Suite='surf';Name=$N;Status=$st;Ms=[int]$sw.ElapsedMilliseconds;Msg=$m})
  $mk=switch($st){'COMPLETED'{'✅'}'THROW'{'💥'}default{'❌'}}
  "  $mk $N  $m"
}

"=== 套件: 曲面（放样/扫描/旋转/筋）==="

# ═══ 旋转 revolve ═══
"── revolve 旋转体 ──"
T 'open_new_part'  { Call 'open_new_part' @{} }
T 'sketch(Front)'  { Call 'create_sketch' @{ plane='Front Plane' } }
T '矩形轮廓' { Call 'add_sketch_entities' @{ segments=@(
    @{entity_type='line';x1=-0.02;y1=-0.03;x2=0.02;y2=-0.03},
    @{entity_type='line';x1= 0.02;y1=-0.03;x2=0.02;y2=0.03},
    @{entity_type='line';x1= 0.02;y1= 0.03;x2=-0.02;y2=0.03},
    @{entity_type='line';x1=-0.02;y1= 0.03;x2=-0.02;y2=-0.03}) } }
T 'extrude(revolve 360)' { Call 'extrude_feature' @{ feature_type='revolve'; angle=360
                                   axis_x1=0; axis_y1=0; axis_x2=0; axis_y2=0.05 } }
T 'verify(revolve)'  { Call 'analyze_model' @{ analysis_type='mass_properties' } }
T 'verify(几何)'     { Call 'analyze_model' @{ analysis_type='geometry' } }

# ═══ 放样 loft ═══
"── loft 放样（两个截面）──"
T 'open_new_part2' { Call 'open_new_part' @{} }
T 'sketch1(Front)' { Call 'create_sketch' @{ plane='Front Plane' } }
T '截面1(小圆)' { Call 'add_sketch_entity' @{ entity_type='circle'; cx=0; cy=0; radius=0.02 } }
T 'sketch2(Top,带offset)' { Call 'create_sketch' @{ plane='Top Plane' } }
T '截面2(大圆)' { Call 'add_sketch_entity' @{ entity_type='circle'; cx=0; cy=0; radius=0.035 } }
T 'extrude(loft)'  { Call 'extrude_feature' @{ feature_type='loft' } }
T 'verify(loft)'   { Call 'analyze_model' @{ analysis_type='geometry' } }

# ═══ 扫描 sweep ═══
"── sweep 扫描（截面沿路径）──"
T 'open_new_part3' { Call 'open_new_part' @{} }
T 'sketch路径(Top)' { Call 'create_sketch' @{ plane='Top Plane' } }
T '路径线' { Call 'add_sketch_entity' @{ entity_type='line'; x1=-0.05; y1=0; x2=0.05; y2=0 } }
T '退出草图' { Call 'edit_sketch' @{ sketch_name='' } }
T 'sketch截面(Front)' { Call 'create_sketch' @{ plane='Front Plane' } }
T '截面圆' { Call 'add_sketch_entity' @{ entity_type='circle'; cx=-0.05; cy=0; radius=0.008 } }
T 'extrude(sweep)' { Call 'extrude_feature' @{ feature_type='sweep'; path_sketch='草图1' } }
T 'verify(sweep)'  { Call 'analyze_model' @{ analysis_type='geometry' } }

"── rib 加强筋 ──"
T 'open_new_part4' { Call 'open_new_part' @{} }
T 'sketch(Front)'  { Call 'create_sketch' @{ plane='Front Plane' } }
T '矩形底板' { Call 'add_sketch_entities' @{ segments=@(
    @{entity_type='line';x1=-0.05;y1=-0.05;x2=0.05;y2=-0.05},
    @{entity_type='line';x1= 0.05;y1=-0.05;x2=0.05;y2=-0.05},
    @{entity_type='line';x1= 0.05;y1=-0.05;x2=-0.05;y2=-0.05},
    @{entity_type='line';x1=-0.05;y1=-0.05;x2=-0.05;y2=-0.05}) } }
T '拉伸底板' { Call 'extrude_feature' @{ feature_type='boss'; depth=0.005 } }
T 'sketch2(筋轮廓)' { Call 'create_sketch' @{ plane='Front Plane' } }
T '筋的开放轮廓' { Call 'add_sketch_entity' @{ entity_type='line'; x1=-0.04; y1=0.05; x2=0.04; y2=0.05 } }
T 'create_rib' { Call 'create_rib' @{ thickness=0.003 } }
T 'verify(rib)' { Call 'analyze_model' @{ analysis_type='geometry' } }

"`n=== 汇总 ==="
$script:Res | Group-Object Status | ForEach-Object { "  {0,-10} {1}/{2}" -f $_.Name,$_.Count,$script:Res.Count }
$ok=($script:Res|Where-Object{$_.Status -eq 'COMPLETED'}).Count
"  通过率 $ok / $($script:Res.Count)"
$script:Res | Export-Csv -Path "C:\Users\Zegel\solidpilot-mcp\api_scan_results.csv" -NoTypeInformation -Encoding UTF8
