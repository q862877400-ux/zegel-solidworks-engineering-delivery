. "C:\Users\Zegel\solidpilot-mcp\tools\call.ps1"
# 参数组合扫描 3：add_mate（9 种配合类型）+ motion_study（3 种 × 参数）
$ErrorActionPreference='Continue'
$script:Res = New-Object System.Collections.ArrayList
function Rec { param($T,$C,$S,$M,$G)
  [void]$script:Res.Add([pscustomobject]@{Tool=$T;Combo=$C;Status=$S;Msg=$M;Geo=$G})
  $mk=switch($S){'OK'{'✅'};'SILENT'{'⚠静默'};'FAIL'{'❌'}else{'💥'}}
  "  $mk [$T] $C  $M $G"
}
function CleanDoc { for($i=0;$i -lt 30;$i++){ if((Call 'close_document' @{}).status -ne 'COMPLETED'){ break }; Start-Sleep -Milliseconds 120 } }

# ═══ ① add_mate：9 种配合类型 ═══
Write-Output "=== ① add_mate 全部配合类型（每次重建装配）==="
$parts = "D:\AI\SW\AI Solidworks\模型"
$mates = @(
  @{n='coincident'; p=@{}},
  @{n='concentric'; p=@{}},
  @{n='perpendicular'; p=@{}},
  @{n='parallel';   p=@{}},
  @{n='tangent';    p=@{}},
  @{n='distance';   p=@{value=0.01}},
  @{n='angle';      p=@{value=90}},
  @{n='lock';       p=@{}},
  @{n='coincident+flip'; p=@{flip=$true}}
)
foreach($m in $mates){
  $null = Call 'open_new_assembly' @{}
  $null = Call 'insert_component' @{ file_path="$parts\主轴壳体_Housing.sldprt" }
  $null = Call 'insert_component' @{ file_path="$parts\刀柄_Holder.sldprt"; x=0.05; y=0; z=0 }
  $a0 = (Call 'analyze_assembly' @{}).cadState.features[0]
  $n0 = ($a0|ConvertFrom-Json).components.Count
  $p = @{ mate_type=$m.n; a_component='主轴壳体_Housing-1'; a_kind='face'; a_index=0
          b_component='刀柄_Holder-1'; b_kind='face'; b_index=0 }
  foreach($k in $m.p.Keys){ $p[$k] = $m.p[$k] }
  $r = Call 'add_mate' $p -TimeoutSec 90
  # 验证：配合数真的增加了吗
  $a1 = (Call 'analyze_assembly' @{}).cadState.features[0]
  $mj = $a1|ConvertFrom-Json
  $hasMate = if($mj.mates){ ($mj.mates|Measure-Object).Count } else { 0 }
  $st = if($r.status -ne 'COMPLETED'){'FAIL'} elseif($hasMate -lt 1){'SILENT'} else {'OK'}
  Rec 'add_mate' $m.n $st $(if($r.status -ne 'COMPLETED'){$r.error.code}else{"mates=$hasMate"}) ''
}
CleanDoc

# ═══ ② motion_study 3 种 × 参数 ═══
Write-Output ""
Write-Output "=== ② motion_study 全部类型 ==="
$asm = "$parts\换刀主轴装配_BT30_ATC_Assembly.SLDASM"
foreach($ms in @(
  @{n='explode';  p=@{study='explode';  name='MC_exp'}},
  @{n='explode';  p=@{study='explode';  name='MC_exp2'; duration=1}},
  @{n='collapse'; p=@{study='collapse'; name='MC_col'}},
  @{n='rotation'; p=@{study='rotation'; name='MC_rot'}},
  @{n='rotation'; p=@{study='rotation'; name='MC_rot2'; revolutions=2}},
  @{n='rotation'; p=@{study='rotation'; name='MC_rot3'; angle=60}}
)){
  $null = Call 'open_document' @{ file_path=$asm }
  $r = Call 'motion_study' $ms.p -TimeoutSec 120
  $k = ''
  if($r.status -eq 'COMPLETED'){
    $j = $r.cadState.features[0]|ConvertFrom-Json
    $k = $j.kind
    $line = ($j.log | Where-Object { $_ -match '-> True' } | Select-Object -First 1)
    $k = "kind=$k  $line"
  }
  # 静默判据：返回的 kind 必须与请求一致
  $st = if($r.status -ne 'COMPLETED'){'FAIL'}
        elseif($k -notmatch $ms.n.Split(' ')[0]){'SILENT'}
        else {'OK'}
  Rec 'motion_study' $ms.n $st $(if($r.status -ne 'COMPLETED'){$r.error.code}else{''}) $k
}

Write-Output ""
Write-Output "=== 汇总 ==="
$script:Res | Group-Object Status | ForEach-Object { "  {0,-8} {1}" -f $_.Name, $_.Count }
$bad = $script:Res | Where-Object { $_.Status -eq 'SILENT' }
if($bad){ "⚠ 静默:"; $bad | ForEach-Object { "   [$($_.Tool)] $($_.Combo)  $($_.Geo)" } } else { "★ 无静默" }
$script:Res | Export-Csv -Path "C:\Users\Zegel\solidpilot-mcp\param_combos3.csv" -NoTypeInformation -Encoding UTF8
