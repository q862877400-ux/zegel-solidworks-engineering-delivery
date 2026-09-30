. "C:\Users\Zegel\solidpilot-mcp\tools\call.ps1"
$ErrorActionPreference = 'Continue'
$script:Res = New-Object System.Collections.ArrayList
function T { param([string]$N,[scriptblock]$A)
  $sw=[Diagnostics.Stopwatch]::StartNew(); $st='ERR'; $m=''
  try{ $r=&$A; $sw.Stop(); $st=$r.status
       if($st -ne 'COMPLETED'){ $m="$($r.error.code)" }
       else { $f=$r.cadState.features; $m=if($f -and $f.Count){ (($f[0] -replace '\s+',' ').Substring(0,[Math]::Min(80,($f[0] -replace '\s+',' ').Length))) }else{'ok'} } }
  catch{ $sw.Stop(); $st='THROW'; $m=($_.Exception.Message -replace '\s+',' ') }
  [void]$script:Res.Add([pscustomobject]@{Suite='dim';Name=$N;Status=$st;Ms=[int]$sw.ElapsedMilliseconds;Msg=$m})
  $mk=switch($st){'COMPLETED'{'✅'}'THROW'{'💥'}default{'❌'}}
  "  $mk $N  $m"
}

# ── 准备：带两个驱动尺寸的矩形草图 ──
Write-Output "=== 建带尺寸的草图 ==="
$null = Call 'open_new_part' @{}
$null = Call 'create_sketch' @{ plane='Front Plane' }
$null = Call 'add_sketch_entities' @{ segments=@(
  @{entity_type='line';x1=-0.05;y1=-0.02;x2=0.05;y2=-0.02},
  @{entity_type='line';x1= 0.05;y1=-0.02;x2=0.05;y2=0.02},
  @{entity_type='line';x1= 0.05;y1= 0.02;x2=-0.05;y2=0.02},
  @{entity_type='line';x1=-0.05;y1= 0.02;x2=-0.05;y2=-0.02}) }

$sk = Call 'analyze_model' @{ analysis_type='sketch'; name='草图1' }
Write-Output "  草图1: $(($sk.cadState.features[0] -replace '\s+',' ').Substring(0,[Math]::Min(300,($sk.cadState.features[0] -replace '\s+',' ').Length)))"

# ── add_dimension：必须点在【线段】上，所以先拿线段的真实坐标 ──
Write-Output ""
Write-Output "=== add_dimension（点在真实线段中点上）==="
$line0 = $null
try {
  $sj = $sk.cadState.features[0] | ConvertFrom-Json
  foreach($seg in $sj.sketch.segments){ if($seg.kind -eq 'line'){ $line0 = $seg; break } }
} catch {}
if($line0){
  $mx = [math]::Round(($line0.x1 + $line0.x2)/2, 6)
  $my = [math]::Round(($line0.y1 + $line0.y2)/2, 6)
  Write-Output "  线段中点 = ($mx, $my)"
  T 'add_dimension(线段中点)' { Call 'add_dimension' @{ px=$mx; py=$my; value=0.1 } }
}

# ── 拉伸一个带尺寸的实体，看能不能改尺寸 ──
T 'extrude(带尺寸草图)' { Call 'extrude_feature' @{ feature_type='boss'; depth=0.01 } }
T 'verify(体积)'        { Call 'analyze_model' @{ analysis_type='mass_properties' } }

# 列出真实草图名与尺寸名
$f2 = Call 'analyze_model' @{ analysis_type='features' }
Write-Output ""
Write-Output "=== 特征树里的草图与尺寸 ==="
try {
  $fj = $f2.cadState.features[0] | ConvertFrom-Json
  $fj.features | Where-Object { $_.type -match 'ProfileFeat|Dimension' } |
    ForEach-Object { "    $($_.name)  [$($_.type)]  $($_.drivingDimensions)" }
} catch { Write-Output "  解析失败" }

# ── modify_dimension：name 格式 D1@草图名 ──
Write-Output ""
Write-Output "=== modify_dimension ==="
foreach($n in 'D1@草图1','草图1@D1','D1'){
  $r = Call 'modify_dimension' @{ name=$n; value=0.12 } -TimeoutSec 60
  Write-Output "  name='$n' => $($r.status) $(if($r.status -ne 'COMPLETED'){$r.error.code})"
  if($r.status -eq 'COMPLETED'){
    Write-Output "    体积应为 0.12*0.04*0.01 = 4.8e-5"
    (Call 'analyze_model' @{ analysis_type='mass_properties' }).cadState.features[0] | ForEach-Object { "    $_" }
    break
  }
}

# ── feature_map：必须先退出草图编辑状态 ──
Write-Output ""
Write-Output "=== analyze_model(feature_map) ==="
T 'feature_map(非编辑态)' { Call 'analyze_model' @{ analysis_type='feature_map' } }

"`n=== 汇总 ==="
$script:Res | Group-Object Status | ForEach-Object { "  {0,-10} {1}/{2}" -f $_.Name,$_.Count,$script:Res.Count }
$ok=($script:Res|Where-Object{$_.Status -eq 'COMPLETED'}).Count
"  通过率 $ok / $($script:Res.Count)"
$script:Res | Export-Csv -Path "C:\Users\Zegel\solidpilot-mcp\api_scan_dim.csv" -NoTypeInformation -Encoding UTF8
