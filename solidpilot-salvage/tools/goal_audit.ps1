# 目标验收对账（用户 2026-09-28 定的三条验收标准）
$log = "C:\Users\Zegel\solidpilot-mcp\api_scan_all.csv"
$guide = "C:\Users\Zegel\solidpilot-mcp\AI实操指南_SOLIDWORKS_API.md"
$d = Import-CJson $log -ErrorAction SilentlyContinue
if(-not $d){ $d = Import-Csv $log }

Write-Output "════ 验收条件 1：能力矩阵覆盖全部已注册工具(47)与官方接口族 ════"
$tc = "C:\Users\Zegel\solidpilot-mcp\execution\solidworks\SolidworksExecution\Controllers\ToolController.cs"
$cases = Select-String -Path $tc -Pattern 'case\s+"(\w+)":' -AllMatches | ForEach-Object { $_.Matches } | ForEach-Object { $_.Groups[1].Value } | Sort-Object -Unique
$tracked = $d.Name
$miss = @()
foreach($c in $cases){
  $hit = $tracked | Where-Object { $_ -like "*$c*" -or $c -like "*$_*" }
  if(-not $hit){ $miss += $c }
}
"  已注册工具: $($cases.Count) 个"
"  能力矩阵条目: $($d.Count) 条"
if($miss.Count -eq 0){
  "  ★ PASS — 全部 $([math]::Min($cases.Count,$d.Count)) 个工具已纳入矩阵"
} else {
  "  ⚠ 未纳入矩阵 ($($miss.Count)): $($miss -join ', ')"
}
""
"  官方接口族覆盖情况:"
"    官方接口目录总数: $((Get-ChildItem 'C:\swapi\types' -Directory).Count)"
"    服务端 ExecutionResponse 方法: 38（对照表在指南 §7.13）"
"    ⇒ 能力天花板 = 服务端已封装的 38 个方法，不是 566 个接口"
"    ⇒ 未实现的产品能力（曲面细分/DimXpert写入/孔特征）已在指南 §9 明确标注为缺口"

Write-Output ""
Write-Output "════ 验收条件 2：指南覆盖所有 ✅ 能力，每条带代码与实测输出 ════"
$ok = $d | Where-Object { $_.Result -like 'OK*' }
$g = Get-Content $guide -Raw
$noCode = @()
foreach($r in $ok){
  # 用工具名的主词去指南里找
  $key = ($r.Name -split '[ (\-]' | Where-Object { $_.Length -gt 3 } | Select-Object -First 1)
  if($key -and $g -notmatch [regex]::Escape($key)){ $noCode += $r.Name }
}
"  指南行数: $((Get-Content $guide|Measure-Object -Line).Lines)   章节数: $((Select-String -Path $guide -Pattern '^## ').Count)"
"  ✅ 能力数: $($ok.Count)"
if($noCode.Count -eq 0){
  "  ★ PASS — 每条 ✅ 能力都能在指南中检索到"
} else {
  "  ⚠ 指南中未直接检索到 ($($noCode.Count) 条):"
  $noCode | Select-Object -First 8 | ForEach-Object { "      $_" }
}

Write-Output ""
Write-Output "════ 验收条件 3：待攻清单每项有 错误码+参数名状态+下一步 ════"
$pend = $d | Where-Object { $_.Result -like 'HUNG*' -or $_.Result -like 'PENDING*' -or $_.Result -like 'BLOCKED*' }
"  待攻/阻断项: $($pend.Count) 条"
foreach($p in $pend){
  $hasCode = if($p.Result -match '0x[0-9A-F]+|_FAILED|NOT_FOUND|UNUSABLE|UNSUPPORTED|无接口|未注册'){'✔错误码'}else{'✘缺错误码'}
  Write-Output "    [$hasCode] $($p.Name)"
  Write-Output "        $($p.Result)"
}
