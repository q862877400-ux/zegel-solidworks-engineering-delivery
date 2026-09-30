. "C:\Users\Zegel\solidpilot-mcp\tools\call.ps1"
# 写操作工具的【产物验证测试】：不审计代码，直接调用并检查产物
# 判据自检（第六次翻车的教训）：
#   ① 这个判据在"确定成功"时会显示变化吗？—— 用"操作前后对比"而不是单点检查
#   ② 我要读的字段真的存在吗？—— 全部用已实证存在的字段
$ErrorActionPreference='Continue'
$script:Res = New-Object System.Collections.ArrayList
function Rec { param($T,$S,$D)
  [void]$script:Res.Add([pscustomobject]@{Tool=$T;Status=$S;Detail=$D})
  $mk=switch($S){'PASS'{'✅'};'SILENT'{'⚠静默'};'FAIL'{'❌'}else{'💥'}}
  "  $mk $T  $D"
}
function CleanDoc { for($i=0;$i -lt 40;$i++){ if((Call 'close_document' @{}).status -ne 'COMPLETED'){ break }; Start-Sleep -Milliseconds 100 } }
function NewPart { CleanDoc; $null = Call 'open_new_part' @{} }
# 已实证存在的读接口（全部用过）
function Geo { (Call 'analyze_model' @{ analysis_type='geometry' }).cadState.features[0] }
function Vol { (Call 'analyze_model' @{ analysis_type='mass_properties' }).cadState.features[0] }
function Faces { [int]([regex]::Match((Geo),'bodies=(\d+)').Groups[1].Value) }
function Edges { [int]([regex]::Match((Call 'analyze_model' @{ analysis_type='edges' }).cadState.features[0],'edge_count=(\d+)').Groups[1].Value) }
function ActiveDoc { (Call 'verify_state' @{}).cadState.activeDocument }

$tmp = "$env:TEMP\wtest"
$parts = "D:\AI\SW\AI Solidworks\模型"

Write-Output "=== 写操作工具的产物验证（11 个）==="

# 1. create_sketch — 判据：草图 plane.ref
NewPart
$r1 = Call 'create_sketch' @{ plane='Front Plane' }
if($r1.status -eq 'COMPLETED'){
  $s = Call 'analyze_model' @{ analysis_type='sketch'; name='草图1' }
  $ref = if($s.cadState.features.Count){ ($s.cadState.features[0]|ConvertFrom-Json).plane.ref }else{''}
  Rec 'create_sketch' $(if($ref -eq 'Front Plane'){'PASS'}else{'SILENT'}) "草图 ref=$ref"
} else { Rec 'create_sketch' 'FAIL' $r1.error.code }

# 2. add_sketch_entities — 判据：segments 数量
$b = Call 'analyze_model' @{ analysis_type='sketch'; name='草图1' }
$n0 = if($b.cadState.features.Count){ ($b.cadState.features[0]|ConvertFrom-Json).sketch.counts.line }else{0}
$r2 = Call 'add_sketch_entities' @{ segments=@(
  @{entity_type='line';x1=-0.05;y1=-0.03;x2=0.05;y2=-0.03},
  @{entity_type='line';x1= 0.05;y1=-0.03;x2=0.05;y2=0.03},
  @{entity_type='line';x1= 0.05;y1= 0.03;x2=-0.05;y2=0.03},
  @{entity_type='line';x1=-0.05;y1= 0.03;x2=-0.05;y2=-0.03}) }
$b2 = Call 'analyze_model' @{ analysis_type='sketch'; name='草图1' }
$n1 = if($b2.cadState.features.Count){ ($b2.cadState.features[0]|ConvertFrom-Json).sketch.counts.line }else{0}
Rec 'add_sketch_entities' $(if($n1 -gt $n0){'PASS'}else{'SILENT'}) "线段数 $n0 → $n1"

# 3. extrude_feature — 判据：bodies 从 0 变 1
$g0 = Geo
$r3 = Call 'extrude_feature' @{ feature_type='boss'; depth=0.01 }
$g1 = Geo
Rec 'extrude_feature' $(if($g0 -match 'bodies=0' -and $g1 -match 'bodies=1'){'PASS'}else{'SILENT'}) "$g0 → $g1"

# 4. set_part_material — 判据：材料库有该材料
$r4 = Call 'set_part_material' @{ material_name='AISI 1020' }
Rec 'set_part_material' $(if($r4.status -eq 'COMPLETED'){'PASS'}else{'FAIL'}) $(if($r4.status -eq 'COMPLETED'){'AISI 1020 已设置'}else{$r4.error.code})

