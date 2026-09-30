. "C:\Users\Zegel\solidpilot-mcp\tools\call.ps1"
# ★ 判据自检（R14 教训）：先确认我要读的字段【真的存在】，再把它当判据
$ErrorActionPreference='Continue'
$script:Res = New-Object System.Collections.ArrayList
function Rec { param($T,$C,$S,$M,$G)
  [void]$script:Res.Add([pscustomobject]@{Tool=$T;Combo=$C;Status=$S;Msg=$M;Geo=$G})
  $mk=switch($S){'OK'{'✅'};'SILENT'{'⚠静默'};'FAIL'{'❌'}else{'💥'}}
  "  $mk [$T] $C  $M $G"
}
function CleanDoc { for($i=0;$i -lt 30;$i++){ if((Call 'close_document' @{}).status -ne 'COMPLETED'){ break }; Start-Sleep -Milliseconds 120 } }
function NewPart { CleanDoc; $null = Call 'open_new_part' @{} }
$parts = "D:\AI\SW\AI Solidworks\模型"

# ═══ ① create_sketch：plane / on_face / face_index ═══
Write-Output "=== ① create_sketch 定位方式（判据=草图 plane.origin 是否落在目标面上）==="
function MakeBox {
  NewPart
  $null = Call 'create_sketch' @{ plane='Front Plane' }
  $null = Call 'add_sketch_entities' @{ segments=@(
    @{entity_type='line';x1=-0.05;y1=-0.03;x2=0.05;y2=-0.03},
    @{entity_type='line';x1= 0.05;y1=-0.03;x2=0.05;y2=0.03},
    @{entity_type='line';x1= 0.05;y1= 0.03;x2=-0.05;y2=0.03},
    @{entity_type='line';x1=-0.05;y1= 0.03;x2=-0.05;y2=-0.03}) }
  $null = Call 'extrude_feature' @{ feature_type='boss'; depth=0.02 }
  $r = Call 'analyze_model' @{ analysis_type='faces' }
  return ($r.cadState.features[0]|ConvertFrom-Json).faces
}
function FaceIdxByNormal { param($faces,$ax,$val)
  foreach($f in $faces){
    $n = ([string]$f.normal) -split '\s+'
    if([math]::Abs([double]$n[[int]$ax] - $val) -lt 1e-6){ return $f.i }
  }
  return -1
}

# A. 三个基准面
foreach($pl in 'Front Plane','Top Plane','Right Plane'){
  NewPart
  $r = Call 'create_sketch' @{ plane=$pl }
  $sk = $null
  if($r.status -eq 'COMPLETED'){
    $s = Call 'analyze_model' @{ analysis_type='sketch'; name='草图1' }
    if($s.cadState.features.Count){
      $j = $s.cadState.features[0]|ConvertFrom-Json
      $sk = "ref=$($j.plane.ref) origin=$($j.plane.frame.origin -join ',')"
    }
  }
  $st = if($r.status -ne 'COMPLETED'){'FAIL'}else{'OK'}
  Rec 'create_sketch' "plane=$pl" $st $(if($r.status -ne 'COMPLETED'){$r.error.code}else{''}) $sk
}
# B. on_face + face_index（三种法向的面）
foreach($case in @(
  @{ax=2; val=1;   nm='+Z 顶面'},
  @{ax=2; val=-1;  nm='-Z 底面'},
  @{ax=0; val=1;   nm='+X 侧面'}
)){
  $faces = MakeBox
  $idx = FaceIdxByNormal $faces $case.ax $case.val
  if($idx -lt 0){ Rec 'create_sketch' "on_face $($case.nm)" 'FAIL' '找不到该法向的面' ''; continue }
  $r = Call 'create_sketch' @{ on_face=$true; face_index=$idx }
  $orig = ''
  if($r.status -eq 'COMPLETED'){
    $s = Call 'analyze_model' @{ analysis_type='sketch'; name='草图1' }
    if($s.cadState.features.Count){
      $j = $s.cadState.features[0]|ConvertFrom-Json
      $orig = ($j.plane.frame.origin -join ',')
    }
  }
  # 判据自检：草图原点必须【不在 z=0】（否则说明建在基准面上了，没用 face_index）
  $silent = if($r.status -eq 'COMPLETED' -and $orig -like '0,0,0*'){'SILENT'}else{'OK'}
  Rec 'create_sketch' "on_face face_index=$idx ($($case.nm))" $(if($r.status -ne 'COMPLETED'){'FAIL'}else{$silent}) $(if($r.status -ne 'COMPLETED'){$r.error.code}else{''}) "origin=($orig)"
}
# C. on_face + face_x/y/z 坐标选面
$faces = MakeBox
$fp = ($faces | Where-Object { ([string]$_.normal) -match '^0\.0 0\.0 1' -or ([string]$_.normal) -match '^0 0 1' } | Select-Object -First 1).point
if($fp){
  $p = ([string]$fp) -split '\s+'
  $r = Call 'create_sketch' @{ on_face=$true; face_x=[double]$p[0]; face_y=[double]$p[1]; face_z=[double]$p[2] }
  Rec 'create_sketch' "on_face + face_x/y/z 坐标选面" $(if($r.status -eq 'COMPLETED'){'OK'}else{'FAIL'}) $(if($r.status -ne 'COMPLETED'){$r.error.code}else{''}) "p=($($p -join ','))"
} else { Rec 'create_sketch' 'on_face + 坐标' 'FAIL' '没找到 +Z 面' '' }

