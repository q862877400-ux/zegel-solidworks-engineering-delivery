# 参数组合扫描：找出每个工具的哪些参数组合能用/静默失败
# 目的：工具层面已全覆盖（46/46），真正的缺口是【参数组合】——
#      同一个工具不同参数走不同代码路径，其中一些可能静默失败。
. "C:\Users\Zegel\solidpilot-mcp\tools\call.ps1"
$ErrorActionPreference='Continue'
$script:Res = New-Object System.Collections.ArrayList

function Rec { param([string]$Tool,[string]$Combo,[string]$Status,[string]$Msg,[string]$Geo)
  [void]$script:Res.Add([pscustomobject]@{Tool=$Tool;Combo=$Combo;Status=$Status;Msg=$Msg;Geo=$Geo})
  $mk = switch($Status){'OK'{'✅'};'SILENT'{'⚠静默'};'FAIL'{'❌'}else{'💥'}}
  "  $mk [$Tool] $Combo  $Msg $Geo"
}

function Build {
  param([double]$d=0.01,[string]$shape='rect',[string]$plane='Front Plane',[switch]$WithCircle)
  $null = Call 'open_new_part' @{}
  $null = Call 'create_sketch' @{ plane=$plane }
  if($shape -eq 'rect'){
    $null = Call 'add_sketch_entities' @{ segments=@(
      @{entity_type='line';x1=-0.05;y1=-0.03;x2=0.05;y2=-0.03},
      @{entity_type='line';x1= 0.05;y1=-0.03;x2=0.05;y2=0.03},
      @{entity_type='line';x1= 0.05;y1= 0.03;x2=-0.05;y2=0.03},
      @{entity_type='line';x1=-0.05;y1= 0.03;x2=-0.05;y2=-0.03}) }
  }
  if($WithCircle){ $null = Call 'add_sketch_entity' @{ entity_type='circle'; cx=0.03; cy=0.03; radius=0.01 } }
  return (Call 'extrude_feature' @{ feature_type='boss'; depth=$d }).status
}

function Geo { # 返回 "vol=... geo=..."
  $v = (Call 'analyze_model' @{ analysis_type='mass_properties' }).cadState.features[0]
  $g = (Call 'analyze_model' @{ analysis_type='geometry' }).cadState.features[0]
  "$v $g"
}

# ═══ 1. extrude_feature 的参数组合 ═══
Write-Output "=== ① extrude_feature 参数组合 ==="
$combos = @(
  @{n='boss blind';        p=@{feature_type='boss'; depth=0.01}},
  @{n='boss mid_plane';     p=@{feature_type='boss'; depth=0.02; mid_plane=$true}},
  @{n='boss reverse';       p=@{feature_type='boss'; depth=0.01; reverse=$true}},
  @{n='boss through';       p=@{feature_type='boss'; through=$true}},
  @{n='boss up_to_face 0';  p=@{feature_type='boss'; depth=0.005; up_to_face_index=0}},
  @{n='boss up_to_face 1';  p=@{feature_type='boss'; depth=0.005; up_to_face_index=1}}
)
foreach($c in $combos){
  Build
  $r = Call 'extrude_feature' $c.p
  $st = if($r.status -eq 'COMPLETED'){'OK'}else{'FAIL'}
  $m = if($r.status -eq 'COMPLETED'){''}else{$r.error.code}
  # 关键：成功但几何没变 = 静默失败
  $g = if($r.status -eq 'COMPLETED'){ Geo } else {''}
  $silent = if($r.status -eq 'COMPLETED' -and $g -match 'bodies=0'){'SILENT'}else{$st}
  Rec 'extrude' $c.n $silent $m $g
}

# ═══ 2. add_edge_feature 参数组合 ═══
Write-Output "=== ② add_edge_feature 参数组合 ==="
$ec = @(
  @{n='fillet 单边';        p=@{feature_type='fillet'; radius_or_distance=0.002; edge_indices='[0]'}},
  @{n='fillet 多边';        p=@{feature_type='fillet'; radius_or_distance=0.001; edge_indices='[0,2,4]'}},
  @{n='fillet 坐标';        p=@{feature_type='fillet'; radius_or_distance=0.002; ex=0.05; ey=-0.03; ez=0.005}},
  @{n='chamfer d-angle 45'; p=@{feature_type='chamfer'; radius_or_distance=0.001; edge_indices='[0]'; angle=45}},
  @{n='chamfer d-angle 30'; p=@{feature_type='chamfer'; radius_or_distance=0.001; edge_indices='[0]'; angle=30}},
  @{n='chamfer d-d';        p=@{feature_type='chamfer'; radius_or_distance=0.001; distance2=0.0005; edge_indices='[0]'}},
  @{n='chamfer d-d flip';   p=@{feature_type='chamfer'; radius_or_distance=0.001; distance2=0.0005; chamfer_flip=$true; edge_indices='[0]'}}
)
foreach($c in $ec){
  Build
  $r = Call 'add_edge_feature' $c.p
  $g = if($r.status -eq 'COMPLETED'){ Geo } else {''}
  $st = if($r.status -ne 'COMPLETED'){'FAIL'} elseif($g -match 'bodies=0'){'SILENT'} else {'OK'}
  Rec 'add_edge' $c.n $st $(if($r.status -ne 'COMPLETED'){$r.error.code}else{''}) $g
}

