# 套件：剩余未测工具（工程图自动化 / LCSC / 多体 / 编辑草图）
$ErrorActionPreference='Continue'
. "C:\Users\Zegel\solidpilot-mcp\tools\call.ps1"
$script:Res = New-Object System.Collections.ArrayList
function T { param([string]$N,[scriptblock]$A)
  $sw=[Diagnostics.Stopwatch]::StartNew(); $st='ERR'; $m=''
  try{ $r=&$A; $sw.Stop(); $st=$r.status
       if($st -ne 'COMPLETED'){ $m="$($r.error.code)" }
       else { $f=$r.cadState.features; $m=if($f -and $f.Count){ (($f[0] -replace '\s+',' ').Substring(0,[Math]::Min(90,($f[0] -replace '\s+',' ').Length))) }else{'ok'} } }
  catch{ $sw.Stop(); $st='THROW'; $m=($_.Exception.Message -replace '\s+',' ') }
  [void]$script:Res.Add([pscustomobject]@{Suite='rest';Name=$N;Status=$st;Ms=[int]$sw.ElapsedMilliseconds;Msg=$m})
  $mk=switch($st){'COMPLETED'{'✅'}'THROW'{'💥'}default{'❌'}}
  "  $mk $N  $m"
}

$parts = "D:\AI\SW\AI Solidworks\模型"
$tmp   = "$env:TEMP\apisc"

"── 组1: 多体零件拆分成单零件 (save_body_as_part) ──"
T 'open_new_part'  { Call 'open_new_part' @{} }
T '草图(矩形)'    { Call 'create_sketch' @{ plane='Front Plane' } }
T '矩形' { Call 'add_sketch_entities' @{ segments=@(
    @{entity_type='line';x1=-0.03;y1=-0.03;x2=0.03;y2=-0.03},
    @{entity_type='line';x1= 0.03;y1=-0.03;x2=0.03;y2=0.03},
    @{entity_type='line';x1= 0.03;y1= 0.03;x2=-0.03;y2=0.03},
    @{entity_type='line';x1=-0.03;y1= 0.03;x2=-0.03;y2=-0.03}) } }
T '拉伸'          { Call 'extrude_feature' @{ feature_type='boss'; depth=0.02 } }
T '再拉伸一个体'  { Call 'create_sketch' @{ plane='Front Plane'; offset=0.02 }
                    Call 'add_sketch_entity' @{ entity_type='circle'; cx=0; cy=0; radius=0.01 }
                    Call 'extrude_feature' @{ feature_type='boss'; depth=0.01 } }
T 'bodies 统计'   { Call 'analyze_model' @{ analysis_type='bodies' } }
T 'save_body_as_part' { Call 'save_body_as_part' @{ body_index=0; file_path="$tmp\body0.sldprt" } }
T '验证拆出的零件'  { Call 'open_document' @{ file_path="$tmp\body0.sldprt" } }
T '  体积'        { Call 'analyze_model' @{ analysis_type='mass_properties' } }

"── 组2: 编辑草图 (edit_sketch) ──"
T 'open_new_part2' { Call 'open_new_part' @{} }
T '建草图'        { Call 'create_sketch' @{ plane='Front Plane' } }
T '画圆'          { Call 'add_sketch_entity' @{ entity_type='circle'; cx=0; cy=0; radius=0.02 } }
T 'edit_sketch(重开草图1)' { Call 'edit_sketch' @{ sketch_name='草图1' } }
T '  草图内加方形'  { Call 'add_sketch_entity' @{ entity_type='rectangle'; x1=0.01; y1=0.01; x2=0.03; y2=0.03 } }
T '  看草图现在有2个实体' { Call 'analyze_model' @{ analysis_type='sketch'; name='草图1' } }

"── 组3: 编辑特征 (edit_feature: suppress/delete) ──"
T 'open_new_part3' { Call 'open_new_part' @{} }
T 'sketch'        { Call 'create_sketch' @{ plane='Front Plane' } }
T '矩形' { Call 'add_sketch_entities' @{ segments=@(
    @{entity_type='line';x1=-0.02;y1=-0.02;x2=0.02;y2=-0.02},
    @{entity_type='line';x1= 0.02;y1=-0.02;x2=0.02;y2=0.02},
    @{entity_type='line';x1= 0.02;y1= 0.02;x2=-0.02;y2=0.02},
    @{entity_type='line';x1=-0.02;y1= 0.02;x2=-0.02;y2=-0.02}) } }
T '凸台1'        { Call 'extrude_feature' @{ feature_type='boss'; depth=0.01 } }
T '凸台2'        { Call 'create_sketch' @{ plane='Front Plane'; offset=0.01 }
                   Call 'add_sketch_entity' @{ entity_type='circle'; cx=0; cy=0; radius=0.008 }
                   Call 'extrude_feature' @{ feature_type='boss'; depth=0.01 } }
T '列出特征'      { Call 'analyze_model' @{ analysis_type='features' } }
T 'suppress 凸台2' { Call 'edit_feature' @{ feature_name='凸台-拉伸2'; action='suppress' } }
T '  体积应变小'   { Call 'analyze_model' @{ analysis_type='mass_properties' } }
T 'unsuppress'   { Call 'edit_feature' @{ feature_name='凸台-拉伸2'; action='unsuppress' } }
T '  体积应恢复'   { Call 'analyze_model' @{ analysis_type='mass_properties' } }
T 'delete 凸台2'  { Call 'edit_feature' @{ feature_name='凸台-拉伸2'; action='delete' } }
T '  体积应再变小' { Call 'analyze_model' @{ analysis_type='mass_properties' } }

"── 组4: LCSC 电子元件抓取 ──"
T 'lcsc_fetch_step' { Call 'lcsc_fetch_step' @{} }

"── 组5: 工程图自动标注（本机已知 view 创建失败，测另外两个）──"
T 'open_document(零件)' { Call 'open_document' @{ file_path="$parts\主轴壳体_Housing.sldprt" } }
T 'create_drawing'     { Call 'create_drawing' @{} }
T 'auto_dimension_drawing' { Call 'auto_dimension_drawing' @{} }
T 'auto_center_marks'  { Call 'auto_center_marks' @{} }
T 'analyze_slddrw'     { Call 'analyze_slddrw_test' @{ include_relations=$true } }

"── 组6: save_document 全格式 ──"
T 'save_document(sldprt)' { Call 'save_document' @{ file_path="$tmp\out1.sldprt" } }
T 'save_document(STEP)'   { Call 'save_document' @{ file_path="$tmp\out2.step" } }
T 'save_document(STL)'    { Call 'save_document' @{ file_path="$tmp\out3.stl" } }
T 'save_document(IGES)'   { Call 'save_document' @{ file_path="$tmp\out4.iges" } }

"`n=== 汇总 ==="
$script:Res | Group-Object Status | ForEach-Object { "  {0,-10} {1}/{2}" -f $_.Name,$_.Count,$script:Res.Count }
$ok=($script:Res|Where-Object{$_.Status -eq 'COMPLETED'}).Count
"  通过率 $ok / $($script:Res.Count)"
$script:Res | Export-Csv -Path "C:\Users\Zegel\solidpilot-mcp\api_scan_rest.csv" -NoTypeInformation -Encoding UTF8
