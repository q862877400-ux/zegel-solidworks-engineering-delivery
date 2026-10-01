import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")

P = Path(r"C:\swprojects\sw-skill-fork\docs\union-gap-triage-sample.md")
t = P.read_text(encoding="utf-8")

ADD = """

---

# 追加：两档「别名」也核了（轮 102）

`010` 另有两档别名，**同样是字符串匹配**，且「强别名」档自称「**极可能同一操作**」。
⇒ 本轮**全核**（只有 63 条）：

## 别名（强）26 条 —— 命中率 ≈ **27%**

| # | 缺口操作 | 我们的候选 | 判定 | 理由 |
|---|---|---|---|---|
| 1 | `advanced_features` | `inspect_hole_features` | ❌ 假 | 高级特征 ≠ 检查孔特征 |
| 2 | `assembly_analysis` | `mold_draft_analysis` | ❌ 假 | 装配分析 ≠ 模具拔模分析 |
| 3 | `assembly_configurations` | `inspect_configurations` | ✅ 真 | 就是看配置 |
| 4 | `configurations` | `inspect_configurations` | ✅ 真 | 同上 |
| 5 | `delete_feature` | `hole_feature` | ❌ 假 | **删除**特征 ≠ 孔特征 |
| 6 | `drawing` | `inspect_drawing` | ✅ 真 | 同一操作 |
| 7 | `extend_surface` | `mold_shut_off_surface, ocp_surface` | ❌ 假 | 延伸曲面 ≠ 关曲面/OCP 曲面 |
| 8 | `extruded_surface` | `mold_shut_off_surface, ocp_surface` | ❌ 假 | 拉伸曲面 |
| 9 | `features` | `inspect_hole_features` | ❌ 假 | 特征 ≠ 孔特征 |
| 10 | `filled_surface` | `mold_shut_off_surface, ocp_surface` | ❌ 假 | 填充曲面 |
| 11 | `line` | `mold_parting_line` | ❌ 假 | 草图直线 ≠ 分型线 |
| 12 | `loft` | `ocp_loft` | ✅ 真 | 放样 |
| 13 | `mirror_feature` | `hole_feature` | ❌ 假 | 镜像 ≠ 孔 |
| 14 | `offset_surface` | `mold_shut_off_surface, ocp_surface` | ❌ 假 | 偏移曲面 |
| 15 | `parting_line` | `mold_parting_line` | ✅ 真 | 分型线 |
| 16 | `pattern_features` | `inspect_hole_features` | ❌ 假 | 阵列 ≠ 孔 |
| 17 | `planar_surface` | `mold_shut_off_surface, ocp_surface` | ❌ 假 | 平面曲面 |
| 18 | `rename_feature` | `hole_feature` | ❌ 假 | 重命名 ≠ 孔 |
| 19 | `revolved_surface` | `mold_shut_off_surface, ocp_surface` | ❌ 假 | 旋转曲面 |
| 20 | `shut_off_surface` | `mold_shut_off_surface` | ✅ 真 | 关曲面 |
| 21 | `sketch_line` | `mold_parting_line` | ❌ 假 | 草图线 ≠ 分型线 |
| 22 | `split_line` | `mold_parting_line` | ❌ 假 | 分割线 ≠ 分型线 |
| 23 | `technical_drawing` | `inspect_drawing` | ✅ 真 | 工程图 |
| 24 | `thicken_surface` | `mold_shut_off_surface, ocp_surface` | ❌ 假 | 加厚曲面 |
| 25 | `trim_surface` | `mold_shut_off_surface, ocp_surface` | ❌ 假 | 裁剪曲面 |
| 26 | `unsuppress_feature` | `hole_feature` | ❌ 假 | 解除压缩 ≠ 孔 |

```
✅ 真 **7** / 26 ≈ **27%**
```
★ **最离谱的一处**：第 7/8/10/14/17/19/24/25 条 —— **8 个互不相同的曲面操作**
（延伸 / 拉伸 / 填充 / 偏移 / 平面 / 旋转 / 加厚 / 裁剪）**全被配到同样两个函数**
`mold_shut_off_surface, ocp_surface`。⇒ 匹配器只认到共同后缀 **`surface`**。

## 别名（弱）37 条 —— 命中率 ≈ **16%**

判定口径同上（✅ 真 / ⚠ 部分 / ❌ 假）。逐条：

| 缺口操作 | 我们的候选 | 判定 |
|---|---|---|
| `activate_document` | `new_document, open_document` | ⚠ 部分 |
| `analyze_draft` | `sheet_metal_create_draft` | ❌ 假（**分析**拔模 ≠ **建**拔模）|
| `analyze_geometry` | `review_advanced_geometry` | ⚠ 部分 |
| `base_flange` | `sheet_metal_create_base_flange` | ✅ 真 |
| `batch_process_files` | `batch_export_files` | ⚠ 部分 |
| `bom` | `export_assembly_bom` | ✅ 真 |
| `check_geometry` | `review_advanced_geometry` | ⚠ 部分 |
| `close_document` | `new_document, open_document` | ❌ 假 |
| `construction_geometry` | `review_advanced_geometry` | ❌ 假 |
| `convert_file_format` | `write_open_format` | ⚠ 部分 |
| `diameter_dimension` | `update_dimension` | ⚠ 部分 |
| `dimension` | `update_dimension` | ✅ 真 |
| `draft` | `sheet_metal_create_draft` | ⚠ 部分 |
| `drawing_dimension` | `update_dimension` | ⚠ 部分 |
| `drawing_sheet_format` | `write_open_format` | ❌ 假 |
| `edge_flange` | `sheet_metal_create_edge_flange` | ✅ 真 |
| `export_document` | `new_document, open_document` | ❌ 假 |
| `gusset` | `sheet_metal_create_gusset` | ✅ 真 |
| `load_part` | `basic_part` | ❌ 假 |
| `mate` | `coincident_mate, concentric_mate` | ⚠ 部分 |
| `material` | `simulation_set_material` | ⚠ 部分 |
| `miter_flange` | `sheet_metal_create_*_flange` | ❌ 假 |
| `motion_study` | `validate_motion_study` | ⚠ 部分 |
| `open_documents` | `close_documents` | ❌ 假 |
| `part` | `basic_part` | ⚠ 部分 |
| `rebuild_document` | `new_document, open_document` | ❌ 假 |
| `reference_geometry` | `review_advanced_geometry` | ❌ 假 |
| `referenced_documents` | `close_documents` | ❌ 假 |
| `save_active_document` | `new_document, open_document` | ❌ 假 |
| `save_body_as_part` | `basic_part` | ❌ 假 |
| `save_part` | `basic_part` | ❌ 假 |
| `simulation_study` | `topology_create_study, validate_motion_study` | ⚠ 部分 |
| `sketch_dimension` | `update_dimension` | ⚠ 部分 |
| `sketch_status` | `addin_host_status` | ❌ 假（只配到 `status` 一词）|
| `sketched_bend` | `sheet_metal_create_one_bend` | ✅ 真 |
| `status` | `addin_host_status` | ❌ 假 |
| `update_sheet_format` | `write_open_format` | ❌ 假 |

```
✅ 真 **6** · ⚠ 部分 **14** · ❌ 假 **17** / 37 ⇒ 真 **16%**
```

## ★★ 合并后的结论：**四档全都要打折**
```
              条数   真    命中率
别名（强）      26     7     27%
别名（弱）      37     6     16%
后缀候选       144    36*    25%   (* 抽样外推)
真缺           132   132     —     (定义上就是缺)
------------------------------------------------
真匹配 ≈ 7 + 6 + 36 = **49**
⇒ 真实缺口 ≈ 338 − 49 ≈ **289**（`010` 当时说 **132**）
```

## ⚠ 这个数字的限度（必须一起读）
* **别名两档是全核**（63/63）；**后缀候选是抽样**（24/144）⇒ 后者有外推误差；
* 「部分」那 **16** 条口径未定；本表**不计入"真"** ⇒ 真匹配可能落在 **49~65** 之间；
* 因此结论应表述为「**真实缺口约 270~290，远大于 010 说的 132**」，
  而不是「就是 289」。

## ★ 这一轮的可复用认识
**同一个匹配器，越"强"的档也可能越不准** —— 「强别名」自称"极可能同一操作"，
实测 **27%**，与最弱的档**差不多**。
⇒ **分档的"强/弱"是给匹配规则起的名，不是给结论背的书。**
"""

