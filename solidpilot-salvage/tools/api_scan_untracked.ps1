. "C:\Users\Zegel\solidpilot-mcp\tools\call.ps1"
# 终检发现 11 项 UNTRACKED。大部分我其实测过，只是矩阵命名对不上。
# 这里【真调用一次】留证，并核对几何/返回，给矩阵补齐。
$parts  = "D:\AI\SW\AI Solidworks\模型"
$stdDir = "D:\AI\SW\AI Solidworks\设计\标准件"
$ErrorActionPreference='Continue'
$R = New-Object System.Collections.ArrayList
function T { param([string]$N,[scriptblock]$A)
  $st='ERR'; $m=''
  try{ $r=&$A; $st=$r.status
       if($st -ne 'COMPLETED'){ $m="$($r.error.code)" }
       else { $f=$r.cadState.features; $m=if($f -and $f.Count){ (($f[0] -replace '\s+',' ').Substring(0,[Math]::Min(72,($f[0] -replace '\s+',' ').Length))) }else{'ok'} } }
  catch{ $st='THROW'; $m=($_.Exception.Message -replace '\s+',' ') }
  [void]$R.Add([pscustomobject]@{Name=$N;Status=$st;Msg=$m})
  $mk=switch($st){'COMPLETED'{'✅'}'THROW'{'💥'}default{'❌'}}
  "  $mk $N  $m"
}

Write-Output "=== 补测 11 项 UNTRACKED ==="

T 'activate_document'   { $null = Call 'open_document' @{ file_path="$parts\刀柄_Holder.sldprt" }
                            Call 'activate_document' @{ title='主轴壳体_Housing.sldprt' } }
T 'close_document'      { Call 'close_document' @{ } }

# 工程图系列：先建图（本机 add_drawing_view 失败，所以这 5 个都可能连带失败）
T 'create_drawing'        { Call 'create_drawing' @{ model_path="$parts\主轴壳体_Housing.sldprt" } }
T 'add_drawing_view'      { Call 'add_drawing_view' @{ view_type='front'; pos_x=0.1; pos_y=0.1 } }
T 'add_section_view'      { Call 'add_section_view' @{ px=0.15; py=0.15; x1=0.10; y1=0.05; x2=0.10; y2=0.20 } }
T 'add_drawing_dimension' { Call 'add_drawing_dimension' @{ px=0.12; py=0.12; value=0.1 } }
T 'add_hole_callout'      { Call 'add_hole_callout' @{ px=0.12; py=0.12 } }
T 'auto_dimension_drawing'{ Call 'auto_dimension_drawing' @{ all_views=$true } }
T 'auto_center_marks'     { Call 'auto_center_marks' @{ } }
T 'analyze_slddrw_test'   { Call 'analyze_slddrw_test' @{ include_relations=$true } }
T 'add_flat_pattern_view' { Call 'add_flat_pattern_view' @{ pos_x=0.15; pos_y=0.15 } }

# 关闭工程图，回到零件
Call 'close_document' @{ } | Out-Null

# insert_standard_part（用已转好的 SLDPRT）
T 'open_new_assembly'   { Call 'open_new_assembly' @{} }
T 'insert_standard_part' { Call 'insert_standard_part' @{ file="$stdDir\平垫圈_M12_ISO7089.SLDPRT" } }
T '  验证组件数'        { Call 'analyze_assembly' @{} }

# topology_optimize（已知 add-in 不稳，只验 probe 入口通不通）
T 'topology_optimize(probe)' { Call 'topology_optimize' @{ action='probe' } }

Write-Output ""
Write-Output "=== 汇总 ==="
$R | Group-Object Status | ForEach-Object { "  {0,-10} {1}/{2}" -f $_.Name,$_.Count,$R.Count }
$R | Export-Csv -Path "C:\Users\Zegel\solidpilot-mcp\api_scan_untracked.csv" -NoTypeInformation -Encoding UTF8
