# S3 施工准备 · 三条 E3 缺陷与一条 E1 限制

**日期**: 2026-10-25

**对应任务**: `specs/350-first-part-delivery/tasks.md` T009 / T010

**依据**: `docs/ENGINEERING-PATH.md` 第四节 E3「必须读什么」

---

## 一、E3 的判据原文

> **必须读什么**：回读特征类型、错误/警告、引用与父子依赖；
> 实际编辑前序草图或参数并验证后续。
> **主尺寸/基准/孔位必须有稳定语义引用，跨重建不依赖选区或下标。**

## 二、★ 发现的真实缺陷：计划里存了下标

`scripts/engineering/planner.py` 有三处 chamfer 步骤写的是下标：

```
planner.py:270   params={"selection": "index:0", "distance_mm": 1.0, "angle_deg": 45.0}
planner.py:568   params={"selection": "index:0", "distance_mm": 2.0}
planner.py:578   params={"selection": "index:0", "distance_mm": 2.0}
```

### 为什么这是缺陷（不是风格问题）

`scripts/engineering/reference_resolver.py` 的 `LIMITATIONS` 自己逐字写着：

> **索引不跨编辑保持** —— 「Anchors are exact for **fresh-doc replay**…
> but **NOT durable across edits**」⇒ 改完模型后，之前算出来的
> face/edge index 全部作废，必须重查

⇒ 计划里存 `index:0`，改板宽之后「第 0 条边」可能已经是另一条边。
   这正好违反 E3 那句「跨重建不依赖选区或下标」。

### 工具层也只给了两种都不可跨编辑的形态

`mcp-server/tool_registry.py` 的 `_SEL` 逐字：

> Declarative EDGE selection: `'__current_selection__'` (use whatever is already selected)
> or `'index:<n>'` (the n-th edge on the body, 0-based).

- `index:<n>` —— 下标会漂
- `__current_selection__` —— 取决于调用时选了什么，不是模型属性

### 已经有现成的正确形态，只是没接上

`reference_resolver.resolve()` 支持三种**几何事实**形态：

| 形态 | 例 | 为什么稳定 |
|---|---|---|
| 方向语义 | `+z` / `-z` / `+x` / `-x` / `+y` / `-y` | 法向 + 质心，改参数后仍是同一方向的面 |
| 语义名 | `top_face` | 法向 +Y 且质心 Y 最大 |
| 几何锚点 | `near:x,y,z` | 取离该点最近的边/面，`resolve()` 明确说「跨重建稳定」 |

⇒ **正确做法**：计划里存语义选择器，`resolve()` 在**用时**解析成下标。
   下标是**计算中间量**，不是要保存的引用。

## 二之二、★★ 更严重的发现：语义选择器是孤岛

上一节说「正确形态早就有，只是没接上」。核查后发现比这更严重。

全仓引用 `reference_resolver` 的文件只有四个：

```
scripts/engineering/reference_resolver.py       ← 自己
scripts/engineering/acceptance/e2_e3_solid.py   ← 只在 reason 文本里提名字，未 import
tests/test_reference_resolver.py                ← 它自己的测试（18 条全绿）
tests/test_acceptance_e3_reference.py           ← 同上，只在 docstring 提名字
```

⇒ **生产代码零引用。** 那套语义选择器（`+z` / `top_face` / `near:`）
实现完整、测试齐全，但**没有任何调用方**。

### 为什么接不上（这是关键，不是懒）

`reference_resolver.resolve()` 需要 `list[FaceInfo]` / `list[EdgeInfo]`：

```
FaceInfo(index, normal, centroid, planar, bbox)   ← 需要法向与质心
EdgeInfo(index, midpoint)                          ← 需要中点
```

而现成的取数函数给不出这些：

| 函数 | 给什么 | 缺什么 |
|---|---|---|
| `sw_selection_spec.entities_on_body(model, kind)` | COM 对象列表 | — |
| `sw_selection_spec.entity_geometry(model, kind, i)` | FACE 只给 `area_mm2` | **没有法向、没有质心** |

⇒ 要接上，必须新增 COM 调用读面法向、面质心、边中点。

★★ **这些成员名必须按铁律 4 先三源互证，不能随手写。**
本轮**不做**这件事 —— 塞一个未核实的成员名进去，
就是「凭印象写一个成员然后看着像对的」（铁律 1 明令不可接受）。

### 所以 T009 的正确修法是五段，不是一段

