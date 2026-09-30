# 静默失败复核：对每个标记 ✅ 的能力，验证几何【真的】变了
# 起因（2026-09-28）：sketched_bend 返回 COMPLETED、特征名也建出来了，
# 但面数 6→6、z 分布完全没变 —— 几何一点没弯。这是第三个静默失败
# （前两个：edit_feature delete、auto_dimension_drawing）。
$ErrorActionPreference = 'Continue'
. "C:\Users\Zegel\solidpilot-mcp\tools\call.ps1"
$script:Res = New-Object System.Collections.ArrayList

function Snap {
  # 返回一个几何指纹：体积 + 面数 + 边数 + 包围盒
  $v = (Call 'analyze_model' @{ analysis_type='mass_properties' }).cadState.features[0]
  $g = (Call 'analyze_model' @{ analysis_type='geometry' }).cadState.features[0]
  $vol = if($v -match 'volume=([0-9.E+-]+)'){ $matches[1] } else { '0' }
  "$vol|$g"
}

function Chk { param([string]$N, [scriptblock]$Act, [string]$Before)
  $sw=[Diagnostics.Stopwatch]::StartNew(); $st='ERR'; $m=''
  try{ $r=&$Act; $sw.Stop(); $st=$r.status
       if($st -ne 'COMPLETED'){ $m="$($r.error.code)" }
       else { $m='ok' } }
  catch{ $sw.Stop(); $st='THROW'; $m=($_.Exception.Message -replace '\s+',' ') }
  $after = Snap
  $changed = ($after -ne $Before)
  $verdict = if($st -ne 'COMPLETED'){ 'FAIL' } elseif($changed){ 'REAL' } else { 'SILENT' }
  [void]$script:Res.Add([pscustomobject]@{Name=$N;Status=$st;GeometryChanged=$changed;Verdict=$verdict})
  $mk = switch($verdict){'REAL'{'✅真实生效'};'SILENT'{'⚠假成功'};default{'❌失败'}}
  "  $mk  $N  (状态=$st)"
}

Write-Output "=== 复核：每个 ✅ 能力是否真的改变了几何 ==="

# 1) extrude boss
$null = Call 'open_new_part' @{}
$b = Snap
$null = Call 'create_sketch' @{ plane='Front Plane' }
$null = Call 'add_sketch_entities' @{ segments=@(
  @{entity_type='line';x1=-0.05;y1=-0.03;x2=0.05;y2=-0.03},
  @{entity_type='line';x1= 0.05;y1=-0.03;x2=0.05;y2=0.03},
  @{entity_type='line';x1= 0.05;y1= 0.03;x2=-0.05;y2=0.03},
  @{entity_type='line';x1=-0.05;y1= 0.03;x2=-0.05;y2=-0.03}) }
Chk 'extrude_feature(boss)' { Call 'extrude_feature' @{ feature_type='boss'; depth=0.01 } } $b

# 2) fillet
$b = Snap
Chk 'add_edge_feature(fillet)' { Call 'add_edge_feature' @{ feature_type='fillet'; radius_or_distance=0.002; edge_indices='[0]' } } $b

# 3) pattern
$b = Snap
$null = Call 'analyze_model' @{ analysis_type='features' }
$f0 = (Call 'analyze_model' @{ analysis_type='features' }).cadState.features[0] | ConvertFrom-Json
$bossName = ($f0.features | Where-Object { $_.type -match 'Extrude' } | Select-Object -First 1).name
Chk 'create_pattern(linear)' { Call 'create_pattern' @{ pattern_type='linear'; feature_name=$bossName; spacing=0.02; count=3; direction='X' } } $b

# 4) cut
$b = Snap
$null = Call 'create_sketch' @{ plane='Front Plane' }
$null = Call 'add_sketch_entity' @{ entity_type='circle'; cx=0; cy=0; radius=0.02 }
Chk 'extrude_feature(cut)' { Call 'extrude_feature' @{ feature_type='cut'; through=$true } } $b

# 5) revolve
$null = Call 'open_new_part' @{}
$null = Call 'create_sketch' @{ plane='Front Plane' }
$null = Call 'add_sketch_entities' @{ segments=@(
  @{entity_type='line';x1=0.02;y1=-0.02;x2=0.05;y2=-0.02},
  @{entity_type='line';x1=0.05;y1=-0.02;x2=0.05;y2=0.02},
  @{entity_type='line';x1=0.05;y1=0.02;x2=0.02;y2=0.02},
  @{entity_type='line';x1=0.02;y1=0.02;x2=0.02;y2=-0.02},
  @{entity_type='line';x1=0.0;y1=-0.03;x2=0.0;y2=0.06}) }
