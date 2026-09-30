. "C:\Users\Zegel\solidpilot-mcp\tools\call.ps1"
$asm = "D:\AI\SW\AI Solidworks\模型\换刀主轴装配_BT30_ATC_Assembly.SLDASM"
function Log1 {
  $r = Call 'motion_study' $args[0] -TimeoutSec 120
  if($r.status -ne 'COMPLETED'){ return "FAILED $($r.error.code)" }
  $j = $r.cadState.features[0]|ConvertFrom-Json
  $l = $j.log | Where-Object { $_ -match 'rotate \d+ turn' } | Select-Object -First 1
  if(-not $l){ $l = ($j.log | Select-Object -First 1) }
  return $l
}

Write-Output "=== 修复后验证 ==="
foreach($c in @(
  @{n='revolutions=1';   p=@{study='rotation'; name='R1'; revolutions=1}},
  @{n='revolutions=2';   p=@{study='rotation'; name='R2'; revolutions=2}},
  @{n='revolutions=3';   p=@{study='rotation'; name='R3'; revolutions=3}},
  @{n='revolutions=0.5'; p=@{study='rotation'; name='R4'; revolutions=0.5}},
  @{n='revolutions=2.5'; p=@{study='rotation'; name='R5'; revolutions=2.5}},
  @{n='angle=60';        p=@{study='rotation'; name='R6'; angle=60}},
  @{n='angle=720';       p=@{study='rotation'; name='R7'; angle=720}},
  @{n='默认(无参数)';      p=@{study='rotation'; name='R8'}}
)){
  $null = Call 'open_document' @{ file_path=$asm }
  $r = Call 'motion_study' $c.p -TimeoutSec 120
  $s = if($r.status -ne 'COMPLETED'){ "❌ $($r.error.code)" }
       else {
         $j = $r.cadState.features[0]|ConvertFrom-Json
         $l = $j.log | Where-Object { $_ -match 'turn\(s\)' } | Select-Object -First 1
         "✅ $l"
       }
  Write-Output ("  {0,-16} {1}" -f $c.n, $s)
  if($r.status -ne 'COMPLETED'){
    $m = $r.error.message -replace '\s+',' '
    Write-Output ("                   └─ {0}" -f $m.Substring(0,[Math]::Min(120,$m.Length)))
  }
}
