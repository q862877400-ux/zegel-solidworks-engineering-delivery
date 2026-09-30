# 需求：全 API 能力扫描（第 2 轮，修正 basic 套件）
# 规则（用户 2026-09-28 定）：同一问题【连续 5 轮跑不通就跳过】，回头集中解决。
# 本轮修正：上一轮 8 个失败全是"调用顺序/参数不对"，不是 API 不可用。

param([string]$Suite = 'basic2')

$ErrorActionPreference = 'Continue'
. "C:\Users\Zegel\solidpilot-mcp\tools\call.ps1"

$script:Results = New-Object System.Collections.ArrayList

function T {
  param([string]$Name, [scriptblock]$Action)
  $sw = [Diagnostics.Stopwatch]::StartNew()
  $st='ERR'; $msg=''
  try {
    $r = & $Action
    $sw.Stop(); $st = $r.status
    if($st -ne 'COMPLETED'){ $m="$($r.error.code)"; $msg = $m }
    else {
      $f = $r.cadState.features
      $msg = if($f -and $f.Count){ (($f[0] -replace '\s+',' ').Substring(0,[Math]::Min(100,($f[0] -replace '\s+',' ').Length))) } else { 'ok' }
    }
  } catch { $sw.Stop(); $st='THROW'; $msg=($_.Exception.Message -replace '\s+',' ') }
  [void]$script:Results.Add([pscustomobject]@{Suite=$Suite;Name=$Name;Status=$st;Ms=[int]$sw.ElapsedMilliseconds;Msg=$msg})
  $mark = switch($st){ 'COMPLETED' {'✅'} 'THROW' {'💥'} default {'❌'} }
  "  $mark $Name ($([int]$sw.ElapsedMilliseconds) ms)  $msg"
}

"=== 套件: $Suite ==="
$null = Call 'open_new_part' @{}
T 'open_new_part' { Call 'open_new_part' @{} }

# ── 1. 画一个【闭合矩形】供拉伸（上一轮画的是散线，profile 不闭合所以 extrude 失败）──
T 'create_sketch' { Call 'create_sketch' @{ plane='Front Plane' } }
T 'add_sketch_entities(闭合矩形)' {
  Call 'add_sketch_entities' @{ segments = @(
    @{entity_type='line'; x1=-0.05; y1=-0.03; x2=0.05; y2=-0.03},
    @{entity_type='line'; x1= 0.05; y1=-0.03; x2=0.05; y2=0.03},
    @{entity_type='line'; x1= 0.05; y1= 0.03; x2=-0.05; y2=0.03},
    @{entity_type='line'; x1=-0.05; y1= 0.03; x2=-0.05; y2=-0.03}
  ) }
}

# ── 2. 拉伸出实体（闭合轮廓后应成功）──
$bossName = $null
T 'extrude_feature(boss)' {
  $r = Call 'extrude_feature' @{ feature_type='boss'; depth=0.01 }
  if($r.status -eq 'COMPLETED'){
    $t = ($r.cadState.features | ForEach-Object { $_.Trim().Trim('"') }) -join ' '
    if($t -match '(Boss-Extrude\d+|凸台-拉伸\d+)'){ $script:Boss = $matches[1] }
  }
  $r
}
"     → 挤出特征名 = $($script:Boss)"

# ── 3. 有实体后再测质量属性 / 边 / 面（上一轮 bodies=0 导致全空）──
T 'analyze_model(geometry)' { Call 'analyze_model' @{ analysis_type='geometry' } }
T 'analyze_model(mass)'     { Call 'analyze_model' @{ analysis_type='mass_properties' } }
T 'analyze_model(bodies)'   { Call 'analyze_model' @{ analysis_type='bodies' } }
T 'analyze_model(edges)'    { Call 'analyze_model' @{ analysis_type='edges' } }
T 'analyze_model(faces)'    { Call 'analyze_model' @{ analysis_type='faces' } }

