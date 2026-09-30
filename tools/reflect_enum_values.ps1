param(
    [string]$Dll = 'D:\Program Files\SOLIDWORKS Corp\SOLIDWORKS\api\redist\SolidWorks.Interop.swconst.dll',
    [string[]]$Enum = @(),
    [string]$Out = ''
)
# 读官方 interop 程序集的枚举**字面值**（纯元数据读取，不是实测）。
#
# ⚑ 为什么用 LoadFrom 而不是 ReflectionOnlyLoadFrom：
#   `ReflectionOnlyLoadFrom` 在 .NET Core / PowerShell 7 上直接抛
#   "Reflection only loading is not supported on this platform"。
#   早先 `reflect-enum.ps1` 用的正是它，**静默产出 0 行的空文件**
#   （本机实测：enum_sldworks.txt 只有 38 字节）⇒ 枚举数值一直缺，
#   根因在这里，不是「官方没给值」。
$ErrorActionPreference = 'Stop'
$asm = [System.Reflection.Assembly]::LoadFrom($Dll)
$lines = New-Object System.Collections.Generic.List[string]
$lines.Add("# 来源: $Dll")
$lines.Add("# 方法: 对官方 interop 程序集的纯元数据读取（非实测）")
foreach ($t in $asm.GetTypes()) {
    if (-not $t.IsEnum) { continue }
    if ($Enum.Count -gt 0 -and ($Enum -notcontains $t.Name)) { continue }
    $lines.Add("## $($t.Name)")
    foreach ($n in [Enum]::GetNames($t)) {
        $v = [System.Convert]::ToInt64([Enum]::Parse($t, $n))
        $lines.Add("    $n = $v")
    }
}
$text = $lines -join "`n"
if ($Out) {
    [System.IO.File]::WriteAllText($Out, $text, [System.Text.UTF8Encoding]::new($false))
    "written: $Out ($($lines.Count) lines)"
} else {
    $text
}
