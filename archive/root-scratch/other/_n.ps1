
param([string]$Dll)
Add-Type -AssemblyName System.Reflection
try { $asm = [System.Reflection.Assembly]::LoadFrom($Dll) } catch { "ERR 0 0"; exit }
$i=0
foreach($t in $asm.GetTypes()){ if($t.IsInterface){$i++} }
"$i"
