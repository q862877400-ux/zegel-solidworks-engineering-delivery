# SolidWorks 启动 + 弹窗自动清除（2026-09-28）
#
# 为什么要这个：SolidWorks 启动时会弹「工具栏信息不一致，将使用默认工具栏设定」
#   （窗口类 #32770，标题 "SOLIDWORKS Design"）。它是【模态】的：
#   弹出后 COM 连不上（health.comAttached=false），SW 内存卡在 184MB，
#   所有自动化调用全部阻塞。实测关掉它后 5 秒 COM 恢复，内存 184MB→932MB。
#
# 用法：.\start_sw.ps1        启动并等到 COM 就绪（自动清弹窗）
#       .\start_sw.ps1 -Restart 先杀再起
param([switch]$Restart)

$ErrorActionPreference = 'Continue'
[System.Net.WebRequest]::DefaultWebProxy = New-Object System.Net.WebProxy

$sig = @'
using System;using System.Text;using System.Runtime.InteropServices;using System.Collections.Generic;
public class SWWin {
  [DllImport("user32.dll")] static extern bool EnumWindows(EnumProc cb, IntPtr p);
  [DllImport("user32.dll")] static extern int GetWindowText(IntPtr h, StringBuilder s, int n);
  [DllImport("user32.dll")] static extern bool IsWindowVisible(IntPtr h);
  [DllImport("user32.dll")] static extern int GetWindowThreadProcessId(IntPtr h, out int pid);
  [DllImport("user32.dll")] static extern int GetClassName(IntPtr h, StringBuilder s, int n);
  [DllImport("user32.dll")] public static extern IntPtr SendMessage(IntPtr h,uint m,IntPtr w,IntPtr l);
  [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h);
  delegate bool EnumProc(IntPtr h, IntPtr p);
  public static List<string> Dialogs(int target){
    var r=new List<string>();
    EnumWindows((h,p)=>{ int pid; GetWindowThreadProcessId(h,out pid);
      if(pid==target && IsWindowVisible(h)){
        var t=new StringBuilder(512); GetWindowText(h,t,512);
        var c=new StringBuilder(256); GetClassName(h,c,256);
        if(c.ToString()=="#32770") r.Add(h.ToInt64()+"  "+t);
      } return true; }, IntPtr.Zero);
    return r;
  }
}
'@
if(-not ("SWWin" -as [type])){ Add-Type -TypeDefinition $sig }

function Clear-SWDialogs {
  $p = Get-Process SLDWORKS -EA SilentlyContinue
  if(-not $p){ return 0 }
  $n = 0
  foreach($d in [SWWin]::Dialogs($p.Id)){
    $h = [IntPtr][int64]($d -split '\s+')[0]
    [void][SWWin]::SetForegroundWindow($h)
    Start-Sleep -Milliseconds 300
    [void][SWWin]::SendMessage($h, 0x0010, [IntPtr]::Zero, [IntPtr]::Zero)   # WM_CLOSE
    $n++
    Start-Sleep -Milliseconds 500
  }
  return $n
}

if($Restart){
  Get-Process SLDWORKS -EA SilentlyContinue | Stop-Process -Force
  Start-Sleep -Seconds 8
}

$p = Get-Process SLDWORKS -EA SilentlyContinue
if(-not $p){
  "启动 SolidWorks（WMI 派发）..."
  Invoke-CimMethod -ClassName Win32_Process -MethodName Create -Arguments @{
    CommandLine = '"D:\Program Files\SOLIDWORKS Corp\SOLIDWORKS\SLDWORKS.exe"' } | Out-Null
} else { "SolidWorks 已在运行 pid=$($p.Id)" }

"等待就绪（自动清弹窗）..."
$ok = $false
for($i=1; $i -le 90; $i++){
  Start-Sleep -Seconds 4
  $cleared = Clear-SWDialogs
  if($cleared -gt 0){ "  t=$($i*4)s  已关闭 $cleared 个弹窗" }
  $h=$null; try { $h=Invoke-RestMethod "http://localhost:5000/health" -TimeoutSec 8 } catch {}
  $q = Get-Process SLDWORKS -EA SilentlyContinue
  if($h -and $h.comAttached -and $q -and $q.WorkingSet64 -gt 300MB){
    "✅ 就绪 t=$($i*4)s  内存=$([int]($q.WorkingSet64/1MB))MB  累计关弹窗=$cleared"
    $ok = $true; break
  }
}
if(-not $ok){
  $q = Get-Process SLDWORKS -EA SilentlyContinue
  "❌ 未就绪。SW 内存=$([int]($q.WorkingSet64/1MB))MB"
  "  剩余弹窗："
  [SWWin]::Dialogs($q.Id) | ForEach-Object { "    $_" }
  exit 1
}
