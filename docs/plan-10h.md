# 十小时计划 · 砌墙阶段（按 Spec Kit 规范排）

> **建立** 2026-10-01（轮 221）· **前置**：`docs/plan-foundation.md` 的**地基四项已完成**
> **作业指导书**：`.specify/commands/speckit.<name>.md`（读它、按它执行）
> **宪法**：`.specify/memory/constitution.md`（§I–§V 是 `analyze` 要对齐的判据）
> **⚠ 本文件不写「当前进度」** —— 那在 `docs/ROADMAP.md` §一 游标、`capabilities.yaml` 与 `docs/metrics.md`（宪法：一处一个家）

---

## 一、这一阶段的判据（**与上一阶段最大的不同**）

```
★ 上一阶段（地基）的判据是"数字只有一个意思"。
★ 这一阶段的判据是 **"挂出去的每一个工具，都必须真机验过"** ——
   即：**A（挂工具）与 B（真机验证）必须配对，缺一不算完成。**
★★ 为什么：`docs/metrics.md` 把覆盖分成三个口径，其中
   「真机碰过」是最窄的那个（当前值见该文件）⇒ **那个数不上涨，就等于没做。**
```

**因此每一批（W1–W7）都必须交出两样东西**：
```
① 静态挂载：`register_capabilities.all_specs()` 里出现该批工具，且门禁全绿
② ★ 真机证据：`output/<族>-evidence.json` 里 `verdict: pass`
   ⚠ 验不过的**回退**，**不许留在柜台上**
```

---

## 二、队列（W1–W7，**已按"值 ÷ 成本"排序**）

> ★ 顺序不是按缺口大小排的，而是按「**包装层难度**」排的：
>   包装层越简单、真机越好验的排前面 ⇒ 早暴露风险、早积累套路。

> ★★ **编号顺移（2026-10-01 轮 228 发现并更正）**：原计划把 W4–W7 编成 134–137，
> 但 **`specs/134-static-simulation-reverified` 是已提交的真实特性**（5 件套、`79cdac1`）
> ⇒ 按 Spec Kit **flow-forward（完成的目录不可变、需求变了开新号）**，W4 起**顺移一号**：
> **W4=135 · W5=136 · W6=137 · W7=138**。
> ⚠ 这正是「编号必须现场核、不能照计划抄」的一个实例。

### W1 · 草图只读族（`specs/131`）· **约 90 分钟**
| 项 | 内容 |
|---|---|
| 取什么 | `sw_sketch` 的只读查询：线 / 弧 / 段 / 是否 3D 草图 / 轮廓数 |
| ★ 前置已有 | `tools/probe_sketch_object_routes.py` 已真机证明：**取草图对象只能按名取**（`FeatureByName` → `GetSpecificFeature2`），`GetActiveSketch2` 与 `ActiveSketch` 在**草图关闭后都是 None** |
| ★ 包装层形状 | **先在 `scripts/sw_sketch.py` 加"只回读数"的薄函数**（`count_lines(sketch) -> int` 之类），再用 `module/function + inject="model"` + `derived_args` 挂 —— ★ **不用 `extra_op`**（保持 `batch1` 立的「全部声明式」） |
| 来源 / license | 本项目自身（MIT）；官方依据 `ISketch.GetSketchSegments` 一族 |
| 验收① | `python -c "import sys;sys.path[:0]=[r'C:\swprojects\sw-skill-fork\mcp-server',r'C:\swprojects\sw-skill-fork'];import register_capabilities as rc;print(len(rc.all_specs()))"` |
| 验收② | `python tools/capture_sketch_evidence.py` ⇒ `verdict: pass` |

### W2 · 工程图族（`specs/132`）· 约 60 分钟 · ★★ **2026-10-01 轮 223 实测后缩批（见下）**
```
★★★ **缩批的理由（实测，不是估的）**：⑪工程图 的 49 个缺口名，逐个核过之后分三类：
   ① **名字差异（已覆盖）**：只读结构那一整类 ——
      `drawing_views` / `drawing_dimensions` / `drawing_annotations` / `drawing_tables` / `sheets` /
      `analyze_drawing_views|dimensions|annotations` … **`solidworks_inspect_drawing` 已经覆盖**
      （内核就是 `drawing_workflow.inspect_drawing_structure`；上游 45 个工具里的 3 个工程图工具之一）
   ② **写操作**（加视图 / 标注 / 表格 / BOM / 中心线 …）：`projected_view` `section_view`
      `detail_view` `auxiliary_view` `broken_view` `balloon` `center_mark` `hole_table`
      `revision_table` `bom` … ⇒ ★ **本阶段不做**（风险与验证成本高，计划已写明）
   ③ ★ **真缺的一小批**：`solidworks_inspect_drawing` 要**自己开件 + 出预览 + 落文件**
      ⇒ **对"当前已打开的图纸"没有轻量读数**。而 AI 的常见需求恰恰是
      「这图几张纸？当前图幅多大？有几个视图？」—— **不需要出预览、不需要落文件**。
⇒ ★★ **所以 W2 缩成一小批（3 个工具），且把上面三类写成文档**（A1 的「不做 + 原因」那一半）。

取什么：**当前活动工程图**的轻量只读读数 —— 图纸张数 / 当前图纸名与图幅 / 视图清单
★ 前置（照 W1 的教训，先写真机探针）：**怎么从 model 拿到 `IDrawingDoc` 与它的 sheet/view**
   —— ⚠ 已知 `drawing_workflow.py` 的只读函数首参叫 **`drawing_model`**（不是 `model`）⇒
     同一件事两个名字，包装层要做映射
来源 / license：本项目自身（MIT）；官方依据 `IDrawingDoc.GetCurrentSheet` / `ISheet` / `IView.GetNextView`
验收①：工具数 + 门禁；②：`python tools/capture_drawing_query_evidence.py` ⇒ `verdict: pass`
```

