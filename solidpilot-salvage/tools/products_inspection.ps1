# R20 续：Inspection（目标明确列出、已装 66MB）的 COM 可用性
# 我上一步读 ProgID 的 "(默认)" 拿到的是 ProgID 字符串本身；CLSID 在它的 CLSID 子键。
$ErrorActionPreference='Continue'
$sig = @'
using System;using System.Runtime.InteropServices;
public class IN { [DllImport("ole32.dll")] public static extern int CoCreateInstance(ref Guid c, IntPtr o, uint ctx, ref Guid i, out IntPtr ppv); }
'@
if(-not ("IN" -as [type])){ Add-Type -TypeDefinition $sig }
$iidUnk = [guid]'00000000-0000-0000-C000-000000000046'

Write-Output "=== ① Inspection 的 ProgID → CLSID 解析 ==="
foreach($pid_ in 'Inspection.BalloonSettingManager','Inspection.BalloonSettingsImpl'){
  $k = "HKLM:\SOFTWARE\Classes\$pid_"
  if(Test-Path $k){
    $clsid = (Get-ItemProperty "$k\CLSID" -EA SilentlyContinue).'(default)'
    Write-Output "  $pid_ → CLSID=$clsid"
    if($clsid -match '\{'){
      $c = [guid]($clsid -replace '[\{\}]','')
      $ppv=[IntPtr]::Zero
      $hr = [IN]::CoCreateInstance([ref]$c,[IntPtr]::Zero,5,[ref]$iidUnk,[ref]$ppv)
      $mark = if($hr -eq 0){'✅ 成功'}else{'❌'}
      Write-Output "     CoCreateInstance = $mark  0x$($hr.ToString('X8'))"
      if($ppv -ne [IntPtr]::Zero){ [void][Runtime.InteropServices.Marshal]::Release($ppv) }
      $k2 = "HKLM:\SOFTWARE\Classes\CLSID\$clsid"
      if(Test-Path "$k2\InprocServer32"){
        Write-Output "     实现 = $((Get-ItemProperty "$k2\InprocServer32").'(default)')"
      }
    }
  } else { Write-Output "  $pid_ 未注册" }
}

Write-Output ""
Write-Output "=== ② Inspection 目录下所有 CLSID 键（找真正入口）==="
$n = 0
Get-ChildItem 'HKLM:\SOFTWARE\Classes\CLSID' -EA SilentlyContinue | ForEach-Object {
  $d = (Get-ItemProperty $_.PSPath -EA SilentlyContinue).'(default)'
  $inp = (Get-ItemProperty "$($_.PSPath)\InprocServer32" -EA SilentlyContinue).'(default)'
  if($inp -and $inp -match 'Inspection'){
    $n++
    if($n -le 5){ Write-Output "  {$($_.PSChildName -replace '^\{|\}$','')}  $d" }
  }
}
Write-Output "  Inspection 相关 CLSID 共 $n 个"

Write-Output ""
Write-Output "=== ③ Visualize / Composer：是不是只有目录壳？==="
foreach($p in 'SOLIDWORKS Visualize','SOLIDWORKS Composer','SOLIDWORKS Composer Player'){
  $d = "D:\Program Files\SOLIDWORKS Corp\$p"
  if(Test-Path $d){
    $files = Get-ChildItem $d -Recurse -File -EA SilentlyContinue
    $exes = ($files | Where-Object { $_.Extension -eq '.exe' }).Count
    $sz = [math]::Round((($files | Measure-Object Length -Sum).Sum)/1MB,1)
    Write-Output "  $p : 共 $($files.Count) 个文件 / exe $exes 个 / $([int]$sz)MB"
    $files | Where-Object { $_.Extension -eq '.exe' } | Select-Object -First 2 | ForEach-Object { Write-Output "      $($_.Name)" }
  } else { Write-Output "  $p : 目录不存在" }
}
