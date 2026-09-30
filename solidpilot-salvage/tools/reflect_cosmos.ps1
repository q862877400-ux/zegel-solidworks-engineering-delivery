param([string]$TypeName)
$dll = "D:\Program Files\SOLIDWORKS Corp\SOLIDWORKS\api\redist\SolidWorks.Interop.cosworks.dll"
$a = [System.Reflection.Assembly]::LoadFrom($dll)
$t = $a.GetType("SolidWorks.Interop.cosworks.$TypeName")
if(-not $t){ "TYPE NOT FOUND: $TypeName"; exit 1 }
"=== $TypeName ==="
$t.GetMembers() | Where-Object { $_.MemberType -in 'Method','Property' } | ForEach-Object {
  if($_.MemberType -eq 'Property'){ "  P {0,-36} {1}" -f $_.Name, $_.PropertyType.Name }
  else { "  M {0}({1}) -> {2}" -f $_.Name, (($_.GetParameters() | ForEach-Object { "$($_.ParameterType.Name) $($_.Name)" }) -join ', '), $_.ReturnType.Name }
}
