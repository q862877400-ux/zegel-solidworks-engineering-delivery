# R20：最后 5 条产品线的真实可用性（沿用 R18 三连判据）
# 判据：① 有没有 exe ② CLSID 有没有注册 ③ CoCreateInstance 成不成功
$ErrorActionPreference='Continue'
$swDir = "D:\Program Files\SOLIDWORKS Corp"

$sig = @'
using System;using System.Runtime.InteropServices;
public class L5 { [DllImport("ole32.dll")] public static extern int CoCreateInstance(ref Guid c, IntPtr o, uint ctx, ref Guid i, out IntPtr ppv); }
'@
if(-not ("L5" -as [type])){ Add-Type -TypeDefinition $sig }
$iidUnk = [guid]'00000000-0000-0000-C000-000000000046'

$prods = @(
  @{n='Inspection'; dir='SOLIDWORKS Inspection'; pat='Inspection|Quality|CMM'},
  @{n='Visualize';  dir='SOLIDWORKS Visualize';  pat='Visualize|sldviz|View'},
  @{n='Composer';   dir='SOLIDWORKS Composer';   pat='Composer|slddocmngr'},
  @{n='CAM';        dir='SOLIDWORKS CAM';        pat='^sldcam|cam'},
  @{n='PDM';        dir='SOLIDWORKS PDM';        pat='^PDM|AddInMgr|swvault'}
)

foreach($p in $prods){
  Write-Output "════ $($p.n) ════"
  $d = Join-Path $swDir $p.dir
  if(Test-Path $d){
    # ① exe
    $exes = Get-ChildItem $d -Recurse -Filter "*.exe" -EA SilentlyContinue |
            Where-Object { $_.Name -match $p.pat -and $_.Name -notmatch 'unins|setup|install|update|vcredist' } |
            Select-Object -First 3
    if($exes){ $exes | ForEach-Object { Write-Output "  [exe] $($_.Name)  ($([int]($_.Length/1KB))KB)" } }
    else { Write-Output "  [exe] 无匹配" }
    # ② dll
    $dlls = Get-ChildItem $d -Recurse -Filter "*.dll" -EA SilentlyContinue |
            Where-Object { $_.Name -match $p.pat -and $_.Name -notmatch 'Interop' -and $_.Length -gt 200KB } |
            Select-Object -First 3
    if($dlls){ $dlls | ForEach-Object { Write-Output "  [dll] $($_.Name)  ($([int]($_.Length/1KB))KB)" } }
    # ③ interop
    $ri = Get-ChildItem "D:\Program Files\SOLIDWORKS Corp\SOLIDWORKS\api\redist" -Filter "*.dll" |
          Where-Object { $_.Name -match ($p.n -replace ' ','') }
    if($ri){ $ri | ForEach-Object { Write-Output "  [interop] $($_.Name)" } } else { Write-Output "  [interop] 无" }
  } else { Write-Output "  ❌ 目录不存在: $d" }

  # ④ CLSID 注册（按名字找 ProgID）
  $progids = Get-ChildItem 'HKLM:\SOFTWARE\Classes' -EA SilentlyContinue |
             Where-Object { $_.PSChildName -match "^$($p.n)\." } | Select-Object -First 2
  if($progids){
    foreach($pr in $progids){
      $clsid = (Get-ItemProperty $pr.PSPath -EA SilentlyContinue).'(default)'
      if($clsid -match '\{[0-9A-Fa-f-]+\}'){
        $c = [guid]($clsid -replace '^\{|\}$','')
        $ppv=[IntPtr]::Zero
        $hr = [L5]::CoCreateInstance([ref]$c,[IntPtr]::Zero,5,[ref]$iidUnk,[ref]$ppv)
        $mark = if($hr -eq 0){'✅'}else{'❌'}
        Write-Output "  [COM] $mark ProgID=$($pr.PSChildName)  0x$($hr.ToString('X8'))"
        if($ppv -ne [IntPtr]::Zero){ [void][Runtime.InteropServices.Marshal]::Release($ppv) }
      } else { Write-Output "  [COM] ProgID=$($pr.PSChildName) CLSID=$clsid" }
    }
  } else { Write-Output "  [COM] 无 $p.n.* ProgID" }
  Write-Output ""
}
