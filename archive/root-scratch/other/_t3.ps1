
param([string]$Dll)
Add-Type -AssemblyName System.Reflection
$asm = [System.Reflection.Assembly]::LoadFrom($Dll)
foreach($t in ($asm.GetTypes() | Sort-Object Name)){
  if($t.IsInterface){ "I  " + $t.Name }
  elseif($t.IsEnum){ "E  " + $t.Name }
}
