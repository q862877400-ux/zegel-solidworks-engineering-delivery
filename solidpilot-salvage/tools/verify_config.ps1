. "C:\Users\Zegel\solidpilot-mcp\tools\call.ps1"
$parts = "D:\AI\SW\AI Solidworks\模型"
Write-Output "=== config 校验验证（正常路径必须仍然成功）==="
foreach($c in @(
  @{n='不传 config';      p=@{}},
  @{n='config=默认';       p=@{config='默认'}},
  @{n='config=空串';       p=@{config=''}},
  @{n='config=不存在名';    p=@{config='NoSuchConfig_不存在'}}
)){
  $null = Call 'open_new_assembly' @{}
  $r = Call 'insert_component' (@{file_path="$parts\主轴壳体_Housing.sldprt"} + $c.p) -TimeoutSec 90
  $n = ''
  if($r.status -eq 'COMPLETED'){
    $a = (Call 'analyze_assembly' @{}).cadState.features[0]|ConvertFrom-Json
    if($a.components.Count){ $n = $a.components[0].name }
  }
  $mark = if($r.status -eq 'COMPLETED'){'✅'}else{'❌'}
  Write-Output ("  {0} {1,-18} {2}" -f $mark, $c.n, $(if($r.status -eq 'COMPLETED'){"插入成功 $n"}else{"$($r.error.code)"}))
  if($r.status -ne 'COMPLETED'){
    $m = $r.error.message -replace '\s+',' '
    Write-Output ("        └─ {0}" -f $m.Substring(0,[Math]::Min(150,$m.Length)))
  }
}
""
"=== 回归：insert_component 核心能力未被破坏 ==="
$null = Call 'open_new_assembly' @{}
$null = Call 'insert_component' @{ file_path="$parts\主轴壳体_Housing.sldprt" }
$null = Call 'insert_component' @{ file_path="$parts\刀柄_Holder.sldprt"; x=0.05; y=0; z=0 }
$a = Call 'analyze_assembly' @{}
$j = $a.cadState.features[0]|ConvertFrom-Json
"  双组件插入: $($j.component_count) 个"
"  组件列表: $(($j.components | ForEach-Object { $_.name }) -join ', ')"
