. "C:\Users\Zegel\solidpilot-mcp\tools\call.ps1"
$ErrorActionPreference='Continue'
$script:Res = New-Object System.Collections.ArrayList
function T { param([string]$N,[scriptblock]$A)
  $sw=[Diagnostics.Stopwatch]::StartNew(); $st='ERR'; $m=''
  try{ $r=&$A; $sw.Stop(); $st=$r.status
       if($st -ne 'COMPLETED'){ $m="$($r.error.code)" }
       else { $f=$r.cadState.features; $m=if($f -and $f.Count){ (($f[0] -replace '\s+',' ').Substring(0,[Math]::Min(80,($f[0] -replace '\s+',' ').Length))) }else{'ok'} } }
  catch{ $sw.Stop(); $st='THROW'; $m=($_.Exception.Message -replace '\s+',' ') }
  [void]$script:Res.Add([pscustomobject]@{Suite='sm2';Name=$N;Status=$st;Ms=[int]$sw.ElapsedMilliseconds;Msg=$m})
  $mk=switch($st){'COMPLETED'{'✅'}'THROW'{'💥'}default{'❌'}}
  "  $mk $N  $m"
}

function NewSheet {
  $null = Call 'open_new_part' @{}
  $null = Call 'create_sketch' @{ plane='Front Plane' }
  $null = Call 'add_sketch_entities' @{ segments=@(
    @{entity_type='line';x1=-0.08;y1=-0.01;x2=0.08;y2=-0.01},
    @{entity_type='line';x1= 0.08;y1=-0.01;x2=0.08;y2=0.01},
    @{entity_type='line';x1= 0.08;y1= 0.01;x2=-0.08;y2=0.01},
    @{entity_type='line';x1=-0.08;y1= 0.01;x2=-0.08;y2=-0.01}) }
  $null = Call 'sheet_metal_feature' @{ feature_type='base_flange'; thickness=0.002; bend_radius=0.001 }
}

Write-Output "=== ① sketched_bend（SM3dBend：绕草图里的【折弯线】弯，固定侧=预选面）==="
NewSheet
# 折弯线必须画在【已成形钣金的面】上
$e = Call 'analyze_model' @{ analysis_type='faces' }
$fj = $e.cadState.features[0] | ConvertFrom-Json
$faceI = -1
foreach($fc in $fj.faces){
  $n = ([string]$fc.normal) -split '\s+'
  if($n.Count -ge 3 -and [math]::Abs([double]$n[2] - 1) -lt 1e-6){
    $p = ([string]$fc.point) -split '\s+'
    if([double]$p[2] -gt 0){ $faceI = $fc.i; break }
  }
}
Write-Output "  顶面 face_index = $faceI"
if($faceI -ge 0){
  $null = Call 'create_sketch' @{ on_face=$true; face_index=$faceI }
  $null = Call 'add_sketch_entity' @{ entity_type='line'; x1=-0.05; y1=0; x2=0.05; y2=0 }
  foreach($pos in 'centerline','material-inside'){
    $r = Call 'sheet_metal_feature' @{ feature_type='sketched_bend'; angle=90; bend_radius=0.001
                                        use_default_radius=$true; bend_position=$pos } -TimeoutSec 90
    Write-Output "  bend_position=$pos => $($r.status) $(if($r.status -ne 'COMPLETED'){$r.error.code})"
    if($r.status -eq 'COMPLETED'){
      Write-Output "    ★★ $(($r.cadState.features[0] -replace '\s+',' '))"
      (Call 'analyze_model' @{ analysis_type='mass_properties' }).cadState.features[0] | ForEach-Object { "       mass = $_" }
      break
    }
  }
}

Write-Output ""
Write-Output "=== ② edge_flange_sketch（第1步：生成翻边轮廓草图，留激活）==="
NewSheet
$e2 = Call 'analyze_model' @{ analysis_type='edges' }
$ej = $e2.cadState.features[0] | ConvertFrom-Json
# 找 20mm 的边
$pick = -1
for($i=0;$i -lt $ej.edges.Count;$i++){
  $ed=$ej.edges[$i]
  $sx=[double]$ed.start[0];$sy=[double]$ed.start[1];$sz=[double]$ed.start[2]
  $ex=[double]$ed.end[0];  $ey=[double]$ed.end[1];  $ez=[double]$ed.end[2]
  $len=[math]::Round([math]::Sqrt([math]::Pow($ex-$sx,2)+[math]::Pow($ey-$sy,2)+[math]::Pow($ez-$sz,2))*1000,1)
  if([math]::Abs($len-20) -lt 0.5){ $pick=$ed.i; break }
}
Write-Output "  选 edge_index=$pick (20mm)"
if($pick -ge 0){
  $r2 = Call 'sheet_metal_feature' @{ feature_type='edge_flange_sketch'; edge_index=$pick; angle=90
                                       clear_profile=$true } -TimeoutSec 90
  Write-Output "  edge_flange_sketch => $($r2.status) $(if($r2.status -ne 'COMPLETED'){$r2.error.code})"
  if($r2.status -eq 'COMPLETED'){
    Write-Output "    ★★ 生成的草图 frame = $(($r2.cadState.features[0] -replace '\s+',' '))"
    # 第3步：在激活的草图里画轮廓 → 第2步完成
    $null = Call 'add_sketch_entity' @{ entity_type='line'; x1=0; y1=0; x2=0.01; y2=0 }
    $r3 = Call 'sheet_metal_feature' @{ feature_type='edge_flange_finish'; flange_length=0.01; angle=90 } -TimeoutSec 90
    Write-Output "  edge_flange_finish => $($r3.status) $(if($r3.status -ne 'COMPLETED'){$r3.error.code})"
    if($r3.status -eq 'COMPLETED'){
      Write-Output "    ★★★ 成功 = $(($r3.cadState.features[0] -replace '\s+',' '))"
      (Call 'analyze_model' @{ analysis_type='mass_properties' }).cadState.features[0] | ForEach-Object { "         mass = $_" }
    }
  }
}

"`n=== 汇总 ==="
$script:Res | Group-Object Status | ForEach-Object { "  {0,-10} {1}/{2}" -f $_.Name,$_.Count,$script:Res.Count }
$ok=($script:Res|Where-Object{$_.Status -eq 'COMPLETED'}).Count
"  通过率 $ok / $($script:Res.Count)"
$script:Res | Export-Csv -Path "C:\Users\Zegel\solidpilot-mcp\api_scan_sm2.csv" -NoTypeInformation -Encoding UTF8
