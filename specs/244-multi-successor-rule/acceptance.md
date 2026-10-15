# 244 · 验收记录

日期：2026-10-09。结论：**离线判据全绿（4/4）**，且**红基线成立（清空登记表 ⇒ 正好 6 条失败）**。
runtime / product = **not_run**（本特性**不涉** COM，纯静态）。

---

## 一、实际命令与读数

受管解释器：`C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe -B`（★ 路径写 3.13.12，二进制实报 **3.13.14**）。

### 1. 先量（Phase 1）

| 命令 | 读数 |
|---|---|
| `output/_probe244_multi_successor.py` | 索引总条目 **1671** · **多后继条目 254** · 涉及成员名 **217** · 真树被调成员名 **910** · **真树被调名 ∩ 索引全部条目(按名) = 82** · **按名命中多后继条目 = 14** |
| `output/_probe244_dump.py` | 152 行 · 14 个名 · 逐条导出官方原句与全链接 |
| `output/_probe244_rule.py` | **无同名链接 243** · **有同名-索引取对了 5** · **有同名-索引取错了 6** |

### 2. ★★ 红基线（T005，本特性的核心证据）

清空 `_KNOWN_WRONG` 后跑 `test_same_name_link_is_the_real_successor`：

```
RED BASELINE 复现 ✓
有同名链接但索引取错、且未登记偏差 6 条：
  IFeature::GetBody 索引给 IFeatures::GetFaces，真后继应是 ['IFace2::GetBody']
  IFeature::IGetBody 索引给 IFeatures::GetFaces，真后继应是 ['IFace2::IGetBody']
  IModelDoc2::SketchTrim 索引给 ISketchManager::SketchExtend，真后继应是 ['ISketchManager::SketchTrim']
  INote::IGetTextFormat 索引给 IAnnotation::GetTextFormat，真后继应是 ['IAnnotation::IGetTextFormat']
  INote::ISetTextFormat 索引给 IAnnotation::SetTextFormat，真后继应是 ['IAnnotation::ISetTextFormat']
  ISheet::ICreateOLEObject 索引给 IModelDocExtension::CreateOLEObject，真后继应是 ['IModelDocExtension::ICreateOLEObject']
```

⇒ ★ **判据不是空判据**（能报出正好 6 条，且报的是**真靶子**）。

### 3. 绿读数（T004/T006）

```
  PASS test_known_wrong_registry_matches_index
  PASS test_multi_successor_count_is_frozen
  PASS test_registry_entries_have_evidence
  PASS test_same_name_link_is_the_real_successor
结果: 4/4 通过
```

### 4. 生成器未改（T008）

`git status --short tools/build_obsolete_index.py` ⇒ **无输出** ✓（FR-005）

---

## 二、核心事实（本轮量出来的）

### 事实 A：★ 「多后继」不是「两个真后继」

254 条里，**243 条根本没有同名链接** —— 那些多链接的形态是：

| 形态 | 例 | 第一个链接对不对 |
|---|---|---|
| **后继 + 进程内变体**（`I` 前缀） | `GetArcs2` → `GetArcs4` + `IGetArcs4` | ✅ 对（`I` 版按已知事实 47 调不到） |
| **后继 + 数据接口** | `FeatureLinearPattern5` → `CreateFeature` + `ILinearPatternFeatureData` | ✅ 对（第二个是读 Remarks 用的，不是后继） |
| **Get 后继 + Set 后继** | `KFactor` → `GetCustomBendAllowance` + `SetCustomBendAllowance` | ⚠️ 看用途（读用 Get、写用 Set） |

⇒ ★ **「254 条要逐条复核」这个前提本身是过宽的** —— 真正需要复核的是**有同名链接的 11 条**。

### 事实 B：★★ 索引取错的**只有 6 条**，且**全是「同名链接」形态**

| 被废弃成员 | 索引给的（错） | 真后继 | 依据 |
|---|---|---|---|
| `IFeature::GetBody` | `IFeatures::GetFaces` | `IFace2::GetBody` | 语义完全不符（GetBody → GetFaces） |
| `IFeature::IGetBody` | `IFeatures::GetFaces` | `IFace2::IGetBody` | 同上 |
| `IModelDoc2::SketchTrim` | `ISketchManager::SketchExtend` | `ISketchManager::SketchTrim` | ★ **签名语义实证**（见下） |
| `INote::IGetTextFormat` | `IAnnotation::GetTextFormat` | `IAnnotation::IGetTextFormat` | 进程内变体对进程内变体 |
| `INote::ISetTextFormat` | `IAnnotation::SetTextFormat` | `IAnnotation::ISetTextFormat` | 同上 |
| `ISheet::ICreateOLEObject` | `IModelDocExtension::CreateOLEObject` | `IModelDocExtension::ICreateOLEObject` | 同上 |

**★ `SketchTrim` 的实证**（本轮读官方页核的）：

| 成员 | 签名 | Description |
|---|---|---|
| `IModelDoc2::SketchTrim` | `(Op, SelEnd, X, Y)` | 被废弃的 |
| **`ISketchManager::SketchTrim`** | `(Option, X, Y, Z)` | **"Trims the selected sketch entities."** ← 真后继 |
| `ISketchManager::SketchExtend` | `(X, Y, Z)` | **"Adds to the length…"** ← 是**延伸**，不是剪裁 |

### 事实 C：真树的靶子规模

真树在调的 **82** 个废弃名里，落在多后继条目的有 **14** 个；
其中落在**错后继**里的只有 **1** 个 —— `SketchTrim`（调用模块 `sw_sketch_edit_ops.py`）。

---

## 三、本轮踩的坑（★ 下一轮别重走）

1. ★★ **量测口径凭印象写 ⇒ 读数差 4**：第一版探针把包装函数硬编码成
   `("get_com_member", "get_com_member_raw")` —— **漏了 `call_com_member` / `call_assembly_doc`，
   还编了一个不存在的 `get_com_member_raw`** ⇒ 「真树在调 ∩ 索引」读成 **78**，真值 **82**。
   ⇒ ★ **定则：口径要么 import，要么逐字抄**（真口径在 `tests/test_deprecated_entry_interlock.py:101`）。
   ★ 这与 243 的「自造过滤器差 3 倍」是**同一族错误**（读数看起来像结论）。
2. ★ **「254 条」这个前提过宽**（事实 A）—— ★ 先量把待办的规模从 254 压到 **11**（有同名链接的），
   真正错的只有 **6**。⇒ ★ **交接单的待办规模也要核**（本仓已连续多轮核出交接单前提有误）。

---

## 四、未过门（不得当通过）

1. **6 条错后继未修** —— ★ 修要动 `tools/build_obsolete_index.py`，那要**重跑索引 + 复核全部 1671 条**，**属独立工作**（FR-005）。
   本轮只做**登记 + 判据化**。
2. **3 条真后继是进程内变体**（`IGetTextFormat` / `ISetTextFormat` / `ICreateOLEObject`）——
   结构上索引取错了，但按**已知事实 47** 那些 `I` 前缀接口在 pywin32 上**调不到**
   ⇒ **消费端要不要用是另一个问题**，本轮只判「索引取错了」。
3. **14 条命中名里只核了 1 条（`SketchTrim`）的语义** —— 另 5 条按「同名规则」判定，
   **未逐条读 Description 复核语义**（同名 + 同族是强信号，但非语义证明）。
4. **未跑门禁全套**（T009 在本轮时间窗内未执行）—— ★ 本特性只新增一个 `tests/*.py`，不改 `scripts/`、不改 `mcp-server/`。
5. 未提交、未部署、未调 COM、未派成员。