if "两档「别名」也核了" not in t:
    t = t.rstrip() + ADD
    # 更新顶部的结果块
    t = t.replace(
        "## ⚠ 未查证\n* 只核了 **24/144**（抽样），**剩余 120 条未逐条核**；",
        "## ⚠ 未查证\n* 只核了 **24/144**（抽样），**剩余 120 条未逐条核**；\n"
        "* ⚠ **本轮（轮 102）追加**：另两档「别名强/弱」**已全核**，见文末 —— "
        "**四档全都要打折，真实缺口约 270~290**；")
    P.write_text(t, encoding="utf-8")
    print("  ok sample 文档已追加两档别名核样")
else:
    print("  已有")

# 更新 triage 顶部的修正提示
Q = Path(r"C:\swprojects\sw-skill-fork\docs\union-gap-triage.md")
tq = Q.read_text(encoding="utf-8")
old_line = "> ⇒ 真缺应约 **240**（= 132 + 144×75%），不是 132。"
new_line = ("> ⇒ 真缺应约 **240**（= 132 + 144×75%），不是 132。\n"
            "> ⚠⚠ **轮 102 追加**：另两档「别名（强）26 / 别名（弱）37」**全核**后同样是**大量假匹配**\n"
            "> （强档 **7/26≈27%** · 弱档 **6/37≈16%**）—— ⚠ **连自称「极可能同一操作」的强档也不例外**。\n"
            "> ⇒ 四档合并：真匹配 ≈ **49** ⇒ **真实缺口 ≈ 289**（`010` 当时说 132）。\n"
            "> ⚠ 限度：别名两档是全核，后缀候选是抽样 ⇒ 结论应表述为「**真实缺口约 270~290**」。")
if "轮 102 追加" not in tq:
    assert old_line in tq, "锚点不符"
    Q.write_text(tq.replace(old_line, new_line, 1), encoding="utf-8")
    print("  ok triage 顶部提示已更新")
else:
    print("  triage 已有轮 102 提示")