$b = Snap
Chk 'extrude_feature(revolve)' { Call 'extrude_feature' @{ feature_type='revolve'; angle=360
                                  axis_x1=0.0; axis_y1=-0.03; axis_x2=0.0; axis_y2=0.06 } } $b

# 6) sheet metal base_flange
$null = Call 'open_new_part' @{}
$null = Call 'create_sketch' @{ plane='Front Plane' }
$null = Call 'add_sketch_entities' @{ segments=@(
  @{entity_type='line';x1=-0.08;y1=-0.01;x2=0.08;y2=-0.01},
  @{entity_type='line';x1= 0.08;y1=-0.01;x2=0.08;y2=0.01},
  @{entity_type='line';x1= 0.08;y1= 0.01;x2=-0.08;y2=0.01},
  @{entity_type='line';x1=-0.08;y1= 0.01;x2=-0.08;y2=-0.01}) }
$b = Snap
Chk 'sheet_metal(base_flange)' { Call 'sheet_metal_feature' @{ feature_type='base_flange'; thickness=0.002; bend_radius=0.001 } } $b

# 7) edge_flange（已验证过的，复核）
$e = Call 'analyze_model' @{ analysis_type='edges' }
$ej = $e.cadState.features[0] | ConvertFrom-Json
$pick = -1
for($i=0;$i -lt $ej.edges.Count;$i++){
  $ed=$ej.edges[$i]
  $sx=[double]$ed.start[0];$sy=[double]$ed.start[1];$sz=[double]$ed.start[2]
  $ex2=[double]$ed.end[0];$ey2=[double]$ed.end[1];$ez2=[double]$ed.end[2]
  $len=[math]::Sqrt([math]::Pow($ex2-$sx,2)+[math]::Pow($ey2-$sy,2)+[math]::Pow($ez2-$sz,2))*1000
  if([math]::Abs($len-20) -lt 0.5){ $pick=$ed.i; break }
}
if($pick -ge 0){
  $b = Snap
  Chk 'sheet_metal(edge_flange)' { Call 'sheet_metal_feature' @{ feature_type='edge_flange'
                                 edge_index=$pick; flange_length=0.01; angle=90 } } $b
}

# 8) add_dimension + modify_dimension（改尺寸后体积应变）
$null = Call 'open_new_part' @{}
$null = Call 'create_sketch' @{ plane='Front Plane' }
$null = Call 'add_sketch_entities' @{ segments=@(
  @{entity_type='line';x1=-0.05;y1=-0.02;x2=0.05;y2=-0.02},
  @{entity_type='line';x1= 0.05;y1=-0.02;x2=0.05;y2=0.02},
  @{entity_type='line';x1= 0.05;y1= 0.02;x2=-0.05;y2=0.02},
  @{entity_type='line';x1=-0.05;y1= 0.02;x2=-0.05;y2=-0.02}) }
$sk = Call 'analyze_model' @{ analysis_type='sketch'; name='草图1' }
$sj = $sk.cadState.features[0] | ConvertFrom-Json
$seg = $sj.sketch.segments | Where-Object { $_.kind -eq 'line' } | Select-Object -First 1
$mx = ($seg.x1 + $seg.x2) / 2; $my = ($seg.y1 + $seg.y2) / 2
$null = Call 'add_dimension' @{ px=$mx; py=$my; value=0.1 }
$null = Call 'extrude_feature' @{ feature_type='boss'; depth=0.01 }
$b = Snap
Chk 'modify_dimension' { Call 'modify_dimension' @{ name='D1@草图1'; value=0.12 } } $b

Write-Output ""
Write-Output "=== 复核汇总 ==="
$script:Res | Group-Object Verdict | ForEach-Object { "  {0,-10} {1} 项" -f $_.Name, $_.Count }
""
$script:Res | ForEach-Object { "  {0,-8} {1,-10} {2}" -f $_.Verdict, $_.Status, $_.Name }
$script:Res | Export-Csv -Path "C:\Users\Zegel\solidpilot-mcp\api_silent_audit.csv" -NoTypeInformation -Encoding UTF8