### W3 · 会话 / 文档 / 文件族（`specs/133`）· 约 85 分钟
```
取什么：文档信息读取 · 打开/关闭/保存的**只读与幂等**部分
⚠ 写操作（保存/另存）**本批不取** —— 它会改用户文件，验证成本与风险都高
来源 / license：本项目自身（MIT）
验收①：工具数 + 门禁；②：证据脚本 `verdict: pass`
```

### W4 · 零件特征族（`specs/135`）· 约 90 分钟 · ★★ **2026-10-01 轮 228 实测后改范围（见下）**

```
★★★ **改范围的理由（实测，不是估的）**：⑯ 那 28 个缺口名**逐个核过之后**——
   ① **已有对应 15 个**：`chamfer` `fillet` `extrude` `extrude_cut` `revolve` `shell` `loft`
      `sweep` `draft` `dome` `helix` `hole` `mirror` `linear_pattern` `pattern_circular` …
   ② **名字对不上 13 个**：`combine_bodies` `delete_body` `split_body` `scale_body` `move_body`
      `intersect` `wrap` `fill_pattern` `pattern_features` `save_body_as_part` `sweep` …
   ⇒ ★★ **这 28 个**全是"建 / 改"操作**，而原计划写的是 W4 取「**回读**」
     ⇒ ★ **两者不对口**：回读**已经有**（`solidworks_collect_model_summary` 就是特征树回读）
     ⇒ 照原计划做 W4 = **做重复功**（与 W2/W3 同一个教训）。
   ★★ 而实测查出一件更该做的事：**首参可注入、且没挂的"建特征"函数有 10 个** ——
     `sw_part.extrude_boss` / `extrude_cut` / `extrude_midplane` / `chamfer` / `fillet` /
     `shell` / `insert_dome` / `linear_pattern` · `sw_helix.insert_helix` ·
     `sw_sketch_edit.create_sketch_chamfer`
     ⇒ ★ 而 MCP 里**已经有** `solidworks_revolve_boss`（batch17）与
       `solidworks_create_hole_feature` ⇒ ★★ **不对称：会旋转、会打孔，却不会拉伸！**
     ▸ **base flange** 也是这一族（batch4 已挂）⇒ 短板在**最基础的拉伸/切除/倒角**。

★ **所以 W4 改为**：挂**建特征**的一小批（拉伸 / 切除 / 倒角），
  ★ 且**验证方式与只读批不同** —— 必须**读写配对**：
    建草图 → 拉伸/切除 → ★ **用只读工具回读断言形状真的变了**
    （`collect_model_summary` 看特征树 · `part_bounding_box` 看包围盒 · W1 的草图读数看草图）
  ⇒ 这是本阶段核心判据（A/B 配对）在"写"类批次上的自然延伸。
★ ⚠ 不做高风险写操作（保存 / 另存 / 删除）—— 本批**只改新文档**，收尾关件不保存。

来源 / license：本项目自身（MIT）；官方依据 `IFeatureManager.FeatureExtrusion3`（23 参数）·
  `FeatureCut4`（★ 事实 1：切除的正确入口是它，不是 `FeatureExtrusion3(Flip=true)`）
验收①：工具数 + 门禁；②：`python tools/capture_feature_evidence.py` ⇒ `verdict: pass`
```

### W5 · 检查 / 测量 / 反馈族（`specs/136`）· 约 70 分钟
```
取什么：质量属性 / 包围盒 / 干涉检查的只读查询
★ 本项目**已有** `solidworks_part_bounding_box` 等 ⇒ 本批取的是**缺口里剩下的那几个**
来源 / license：本项目自身（MIT）
验收①：工具数 + 门禁；②：证据脚本 `verdict: pass`
```