# ── 4. 拿到真实边坐标后再测圆角/倒角（上一轮坐标是瞎猜的，必然 EDGE_NOT_FOUND）──
$edgeMid = $null
$e = Call 'analyze_model' @{ analysis_type='edges' }
if($e.status -eq 'COMPLETED'){
  try{
    $ej = ($e.cadState.features[0] | ConvertFrom-Json)
    if($ej.edges -and $ej.edges.Count){ $edgeMid = $ej.edges[0].mid; "     → 首条边中点 = $edgeMid" }
  } catch { "     （解析边失败）" }
}
if($edgeMid){
  $mx=[double]$edgeMid[0]; $my=[double]$edgeMid[1]; $mz=[double]$edgeMid[2]
  T 'add_edge_feature(fillet)'  { Call 'add_edge_feature' @{ feature_type='fillet';  radius_or_distance=0.001; ex=$mx; ey=$my; ez=$mz } }
  T 'add_edge_feature(chamfer)' { Call 'add_edge_feature' @{ feature_type='chamfer'; radius_or_distance=0.0005; ex=$mx; ey=$my; ez=$mz } }
} else { "  ⚠ 拿不到边坐标，跳过圆角/倒角" }

# ── 5. 阵列：传真实特征名（上一轮 feature_name 空）──
if($script:Boss){
  T 'create_pattern(linear)' { Call 'create_pattern' @{ pattern_type='linear'; feature_name=$script:Boss; spacing=0.01; count=3; direction='X' } }
} else { "  ⚠ 没有挤出特征名，跳过阵列" }

# ── 6. 筋：需要先有草图且轮廓开放 ──
T 'create_sketch(2)' { Call 'create_sketch' @{ plane='Front Plane' } }
T 'add_sketch_entities(开放线)' { Call 'add_sketch_entity' @{ entity_type='line'; x1=-0.03; y1=0.0; x2=0.03; y2=0.0 } }
T 'create_rib' { Call 'create_rib' @{ thickness=0.002 } }

# ── 7. 草图分析：上一轮找 'Sketch1' 找不到，真实名字要用特征树里的 ──
T 'analyze_model(features)' { Call 'analyze_model' @{ analysis_type='features' } }
$sk = $null
$f = Call 'analyze_model' @{ analysis_type='features' }
if($f.status -eq 'COMPLETED'){
  try{
    $fj = ($f.cadState.features[0] | ConvertFrom-Json)
    $sk = ($fj.features | Where-Object { $_.type -match 'ProfileFeat|ProfileFeature' } | Select-Object -First 1).name
    "     → 草图特征名 = $sk"
  } catch {}
}
if($sk){ T 'analyze_model(sketch)' { Call 'analyze_model' @{ analysis_type='sketch'; name=$sk } } }

# ── 8. 材料 / 导出 / 钣金 ──
T 'set_part_material' { Call 'set_part_material' @{ material_name='AISI 1020' } }
T 'sheet_metal(base_flange)' { Call 'sheet_metal_feature' @{ feature_type='base_flange'; thickness=0.002; bend_radius=0.001 } }
T 'edit_feature(rename)' { if($script:Boss){ Call 'edit_feature' @{ feature_name=$script:Boss; action='rename'; new_name='MainBoss' } } else { throw 'no boss' } }
T 'modify_dimension' { Call 'modify_dimension' @{ name='D1@Sketch1'; value=0.12 } }
T 'export_document(STEP)' { Call 'export_document' @{ format='STEP'; file_path="$env:TEMP\api_scan2.step" } }
T 'save_document' { Call 'save_document' @{ file_path="$env:TEMP\api_scan2.sldprt" } }

# ── 汇总 ──
"`n=== 套件 $Suite 汇总 ==="
$script:Results | Group-Object Status | ForEach-Object { "  {0,-10} {1}/{2}" -f $_.Name, $_.Count, $script:Results.Count }
$ok = ($script:Results | Where-Object { $_.Status -eq 'COMPLETED' }).Count
"  通过率 $ok / $($script:Results.Count)"
$script:Results | Export-Csv -Path "C:\Users\Zegel\solidpilot-mcp\api_scan_results.csv" -Append -NoTypeInformation -Encoding UTF8
