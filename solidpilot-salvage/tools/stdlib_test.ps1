. "C:\Users\Zegel\solidpilot-mcp\tools\call.ps1"
# 验证标准件库的真实可用性：能不能把库里的零件真的插进装配
$lib = 'C:\ProgramData\SOLIDWORKS\SOLIDWORKS 2026\design library'
$r = Call 'list_standard_parts' @{ folder=$lib } -TimeoutSec 120
$j = $r.cadState.features[0] | ConvertFrom-Json
"  库统计: 共 $($j.total_sldprt) 个 sldprt"
"  分类: $(($j.by_category.PSObject.Properties | ForEach-Object { "$($_.Name)=$($_.Value)" }) -join ', ')"

Write-Output ""
Write-Output "=== 抽样：每类各取一个，尝试插入装配 ==="
$null = Call 'open_new_assembly' @{}
$byCat = @{}
foreach($p in $j.parts){
  $rel = $p.file -replace [regex]::Escape($lib+'\'),''
  $cat = ($rel -split '\\')[0]
  if(-not $byCat.ContainsKey($cat)){ $byCat[$cat] = $p.file }
}
foreach($cat in ($byCat.Keys | Sort-Object)){
  $f = $byCat[$cat]
  $r2 = Call 'insert_standard_part' @{ file=$f } -TimeoutSec 90
  $mark = if($r2.status -eq 'COMPLETED'){'✅'}else{'❌'}
  $short = ($f -replace [regex]::Escape($lib+'\'),'') -replace '\\[^\\]+$',''
  Write-Output ("  {0} [{1,-18}] {2} {3}" -f $mark, $cat, (Split-Path $f -Leaf), $(if($r2.status -ne 'COMPLETED'){$r2.error.code}else{''}))
}

Write-Output ""
Write-Output "=== 验证：插了几个组件 ==="
$a = Call 'analyze_assembly' @{}
$aj = $a.cadState.features[0] | ConvertFrom-Json
Write-Output "  组件数 = $($aj.component_count)"
$aj.components | ForEach-Object { "    $($_.name)" }
