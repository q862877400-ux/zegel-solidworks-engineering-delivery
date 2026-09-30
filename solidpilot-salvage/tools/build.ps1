# 重编执行层并重启服务（手册 §七 配方）。
# 关键：必须用 WMI 派发新进程，否则它落在宿主的 kill-on-close Job object 里，
# 下次宿主重启会把它一起带走（本项目已因此白跑两次）。
param([switch]$SkipBuild)

$proj = "C:\Users\Zegel\solidpilot-mcp\execution\solidworks\SolidworksExecution"
$bin  = "$proj\bin\Debug"
$exe  = "$bin\SolidworksExecution.exe"
$ref  = "$env:TEMP\swref"

if(-not $SkipBuild){
  $csc = "C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\MSBuild\Current\Bin\Roslyn\csc.exe"
  New-Item -ItemType Directory -Force -Path $ref | Out-Null
  foreach($n in 'sldworks','swconst','swpublished'){
    Copy-Item "D:\Program Files\SOLIDWORKS Corp\SOLIDWORKS\api\redist\SolidWorks.Interop.$n.dll" $ref -Force }
  $src  = Get-ChildItem $proj -Recurse -Filter *.cs | Where-Object { $_.FullName -notmatch '\\obj\\|\\bin\\' } | ForEach-Object { $_.FullName }
  $refs = @('/r:System.dll','/r:System.Core.dll','/r:System.Net.Http.dll','/r:Microsoft.CSharp.dll')
  $refs += (Get-ChildItem $bin -Filter *.dll | Where-Object { $_.Name -match 'Owin|Newtonsoft|System\.(Net\.Http\.Formatting|Web\.Http)' } | ForEach-Object { "/r:$($_.FullName)" })
  $refs += (Get-ChildItem $ref -Filter *.dll | ForEach-Object { "/r:$($_.FullName)" })
  & $csc (@('/nologo','/target:exe','/platform:anycpu','/debug:full','/langversion:latest',"/out:$env:TEMP\new.exe") + $refs + $src)
  if($LASTEXITCODE -ne 0){ throw "csc FAILED ($LASTEXITCODE) — exe NOT replaced" }
  Get-Process SolidworksExecution -EA SilentlyContinue | Stop-Process -Force
  Start-Sleep -Seconds 3
  Copy-Item "$env:TEMP\new.exe" $exe -Force
  "build+replace OK ($((Get-Item $exe).Length) bytes)"
} else {
  Get-Process SolidworksExecution -EA SilentlyContinue | Stop-Process -Force
  Start-Sleep -Seconds 3
}

$r = Invoke-CimMethod -ClassName Win32_Process -MethodName Create -Arguments @{ CommandLine = "`"$exe`"" }
"WMI launch -> ReturnValue=$($r.ReturnValue) pid=$($r.ProcessId)"
Start-Sleep -Seconds 6
[System.Net.WebRequest]::DefaultWebProxy = New-Object System.Net.WebProxy
try { Invoke-RestMethod "http://localhost:5000/health" -TimeoutSec 25 | ConvertTo-Json -Depth 4 -Compress }
catch { "HEALTH ERR: $($_.Exception.Message)" }
