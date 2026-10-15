# Baseline — **EC08 工程图与多工艺建模方法**

**Feature**: `specs/310-ec08-drawing-and-processes/`
**日期**: 2026-10-10
**上游**: `output/ENGINEERING_CONSTRUCTION_PLAN.md` **§5 EC08**（★ **四个子域** + 共同任务）
**前置**: ★ **EC00–EC07 已收口**（★ 规格 302–309）
**对应任务**: **EC08A–EC08D**（★ **四个子域逐一放行** —— ★ 逐字：「★ **不合并成一个大任务**」）

---

## 一、★★★★★ 编号与权属

| ★ 项 | ★ 读数 | ★ 处置 |
|---|---|---|
| ★ **最高正式编号** | ★ **309** | ★★ **本特性取 `310`** ✓ |
| ★ 分支 / `HEAD` | `master` / `d072d0c7…` | ★ **不切分支 · 不提交** |
| ★★ **权属** | ★ 承 **D6**（★ **B 组禁止覆盖**） | ★ 只写 §三 的路径 |

---

## 二、★★★★★ 起点状态（★ 四个子域各自的能力实测）

★★★ **计划逐字**：★「★ **分四个子域逐一放行，不合并成一个大任务**」。

### 2.1 ★★ EC08A 工程图基础

| ★ 能力 | ★ 实测 |
|---|---|
| ★ 视图/剖视/局部放大 | ★ `solidworks_drawing_create_projected_view` · `_create_section_view` · `_create_detail_view` **在工具面** |
| ★ 尺寸/基准/公差 | ★ `solidworks_drawing_add_note` · `_insert_datum_tag` · `_insert_surface_finish_symbol` · `_insert_model_items` **在工具面** |
| ★ BOM/气泡 | ★ `solidworks_drawing_insert_balloons` · `_create_hole_table` · `_create_revision_table` **在工具面** |
| ★ 读侧 | ★ `solidworks_drawing_list_views` · `_view_annotations` · `_sheet_scale` **在工具面** |

### 2.2 ★★ EC08B 钣金

| ★ 能力 | ★ 实测 |
|---|---|
| ★ 基体法兰 | ★ `solidworks_sheet_metal_create_base_flange` **在工具面**（★ 真机验过） |
| ★ 展开/折叠 | ★ `_create_unfold` · `_create_fold` **在工具面**（★ 真机建成过 `展开1`/`折叠1`） |
| ★ 卷边/边法兰/斜接 | ★ `_create_hem` · `_create_edge_flange` · `_insert_miter_flange` **在工具面**（★ 部分**本机不建** —— ★ `capabilities.yaml` 有 `limitations`） |
| ★ 读侧 | ★ `solidworks_sheet_metal_evidence` · `_iter_features` **在工具面** |

### 2.3 ★★ EC08C 焊件

| ★ 能力 | ★ 实测 |
|---|---|
| ★ 结构构件 | ★ `solidworks_weldment_create_structural_member` **在工具面** |
| ★ 切割清单 | ★ `_create_cut_list` · `_update_cut_list` · `_export_cut_list_csv` **在工具面** |
| ★ 角撑板/端盖/圆角焊缝 | ★ `_gusset_create` · `_insert_end_cap` · `solidworks_weld_fillet_bead_report` **在工具面** |
| ★ 读侧 | ★ `solidworks_weldment_evidence` · `_iter_features` **在工具面** |

### 2.4 ★★ EC08D 曲面

| ★ 能力 | ★ 实测 |
|---|---|
| ★ 拉伸/旋转/放样/扫描曲面 | ★ `solidworks_surface_create_extruded` · `_create_revolved_surface` · `_insert_lofted_ref_surface` · `_sweep_surface` **在工具面** |
| ★ 缝/填充/延伸/裁剪 | ★ `_knit` · `_fill` · `_extend` · `_untrim_surface` **在工具面** |
| ★ 中面/加厚 | ★ `_midsurface_create` · `solidworks_thicken` **在工具面** |
| ★ 读侧 | ★ `solidworks_surface_evidence` · `_runtime_available` **在工具面** |

★★★ **⇒ 四个子域的**能力都已在工具面** —— ★ **本特性做的是**验收方法**与**判据**，★ 不是新造能力** ✓

---

## 三、★★★ 本轮允许写入的文件

| ★ 类 | ★ 路径 |
|---|---|
| ★ **本特性目录** | `specs/310-ec08-drawing-and-processes/**` |
| ★ **判据** | `tests/test_ec08_*.py` |
| ★★ **实现** | ★ `scripts/engineering/`（★ 扩展） |
| ★★ **禁止写** | ★ B 组 · ★ `AGENTS.md` 纪律正文 · ★ `.gitignore` · ★ `.codebuddy/` · ★ `.workbuddy-ai/` |

---

## 四、★★★★★ 本特性的核心（★ 由计划 §5 EC08 的「验收」推出）

★★★ **计划 §5 EC08 验收逐字**：
> ★ 尺寸值、基准、公差、**模型配置版本**都能**回读比对**；★ **悬空标注检测**；
> ★ 版面/遮挡/线型与可读性另设检查。★ **制图标准符合不代表整机安全合规**。

★★★ **⇒ 三条各自对应一个设计决定**：

| ★ 验收 | ★ 设计决定 |
|---|---|
| ★ **尺寸/基准/公差/配置版本都能回读比对** | ★★ 每项标注**必须有对应回读**；★ **配置版本**绑进证据 |
| ★ **悬空标注检测** | ★★ 标注**必须能指回**它标的几何；★ 指不回 ⇒ **悬空** |
| ★★★ **制图标准符合 ≠ 整机安全合规** | ★★ 交付物**必须带**那条**免责声明**（★ 不是可选） |

---

## 五、★★★ 与 EC05 / EC09 / EC11 的边界

| ★ 谁 | ★ 做什么 | ★ **不做什么** |
|---|---|---|
| ★ **EC05**（★ 已收口） | ★ 首个零件闭环 | ★ 不做工程图 |
| ★ **EC08**（★ 本特性） | ★★ **制图 + 钣金/焊件/曲面** | ★ 不做 CAE（★ EC09）· ★ **不判安全合规**（★ EC11） |
| ★ **EC09** | ★ CAE/拓扑 | ★ 不改几何 |
| ★ **EC11** | ★ 合规发布 | ★ **它才判合规** —— ★ EC08 **只出图纸** |

---

## 六、★★ G0 判据

| ★ 门 | ★ 放行条件 | ★ 本文件 |
|---|---|---|
| **G0 基线** | ★ 权属和起点明确；★ **没有覆盖别人的改动** | ★★ **满足** ✓ —— ★ 编号 **310** · ★ 权属按 D6 · ★ 写入面已列 · ★ **四子域能力已实测** · ★ **未触碰 B 组** |

★★★ **⇒ G0 通过** ⇒ ★ 可进入 **EC08A**。
