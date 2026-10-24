# 缺口操作的批量判定（★ 由 `tools/judge_gap_candidates.py` 生成）

> ⚠ **限度**："名字不撞"**不是**"能力不在" —— 我们的实现可能叫完全不同的名字。
> ★ 本表**只用于挑候选**；★ **不产出"我们缺 N 个能力"这种数**（§10.3 更正掉的读法）。

## 统计

| 口径 | 数 |
|---|---|
| 有描述可判 | 174 |
| **真缺候选**（无实现 + 名字不撞） | **104** |
| 有候选 | 70 |

## 真缺候选（★ 逐条带四家描述，★ 供人工核）

| 操作 | 四家怎么说 | 我们有无实现 |
|---|---|---|
| `delete_feature` | Delete a feature from the FeatureManager tree by name. WARNING: This is irreversible (unless you undo). Use sw_list_feat | 无 |
| `extend_surface` | Extend a surface by a distance, up to a point, or up to another surface. | 无 |
| `filled_surface` | Fill a closed boundary of edges with a new surface. | 无 |
| `rename_feature` | Rename a feature on the feature tree. SolidWorks silently refuses a rename onto a name another feature already uses, so  | 无 |
| `revolved_surface` | Create a revolved surface from the active sketch profile + axis. | 无 |
| `split_line` | Split a face into sub-faces using a sketch (for selective face operations). | 无 |
| `thicken_surface` | Thicken a selected surface body into a solid. Select a surface body with sw_select_entity (type='BODY') first. thickness | 无 |
| `unsuppress_feature` | Unsuppress (re-enable) a previously suppressed feature. Use sw_list_features to find feature names and their suppression | 无 |
| `activate_document` | Switch which open document is the active one. Matches the argument against open documents by title, full path, or file n | 无 |
| `analyze_draft` | Perform draft analysis on the active part model. Highlights faces with sufficient draft (green), faces requiring draft ( | 无 |
| `analyze_geometry` | Perform geometry analysis on the current model. | 无 |
| `batch_process_files` | Perform batch operations on multiple SolidWorks files. | 无 |
| `check_geometry` | Check the active part for geometry errors (invalid faces, edges, etc.). Returns error count and status. Run after comple | 无 |
| `convert_file_format` | Convert a SolidWorks file from one format to another. | 无 |
| `load_part` | Load (open) a SolidWorks part file. | 无 |
| `save_body_as_part` | Extract one solid body from the active multibody part into its own standalone `.sldprt`. Runs SolidWorks' Save Bodies on | 无 |
| `save_part` | Save the active SolidWorks part document. | 无 |
| `update_sheet_format` | Update the sheet format and title block information. | 无 |
| `activate_display_state` | Activate a named display state. | 无 |
| `analyze_drawing_annotations` | Analyze drawing annotations and notes quality. | 无 |
| `analyze_macro` | Analyze a macro for complexity, dependencies, and optimization opportunities. | 无 |
| `apply_template` | Apply a template to an existing SolidWorks model. | 无 |
| `auto_dimension_view` | Automatically dimension a drawing view. | 无 |
| `batch_apply_template` | Apply template to multiple models in batch. | 无 |
| `boundary_boss` | Create a boundary boss/cut from two or more profile curves. | 无 |
| `calculate_mass_properties` | Get mass properties of the current SolidWorks model. | 无 |
| `check_drawing_standards` | Check the current drawing against drafting standards. | 无 |
| `classify_feature_tree` | Classify the active model into a likely feature family using `get_model_info` and `list_features`. | 无 |
| `close_all` | Close all open SolidWorks documents. | 无 |
| `close_model` | Close the current SolidWorks model. | 无 |
| `combine_bodies` | Combine selected bodies via boolean operation (union/subtract/intersect). | 无 |
| `compare_templates` | Compare two templates and generate difference report. | 无 |
| `delete_body` | Delete the selected body. | 无 |
| `delete_face` | Delete selected face(s). Optionally patch the resulting hole. | 无 |
| `execute_macro` | Execute a saved SolidWorks macro. | 无 |
| `exit_sketch` | Exit sketch editing mode. Exit the active sketch and return to the 3D model view. Must be called after finishing sketch  | 无 |
| `export_drawing_pdf` | Export the active drawing to PDF (output_path must end in .pdf). | 无 |
| `extract_template` | Extract template from existing SolidWorks model. | 无 |
| `generate_drawing_report` | Generate comprehensive drawing analysis report. | 无 |
| `generate_vba_batch_export` | Generate VBA code for batch file export operations. | 无 |
| `generate_vba_code` | Generate VBA code for SolidWorks automation. | 无 |
| `load_assembly` | Load (open) a SolidWorks assembly file. | 无 |
| `manage_design_table` | Create or manage design tables for parametric modeling. | 无 |
| `manage_file_properties` | Read, update, copy, move, rename, or delete file-related properties. | 无 |
| `move_body` | Move or copy the selected body by translation (mm) and rotation (deg). | 无 |
| `open_model` | Open a SolidWorks model (part, assembly, or drawing). | 无 |
| `optimize_macro` | Optimize an existing macro for better performance and reliability. | 无 |
| `pack_and_go_assembly` | Copy a SolidWorks assembly and all its referenced parts to a self-contained folder — equivalent to the SolidWorks GUI ** | 无 |
| `rebuild_model` | Force-rebuild the active model (Ctrl+B equivalent). Use after making multiple dimension or property changes to update th | 无 |
| `run_vba_code` | Execute arbitrary VBA code against SolidWorks. Writes the code to a temporary macro file and runs it. If no Sub declarat | 无 |
| `save_all` | Save all open SolidWorks documents that have unsaved changes. | 无 |
| `save_assembly` | Save the active SolidWorks assembly document. | 无 |
| `save_file` | Save the current SolidWorks model. | 无 |
| `save_to_template_library` | Save template to the organization's template library. | 无 |
| `scale_body` | Uniformly scale the selected body by a factor. | 无 |
| `sketch_circular_pattern` | Create a circular pattern of sketch entities. Create a circular pattern of selected sketch entities. Select the sketch e | 无 |
| `sketch_linear_pattern` | Create a linear pattern of sketch entities. Create a linear step-and-repeat pattern of selected sketch entities. Select  | 无 |
| `sketch_tutorial_simple_hole` | Tutorial: Create a simple circular hole sketch. | 无 |
| `split_body` | Split the selected body using the selected trim tool (sketch/surface/plane). | 无 |
| `tutorial_simple_hole` | Create a simple hole as a guided tutorial workflow. | 无 |
| `analyze_drawing_comprehensive` | Perform comprehensive analysis of SolidWorks drawing. | 无 |
| `analyze_drawing_dimensions` | Analyze dimensions in a SolidWorks drawing for consistency and completeness. | 无 |
| `analyze_drawing_views` | Analyze drawing views arrangement and quality. | 无 |
| `auto_center_marks` | Auto-insert centre marks on circular features in a drawing view. Runs SolidWorks' automatic centre-mark insertion for th | 无 |
| `batch_execute_macros` | Execute multiple macros in batch mode. | 无 |
| `batch_file_operations` | Run a file operation across multiple files as a batch workflow. | 无 |
| `check_drawing_compliance` | Check drawing compliance with company standards. | 无 |
| `compare_drawing_versions` | Compare different versions of drawing files. | 无 |
| `execute_workflow` | Execute a predefined automation workflow. | 无 |
| `export_drawing_dwg` | Export the active drawing to DWG or DXF (output_path determines format). | 无 |
| `export_dwg` | Export the current drawing to DWG format. | 无 |
| `flatten_sheet_metal` | Toggle the flat pattern view of the active sheet metal part. Shows the unbent, flat state of the sheet metal part. Use s | 无 |
| `generate_vba_assembly_insert` | Generate VBA code for assembly component insertion. | 无 |
| `generate_vba_assembly_mates` | Generate VBA code for assembly mate creation. | 无 |
| `generate_vba_drawing_dimensions` | Generate VBA code for creating drawing dimensions. | 无 |
| `generate_vba_drawing_views` | Generate VBA code for drawing view creation. | 无 |
| `generate_vba_extrusion` | Generate VBA code for complex extrusion operations. | 无 |
| `generate_vba_file_operations` | Generate VBA code for file management operations. | 无 |
| `generate_vba_macro_recorder` | Generate VBA code using macro recording patterns. | 无 |
| `generate_vba_part_modeling` | Generate VBA code for complex part modeling operations. | 无 |
| `generate_vba_revolve` | Generate VBA code for complex revolve operations. | 无 |
| `hide_all_planes` | Hide all reference planes in the viewport. | 无 |
| `hide_all_sketches` | Hide all sketches in the viewport. | 无 |
| `link_dimension_to_equation` | Link a dimension to an expression via an equation (drives the dimension parametrically). | 无 |
| `optimize_performance` | Optimize SolidWorks performance settings. | 无 |
| `pattern_component_circular` | Circularly pattern a selected component about an axis. | 无 |
| `pattern_component_linear` | Linearly pattern a selected component (select seed component + direction reference first). | 无 |
| `projected_curve` | Project a sketch onto a face to create a 3D curve. | 无 |
| `save_as_copy` | Save the active document as a copy without changing the current open file. | 无 |
| `show_all_planes` | Show all reference planes in the viewport. | 无 |
| `show_all_sketches` | Show all sketches in the viewport. | 无 |
| `sketch_construction` | Toggle selected sketch entities to construction (dashed) geometry. | 无 |
| `sketch_extend` | Extend selected sketch entity until next boundary. | 无 |
| `sketch_fillet` | Fillet (round) the corner between two selected sketch lines. | 无 |
| `sketch_offset` | Create an offset of sketch entities. Offset selected sketch entities by a given distance. Select the entities to offset  | 无 |
| `sketch_trim` | Trim selected sketch entity (power trim mode). | 无 |
| `stop_macro_recording` | Stop macro recording and save the recorded macro. Stop recording a SolidWorks macro and save the file. The recorded macr | 无 |
| `take_photoview_screenshot` | Render via PhotoView 360 add-in if available, else regular screenshot. | 无 |
| `tooling_split` | Split a mold block into core and cavity using the parting line/surfaces. | 无 |
| `trim_weldment` | Trim selected weldment members to a planar or solid trim tool. | 无 |
| `unfold` | Unfold sheet-metal bends to flatten (use with subsequent features then sw_fold). | 无 |
| `update_title_block` | Update title block fields for the active drawing. | 无 |
| `validate_drawing_completeness` | Validate drawing completeness for production readiness. | 无 |
| `view_rotate` | Rotate the current view by Euler angles (degrees). | 无 |