# ═══ 3. create_pattern 参数组合 ═══
Write-Output "=== ③ create_pattern 参数组合 ==="
Build
$f = Call 'analyze_model' @{ analysis_type='features' }
$seed = ($f.cadState.features[0]|ConvertFrom-Json).features | Where-Object { $_.type -eq 'Extrusion' } | Select-Object -First 1
$null = Call 'add_reference_geometry' @{ type='axis'; entity1_name='Front Plane'; entity1_type='PLANE'; entity2_name='Top Plane'; entity2_type='PLANE' }
$pc = @(
  @{n='linear X 间距20 count3'; p=@{pattern_type='linear'; feature_name=$seed.name; spacing=0.02; count=3; direction='X'}},
  @{n='linear Y 间距20 count3'; p=@{pattern_type='linear'; feature_name=$seed.name; spacing=0.02; count=3; direction='Y'}},
  @{n='linear Z 间距20 count3'; p=@{pattern_type='linear'; feature_name=$seed.name; spacing=0.02; count=3; direction='Z'}},
  @{n='circular 90 count4';    p=@{pattern_type='circular'; feature_name=$seed.name; axis_name='基准轴1'; angle=90; count=4; equal_spacing=$true}},
  @{n='circular 360 count6';   p=@{pattern_type='circular'; feature_name=$seed.name; axis_name='基准轴1'; angle=360; count=6; equal_spacing=$true}},
  @{n='circular 间距模式';      p=@{pattern_type='circular'; feature_name=$seed.name; axis_name='基准轴1'; angle=60; count=6; equal_spacing=$false}},
  @{n='mirror Right Plane';    p=@{pattern_type='mirror'; features_json="[`"$($seed.name)`"]"; plane='Right Plane'}},
  @{n='mirror Front Plane';    p=@{pattern_type='mirror'; features_json="[`"$($seed.name)`"]"; plane='Front Plane'}}
)
foreach($c in $pc){
  Build
  $null = Call 'add_reference_geometry' @{ type='axis'; entity1_name='Front Plane'; entity1_type='PLANE'; entity2_name='Top Plane'; entity2_type='PLANE' }
  $r = Call 'create_pattern' $c.p
  $g = if($r.status -eq 'COMPLETED'){ Geo } else {''}
  $st = if($r.status -ne 'COMPLETED'){'FAIL'} elseif($g -match 'bodies=0'){'SILENT'} else {'OK'}
  Rec 'pattern' $c.n $st $(if($r.status -ne 'COMPLETED'){$r.error.code}else{''}) $g
}

# ═══ 4. export_document 格式矩阵 ═══
Write-Output "=== ④ export_document 格式矩阵 ==="
Build
$fmt = 'STEP','STL','IGES','PDF'
foreach($f2 in $fmt){
  $r = Call 'export_document' @{ format=$f2; file_path="$env:TEMP\pc.$($f2.ToLower())" } -TimeoutSec 90
  $sz = 0
  if($r.status -eq 'COMPLETED'){
    $p = "$env:TEMP\pc.$($f2.ToLower())"
    if($f2 -eq 'IGES'){ $p = "$env:TEMP\pc.igs" }
    if(Test-Path $p){ $sz = [int]((Get-Item $p).Length/1KB) } else { $sz = -1 }
  }
  $st = if($r.status -ne 'COMPLETED'){'FAIL'} elseif($sz -le 0){'SILENT'} else {'OK'}
  Rec 'export' $f2 $st $(if($r.status -ne 'COMPLETED'){$r.error.code}else{"${sz}KB"}) ''
}

# ═══ 汇总 ═══
Write-Output ""
Write-Output "=== 参数组合汇总 ==="
$script:Res | Group-Object Status | ForEach-Object { "  {0,-8} {1}" -f $_.Name, $_.Count }
""
Write-Output "=== ⚠ 静默失败的组合（成功但没产物）==="
$script:Res | Where-Object { $_.Status -eq 'SILENT' } | ForEach-Object { "  [$($_.Tool)] $($_.Combo)  $($_.Geo)" }
if(-not ($script:Res | Where-Object { $_.Status -eq 'SILENT' })){ "  （无）" }
$script:Res | Export-Csv -Path "C:\Users\Zegel\solidpilot-mcp\param_combos.csv" -NoTypeInformation -Encoding UTF8
