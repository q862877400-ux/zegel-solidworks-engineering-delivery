. "C:\Users\Zegel\solidpilot-mcp\tools\call.ps1"
# 加固后的回归测试：正常路径必须仍然 COMPLETED（不能把好工具改坏）
$ErrorActionPreference='Continue'
$R = New-Object System.Collections.ArrayList
function T { param([string]$N,[scriptblock]$A)
  $st='ERR'; $m=''
  try{ $r=&$A; $st=$r.status
       if($st -ne 'COMPLETED'){ $m="$($r.error.code)" } else { $m='ok' } }
  catch{ $st='THROW'; $m=($_.Exception.Message -replace '\s+',' ') }
  [void]$R.Add([pscustomobject]@{Name=$N;Status=$st;Msg=$m})
  $mk=switch($st){'COMPLETED'{'✅'}'THROW'{'💥'}default{'❌'}}
  "  $mk $N  $m"
}

Write-Output "=== 回归：加固后的 extrude / add_edge_feature 必须仍然正常 ==="
T 'extrude(boss)' {
  $null = Call 'open_new_part' @{}
  $null = Call 'create_sketch' @{ plane='Front Plane' }
  $null = Call 'add_sketch_entities' @{ segments=@(
    @{entity_type='line';x1=-0.05;y1=-0.03;x2=0.05;y2=-0.03},
    @{entity_type='line';x1= 0.05;y1=-0.03;x2=0.05;y2=0.03},
    @{entity_type='line';x1= 0.05;y1= 0.03;x2=-0.05;y2=0.03},
    @{entity_type='line';x1=-0.05;y1= 0.03;x2=-0.05;y2=-0.03}) }
  Call 'extrude_feature' @{ feature_type='boss'; depth=0.01 }
}
T '  体积正常' { Call 'analyze_model' @{ analysis_type='mass_properties' } }
T 'fillet'      { Call 'add_edge_feature' @{ feature_type='fillet'; radius_or_distance=0.002; edge_indices='[0]' } }
T 'chamfer'     { Call 'add_edge_feature' @{ feature_type='chamfer'; radius_or_distance=0.001; edge_indices='[2]' } }
T 'cut'         {
  $null = Call 'create_sketch' @{ plane='Front Plane' }
  $null = Call 'add_sketch_entity' @{ entity_type='circle'; cx=0; cy=0; radius=0.02 }
  Call 'extrude_feature' @{ feature_type='cut'; through=$true }
}
T 'revolve'     {
  $null = Call 'open_new_part' @{}
  $null = Call 'create_sketch' @{ plane='Front Plane' }
  $null = Call 'add_sketch_entities' @{ segments=@(
    @{entity_type='line';x1=0.02;y1=-0.02;x2=0.05;y2=-0.02},
    @{entity_type='line';x1=0.05;y1=-0.02;x2=0.05;y2=0.02},
    @{entity_type='line';x1=0.05;y1=0.02;x2=0.02;y2=0.02},
    @{entity_type='line';x1=0.02;y1=0.02;x2=0.02;y2=-0.02},
    @{entity_type='line';x1=0.0;y1=-0.03;x2=0.0;y2=0.06}) }
  Call 'extrude_feature' @{ feature_type='revolve'; angle=360; axis_x1=0; axis_y1=-0.03; axis_x2=0; axis_y2=0.06 }
}
T 'pattern'     {
  $f = Call 'analyze_model' @{ analysis_type='features' }
  $n = ($f.cadState.features[0]|ConvertFrom-Json).features | Where-Object { $_.type -eq 'Extrusion' } | Select-Object -First 1
  Call 'create_pattern' @{ pattern_type='linear'; feature_name=$n.name; spacing=0.02; count=3; direction='X' }
}
T 'sheet_metal(base_flange)' {
  $null = Call 'open_new_part' @{}
  $null = Call 'create_sketch' @{ plane='Front Plane' }
  $null = Call 'add_sketch_entities' @{ segments=@(
    @{entity_type='line';x1=-0.08;y1=-0.01;x2=0.08;y2=-0.01},
    @{entity_type='line';x1= 0.08;y1=-0.01;x2=0.08;y2=0.01},
    @{entity_type='line';x1= 0.08;y1= 0.01;x2=-0.08;y2=0.01},
    @{entity_type='line';x1=-0.08;y1= 0.01;x2=-0.08;y2=-0.01}) }
  Call 'sheet_metal_feature' @{ feature_type='base_flange'; thickness=0.002; bend_radius=0.001 }
}
T 'edge_flange' {
  $e = Call 'analyze_model' @{ analysis_type='edges' }
  $ej = $e.cadState.features[0]|ConvertFrom-Json
  $pick=-1
  for($i=0;$i -lt $ej.edges.Count;$i++){
    $ed=$ej.edges[$i]
    $sx=[double]$ed.start[0];$sy=[double]$ed.start[1];$sz=[double]$ed.start[2]
    $ex=[double]$ed.end[0];$ey=[double]$ed.end[1];$ez=[double]$ed.end[2]
    if([math]::Abs([math]::Sqrt([math]::Pow($ex-$sx,2)+[math]::Pow($ey-$sy,2)+[math]::Pow($ez-$sz,2))*1000 - 20) -lt 0.5){ $pick=$ed.i; break }
  }
  Call 'sheet_metal_feature' @{ feature_type='edge_flange'; edge_index=$pick; flange_length=0.01; angle=90 }
}

Write-Output ""
Write-Output "=== 汇总 ==="
$R | Group-Object Status | ForEach-Object { "  {0,-10} {1}/{2}" -f $_.Name,$_.Count,$R.Count }
$fail = $R | Where-Object { $_.Status -ne 'COMPLETED' }
if($fail.Count -gt 0){
  "  ⚠ 回归失败（加固把好工具改坏了？）:"
  $fail | ForEach-Object { "    $($_.Name): $($_.Msg)" }
} else { "  ★ 全部回归通过 —— 加固没有破坏正常功能" }
