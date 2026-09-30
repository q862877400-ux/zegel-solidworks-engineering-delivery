. "C:\Users\Zegel\solidpilot-mcp\tools\call.ps1"
# ★ 用 list_standard_parts 返回的【真实路径】，不要自己拼（前两次失败都是路径拼错）
$lib = 'C:\ProgramData\SOLIDWORKS\SOLIDWORKS 2026\design library'
$asm = 'D:\AI\SW\AI Solidworks\模型\换刀主轴装配_BT30_ATC_Assembly.SLDASM'
$r = Call 'list_standard_parts' @{ folder=$lib } -TimeoutSec 120
$j = $r.cadState.features[0] | ConvertFrom-Json
Write-Output "库内零件 $($j.parts.Count) 个"
Write-Output ""
Write-Output "=== 真实路径抽样 + 文件存在性 ==="
$byCat = @{}
foreach($p in $j.parts){
  $rel = $p.file -replace [regex]::Escape($lib+'\'),''
  $cat = ($rel -split '\\')[0]
  if(-not $byCat.ContainsKey($cat)){ $byCat[$cat] = $p }
}
foreach($cat in ($byCat.Keys | Sort-Object)){
  $f = $byCat[$cat].file
  $ex = Test-Path $f
  $sz = if($ex){ [int]((Get-Item $f).Length/1KB) }else{ -1 }
  Write-Output ("  [{0,-18}] 存在={1,-5} {2,5}KB  {3}" -f $cat, $ex, $sz, (Split-Path $f -Leaf))
}

Write-Output ""
Write-Output "=== 逐个尝试：open → insert_standard_part ==="
$ok = 0; $tried = 0
foreach($cat in ($byCat.Keys | Sort-Object)){
  $f = $byCat[$cat].file
  $null = Call 'open_document' @{ file_path=$f } -TimeoutSec 90
  $o = Call 'verify_state' @{}
  $docOk = $o.cadState.activeDocument
  $null = Call 'open_document' @{ file_path=$asm }
  $r2 = Call 'insert_standard_part' @{ file=$f } -TimeoutSec 90
  $tried++
  $mark = if($r2.status -eq 'COMPLETED'){'✅'; $ok++}else{'❌'}
  Write-Output ("  {0} [{1,-18}] open→{2,-42} insert={3}" -f $mark, $cat, $(if($docOk){$docOk}else{'(未打开)'}), $(if($r2.status -ne 'COMPLETED'){$r2.error.code}else{'OK'}))
}
Write-Output "  ⇒ $ok / $tried 成功"

$a = Call 'analyze_assembly' @{}
$aj = $a.cadState.features[0] | ConvertFrom-Json
Write-Output "  装配组件数 = $($aj.component_count)"
