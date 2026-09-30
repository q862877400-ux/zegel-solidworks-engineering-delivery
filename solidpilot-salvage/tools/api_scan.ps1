# 需求：全 API 能力扫描
# 规则（用户 2026-09-28 定）：同一问题【连续 5 轮跑不通就跳过】，回头集中解决。
# 目的：把 566 个官方接口族 / 47 个已注册工具逐个实测，产出"哪些能用、哪些不能"的地图。

# 用法：.\api_scan.ps1 -Suite <名字> [-Verbose]
param(
  [string]$Suite = 'basic',
  [switch]$KeepDoc      # 不关文档（链式操作时用）
)

$ErrorActionPreference = 'Continue'
. "C:\Users\Zegel\solidpilot-mcp\tools\call.ps1"

$script:Results = New-Object System.Collections.ArrayList

function T {
  param([string]$Name, [string]$Cmd, [scriptblock]$Action, [string]$Doc = '零件')
  $sw = [Diagnostics.Stopwatch]::StartNew()
  $st = 'ERR'; $msg = ''
  try {
    $r = & $Action
    $sw.Stop()
    $st = $r.status
    if($st -ne 'COMPLETED'){ $msg = "$($r.error.code): $(($r.error.message -replace '\s+',' ').Substring(0,[Math]::Min(90,($r.error.message -replace '\s+',' ').Length)))" }
    else {
      $f = $r.cadState.features
      if($f -and $f.Count){ $msg = (($f[0] -replace '\s+',' ').Substring(0,[Math]::Min(100,($f[0] -replace '\s+',' ').Length))) }
      else { $msg = 'ok' }
    }
  } catch {
    $sw.Stop(); $st = 'THROW'; $msg = (($_.Exception.Message -replace '\s+',' ').Substring(0,[Math]::Min(90,($_.Exception.Message -replace '\s+',' ').Length)))
  }
  $ms = [int]$sw.ElapsedMilliseconds
  [void]$script:Results.Add([pscustomobject]@{
    Suite=$Suite; Name=$Name; Cmd=$Cmd; Status=$st; Ms=$ms; Msg=$msg
  })
  $mark = switch($st){ 'COMPLETED' {'✅'} 'THROW' {'💥'} default {'❌'} }
  "  $mark $Name ($ms ms)  $msg"
}

# ── 准备环境 ──
"=== 套件: $Suite ==="
$null = Call 'open_new_part' @{ }
T 'open_new_part' 'open_new_part' { Call 'open_new_part' @{} }

