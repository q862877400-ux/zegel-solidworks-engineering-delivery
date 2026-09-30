# SolidWorks 资源回收（2026-09-28）
# 问题：自动化测试会不断 open_document，服务从不 CloseDoc，
#       COM 包装器不释放 ⇒ SW 私有内存涨到 8.28GB、句柄 4926。
# 依据：CADOverflow "SOLIDWORKS API Memory Access Violation Caused by GDI Object Count
#        and Unreleased COM Objects" —— 他们的解法就是 CloseDoc + ReleaseComObject + GC。
param([switch]$Hard)   # -Hard 连 SolidWorks 进程一起重启

$ErrorActionPreference = 'Continue'
. "C:\Users\Zegel\solidpilot-mcp\tools\call.ps1"

function Show {
  param([string]$tag)
  $p = Get-Process SLDWORKS -EA SilentlyContinue
  if($p){ "  [{0}] 内存={1}MB 私有={2}MB 句柄={3}" -f $tag, [int]($p.WorkingSet64/1MB), [int]($p.PrivateMemorySize64/1MB), $p.HandleCount }
  else { "  [{0}] SolidWorks 未运行" -f $tag }
}

Show "before"

# 1) 关掉所有打开的文档（COM 包装器随之释放）
$closed = 0
for($i=0; $i -lt 40; $i++){
  $r = Call 'close_document' @{ }
  if($r.status -ne 'COMPLETED'){ break }
  $closed++
  Start-Sleep -Milliseconds 250
}
"  已关闭文档数 = $closed"

# 2) 服务端 GC（释放它持有的 RCW）
try { $null = Invoke-RestMethod "http://localhost:5000/verify_state" -TimeoutSec 10 } catch { }

# 3) 清理我测试产生的临时文件
$patterns = @("$env:TEMP\api_*.step", "$env:TEMP\api_*.sldprt", "$env:TEMP\vt.*",
              "$env:TEMP\test1.*", "$env:TEMP\out*.step", "$env:TEMP\out*.stl",
              "$env:TEMP\apisc", "$env:TEMP\new.exe", "$env:TEMP\api_scan2.*")
$freed = 0
foreach($pat in $patterns){
  Get-ChildItem $pat -EA SilentlyContinue | ForEach-Object {
    $freed += $_.Length
    Remove-Item $_.FullName -Recurse -Force -EA SilentlyContinue
  }
}
"  已清理临时文件 $([math]::Round($freed/1KB,1)) KB"

# 4) 可选：连 SW 进程一起重启（只有当内存/句柄仍然很高时才需要）
Start-Sleep -Seconds 2
$p = Get-Process SLDWORKS -EA SilentlyContinue
if($Hard -or ($p -and $p.PrivateMemorySize64 -gt 3GB)){
  if($p){
    "  私有内存过高 ⇒ 重启 SolidWorks"
    Stop-Process -Id $p.Id -Force
    Start-Sleep -Seconds 8
    Invoke-CimMethod -ClassName Win32_Process -MethodName Create -Arguments @{
      CommandLine = '"D:\Program Files\SOLIDWORKS Corp\SOLIDWORKS\SLDWORKS.exe"' } | Out-Null
    for($i=1;$i -le 60;$i++){
      Start-Sleep -Seconds 6
      [System.Net.WebRequest]::DefaultWebProxy = New-Object System.Net.WebProxy
      $h=$null; try { $h=Invoke-RestMethod "http://localhost:5000/health" -TimeoutSec 8 } catch {}
      $q = Get-Process SLDWORKS -EA SilentlyContinue
      if($h -and $h.comAttached -and $q -and $q.WorkingSet64 -gt 300MB){ "  重启就绪 t=$($i*6)s"; break }
    }
  }
} else {
  "  私有内存正常，无需重启 SW"
}

Show "after"
