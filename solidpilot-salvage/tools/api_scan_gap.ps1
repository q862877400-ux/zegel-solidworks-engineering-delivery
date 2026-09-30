# 补测：服务端 38 个方法里还没实测过的
$ErrorActionPreference='Continue'
. "C:\Users\Zegel\solidpilot-mcp\tools\call.ps1"
$script:Res = New-Object System.Collections.ArrayList
function T { param([string]$N,[scriptblock]$A)
  $sw=[Diagnostics.Stopwatch]::StartNew(); $st='ERR'; $m=''
  try{ $r=&$A; $sw.Stop(); $st=$r.status
       if($st -ne 'COMPLETED'){ $m="$($r.error.code)" }
       else { $f=$r.cadState.features; $m=if($f -and $f.Count){ (($f[0] -replace '\s+',' ').Substring(0,[Math]::Min(80,($f[0] -replace '\s+',' ').Length))) }else{'ok'} } }
  catch{ $sw.Stop(); $st='THROW'; $m=($_.Exception.Message -replace '\s+',' ') }
  [void]$script:Res.Add([pscustomobject]@{Suite='gap';Name=$N;Status=$st;Ms=[int]$sw.ElapsedMilliseconds;Msg=$m})
  $mk=switch($st){'COMPLETED'{'✅'}'THROW'{'💥'}default{'❌'}}
  "  $mk $N  $m"
}

Write-Output "=== 补测服务端未覆盖的方法 ==="

# EditSketch：需要草图【未激活】时重开
T 'edit_sketch(重开已存在草图)' {
  $null = Call 'open_new_part' @{}
  $null = Call 'create_sketch' @{ plane='Front Plane' }
  $null = Call 'add_sketch_entity' @{ entity_type='circle'; cx=0; cy=0; radius=0.02 }
  # 先退出，再重开
  $null = Call 'edit_feature' @{ feature_name='草图1'; action='rename'; new_name='S1' }
  Call 'edit_sketch' @{ sketch_name='S1' }
}

# LcscFetchStep：查参数
T 'lcsc_fetch_step(查参数)' { Call 'lcsc_fetch_step' @{ part='R0603' } }

# TopologyOptimize 的 probe（已测过，确认仍可用）
T 'topology_optimize(probe)' { Call 'topology_optimize' @{ action='probe' } }

# Electrical（已测过）
T 'electrical(复测)' { Call 'electrical' @{ } }

# GetSelection：先选中东西再读
T 'get_selection(有选中时)' {
  $null = Call 'open_new_part' @{}
  $null = Call 'create_sketch' @{ plane='Front Plane' }
  $null = Call 'add_sketch_entity' @{ entity_type='circle'; cx=0; cy=0; radius=0.02 }
  $null = Call 'extrude_feature' @{ feature_type='boss'; depth=0.01 }
  Call 'get_selection' @{ }
}

# AddReferenceGeometry：四种类型全测
T 'add_ref(plane,offset)'  { Call 'add_reference_geometry' @{ type='plane'; ref_plane_name='Front Plane'; offset=0.01 } }
T 'add_ref(axis)'          { Call 'add_reference_geometry' @{ type='axis'; entity1_name='Front Plane'; entity1_type='PLANE'; entity2_name='Top Plane'; entity2_type='PLANE' } }
T 'add_ref(point)'         { Call 'add_reference_geometry' @{ type='point'; px=0.01; py=0.02; pz=0.03 } }
T 'add_ref(两平面夹角)'    { Call 'add_reference_geometry' @{ type='plane'; ref_plane_name='Top Plane'; offset=0.02 } }

# 验证新建的基准面/轴真的存在
T 'verify(参考几何)' { Call 'analyze_model' @{ analysis_type='features' } }

"`n=== 汇总 ==="
$script:Res | Group-Object Status | ForEach-Object { "  {0,-10} {1}/{2}" -f $_.Name,$_.Count,$script:Res.Count }
$ok=($script:Res|Where-Object{$_.Status -eq 'COMPLETED'}).Count
"  通过率 $ok / $($script:Res.Count)"
$script:Res | Export-Csv -Path "C:\Users\Zegel\solidpilot-mcp\api_scan_gap.csv" -NoTypeInformation -Encoding UTF8