### W6 · 装配族（`specs/137`）· 约 85 分钟
```
取什么：装配结构的只读查询（零部件树 / 配合回读）
来源 / license：本项目自身（MIT）
验收①：工具数 + 门禁；②：证据脚本 `verdict: pass`
```

### W7 · 仿真载荷包装层（`specs/138`）· 约 95 分钟 · ★ **护城河**
```
★★ 为什么它排最后但最重要：**四家外部项目里 0 个做这块**（实测：只有 Eduardof0nt 有 3 个
   仿真工具，且无一个是"加力/加约束"）⇒ 这块**同时满足护城河的两个条件**（别人没做 + 用户用得上）
★ 第一步**不是写包装层**，而是**先核清是否已有**：
   `scripts/sw_simulation.py` 里有 `apply_fixed_restraint(study, *, model=None, ...)` 与
   `apply_normal_force(...)` —— ★ 它们**首参是 `study`（既有注入点）**，疑似**已经是包装层**
   ⇒ 先核清：**有就直接挂，没有才写**（「不要为了修房子创建公司」）
底层 helper 已具备：`_loads_and_restraints_manager(study)` · `_selected_dispatch_array(model, expected)`
来源 / license：本项目自身（MIT）；官方依据 `ICWLoadsAndRestraintsManager` 的 24 个 `Add*`
验收①：工具数 + 门禁；②：证据脚本 `verdict: pass`
```

---

## 三、每批的收工纪律（**约 20 分钟/批，已算进上面的估时**）

```
1. 该批的**验收①**（静态）与**验收②**（真机）都跑绿
2. 修 `harvest-report.md` 的偏离数字（`python D:\AI\SW\_fix_report183.py`）
3. 门禁链：sync_bundled_skill → check_union_conventions → gen_metrics → gen_harvest_digest
           → check_digest_freshness → check_report_freshness → release_check → check_spec_acceptance_paths
4. 全量 pytest（0 failed；★ 计数类测试报红就**同步更新那个数**）
5. `docs/metrics.md` 会由 `gen_metrics.py` 自动刷新 —— ★ **不要手改它**
6. Spec Kit 五件套（spec / plan / tasks / checklist / converge）落 `specs/<NNN>-<slug>/`
7. ROADMAP §一 游标 +5 行 · known-facts 追加一条
8. **两仓库各自 commit**（本地，**不 push**）
```

---

## 四、Spec Kit 规范（每批都要遵守，摘自宪法）

| 条 | 要求 |
|---|---|
| §I 来源 | `spec.md` **每条需求带「来源」**（官方文档 / 其它开源项目 / 四家外部 MCP / 本项目既有模式）|
| §II 官方源 | `plan.md` 列出要查的**官方源**（CHM 解包 / `C:\swapi` / 反射转储）与**冲突裁决顺序** |
| §III 查不到 | 出现「应该有」时**必须附一条实际查过的命令**；查不到就写「查不到」并停下换思路 |
| §IV license | **每个来源行带 license**（MIT 可抄；Apache-2.0 带 NOTICE；AGPL/GPL/无许可只读思想）|
| §V 可跑验收 | `tasks.md` **每条任务带 `→ 验收:`**，且是一条**能跑出绿的命令** |
| Flow-forward | 完成的特性目录**不可变**；需求变了**开新号** |
| 三处不许写 | 不写「当前进度」（在 ROADMAP 游标 / `capabilities.yaml` / `docs/metrics.md`）· 不重述六条铁律 · 不重述已知事实 |

---

## 五、不做的（有据）

```
❌ 不搬别家那 336 个"缺口" —— 16/17 个域都标了「我们有实现、只是没挂」⇒ 先挂自己的（少两道工序）
❌ 不把"成员没碰过"当待办 —— 8,238 个成员名里大半是属性 / 中间产物 / Obsolete，**不该碰**
❌ 不用"工具数"当进度 —— 会诱导凑数；进度看 `docs/metrics.md` 的**「真机碰过」那个数**
❌ 不重蹈事实 74（脚本层单位声明的跨模块门禁 —— 实测 4/4 假阳性）
❌ 不做"写操作"的高风险批（保存/另存/删除）—— 除非配对一次**可回滚**的真机验证
```

## 六、停下等用户的条件（**只有这几条**）

```
① 需要 push / 任何远端写入（红线：要批准）
② 需要碰注册表 / 系统层 / 破解相关（红线）
③ 真机操作可能造成不可逆后果（删文档 / 覆盖用户数据）
④ 同一处**连续 3 次**修不好（事实 53：回退 + 记证据，不再试）
⑤ 需要用户才能提供的东西（凭据 / 业务口径 / **Motion 加载项**）
★ 除以上**一律自行判断并继续**；不确定的写进「未查证」，不要停下来问。
```