# 5. save_document — 判据：文件真的落盘且非空
$f5 = "$tmp\s5.sldprt"
$r5 = Call 'save_document' @{ file_path=$f5 } -TimeoutSec 60
$sz5 = if(Test-Path $f5){ [int]((Get-Item $f5).Length/1KB) }else{ 0 }
Rec 'save_document' $(if($sz5 -gt 0){'PASS'}else{'SILENT'}) "落盘 ${sz5}KB"

# 6. export_document — 判据：导出文件真的存在
$okExp = 0
$szExp = 0
foreach($fmt in 'STEP','STL'){
  $fp = "$tmp\e6.$($fmt.ToLower())"
  $r6 = Call 'export_document' @{ format=$fmt; file_path=$fp } -TimeoutSec 60
  if((Test-Path $fp) -and (Get-Item $fp).Length -gt 0){ $okExp++ }
}
Rec 'export_document' $(if($okExp -eq 2){'PASS'}else{'SILENT'}) "$okExp/2 格式落盘, 共 $([int]$szExp)KB"

# 7. batch_export — 判据：两个文件都在
$r7 = Call 'batch_export' @{ file_path_base="$tmp\b7"; formats_json='["STEP","STL"]' } -TimeoutSec 90
$n7 = 0
foreach($e in 'step','stl'){ if((Test-Path "$tmp\b7.$e") -and (Get-Item "$tmp\b7.$e").Length -gt 0){ $n7++ } }
Rec 'batch_export' $(if($n7 -eq 2){'PASS'}else{'SILENT'}) "$n7/2 文件落盘"

# 8. edit_feature rename — 判据：特征树里新名字出现
$before = (Call 'analyze_model' @{ analysis_type='features' }).cadState.features[0]
$seed = ($before|ConvertFrom-Json).features | Where-Object { $_.type -eq 'Extrusion' } | Select-Object -First 1
$r8 = Call 'edit_feature' @{ feature_name=$seed.name; action='rename'; new_name='RenamedBoss' } -TimeoutSec 60
$after = (Call 'analyze_model' @{ analysis_type='features' }).cadState.features[0]
$found = ($after -match 'RenamedBoss')
Rec 'edit_feature(rename)' $(if($found){'PASS'}else{'SILENT'}) "树里出现 RenamedBoss = $found"

# 9. insert_component — 判据：组件数增加
$null = Call 'open_new_assembly' @{}
$c0 = [int]([regex]::Match((Call 'analyze_assembly' @{}).cadState.features[0],'component_count=(\d+)').Groups[1].Value)
$r9 = Call 'insert_component' @{ file_path="$parts\主轴壳体_Housing.sldprt" } -TimeoutSec 90
$c1 = [int]([regex]::Match((Call 'analyze_assembly' @{}).cadState.features[0],'component_count=(\d+)').Groups[1].Value)
Rec 'insert_component' $(if($c1 -gt $c0){'PASS'}else{'SILENT'}) "组件数 $c0 → $c1"

# 10. bom_from_assembly — 判据：rows 数量 = 组件数
$r10 = Call 'bom_from_assembly' @{ } -TimeoutSec 90
$rows = if($r10.status -eq 'COMPLETED'){ ($r10.cadState.features[0]|ConvertFrom-Json).rows.Count }else{0}
Rec 'bom_from_assembly' $(if($rows -ge $c1){'PASS'}else{'SILENT'}) "rows=$rows 组件数=$c1"

# 11. close_document — 判据：活动文档变了或为空
$docBefore = ActiveDoc
Call 'close_document' @{ } | Out-Null
$docAfter = ActiveDoc
Rec 'close_document' $(if($docAfter -ne $docBefore){'PASS'}else{'SILENT'}) "'$docBefore' → '$docAfter'"

Write-Output ""
Write-Output "=== 汇总 ==="
$script:Res | Group-Object Status | ForEach-Object { "  {0,-8} {1}" -f $_.Name, $_.Count }
$bad = $script:Res | Where-Object { $_.Status -ne 'PASS' }
if($bad){ Write-Output ""; Write-Output "⚠ 非 PASS:"; $bad | ForEach-Object { Write-Output "   $($_.Tool): $($_.Detail)" } }
else { Write-Output ""; Write-Output "  ★ 11/11 写操作工具的产物验证全部通过" }
$script:Res | Export-Csv "C:\Users\Zegel\solidpilot-mcp\write_ops_verify.csv" -NoTypeInformation -Encoding UTF8


