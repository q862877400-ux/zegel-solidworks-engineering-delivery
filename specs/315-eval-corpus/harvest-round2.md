# A 阶段扫描汇总 · **仓库里早就有的（第二批）**

**来源**：业主 2026-10-14「A → B 一次做完中间别问我」
**A = 继续扫那 6 处**（★ 上一轮列的还没读的）

---

## §1 ★★★ `subskills/solidworks-threaded-holes/references/threaded-hole-lessons.md`

### ① ★★ **三组枚举不能混用**（★ 逐字）

```text
底孔 FeatureCut4:
  Blind      = swEndCondBlind (0)
  ThroughAll = swEndCondThroughAll (1)

ThreadFeatureData:
  Blind       = swThreadEndCondition_Blind (0)
  Revolutions = swThreadEndCondition_Revolutions (1)
  UpToSelect  = swThreadEndCondition_UpToSelection (2)

CosmeticThread:
  Blind   = swEndConditionBlind (0)
  Through = swEndConditionThrough (2)
```

### ② ★★ **贯穿底孔必须用 `T1=1`**

> 贯穿底孔必须用 `FeatureCut4(..., T1=1, ...)`。使用「**厚度 + 1 mm**」的盲孔
> 虽然视觉上穿透，但**特征语义、后续修改和工程图识别都不正确**。

### ③ ★★ **参数验证底线**（★ COM 调用前必须拒绝）

- NaN/无穷大、非正的基体尺寸、底孔、深度和倒角
- **底孔直径 ≥ 公称直径**
- 螺纹深度 > 盲孔底孔深度，或贯穿螺纹深度 > 板厚
- 孔中心越出基体，或没为**螺纹大径和孔口倒角保留边界**
- ★ 表外公制螺距却没有显式 `--tap-drill` ⇒
  **攻丝底孔受切削材料/丝锥类型/螺纹百分比影响，不能只靠 `D-P` 通用估算**

### ④ ★★★ **特征持久化证据**（★ 逐字）

> Thread/CosmeticThread **返回非空 COM 对象只是"尝试创建"，不是最终证据**。
> 脚本在 `ForceRebuild3(False)` 后遍历 `FirstFeature/GetNextFeature`，
> 并**递归遍历 `GetFirstSubFeature/GetNextSubFeature`**，输出：
> - `thread_attempts`：每种 API 的尝试结果和失败原因
> - `thread_evidence`：底孔、倒角、真实 Thread、CosmeticThread 和 3D 证据草图
>   **是否留在特征树**
> - `thread_status`：`real-thread-verified` / `cosmetic-thread-verified` /
>   `visible-helix-verified`；**若只剩自定义属性，模板会阻断交付**

**★★★ 关键**（逐字）：

> SolidWorks 官方示例说明 **CosmeticThread 是孔或切除的子特征**。
> **只遍历顶层特征会把已经持久化的 CosmeticThread 误判为丢失**；
> 当前证据收集**已包含子特征**。

### ⑤ ★ 3D 螺旋线：**不能四舍五入圈数**

> 旧实现将 `thread_depth / pitch` 四舍五入为整数圈，**会改变真实螺距**。
> 例如 **16 mm 深、P=1.25 mm 应为 12.8 圈，不应改为 13 圈**。

**★ 且**：3D 草图**不是可切削牙型**，**不得宣称为 CAM 实体螺纹**。

### ⑥ ★ **尚未覆盖的制造细节**（★ 如实记）

> 当前盲孔底孔**仍是平底切除**，没有建模**标准钻尖、有效全牙深度、不完整牙、
> 攻丝退刀量和排屑空间**。因此「底孔 + Thread」是良好的 CAD 和工程图语义，
> 但**不能在没有工艺复核的情况下宣称已完成**。

---

## §2 ★★★ `subskills/solidworks-vibecad/prompts/solidworks_parametric_planner.md`

**这是一份现成的「规划器提示词」** —— ★ 与我做的「做法规划」**同一个目的**。

**★ 规划原则（逐字）**：
1. 先识别**零件类型**：安装座、连接块、支架、板件、轴类、外壳、装配体
2. ★ 所有尺寸统一 **mm**，角度 **deg**
3. ★★ **对螺纹孔必须区分**：公称直径、攻丝底孔、螺纹深度、底孔深度、孔口倒角
4. ★★ **CNC 件必须保持稳定特征顺序**：基础体 → **外轮廓圆角/倒角** →
   孔槽切除 → 孔口倒角 → 审查
5. ★ 不确定的参数**可以用保守默认值，但必须写入 `assumptions`**
6. ★ **不要承诺 `ThreadFeatureData` 一定成功**；螺纹表达要允许
   真实 Thread / CosmeticThread / 可见 3D 螺旋线 / 属性兜底
7. ★ 不要用未封装的长参数 API，除非 `api_lookup_required` 标 true
8. ★★ 输出**必须包含审查计划**，不能只到保存模型

**★ 禁止（逐字）**：
- 禁止输出 VBA 或 Python 宏正文
- ★ 禁止**凭空编造**不存在的 SolidWorks API 签名
- ★★ 禁止把**外观成功当成几何成功**
- 禁止跳过保存、导出和预览审查

---

## §3 ★★ `docs/known-facts.md` 事实 432：**槽口四种 = 一条方法 + 一个枚举**

**`ISketchManager.CreateSketchSlot`（14 参）**：

