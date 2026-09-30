. "C:\Users\Zegel\solidpilot-mcp\tools\call.ps1"
# R19 修正：insert_standard_part 必须在【从磁盘打开的既有装配】里用（R7 已发现，我上一步又踩了）
$lib = 'C:\ProgramData\SOLIDWORKS\SOLIDWORKS 2026\design library'
$asm = 'D:\AI\SW\AI Solidworks\模型\换刀主轴装配_BT30_ATC_Assembly.SLDASM'
$r = Call 'list_standard_parts' @{ folder=$lib } -TimeoutSec 120
$j = $r.cadState.features[0] | ConvertFrom-Json

Write-Output "=== 在【既有装配】里插入各类标准件 ==="
$byCat = @{}
foreach($p in $j.parts){
  $rel = $p.file -replace [regex]::Escape($lib+'\'),''
  $cat = ($rel -split '\\')[0]
  if(-not $byCat.ContainsKey($cat)){ $byCat[$cat] = $p.file }
}
$okCount = 0
foreach($cat in ($byCat.Keys | Sort-Object)){
  $f = $byCat[$cat]
  $null = Call 'open_document' @{ file_path=$asm }        # ★ 打开既有装配
  $r2 = Call 'insert_standard_part' @{ file=$f } -TimeoutSec 90
  $mark = if($r2.status -eq 'COMPLETED'){'✅'}else{'❌'}
  if($r2.status -eq 'COMPLETED'){ $okCount++ }
  Write-Output ("  {0} [{1,-18}] {2,-40} {3}" -f $mark, $cat, (Split-Path $f -Leaf), $(if($r2.status -ne 'COMPLETED'){$r2.error.code}else{''}))
}
Write-Output "  ⇒ $okCount / $($byCat.Count) 类插入成功"

Write-Output ""
Write-Output "=== 验证装配里的组件数 ==="
$a = Call 'analyze_assembly' @{}
$aj = $a.cadState.features[0] | ConvertFrom-Json
Write-Output "  组件数 = $($aj.component_count)  (插入前是 11)"
$new = $aj.components | Select-Object -Last 4
$new | ForEach-Object { "    $($_.name)" }
& "C:\Users\Zegel\solidpilot-mcp\tools\reclaim.ps1" 2>&1 | Select-Object -Last 2