| 段 | 内容 | 状态 |
|---|---|---|
| ① | 三源互证查面法向 / 面质心 / 边中点的官方成员名 | ⬜ 待做 |
| ② | 写 `collect_faces()` / `collect_edges()` 把模型读成 `FaceInfo` / `EdgeInfo` | ⬜ 待做 |
| ③ | 让 `sw_selection_spec.resolve_entity()` 接受语义选择器 | ⬜ 待做 |
| ④ | `planner.py` 三处 `index:0` 换成语义选择器 | ⬜ 待做 |
| ⑤ | 真机验证：改主参数后语义选择器仍指同一条边 | ⬜ 待做 |

★ 第 ① 段是硬前置。跳过它去写 ②③④，就是在没有官方依据的情况下猜成员名。

## 三、把这条缺陷做成了判据

`scripts/engineering/acceptance/e2_e3_solid.py` 新增：

```
collect_reference_stability(*, target, steps) -> Observation
judge_reference_stability(obs, *, requirement_id) -> CheckResult
```

`check_id = "E3.reference_stability"`。

判据：

| 计划里的形态 | 结论 |
|---|---|
| `index:<n>` | **fail** |
| `__current_selection__` | **fail** |
| `+z` / `top_face` / `near:x,y,z` | pass |
| 不涉及选区 | pass |
| 没有步骤 | unknown |

实测：拿真实 `plan_from_requirement()` 的输出跑，**`plate_chamfer` 那条候选被判 fail**，
其余四条 pass。这证明判据不是纸面上的，它抓到了当前实现的具体缺陷。

`tests/test_acceptance_e3_reference.py` 16 条测试，其中两条用真实 planner 输出做回归：
- `test_planner的倒角候选仍带下标` —— **记录现状**。一旦 planner 改成语义选择器，
  这条会转红，那时应把断言反过来（缺陷已修）
- `test_planner的倒角候选命中chamfer_step` —— 精确定位被抓的是 chamfer 步骤

## 三之二、T009 第 ① 段完成：三源互证的结果

上一节说「第 ① 段（三源互证查法向/质心/中点）是硬前置」。本节把它做完了。

### `IFace2.Normal` —— ✅ 三源互证成立

| 源 | 读数 |
|---|---|
| `C:\swapi`（`types/IFace2/Normal.md`） | `System.object Normal {get; set;}`；Returns「Array of 3 doubles (i,j,k)」；NOTE「get-only，**Set is not implemented**」 |
| 出厂反射（`_raw/reflect/iface_sldworks.txt`） | `Object get_Normal()` |
| 官方 CHM 解包 | `sw_know verify` 的「草图/零件特征」域报 `[OK]`（覆盖自检，未逐页比对） |

⇒ 读平面法向**有官方入口**，用法：`Normal` → 3 个 double 的数组。

### 面质心 —— ❌ 三源确认**不存在**

全库检索 `Centroid`，只命中两个**无关**成员：

```
types/ISketchPatternFeatureData/UseCentroid
types/ITablePatternFeatureData/UseCentroid
```

反射转储的 `IFace2` 段落里也没有任何质心成员（只有 `Object get_Normal()` / `Double GetArea()` / `Object GetBox()`）。

⇒ **`FaceInfo.centroid` 这个字段没有直接 API 可填。**

这是 `reference_resolver` 的第二个问题：它不仅没被接上，
它假设的输入模型（面质心）在 API 里根本不存在。

### 可用的替代（但要如实标注是近似）

| 想要 | 可用什么 | 性质 |
|---|---|---|
| 面质心 | `IFace2.GetBox()` 的盒中心 | **近似**（平面矩形面上等价；曲面上不等价） |
| 面质心 | `GetTessTriangles()` 三角面片重心加权 | **近似**（离散化，付费换精度） |
| 边中点 | `GetStartVertex` / `GetEndVertex` 的两点均值 | **精确**（`sw_selection_spec.entity_geometry` 已给 start/end，直接平均即可，**无需新 COM 调用**） |

★ 边中点这一项**已经不用做**：`entity_geometry(model, "EDGE", i)` 已经回
`start_mm` / `end_mm`，中点取平均即可，纯计算。

### 所以 T009 的剩余四段这样改

| 段 | 内容 | 变化 |
|---|---|---|
| ② | 写 `collect_faces()` | 用 `IFace2.Normal` 读法向（已三源互证）；**质心用 `GetBox` 盒中心，并标注为近似** |
| ② | 写 `collect_edges()` | **不需要新 COM**：用现成的 `entity_geometry` 的 start/end 求均值 |
| ③ | `resolve_entity()` 接受语义选择器 | 依赖 ② |
| ④ | `planner.py` 三处 `index:0` 换语义选择器 | 依赖 ③ |
| ⑤ | 真机验证：改主参数后仍指同一条边 | 依赖 ④ |