```
CreateSketchSlot(SlotCreationType, SlotLengthType, Width,
                 X1,Y1,Z1, X2,Y2,Z2, X3,Y3,Z3,
                 CenterArcDirection, AddDimension)
```

**★ 两个枚举（★ 值来自反射）**：
```
swSketchSlotCreationType_e :  0=line · 1=center_line · 2=arc · 3=3pointarc
swSketchSlotLengthType_e   :  0=CenterCenter · 1=FullLength
```

**★ 真机（`tools/prove_sketch_slot_four_types.py`）**：
★ **四个 type 全成** ⇒ 均令草图段数 **0 → 5** · 回 `CDispatch`。

**★★ 命中我的 `L3-008`**（半圆端槽）—— ★ 我只写了「用槽口工具画」，
★ 而**它有四种类型 + 两种长度口径**（★ `CenterCenter` vs `FullLength`
**正是官方 2026 SP1 那条「圆弧中心之间 vs 圆弧切线长度」**）。

---

## §4 ★★ `docs/known-facts.md` 事实 461：**草图段有名字、按名能选中**

**★★ 两件事只有从官方例子里才知道**（逐字）：

> ① ★ **草图段有名字**（`"Line1"` / `"Line3"`）、**而按名能选中**
>    （★ 与事实 32 **不矛盾**：32 说的是**边/面**）
> ② ★★ **必须先抑制尺寸对话框** ——
>    它正是 swapi 那句**被截断的前置**

**★ 调用序（逐字）**：
```
InsertSketch(True) → CreateCenterLine → CreateLine×3
→ SelectByID2("Line1", "SKETCHSEGMENT", x,y,z, False, 0, Nothing, 0)
→ SelectByID2("Line3", "SKETCHSEGMENT", x,y,z, True, 0, Nothing, 0)
→ ClearSelection2(True) → 再选一次
→ SetUserPreferenceToggle(swInputDimValOnCreate, False)
→ AddSymmetricDimension(x, y, z) → 回 DisplayDimension
```

**★★ 判据**：★ 对照（什么都不选）**也回 `CDispatch`** ⇒
★ **故判据必须看「草图尺寸计数」**。

---

## §5 ★ `subskills/solidworks-engineering-drawing/references/`

### `drawing.md`
- ★ GB/T 路线**默认第一角投影**：俯视位于主视下方，右视位于主视左侧
- ★ `SetupSheet6` / `NewSheet4` 的投影参数**必须和布局一致，并在生成后回读**
- ★★ `InsertModelAnnotations3/4` 返回值**不能单独作为尺寸已插入证据**，
  必须**再次读取真实 `DisplayDimension`**
- ★ **图框文件名只代表候选证据**，不能证明模板内容符合 GB/T
- ★ PDF/BMP 输出**必须存在且非空**；PDF 文字边界**只能用于风险筛查**

### `review.md`
- ★★ **三层证据**：结构 / 制造 / 视觉 —— **任何一层缺失都不能升级为无人值守交付**
- ★★ **尺寸 ID 必须精确匹配**；★ **`D1` 不得命中 `D10`**
- ★★ **螺纹规格只接受专用螺纹/孔标注证据**，
  **不能由同名数字或光孔直径推断**
- ★ `BOM` 只接受 `swTableAnnotation_BillOfMaterials`，要求**非空数据行**
- ★★ **基准标签精确匹配**，**`A` 不得命中 `AB`**
- ★ 孔标注必须来自 `IDisplayDimension.IsHoleCallout`；
  **不能用相同文字的普通注释替代**

---

## §6 ★★ A 阶段**净收获**（★ 汇总）

| # | 发现 | 命中我的哪条 |
|---|---|---|
| **1** | ★★★ **CosmeticThread 是孔/切除的子特征** —— 只遍历顶层会**误判为丢失** | 通用判据 |
| **2** | ★★ **返回非空 ≠ 持久化** ⇒ 必须 `ForceRebuild3` + **递归子特征**回读 | 通用判据 |
| **3** | ★★ **贯穿底孔必须 `T1=1`**，不能用「厚度+1mm」 | `L3-001` 等所有通孔 |
| **4** | ★★ **槽口四种类型 + 两种长度口径**（`CenterCenter`/`FullLength`） | **`L3-008`** |
| **5** | ★★ **参数验证底线**（底孔 ≥ 公称 ⇒ 拒） | `L3-009/015` |
| **6** | ★ **3D 螺旋线不能四舍五入圈数**（改螺距） | `L3-046` |
| **7** | ★★ **螺纹三组枚举不能混用** | `L3-046` |
| **8** | ★★ **草图段有名字、按名能选中**（★ 与边/面不同） | 通用判据 |
| **9** | ★ **必须先抑制尺寸对话框** | 通用判据 |
| **10** | ★★ **CNC 特征顺序**（外轮廓圆角/倒角在孔槽前） | ★ 已在 §B 用过 |
| **11** | ★ **不确定的参数可用保守默认值，但必须写入 `assumptions`** | 通用原则 |
| **12** | ★★ **禁止把外观成功当成几何成功** | 通用原则 |
| **13** | ★★ **三层证据缺失不得升级无人值守** | 通用判据 |
| **14** | ★★ **ID 精确匹配**（`D1` ≠ `D10` · `A` ≠ `AB`） | 工程图判据 |
| **15** | ★★ **螺纹规格不能由光孔直径推断** | `L3-046` |