# ═══ ② insert_component：config / fixed / transform ═══
Write-Output ""
Write-Output "=== ② insert_component 参数（判据=analyze_assembly 的 components[].transform）==="
foreach($c in @(
  @{n='默认(自动位置)';   p=@{}},
  @{n='指定 x/y/z';       p=@{x=0.1; y=0.05; z=-0.02}},
  @{n='fixed=true';      p=@{fixed=$true}},
  @{n='fixed=false';     p=@{fixed=$false}},
  @{n='config=默认';      p=@{config='默认'}},
  @{n='config=空串';      p=@{config=''}},
  @{n='config=不存在名';   p=@{config='NoSuchConfig'}}
)){
  $null = Call 'open_new_assembly' @{}
  $r = Call 'insert_component' (@{file_path="$parts\主轴壳体_Housing.sldprt"} + $c.p) -TimeoutSec 90
  $n = ''; $fx = ''; $t = ''
  if($r.status -eq 'COMPLETED'){
    $a = (Call 'analyze_assembly' @{}).cadState.features[0] | ConvertFrom-Json
    if($a.components.Count){
      $c0 = $a.components[0]
      $n = $c0.name; $fx = $c0.fixed
      $t = ($c0.transform[9..11] -join ',')
    }
  }
  $st = if($r.status -ne 'COMPLETED'){'FAIL'}else{'OK'}
  Rec 'insert_component' $c.n $st $(if($r.status -ne 'COMPLETED'){$r.error.code}else{''}) "name=$n fixed=$fx pos=($t)"
}
NewPart

# ═══ ③ bom_from_assembly：out_dir ═══
Write-Output ""
Write-Output "=== ③ bom_from_assembly out_dir（判据=文件真的落盘）==="
$null = Call 'open_document' @{ file_path="$parts\换刀主轴装配_BT30_ATC_Assembly.SLDASM" }
foreach($c in @(@{n='无 out_dir'; p=@{}}, @{n='指定 out_dir'; p=@{out_dir="$env:TEMP\bomtest"}})){
  if(Test-Path "$env:TEMP\bomtest"){ Remove-Item "$env:TEMP\bomtest" -Recurse -Force -EA SilentlyContinue }
  $r = Call 'bom_from_assembly' $c.p -TimeoutSec 90
  $j = $null
  if($r.status -eq 'COMPLETED'){ $j = $r.cadState.features[0]|ConvertFrom-Json }
  $cnt = if($j -and $j.rows){ ($j.rows|Measure-Object).Count } else { 0 }
  $of = if($j){ $j.out_file } else { '' }
  $onDisk = 0
  if($of -and (Test-Path $of)){ $onDisk = [int]((Get-Item $of).Length/1KB) }
  $st = if($r.status -ne 'COMPLETED'){'FAIL'}else{'OK'}
  Rec 'bom_from_assembly' $c.n $st $(if($r.status -ne 'COMPLETED'){$r.error.code}else{"rows=$cnt"}) "out_file=$of onDisk=${onDisk}KB"
}

Write-Output ""
Write-Output "=== 汇总 ==="
$script:Res | Group-Object Status | ForEach-Object { "  {0,-8} {1}" -f $_.Name, $_.Count }
$bad = $script:Res | Where-Object { $_.Status -eq 'SILENT' }
if($bad){ "⚠ 静默:"; $bad | ForEach-Object { "   [$($_.Tool)] $($_.Combo)  $($_.Geo)" } } else { "★ 无静默" }
$script:Res | Export-Csv -Path "C:\Users\Zegel\solidpilot-mcp\param_combos4.csv" -NoTypeInformation -Encoding UTF8

