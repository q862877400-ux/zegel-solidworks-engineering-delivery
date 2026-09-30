# 套件：装配 / 配合 / BOM / 工程图
$ErrorActionPreference='Continue'
. "C:\Users\Zegel\solidpilot-mcp\tools\call.ps1"
$script:Res = New-Object System.Collections.ArrayList
function T { param([string]$N,[scriptblock]$A)
  $sw=[Diagnostics.Stopwatch]::StartNew(); $st='ERR'; $m=''
  try{ $r=&$A; $sw.Stop(); $st=$r.status
       if($st -ne 'COMPLETED'){ $m="$($r.error.code)" }
       else { $f=$r.cadState.features; $m=if($f -and $f.Count){ (($f[0] -replace '\s+',' ').Substring(0,[Math]::Min(80,($f[0] -replace '\s+',' ').Length))) }else{'ok'} } }
  catch{ $sw.Stop(); $st='THROW'; $m=($_.Exception.Message -replace '\s+',' ') }
  [void]$script:Res.Add([pscustomobject]@{Suite='asm';Name=$N;Status=$st;Ms=[int]$sw.ElapsedMilliseconds;Msg=$m})
  $mk=switch($st){'COMPLETED'{'✅'}'THROW'{'💥'}default{'❌'}}
  "  $mk $N  $m"
}

$partsDir = "D:\AI\SW\AI Solidworks\模型"

"── 组1: 零件库索引 ──"
T 'list_standard_parts' { Call 'list_standard_parts' @{ folder="$partsDir" } }

"── 组2: 装配 ──"
T 'open_new_assembly' { Call 'open_new_assembly' @{} }
T 'insert_component(壳体)'  { Call 'insert_component' @{ file_path="$partsDir\主轴壳体_Housing.sldprt" } }
T 'insert_component(刀柄)'  { Call 'insert_component' @{ file_path="$partsDir\刀柄_Holder.sldprt"; x=0.05; y=0; z=0 } }
T 'analyze_assembly'      { Call 'analyze_assembly' @{} }

"── 组3: 配合（需要真实面索引）──"
$fc = $null
$fa = Call 'analyze_assembly' @{}
if($fa.status -eq 'COMPLETED'){
  try{
    $aj = ($fa.cadState.features[0] | ConvertFrom-Json)
    "     组件数 = $($aj.component_count)"
  } catch {}
}
# 配合需要 component+face 索引，先看接口要什么
T 'add_mate(同轴试)' { Call 'add_mate' @{ mate_type='coincident'; a_component='主轴壳体_Housing-1'; a_kind='face'; a_index=0; b_component='刀柄_Holder-1'; b_kind='face'; b_index=0 } }
T 'analyze(配合后)'  { Call 'analyze_assembly' @{} }

"── 组4: BOM ──"
T 'bom_from_assembly' { Call 'bom_from_assembly' @{ } }

"── 组5: 工程图 ──"
T 'open_document(零件)'  { Call 'open_document' @{ file_path="$partsDir\主轴壳体_Housing.sldprt" } }
T 'create_drawing'      { Call 'create_drawing' @{} }
T 'add_drawing_view'    { Call 'add_drawing_view' @{ view_type='front'; pos_x=0.1; pos_y=0.1 } }
T 'export(PDF)'         { Call 'export_document' @{ format='PDF'; file_path="$env:TEMP\api_scan_dwg.pdf" } }
T 'export(DXF)'         { Call 'export_document' @{ format='DXF'; file_path="$env:TEMP\api_scan_dwg.dxf" } }

"── 组6: 打开已有文件 / 文档管理 ──"
T 'open_document(装配)'  { Call 'open_document' @{ file_path="$partsDir\换刀主轴装配_BT30_ATC_Assembly.SLDASM" } }
T 'activate_document'    { Call 'activate_document' @{ title='主轴壳体_Housing.sldprt' } }
T 'close_document'      { Call 'close_document' @{ } }
T 'verify_state'        { Call 'verify_state' @{} }

"`n=== 汇总 ==="
$script:Res | Group-Object Status | ForEach-Object { "  {0,-10} {1}/{2}" -f $_.Name,$_.Count,$script:Res.Count }
$ok=($script:Res|Where-Object{$_.Status -eq 'COMPLETED'}).Count
"  通过率 $ok / $($script:Res.Count)"
$script:Res | Export-Csv -Path "C:\Users\Zegel\solidpilot-mcp\api_scan_results.csv" -NoTypeInformation -Encoding UTF8