switch ($Suite) {

'basic' {
  # ── 基础建模回归 ──
  T 'create_sketch' 'create_sketch' { Call 'create_sketch' @{ plane='Front Plane' } }
  T 'add_sketch_entity(line)' 'add_sketch_entity' {
    Call 'add_sketch_entity' @{ entity_type='line'; x1=-0.05; y1=-0.03; x2=0.05; y2=-0.03 }
  }
  T 'add_sketch_entity(circle)' 'add_sketch_entity' {
    Call 'add_sketch_entity' @{ entity_type='circle'; cx=0.02; cy=0.02; radius=0.01 }
  }
  T 'add_sketch_entity(arc_center)' 'add_sketch_entity' {
    Call 'add_sketch_entity' @{ entity_type='arc_center'; cx=0.05; cy=0.0; x1=0.05; y1=0.01; x2=0.06; y2=0.0 }
  }
  T 'add_sketch_entity(rectangle)' 'add_sketch_entity' {
    Call 'add_sketch_entity' @{ entity_type='rectangle'; x1=-0.02; y1=-0.02; x2=0.02; y2=0.02 }
  }
  T 'add_sketch_constraint' 'add_sketch_constraint' {
    Call 'add_sketch_constraint' @{ constraint_type='horizontal'; px1=-0.05; py1=-0.03 }
  }
  T 'add_dimension' 'add_dimension' {
    Call 'add_dimension' @{ px=0.0; py=-0.03; value=0.1 }
  }
  T 'extrude_feature' 'extrude_feature' { Call 'extrude_feature' @{ feature_type='boss'; depth=0.01 } }
  T 'analyze_model(features)' 'analyze_model' { Call 'analyze_model' @{ analysis_type='features' } }
  T 'analyze_model(geometry)' 'analyze_model' { Call 'analyze_model' @{ analysis_type='geometry' } }
  T 'analyze_model(mass)' 'analyze_model' { Call 'analyze_model' @{ analysis_type='mass_properties' } }
  T 'analyze_model(bodies)' 'analyze_model' { Call 'analyze_model' @{ analysis_type='bodies' } }
  T 'analyze_model(edges)' 'analyze_model' { Call 'analyze_model' @{ analysis_type='edges' } }
  T 'analyze_model(faces)' 'analyze_model' { Call 'analyze_model' @{ analysis_type='faces' } }
  T 'analyze_model(sketch)' 'analyze_model' { Call 'analyze_model' @{ analysis_type='sketch'; name='Sketch1' } }
  T 'analyze_model(feature_map)' 'analyze_model' { Call 'analyze_model' @{ analysis_type='feature_map' } }
  T 'analyze_model(face_near)' 'analyze_model' { Call 'analyze_model' @{ analysis_type='faces'; near='[0,0,0.005]'; k=3 } }
  T 'add_edge_feature(fillet)' 'add_edge_feature' {
    Call 'add_edge_feature' @{ feature_type='fillet'; radius_or_distance=0.001; ex=0.05; ey=0.0; ez=0.005 }
  }
  T 'add_edge_feature(chamfer)' 'add_edge_feature' {
    Call 'add_edge_feature' @{ feature_type='chamfer'; radius_or_distance=0.0005; ex=0.05; ey=0.0; ez=0.005 }
  }
  T 'create_pattern(linear)' 'create_pattern' {
    Call 'create_pattern' @{ pattern_type='linear'; feature_name=''; spacing=0.01; count=3; direction='X' }
  }
  T 'create_rib' 'create_rib' { Call 'create_rib' @{ thickness=0.002 } }
  T 'add_reference_geometry' 'add_reference_geometry' {
    Call 'add_reference_geometry' @{ type='axis'; entity1_name='Front Plane'; entity1_type='PLANE'; entity2_name='Top Plane'; entity2_type='PLANE' }
  }
  T 'set_part_material' 'set_part_material' {
    Call 'set_part_material' @{ material_name='AISI 1020' }
  }
  T 'export_document(STEP)' 'export_document' {
    Call 'export_document' @{ format='STEP'; file_path="$env:TEMP\api_scan_out.step" }
  }
  T 'batch_export' 'batch_export' {
    Call 'batch_export' @{ file_path_base="$env:TEMP\api_scan_batch"; formats_json='["STEP","STL"]' }
  }
  T 'verify_state' 'verify_state' { Call 'verify_state' @{} }
  T 'get_selection' 'get_selection' { Call 'get_selection' @{} }
}

'sheetmetal' {
  T 'sheet_metal(base_flange)' 'sheet_metal_feature' {
    Call 'sheet_metal_feature' @{ feature_type='base_flange'; thickness=0.002; bend_radius=0.001 }
  }
}

'picture' {
  T 'add_drive_placeholder' 'n/a' { Call 'analyze_model' @{ analysis_type='geometry' } }
}

default { "  (未知套件: $Suite)" }
}

# ── 汇总 ──
"`n=== 套件 $Suite 汇总 ==="
$script:Results | Group-Object Status | ForEach-Object {
  "  {0,-10} {1}/{2}" -f $_.Name, $_.Count, $script:Results.Count
}
$ok = ($script:Results | Where-Object { $_.Status -eq 'COMPLETED' }).Count
"  通过率 $ok / $($script:Results.Count)"

# 落盘（追加，供最终汇总）
$log = "C:\Users\Zegel\solidpilot-mcp\api_scan_results.csv"
if(Test-Path $log){ $script:Results | Export-Csv -Path $log -Append -NoTypeInformation -Encoding UTF8 }
else { $script:Results | Export-Csv -Path $log -NoTypeInformation -Encoding UTF8 }
"  已追加到 $log"
