# 终检：把服务端每个 ExecutionResponse 方法，与我的能力矩阵逐条对账
# 目的：证明"穷尽式覆盖"真的做到了（目标验收条件之一）
$svc = "C:\Users\Zegel\solidpilot-mcp\execution\solidworks\SolidworksExecution"
$log = "C:\Users\Zegel\solidpilot-mcp\api_scan_all.csv"

# 1) 服务端所有方法
$caps = @()
Get-ChildItem $svc -Recurse -Filter *.cs | ForEach-Object {
  Select-String -Path $_.FullName -Pattern 'public\s+ExecutionResponse\s+(\w+)\s*\(|internal\s+ExecutionResponse\s+(\w+)\s*\(' -AllMatches |
    ForEach-Object { $_.Matches } | ForEach-Object {
      if($_.Groups[1].Success){ $caps += $_.Groups[1].Value } else { $caps += $_.Groups[2].Value }
    }
}
$caps = $caps | Sort-Object -Unique
Write-Output "服务端 ExecutionResponse 方法 = $($caps.Count) 个"

# 2) 工具名（ToolController 注册的 case）映射到方法
$tc = "C:\Users\Zegel\solidpilot-mcp\execution\solidworks\SolidworksExecution\Controllers\ToolController.cs"
$cases = Select-String -Path $tc -Pattern 'case\s+"(\w+)":\s*return\s+_service\.(\w+)\(' -AllMatches |
  ForEach-Object { $_.Matches } | ForEach-Object {
    [pscustomobject]@{ Tool=$_.Groups[1].Value; Method=$_.Groups[2].Value }
  }
Write-Output "ToolController 已注册 case = $($cases.Count) 个"
""
Write-Output "=== 逐条对账：工具 → 服务方法 → 矩阵状态 ==="
$d = Import-Csv $log
$rows = @()
foreach($c in $cases){
  $row = $d | Where-Object { $_.Name -like "*$($c.Tool)*" -or $_.Name -like "*$($c.Method)*" } | Select-Object -First 1
  $status = if($row){ $row.Result } else { 'UNTRACKED' }
  $rows += [pscustomobject]@{ Tool=$c.Tool; Method=$c.Method; Result=$status }
}
$rows | Sort-Object Result, Tool | ForEach-Object { "  {0,-26} {1,-22} {2}" -f $_.Tool, $_.Method, $_.Result }
""
Write-Output "=== 覆盖统计 ==="
$rows | Group-Object { if($_.Result -like 'OK*'){'OK'} elseif($_.Result -like 'UNTRACKED*'){'UNTRACKED'} else {'OTHER'} } |
  ForEach-Object { "  {0,-12} {1} 个" -f $_.Name, $_.Count }
""
$un = $rows | Where-Object { $_.Result -eq 'UNTRACKED' }
if($un.Count){
  Write-Output "=== ⚠ 未纳入矩阵的工具（需补测）==="
  $un | ForEach-Object { "  $($_.Tool) → $($_.Method)" }
} else {
  Write-Output "  ★ 所有已注册工具都已纳入矩阵，无遗漏"
}
# 有些服务方法没有对应 case（内部用）
$internal = $caps | Where-Object { $n = $_; -not ($cases | Where-Object { $_.Method -eq $n }) }
if($internal){
  Write-Output ""
  Write-Output "=== 内部方法（无 case 入口，供其它方法内部调用）==="
  $internal | ForEach-Object { "  $_" }
}
