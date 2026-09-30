# 最终收口盘点：是否真的"没有未测的能力"？
# 三个角度：① 服务端每个方法都被调过吗 ② 每个工具的参数组合覆盖度 ③ 官方接口族的处理状态
$ErrorActionPreference='Continue'
$svc  = "C:\Users\Zegel\solidpilot-mcp\execution\solidworks\SolidworksExecution"
$tc   = "$svc\Controllers\ToolController.cs"
$log  = "C:\Users\Zegel\solidpilot-mcp\api_scan_all.csv"
$all  = Get-Content $log -Raw
$combos = @(
  "C:\Users\Zegel\solidpilot-mcp\param_combos.csv"
  "C:\Users\Zegel\solidpilot-mcp\param_combos2.csv"
  "C:\Users\Zegel\solidpilot-mcp\param_combos3.csv"
  "C:\Users\Zegel\solidpilot-mcp\param_combos4.csv"
  "C:\Users\Zegel\solidpilot-mcp\api_scan_results.csv"
  "C:\Users\Zegel\solidpilot-mcp\api_scan_rest.csv"
  "C:\Users\Zegel\solidpilot-mcp\api_scan_gap.csv"
  "C:\Users\Zegel\solidpilot-mcp\api_scan_untracked.csv"
  "C:\Users\Zegel\solidpilot-mcp\api_silent_audit.csv"
  "C:\Users\Zegel\solidpilot-mcp\api_products.csv"
  "C:\Users\Zegel\solidpilot-mcp\product_availability.csv"
)
$cum = @()
foreach($c in $combos){ if(Test-Path $c){ $cum += (Import-Csv $c) } }
"════ ① 累计实测调用次数 ════"
"  各扫描文件合计 $(($cum|Measure-Object).Count) 条记录"
"  能力矩阵 $(($all -split "`n"|Where-Object{$_ -match ','}).Count) 条"

"`n════ ② 每个已注册工具：是否被真实调用过 ════"
$cases = Select-String -Path $tc -Pattern 'case\s+"(\w+)":' -AllMatches | ForEach-Object { $_.Matches } | ForEach-Object { $_.Groups[1].Value } | Sort-Object -Unique
$hit = @(); $miss = @()
foreach($c in $cases){
  $found = $false
  # 在所有扫描结果里找这个工具名
  foreach($f in $combos){
    if(-not (Test-Path $f)){ continue }
    $txt = Get-Content $f -Raw
    if($txt -match [regex]::Escape($c)){ $found = $true; break }
  }
  if(-not $found -and $all -match [regex]::Escape($c)){ $found = $true }
  if($found){ $hit += $c } else { $miss += $c }
}
"  ✅ 被实测过: $($hit.Count) / $($cases.Count)"
if($miss.Count){ "  ❌ 从未在任何扫描里出现: $($miss -join ', ')" }

"`n════ ③ 服务端方法：有没有一次都没调过的 ════"
$methods = @()
Get-ChildItem $svc -Recurse -Filter *.cs | ForEach-Object {
  Select-String -Path $_.FullName -Pattern 'public ExecutionResponse (\w+)\(|internal ExecutionResponse (\w+)\(' -AllMatches |
    ForEach-Object { $_.Matches } | ForEach-Object {
      if($_.Groups[1].Success){ $methods += $_.Groups[1].Value } else { $methods += $_.Groups[2].Value }
    }
}
$methods = $methods | Sort-Object -Unique
$txtAll = ($all + "`n" + (($cum | ForEach-Object { $_.ToString() }) -join "`n"))
$never = @()
foreach($m in $methods){
  if($txtAll -notmatch [regex]::Escape($m)){ $never += $m }
}
"  服务端方法总数: $($methods.Count)"
if($never.Count -eq 0){
  "  ★ 全部 $($methods.Count) 个方法都在实测记录里出现过"
} else {
  "  ⚠ 未在扫描记录中出现的 ($($never.Count)): $($never -join ', ')"
}

"`n════ ④ 参数组合覆盖 ════"
"  已扫过的参数组合文件: $(($combos | Where-Object {Test-Path $_}).Count) / $($combos.Count)"
"  组合记录合计: $(($cum|Measure-Object).Count) 条"
"  （同一工具的不同参数走不同代码路径，这是'穷尽式覆盖'的真正缺口）"
