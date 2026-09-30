# 给 35 处 DIRECT 判据分类：只读 vs 写操作
# 判据：① 这个工具【产生副作用】吗 ② 有可验证的产物吗
#   - 只读（返回数据给调用方，调用方能看到对不对）⇒ 不需要产物验证
#   - 写操作（改了模型/写了文件）⇒ 必须验证，否则可能静默失败
$svc = "C:\Users\Zegel\solidpilot-mcp\execution\solidworks\SolidworksExecution"
$tc  = "$svc\Controllers\ToolController.cs"

# 工具 → 是否写操作（按目标验收里的分类）
$writeOps = @{
  'extrude_feature'='建模'; 'create_rib'='建模'; 'add_edge_feature'='建模';
  'create_pattern'='建模'; 'sheet_metal_feature'='建模'; 'edit_sketch'='建模';
  'edit_feature'='建模'; 'add_dimension'='建模'; 'modify_dimension'='建模';
  'add_sketch_entity'='建模'; 'add_sketch_entities'='建模'; 'add_sketch_constraint'='建模';
  'add_reference_geometry'='建模'; 'set_part_material'='建模';
  'create_sketch'='建模'; 'open_new_part'='建模';
  'insert_component'='写装配'; 'insert_standard_part'='写装配'; 'add_mate'='写装配';
  'open_new_assembly'='写装配';
  'create_drawing'='写文件'; 'add_drawing_view'='写文件'; 'add_section_view'='写文件';
  'add_drawing_dimension'='写文件'; 'add_hole_callout'='写文件'; 'add_flat_pattern_view'='写文件';
  'auto_dimension_drawing'='写文件'; 'auto_center_marks'='写文件';
  'save_document'='写文件'; 'export_document'='写文件'; 'batch_export'='写文件';
  'save_body_as_part'='写文件';
  'motion_study'='写文档'; 'topology_optimize'='写文档'; 'design_check'='写文件';
  'open_document'='改状态'; 'activate_document'='改状态'; 'close_document'='改状态';
  'lcsc_fetch_step'='网络+写文件'
}
$readOnly = @{
  'analyze_model'='纯读'; 'analyze_assembly'='纯读'; 'analyze_slddrw_test'='纯读';
  'verify_state'='纯读'; 'get_selection'='纯读'; 'list_standard_parts'='纯读';
  'product_probe'='纯读'; 'electrical'='纯读'; 'bom_from_assembly'='纯读(返回rows)';
  'get_materials'='纯读'
}

# 找出所有 DIRECT 的位置并归属工具
$hits = @()
Get-ChildItem $svc -Recurse -Filter *.cs | ForEach-Object {
  $file = $_.Name; $lines = Get-Content $_.FullName
  for($i=0; $i -lt $lines.Count; $i++){
    if($lines[$i] -match 'Status\s*=\s*"COMPLETED"'){
      $lo = [Math]::Max(0,$i-25); $ctx = $lines[$lo..$i] -join "`n"
      if($ctx -match 'GetFaceCount|GetEdgeCount|reports\.Count|Directory\.GetFiles|LastFeatureName|FindFeatureByName'){ continue }
      # 往上找最近的 public ExecutionResponse
      $tool='?'
      for($k=$i; $k -ge 0; $k--){
        if($lines[$k] -match 'ExecutionResponse\s+(\w+)\('){ $tool=$matches[1]; break }
      }
      $hits += [pscustomobject]@{ File=$file; Line=($i+1); Method=$tool }
    }
  }
}
Write-Output "=== DIRECT 判据共 $($hits.Count) 处，按工具归属 ===`n"
$ro = $hits | Where-Object { $readOps.ContainsKey($_.Method) }
$wr = $hits | Where-Object { $writeOps.ContainsKey($_.Method) }
$un = $hits | Where-Object { -not $readOps.ContainsKey($_.Method) -and -not $writeOps.ContainsKey($_.Method) }

Write-Output "【A】✅ 只读操作 —— 不需要产物验证（调用方能看到返回数据对不对）: $($ro.Count) 处"
$ro | Group-Object Method | ForEach-Object { "      $($_.Name) × $($_.Count)" }

Write-Output ""
Write-Output "【B】⚠ 写操作 —— 可能有静默失败风险: $($wr.Count) 处"
$wr | Group-Object Method | Sort-Object Count -Descending | ForEach-Object { "      $($_.Name) × $($_.Count)  [$($writeOps[$_.Name])]" }

Write-Output ""
Write-Output "【C】? 未分类: $($un.Count) 处"
$un | Group-Object Method | ForEach-Object { "      $($_.Name) × $($_.Count)" }

Write-Output ""
Write-Output "=== 结论：真正需要加固的是 B 组 ==="
Write-Output "  B 组共 $(($wr|Measure-Object).Count) 处，分布在 $(($wr.Method|Sort-Object -Unique|Measure-Object).Count) 个工具"
Write-Output "  优先加固：$((($wr.Method|Sort-Object -Unique)) -join ', ')"
