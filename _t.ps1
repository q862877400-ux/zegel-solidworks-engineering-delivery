
param([string]$Dll)
Add-Type -AssemblyName System.Reflection
$asm = [System.Reflection.Assembly]::LoadFrom($Dll)
$i=0; $e=0; $c=0
foreach($t in $asm.GetTypes()){
  if($t.IsInterface){$i++} elseif($t.IsEnum){$e++} else {$c++}
}
"$i interfaces, $e enums, $c classes"
