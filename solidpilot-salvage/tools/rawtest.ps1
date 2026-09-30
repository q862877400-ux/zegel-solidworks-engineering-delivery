# Raw IDispatch Invoke 单变量测试：每轮重启服务、只发一次 Invoke
# 用法：.\rawtest.ps1 -Elem 0xC -WFlags 1 -RestType 0 -RefGeom 'empty' [-Mesh]
param(
  [int]$Elem = 9, [int]$WFlags = 1, [int]$RestType = 0, [string]$RefGeom = 'empty',
  [switch]$Mesh, [string]$FaceSrc = 'sel', [int]$Faces = 1, [int]$Order = 0,
  [int]$MeshUnits = 0, [double]$MeshElem = 5.0, [string]$RawMode = 'array',
  [string]$Reuse = ''
)$ErrorActionPreference = 'Continue'
$out = & "$env:TEMP\swprobe\build.ps1" 2>&1
if(-not ($out -join "`n").Contains('build+replace OK')){ "BUILD FAILED"; $out | Select-Object -Last 6; exit 1 }
Get-Process SLDWORKS,SolidworksExecution -EA SilentlyContinue | Stop-Process -Force
Start-Sleep -Seconds 8
Invoke-CimMethod -ClassName Win32_Process -MethodName Create -Arguments @{ CommandLine = '"D:\Program Files\SOLIDWORKS Corp\SOLIDWORKS\SLDWORKS.exe"' } | Out-Null
Invoke-CimMethod -ClassName Win32_Process -MethodName Create -Arguments @{ CommandLine = '"C:\Users\Zegel\solidpilot-mcp\execution\solidworks\SolidworksExecution\bin\Debug\SolidworksExecution.exe"' } | Out-Null
for($i=1;$i -le 50;$i++){ Start-Sleep -Seconds 6
  [System.Net.WebRequest]::DefaultWebProxy = New-Object System.Net.WebProxy
  $h=$null; try { $h = Invoke-RestMethod "http://localhost:5000/health" -TimeoutSec 10 } catch {}
  if($h -and $h.comAttached){ break } }
. "C:\Users\Zegel\solidpilot-mcp\tools\call.ps1"
Call 'open_document' @{ file_path = "D:\AI\SW\AI Solidworks\模型\主轴壳体_Housing.sldprt" } | Out-Null
$req = @{ action='solve'; material='AISI 1020'; add_fixture=$true; raw_invoke=$true
          raw_elem=$Elem; raw_wflags=$WFlags; raw_resttype=$RestType; raw_refgeom=$RefGeom
          raw_face_src=$FaceSrc; raw_faces=$Faces; raw_order=$Order; raw_mode=$RawMode }
if($Mesh){ $req['mesh_first']=$true; $req['mesh_units']=$MeshUnits; $req['mesh_elem']=$MeshElem }
if($Reuse){ $req['study_reuse'] = $Reuse }
$trace = "$env:TEMP\rawinvoke_trace.txt"
Remove-Item $trace -EA SilentlyContinue
$r = Call 'topology_optimize' $req -TimeoutSec 500
$tag = "elem=0x$($Elem.ToString('X')) wFlags=$WFlags restType=$RestType ref=$RefGeom src=$FaceSrc nfaces=$Faces order=$(if($Order -eq 0){'DECL'}else{'REV'}) mesh=$([bool]$Mesh)"
if($r.status -ne 'COMPLETED'){
  "$tag => 服务崩溃"
  "  --- 崩溃追踪文件 ---"
  if(Test-Path $trace){ Get-Content $trace | ForEach-Object { "    $_" } } else { "    (无追踪文件)" }
}
else {
  $j = ($r.cadState.features[0] | ConvertFrom-Json)
  $j.log | Where-Object { $_ -match 'RAW-INVOKE|mesh' } | ForEach-Object { "$tag`n   $_" -replace ' \| ',"`n     " }
}
