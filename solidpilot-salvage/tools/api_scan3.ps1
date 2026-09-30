# 综合套件：建模全链路 + 特征 + 修饰
# 规则：同一问题连续 5 轮不通就跳过，回头集中解决。
# 关键教训：每组测试必须【自建环境】（上轮切了文档导致 bodies=0，后面全废）。

param([string]$Suite = 'chain')

$ErrorActionPreference='Continue'
. "C:\Users\Zegel\solidpilot-mcp\tools\call.ps1"
$script:Res = New-Object System.Collections.ArrayList

function T {
  param([string]$N, [scriptblock]$A)
  $sw=[Diagnostics.Stopwatch]::StartNew(); $st='ERR'; $m=''
  try{ $r=&$A; $sw.Stop(); $st=$r.status
       if($st -ne 'COMPLETED'){ $m="$($r.error.code)" }
       else { $f=$r.cadState.features
              $m = if($f -and $f.Count){ (($f[0] -replace '\s+',' ').Substring(0,[Math]::Min(90,($f[0] -replace '\s+',' ').Length))) } else {'ok'} } }
  catch{ $sw.Stop(); $st='THROW'; $m=($_.Exception.Message -replace '\s+',' ') }
  [void]$script:Res.Add([pscustomobject]@{Suite=$Suite;Name=$N;Status=$st;Ms=[int]$sw.ElapsedMilliseconds;Msg=$m})
  $mk = switch($st){'COMPLETED'{'✅'}'THROW'{'💥'}default{'❌'}}
  "  $mk $N  $m"
}

# ═══ 第 1 组：自建带 12 条边的实体 ═══
"── 组1: 建模基础 ──"
T 'open_new_part'      { Call 'open_new_part' @{} }
T 'create_sketch'      { Call 'create_sketch' @{ plane='Front Plane' } }
T '闭合矩形x2' { Call 'add_sketch_entities' @{ segments=@(
    @{entity_type='line';x1=-0.05;y1=-0.03;x2=0.05;y2=-0.03},
    @{entity_type='line';x1= 0.05;y1=-0.03;x2=0.05;y2=0.03},
    @{entity_type='line';x1= 0.05;y1= 0.03;x2=-0.05;y2=0.03},
    @{entity_type='line';x1=-0.05;y1= 0.03;x2=-0.05;y2=-0.03}) } }
T 'extrude(boss)'      { $r=Call 'extrude_feature' @{feature_type='boss';depth=0.01}
                         if($r.status -eq 'COMPLETED'){
                           $t=($r.cadState.features|%{$_.Trim().Trim('"')}) -join ' '
                           if($t -match '(凸台-拉伸\d+|Boss-Extrude\d+)'){ $script:Boss=$matches[1] } }
                         $r }
"     boss = $($script:Boss)"

# ═══ 第 2 组：修饰特征（用真实 edge_indices）═══
"── 组2: 修饰特征 ──"
$edgeCount = 0
$e = Call 'analyze_model' @{ analysis_type='edges' }
if($e.status -eq 'COMPLETED'){
  try{ $ej=($e.cadState.features[0]|ConvertFrom-Json); $edgeCount=$ej.edge_count; "     边数 = $edgeCount" }catch{}
}
if($edgeCount -gt 0){
  T 'fillet(edge_indices)'  { Call 'add_edge_feature' @{feature_type='fillet';  radius_or_distance=0.002; edge_indices='[0]'} }
  T 'verify(fillet)'        { Call 'analyze_model' @{analysis_type='mass_properties'} }
  T 'chamfer(edge_indices)' { Call 'add_edge_feature' @{feature_type='chamfer'; radius_or_distance=0.001; edge_indices='[2]'} }
  T 'verify(chamfer)'       { Call 'analyze_model' @{analysis_type='mass_properties'} }
} else { "  ⚠ 无实体，跳过组2" }

# ═══ 第 3 组：阵列 ═══
"── 组3: 阵列 ──"
if($script:Boss){
  T 'create_pattern(linear)' { Call 'create_pattern' @{pattern_type='linear';feature_name=$script:Boss;spacing=0.02;count=3;direction='X'} }
  T 'create_pattern(mirror)' { Call 'create_pattern' @{pattern_type='mirror';features_json="[`"$script:Boss`"]";plane='Right Plane'} }
  T 'verify(pattern)'       { Call 'analyze_model' @{analysis_type='bodies'} }
} else { "  ⚠ 无 boss，跳过组3" }

# ═══ 第 4 组：钣金（需要专门的草图）═══
"── 组4: 钣金 ──"
T 'sheet_metal(新草图)' { Call 'create_sketch' @{plane='Front Plane'} }
T 'sheet_metal(细长条)' { Call 'add_sketch_entities' @{segments=@(
    @{entity_type='line';x1=-0.08;y1=-0.01;x2=0.08;y2=-0.01},
    @{entity_type='line';x1= 0.08;y1=-0.01;x2=0.08;y2=0.01},
    @{entity_type='line';x1= 0.08;y1= 0.01;x2=-0.08;y2=0.01},
    @{entity_type='line';x1=-0.08;y1= 0.01;x2=-0.08;y2=-0.01}) } }
T 'sheet_metal(base_flange)' { Call 'sheet_metal_feature' @{feature_type='base_flange';thickness=0.002;bend_radius=0.001} }
T 'verify(钣金)'           { Call 'analyze_model' @{analysis_type='geometry'} }

# ═══ 第 5 组：草图约束与尺寸 ═══
"── 组5: 草图约束/尺寸 ──"
T 'create_sketch'         { Call 'create_sketch' @{plane='Top Plane'} }
T 'circle'                { Call 'add_sketch_entity' @{entity_type='circle';cx=0;cy=0;radius=0.02} }
T 'constraint(vertical)'  { Call 'add_sketch_constraint' @{constraint_type='vertical';px1=0.02;py1=0} }
T 'dimension(圆直径)'      { Call 'add_dimension' @{px=0;py=0.02;value=0.05} }
T 'analyze(sketch)'       { Call 'analyze_model' @{analysis_type='features'} }
T 'modify_dimension'      { $f=Call 'analyze_model' @{analysis_type='features'}
                            $sk = $null
                            try{ $fj=($f.cadState.features[0]|ConvertFrom-Json)
                                 $sk = ($fj.features|Where-Object{$_.type -match 'ProfileFeat'}|Select-Object -Last 1).name }catch{}
                            "     草图=$sk"
                            Call 'modify_dimension' @{name="D1@$sk";value=0.06} }

# ═══ 汇总 ═══
"`n=== 套件 $Suite 汇总 ==="
$script:Res | Group-Object Status | ForEach-Object { "  {0,-10} {1}/{2}" -f $_.Name,$_.Count,$script:Res.Count }
$ok=($script:Res|Where-Object{$_.Status -eq 'COMPLETED'}).Count
"  通过率 $ok / $($script:Res.Count)"
$log="C:\Users\Zegel\solidpilot-mcp\api_scan_results.csv"
if(Test-Path $log){
  $hdr = (Get-Content $log -First 1)
  $need = ($script:Res[0].PSObject.Properties.Name | Where-Object { $hdr -notmatch $_ })
  if($need.Count -eq 0){ $R | Export-Csv -Path $log -Append -NoTypeInformation -Encoding UTF8 }
  else { $R | Select-Object Suite,Name,Status,Ms,Msg | Export-Csv -Path $log -Append -NoTypeInformation -Encoding UTF8 }
} else {
  $R | Select-Object Suite,Name,Status,Ms,Msg | Export-Csv -Path $log -NoTypeInformation -Encoding UTF8
}