★★ **一个必须写进代码的限制**：`top_face` 的语义是「法向 +Y 且质心 Y 最大」。
   对平面矩形（首件安装板）盒中心与质心等价，所以**首件场景下这个近似不引入误差**。
   但对曲面/异形面，盒中心 ≠ 质心 ⇒ 那时 `top_face` 会选错。
   ⇒ 代码里必须把这条写成显式限制，不能等到 S4 装配异形件时才踩。

## 三之三、T009 第 ③ 段完成 / 第 ④ 段受阻：不是换个字符串就能修

### ③ 段已做（语义选择器接进 `resolve_entity`）

`sw_selection_spec.resolve_entity()` 现在多认一类选择器：

| 类 | 形态 | 可跨重建 |
|---|---|---|
| 现有 | `__current_selection__` | ❌ 取决于调用时选了什么 |
| 现有 | `index:<n>` | ❌ 下标会漂 |
| 现有 | COM 对象 | — |
| **新增** | `+x`/`-x`/`+y`/`-y`/`+z`/`-z`、`top_face`、`near:<x>,<y>,<z>` | ✅ 几何事实 |

分流方式：语义形态 ⇒ `reference_collect.resolve_semantic()` 先解析成下标，
再走原有 `index:` 那条路。**下标只是中间量，不保存。**

`reference_collect.py`（新模块）负责把模型读成 `FaceInfo` / `EdgeInfo`，
`reference_resolver`（纯模块）保持不碰 COM。

### ④ 段受阻：三个问题都不是「换个字符串」

原以为是「把 `index:0` 换成 `+z` 就行」。实测发现不行，三个问题：

#### 问题 1：倒哪条边？**意图未定**

`planner.py` 三处 `derive` 逐字：

```
:270  derive="★ 端部倒角 1×45°（★ 需求要求）"      ← 轴类「两端倒角」
:568  derive="★ 倒角后置（★ 避免早期拓扑依赖）"     ← 板
:578  derive="★ 倒角后置"                          ← 板（无孔时）
```

三处都**没说倒哪条边**。`index:0` 是「随便一条」的占位，不是「正确的那条」。

⇒ 换成语义选择器之前，必须先回答：板的倒角是倒**顶面外轮廓**？还是**四角竖边**？
   这是工程意图，不是代码问题。**不能猜**（铁律 1：不可凭印象写）。

#### 问题 2：工具层只支持**单边**

`sw_selection_spec.resolve_selection()` 逐字：

> 同 `resolve_entity`，但**只返回回读到的选区计数**

而 `resolve_entity()` 选**一个**实体。⇒ `chamfer` 的 `selection` 只能选中一条边。

一块 100×60×20 的板有 12 条边。若意图是「外轮廓倒角」，那是 4 条边 ——
**当前工具层做不到**。

#### 问题 3：方向语义对 EDGE 不起作用

`reference_resolver.resolve()` 里方向形态走的是 `top_face(faces, axis=...)`
—— **只在面上找**。而 `chamfer` 要的是**边**。

⇒ 想让 `chamfer` 用上语义选择器，现在**只有 `near:` 锚点可用**
（例如 `near:<w/2>,0,<d>` 指到顶面前边）。而锚点坐标要由 plam 算，
还牵扯单位（本仓 COM 侧用米、参数用毫米）。

### 所以 ④ 要先回答三个问题，才能动手

| # | 问题 | 谁能答 |
|---|---|---|
| 1 | 板的倒角是倒外轮廓、四角竖边、还是别的？轴类的「端部倒角」是哪一端？ | 工程负责人 |
| 2 | 若是外轮廓（多条边），是否需要给 `chamfer` 加**多选**能力？ | 需三源互证多选 API |
| 3 | 若只需单边，用 `near:` 锚点的坐标怎么由参数算（含单位换算）？ | 可实现，但要定规则 |

★ 在第 1 问有答案之前，④ **不做**。
   把 `index:0` 换成一个看似合理的方向语义（如 `+z`），只是把「明显是占位」
   变成「看着像有依据的错」—— 那比现在更危险。

★ ⑤ 段（真机验证「改主参数后语义选择器仍指同一条边」）依赖 ④，也顺延。

### 当前状态（供报告引用）

