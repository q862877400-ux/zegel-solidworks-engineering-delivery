# ─────────────────────────────────────────────────────────────────────
# 用途：对 SolidWorks interop DLL 做纯元数据反射，产出官方接口清单。
# 定位：读官方程序集（铁律 2 允许 —— 不是实测、不碰 SolidWorks 进程、
#       不执行任何 COM 调用、不编译 csc/msbuild）。
# 覆盖：C:\swapi 完全没有的域 13/14 程序集。
# 用法：pwsh -File reflect-interop.ps1 -Out <目录>
# ─────────────────────────────────────────────────────────────────────
param(
  # ⚑⚑ 顺序要紧：``$Targets`` 必须在 ``$Out`` **之前**。
  #   否则 PowerShell 把 `-Targets a b c` 里多出来的值按位置绑到第一个参数
  #   （也就是 $Out）上 —— 本轮就因此只反射了第一个程序集，
  #   并且把 $Out 覆写成 "swpublished"，最后一行打印成 `OK -> swpublished`。
  [string[]]$Targets = @(),
  [string]$Out = 'D:\AI\SW\_raw\reflect'
)
$ErrorActionPreference = 'Stop'
$redist = 'D:\Program Files\SOLIDWORKS Corp\SOLIDWORKS\api\redist'

# 目标：sw_know.py verify 报「库中无此类型」的域 13/14 对应程序集
if (-not $Targets -or $Targets.Count -eq 0) {
  $Targets = @(
    'cosworks','SWRoutingLib','sldcostingapi','fworks',
    'sustainability','swdocumentmgr','swmotionstudy'
  )
}

New-Item -ItemType Directory -Force -Path $Out | Out-Null

# 依赖解析：interop DLL 互相引用，统一在 redist 目录里找
$handler = [System.ResolveEventHandler]{
  param($s,$e)
  $n = (New-Object System.Reflection.AssemblyName($e.Name)).Name
  $p = Join-Path $redist "SolidWorks.Interop.$n.dll"
  if (Test-Path $p) { return [System.Reflection.Assembly]::LoadFrom($p) }
  return $null
}
[System.AppDomain]::CurrentDomain.add_AssemblyResolve($handler)

foreach ($t in $Targets) {
  $dll = Join-Path $redist "SolidWorks.Interop.$t.dll"
  if (-not (Test-Path $dll)) { Write-Host "SKIP $t (no dll)"; continue }
  try {
    $asm = [System.Reflection.Assembly]::LoadFrom($dll)
  } catch {
    # ⚑ 单个程序集加载失败**不许中断整轮** —— 早先 $ErrorActionPreference='Stop'
    #   让它直接终止，于是后面所有程序集一个都没处理，调用方只看到「文件不存在」。
    Write-Host ("FAIL {0,-16} 加载失败: {1}" -f $t, $_.Exception.Message)
    continue
  }

  # ⚑⚑ `$asm.GetTypes()` 只要**有一个**类型加载不了就抛 ReflectionTypeLoadException。
  #   实测 7 个程序集都栽在这（swdimxpert 102 接口 / swpublished 62 / …）——
  #   表现为「脚本说 0 接口」，实际接口都在。
  #   ⇒ 捕获后改用异常里**已经成功加载的那部分**类型，
  #     并在文件头**显式记下有几个类型没加载**，让「没读到」和「确实没有」可区分。
  $types = $null; $loadFailed = 0
  try {
    $types = $asm.GetTypes()
  } catch [System.Reflection.ReflectionTypeLoadException] {
    $types = $_.Exception.Types | Where-Object { $null -ne $_ }
    $loadFailed = $_.Exception.LoaderExceptions.Count
    Write-Host ("PARTIAL {0,-14} {1} 个类型未加载，已用其余 {2} 个继续" -f $t, $loadFailed, $types.Count)
  } catch {
    Write-Host ("FAIL {0,-16} 取类型失败: {1}" -f $t, $_.Exception.Message)
    continue
  }

  $ifaces = @($types | Where-Object { $_.IsInterface -and $_.IsPublic })
  $enums  = @($types | Where-Object { $_.IsEnum -and $_.IsPublic })
  $cls    = @($types | Where-Object { $_.IsClass -and $_.IsPublic -and -not $_.IsEnum })

  $memberCount = 0
  foreach ($i in $ifaces) { $memberCount += $i.GetMembers().Count }

  $note = ''
  if ($loadFailed -gt 0) { $note = "  [$loadFailed types not loaded]" }
  Write-Host ("{0,-16} ifaces={1,-5} enums={2,-5} classes={3,-4} members={4}{5}" -f $t, $ifaces.Count, $enums.Count, $cls.Count, $memberCount, $note)

  # ---- 接口清单：每个方法一行，含返回类型/参数类型顺序（步骤 4 签名比对表要用）
  $lines = [System.Collections.Generic.List[string]]::new()
  $lines.Add("# 反射清单 :: $($asm.GetName().Name) $($asm.GetName().Version)")
  $lines.Add("# 由 reflect-interop.ps1 生成 —— 纯元数据枚举，未实例化任何 COM 对象。")
  $lines.Add("# 格式：<接口> :: <返回类型> <方法名>(<参数类型>, ...)")
  # ⚑ 把「这次读全了没有」写进文件头 —— 否则「没读到」与「确实没有」无法区分，
  #   而本任务已经因此把 212 个接口误判成不存在。
  $state = 'complete'
  if ($loadFailed -gt 0) { $state = "partial: $loadFailed types not loaded" }
  $lines.Add("# read-status: $state")
  $lines.Add('')
  foreach ($i in ($ifaces | Sort-Object Name)) {
    $lines.Add("## $($i.Name)")
    foreach ($m in ($i.GetMethods() | Sort-Object Name)) {
      $ps = ($m.GetParameters() | ForEach-Object { $_.ParameterType.Name }) -join ', '
      $lines.Add("  $($m.ReturnType.Name) $($m.Name)($ps)")
    }
    $lines.Add('')
  }
  Set-Content -Encoding UTF8 (Join-Path $Out "iface_$t.txt") $lines

  # ---- 枚举清单：官方枚举值不许猜，必须落盘
  $elines = [System.Collections.Generic.List[string]]::new()
  $elines.Add("# 枚举清单 :: $($asm.GetName().Name)")
  foreach ($e in ($enums | Sort-Object Name)) {
    $elines.Add("## $($e.Name)")
    foreach ($f in [System.Enum]::GetNames($e)) {
      $elines.Add("  $f = $([int][System.Enum]::Parse($e,$f))")
    }
    $elines.Add('')
  }
  Set-Content -Encoding UTF8 (Join-Path $Out "enum_$t.txt") $elines
}

[System.AppDomain]::CurrentDomain.remove_AssemblyResolve($handler)
Write-Host "OK -> $Out"
