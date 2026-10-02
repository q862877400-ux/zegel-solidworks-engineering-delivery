# 「缺口操作」的有依据判定（objective② · 2026-10-01 轮 353 起）

## 〇、★ 这个文件解决什么问题
```
★ `docs/union-gap-triage.md` 的"后缀候选"档（144 条）是**按词面**匹配出来的
   ⇒ 抽样 24 条：**真 6 · 部分 2 · 假 16**（★ **67% 假**）。
★★ 而 `tools/union-sources.json` 的 `union_operations` 是 **349 个纯名字**（**无描述**）
   ⇒ ★ 光看名字**判不了"真缺 vs 语义等价"**。
⇒ ★★★ **本文件的做法**：★ **先去四家仓库取那个操作的**描述**，★ 再判我们有没有** ——
   ★ 抽取脚本 `tools/extract_operation_descriptions.py` ⇒ 产物 `docs/operation-descriptions.json`。
```

## 一、★ 抽取结果（★ 可重跑）
```
★ `andrewbartels1/docs/user-guide/tool-catalog/*.md`（12 个分类）⇒ **117 个操作名**
★ `Eduardof0nt/server.py` 的 **187 个 `@mcp.tool`**（★ 用 AST 取 `name=` + docstring）⇒ **187 个**
★ 合并（★ 含去掉 `sw_` / `sws_` / `solidworks_` 前缀的短名）⇒ **464 个**
★★ 分诊表里的 **339** 个缺口操作 ⇒ ★ **174 个能在四家找到描述**（★ **判据依据**）✓
```

## 二、★★★★★ 判据（★ 有依据，不是词面）
```
① ★ **取描述**：`docs/operation-descriptions.json` 里该操作名下四家的原文；
② ★ **在我们这边找**：★ 从 `ToolSpec` 取**工具名 / 函数名 / 模块名**（★ 经 `rc.all_specs()`，★ 不手写），
   ★ 看有没有一个名字**同时含**该操作的关键词元组；
③ ★ **判**：★ 命中 ⇒ ★ **有候选**（★ 再人工核是不是同一件事）；★ 未命中 ⇒ ★ **真缺**。
```

## 三、★ 首批 12 条判定（★ 冒烟：先证方法有效，再谈批量）
| 缺口操作 | 四家描述（截断） | 判定 |
|---|---|---|
| `extend_surface` | Extend a surface by a distance, up to a point, or up to another surface. | **真缺** |
| `filled_surface` | Fill a closed boundary of edges with a new surface. | **已补**（★ 2026-10-02 轮 388 真机 **PASS**：`曲面填充1` · 树 7→8 · 选 4 边 —— 边界按**中点 + mark=1** 选；★ 详见 known-facts 事实 305）|
| `offset_surface` | Offset a selected face/surface by a distance. | **有实现** `sw_surface.py:134` ✓ |
| `planar_surface` | Create a planar surface from selected closed sketch profile or edges. | **有实现** `sw_surface.py:125` ✓ |
| `revolved_surface` | Create a revolved surface from the active sketch profile + axis. | ⚠ **2026-10-02 轮 385 更正：有实现** —— `scripts/sw_surface.py` 的 `create_revolution_surface`（★ 旧判定“真缺”是**按名字找**的误判，事实 52/265）|
| `delete_feature` | Delete a feature from the FeatureManager tree by name. WARNING: irreversible… | **真缺** |
| `rename_feature` | Rename a feature on the feature tree. SolidWorks silently refuses a rename onto… | **真缺** |
| `extruded_surface` | Create an extruded surface from the active sketch. | 有候选 `create_extruded_surface_report` |
| `parting_line` | Create a parting line for mold design… | 有候选 `insert_parting_line` 等 |
| `shut_off_surface` | Automatically create shut-off surfaces over holes… | 有候选 `insert_shut_off_surface` 等 |
| `loft` | Create a loft between selected sketch profiles… | 有候选 `create_loft_report`（★ 本会话真机通过）|
| `sketch_line` | Draw a line in the active sketch… | 有候选 `solidworks_sketch_add_line` |

**方向验证**：★ **5 条"有候选"的，我本会话都能指认它们确实存在**
（`loft` 真机通过 · `parting_line` / `shut_off_surface` 在 `sw_mold.py`）⇒
★★ **判据没有把"我们有的"误判成缺**（★ 那是最危险的错向）。

## 四、★★★ 真缺的**族**（★ 复核后的准确结论）

```
★ 复核判据（★ 这一步**必须排除反射转储**）：在 `scripts/sw_*.py` 里找该操作的实现，
   ★★ **但排除 `sw_api_*.py`** —— ★ 那是**反射转储表**，列出**所有**成员名，**不是调用**。
   ⚠ 我第一遍**忘了排除** ⇒ `extend_surface` / `filled_surface` / `offset_surface` / `planar_surface` /
     `delete_feature` / `rename_feature` **全部"命中"**进了 `sw_api_sldworks.py` ⇒
     ★★ **把两条"其实有实现"的错判成真缺**（★ `offset_surface` / `planar_surface` 实际在 `sw_surface.py`）。
   ⇒ ★★★ **排除后：真缺 5 条**（★ 而不是 7 条）✓
```

| 族 | 真缺的操作 | 我们的现状 |
|---|---|---|
| **曲面族** | `extend_surface` · `filled_surface` · `revolved_surface` | 已有 `offset_surface` / `planar_surface` / `create_extruded_surface_report`（★ 在 `sw_surface.py`）⇒ **可成批补同族其余** |
| **特征管理** | `delete_feature` · `rename_feature` | 无实现 |

```
★ **曲面族 3 条**：★ 我们**已有同族的 3 个**（`offset` / `planar` / `extruded`）
   ⇒ ★★ 与 `capabilities.yaml` 的 `surface_modeling`（★ `stitched`）对得上 ⇒ **可成批补** ✓
★ **特征管理 2 条**：★ `delete_feature` 的描述自带 **WARNING: irreversible** ⇒
   ★★★ **与硬约束⑦（不碰高风险写操作）直接相关** ⇒ ★ **先查、再定要不要做**（★ 不贸然）。
```

## 四之二、★★★ 本次又踩的坑（★ 本会话**第三次**）
```
★ **「名字出现过」≠「真的在用」** ——
   · 轮 351（事实 271）：按字符串扫"废弃入口"得 **1020** 处，★ 而绝大多数来自 `sw_api_sldworks.py`；
   · 本轮：判"我们有没有"时**同一个错**，★ 把 2 条**有实现**的错判成真缺。
⇒ ★★ **定则：凡"扫仓库看某名字在不在"，一律先排除 `sw_api_*.py`（反射转储）** ——
   ★ 本仓库的互锁测试（`tests/test_deprecated_entry_interlock.py`）**已经这么写了**
   （`_scan_all_modules()` 里 `if path.name.startswith("sw_api_"): continue`）
   ⇒ ★★★ **说明该把这条提取成**公共函数**，而不是每处各写一遍**（★ 三次都是手写漏了）。
```


## 五、⚠ 限度（★ 如实标，★ 且**经过一轮收紧**）
```
⚠ **只判了 12 条**（★ 抽样冒烟），★ **不是**174 条全判** —— ★ 余下 162 条要逐条。
⚠ **"有候选"不等于"语义等价"** —— ★ 仍需人工核（★ 本表把**依据**摆出来了，★ 使那一步可做）。
⚠ **判据是"名字含关键词"** ⇒ ★ **名字对不上而能力其实在**的情形会漏（★ 即"假缺"）——
   ★ 本表**只用于挑候选**，★ **不用于宣称"我们缺"**（★ 那要逐条核）。
```

### ★★★★ 2026-10-01（轮 357）**又发现两条判据的硬限度**（★ 都实测过）
```
① **"按描述里的词去代码里找"** —— 我试过用它核 `analyze_draft` 一类：
   ★ 判据：★ 从四家描述里取 ≥4 字母的词，★ 拿每个词去 `find_real_implementations`。
   ★★ **结果 12/12 全"命中"** —— ★ 因为 `perform` / `create` / `get` / `selected` / `open` /
     `document` / `file` / `feature` 这类**通用词**到处都是 ⇒ ★ **零判别力**。
② ★ 加**停用词表**（通用动词 + 虚词 + 色彩词，约 60 个）后重跑 ⇒ ★★ **仍然 11/12** ——
   ★ 因为 `body` / `face` / `draft` / `assembly` / `render` 这类**领域名词**在代码里**同样泛滥**。
⇒ ★★★ **定则**：★ **"某个词在不在仓库里"这个判据，无论加多少停用词，都不能判"我们有没有某能力"** ——
   ★★ **它与调研 v2 那条「名字出现过 100%（无判别力）」是同一类错**（★ 只是从"工具名"换成了"描述里的词"）。
```

### ★★★ 那"判我们有没有"该用什么粒度（★ 结论）
```
★ **唯一有判别力的粒度是 `capabilities.yaml` 的能力条目** ——
   ★ 那是**人工核过的语义单元**（★ 每条有 `id` + `mcp_tools` + `evidence` + `limitations`），
   ★ **而不是函数名、也不是描述里的词**。
⇒ ★ 本文件的 `docs/union-gap-batch-judgement.md`（104 条）用的是**名字词集**判据 ⇒
   ★★ **它的"真缺候选"该读成「名字层面没对上」**，★ **不是**「能力不在」** —— ★ 限度比我上一版写的**更严**。
   ⇒ ★ **要把它变成"能力级"的判定，得拿 `capabilities.yaml` 的 79 条逐条比对**（★ 那是下一步）。
```


**依据**：`tools/extract_operation_descriptions.py`（★ 可重跑）· `docs/operation-descriptions.json`
（★ `counts`: andrewbartels1 **117** · Eduardof0nt **187** · merged **464** · gap_hit **174**）·
`docs/union-gap-triage.md`（★ 后缀候选 144 / 真缺 132）· `rc.all_specs()`（★ 我们这边的名字来源）·
来源许可：`Eduardof0nt/Solidworks-MCP-Server` **MIT** · `andrewbartels1/SolidworksMCP-python` **MIT**
（★ **只读其工具名与描述文本用于对照，未抄代码**）。