| 段 | 内容 | 状态 |
|---|---|---|
| ① | 三源互证查法向/质心/中点 | ✅ 完成（见「三之二」） |
| ② | `collect_faces()` / `collect_edges()` | ✅ 完成（`reference_collect.py`） |
| ③ | `resolve_entity()` 接受语义选择器 | ✅ 完成 |
| ④ | `planner.py` 三处 `index:0` 换语义选择器 | ⏸ **停线：意图未定** |
| ⑤ | 真机验证跨重建仍指同一条边 | ⬜ 依赖 ④ |

## 四、T010 孔型/孔位逐项回读 —— 已落判据

### 发现：既有能力覆盖了三分之二

`scripts/sw_review.py:validate_hole_positions()` 已经逐孔给
「孔径误差 / 孔位误差 / 是否通过」，且带独立参考基准
（`part_loop.reference_hole_positions()` 手算孔坐标）。
**不需要新造**，直接复用（铁律 1）。

### 但它自己声明了一个缺口

`validate_hole_positions` 的 docstring 逐字：

> 该函数只证明孔径与轴线位置。盲孔深度、通孔状态和沉头类型必须继续使用
> 特征参数回读或创建函数返回的 feature_evidence 交叉验证。

⇒ **孔型（通孔 / 盲孔 / 沉头 / 螺纹）不在它覆盖范围**。

### 新增判据补上这一项

`e2_e3_solid.py` 新增：

```
collect_hole_readback(*, target, requested, measured, ...) -> Observation
judge_hole_readback(obs, *, requirement_id) -> CheckResult
```

`check_id = "E2.hole_readback"`。判据：

| 情形 | 结论 |
|---|---|
| 孔数不符 | **fail**（挡住「两个 φ12 换四个 φ6」这类聚合量代替） |
| 孔径/孔位超差 | **fail**（复用 `validate_hole_positions`） |
| B-Rep 给不出孔型 | **unknown**（★★ 没测到 ≠ 合格） |
| 孔型不符 | **fail** |
| 要求里的孔型不在词表 | **fail**（封闭词表五种） |
| 全对 | pass |

孔型词表：`through` / `blind` / `counterbore` / `countersink` / `threaded`。

`tests/test_acceptance_e2_hole.py` 18 条，含：
- 数量不对时拒绝（核心：不许用体积之类聚合量代替）
- **孔型给不出时判 unknown 不是 pass**（最重要的一条）
- 每种允许孔型都能通过

### 孔型匹配为什么按孔位就近

实测孔**没有 `id`** —— `collect_geometry_measurements()` 只给直径/位置/轴线。
⇒ 按孔位就近配对。孔位已在前面通过容差校验，所以配对是明确的
（除非两孔重合，而那本身是设计错误）。

## 五、S3 要改什么（按优先级）

| # | 改什么 | 判据 |
|---|---|---|
| 1 | 工具层 `selection` 接受语义选择器 | `judge_reference_stability` 对 `+z` / `near:` 判 pass |
| 2 | `planner.py` 三处 chamfer 改成语义选择器 | `test_planner的倒角候选仍带下标` 转红后按新语义更新 |
| 3 | 孔位也用语义引用（`near:` 锚点） | E5 的孔位标注能绑定到真实图纸对象 |
| 4 | 计划里**不缓存**下标 | `reference_resolver.LIMITATIONS` 第 1 条 |
| 5 | 孔型从特征参数回读接上 | `judge_hole_readback` 从 unknown 转 pass |

⚠ 第 1、5 项要改 `mcp-server` 的工具层与真机回读，**必须真机验证** —— 留 S3 真机部分。
   本文件交付的是判据（能让缺陷可见），不是修复。

## 六、E1 的一条限制（不再叫「待查」）

三源确认：SolidWorks API **没有数值自由度读取入口**
（1032 接口 / 20627 成员零命中，见 `source-verification.md`）。

⇒ E1 有两层：

| 层 | 信号 | 能判吗 |
|---|---|---|
| 是否全约束 | `GetConstrainedStatus()` 枚举 | ✅ 能 |
| 剩几个自由度 | 无 API | ❌ 不能 |
| 有意保留的自由度 | 无 API | ❌ 不能（只能靠需求声明） |

所以「有意保留自由度」这一项**无法事后校验** —— 它必须写进需求冻结表，
由工程负责人明示，不能在产检时反读。已记入 `requirements.md`。

## 七、未做的（如实）

1. **未改 `planner.py`** —— 改它要同时改工具层并真机验证，属 S3 真机部分
2. **未改工具层 `selection`** —— 同上
3. **未接真机** —— 本文件全部离线
4. **T010（孔型/孔位逐项回读）未做** —— 它需要真机才能验证读回值对不对；
   离线能做的是判据本身，已并入第 4 项
