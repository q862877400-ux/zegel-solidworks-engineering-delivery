# S3 · E3 特征树可编辑 —— 真机验成

**日期**: 2026-10-25

**探针**: `tools/probe_s3_e3_feature_tree.py`

**编号**: `E3.tree` · 采集器 `collect_feature_tree` · 判定器 `judge_feature_tree`

**依据**: `docs/ENGINEERING-PATH.md` 第四节 E3

> 回读特征类型、错误/警告、引用与父子依赖；**实际编辑前序草图或参数并验证后续**
> 负例：导入死实体冒充原生特征、悬空引用、错误配置、目标对象漂移
> 替代品：特征数大于零、STEP 可打开

---

## 一、结论

**E3 在真机上验成。**

在交付件 `板1_rev-1` 的副本上：

```
① 特征 15 个 · 错误/警告 = 0
② 改 `D1@草图1`（板宽）100.0 → 120.0 —— 改的是**已有**尺寸
③ 下游全部跟随：
     错误数仍 0
     特征数 15 不变（没有东西被吃掉）
     孔特征 4 个仍在
     包围盒 X  100.0 → 120.0 mm
```

| 判据 | 结果 |
|---|---|
| 回读特征类型 | ✅ `ProfileFeature` / `Extrusion` / `ICE` |
| 错误 / 警告 | ✅ 0 / 0 |
| 父子依赖 | ✅ 每个特征都有父；草图子=1、拉伸子=4 |
| **实际编辑前序并验证后续** | ✅ 四条下游判据全 True |
| 导入死实体（负例） | ⬜ 未做真机 STEP 导入，判定器侧有测试覆盖 |

## 二、★ 类型名是**量出来的**，不是猜的

| 特征 | `GetTypeName2` 实测值 | 面数 | 父 | 子 |
|---|---|---:|---:|---:|
| 草图1 | `ProfileFeature` | 0 | 2 | 1 |
| 凸台-拉伸1 | `Extrusion` | 6 | 3 | 4 |
| 草图2 ~ 草图5 | `ProfileFeature` | 0 | 1 | 1 |
| 切除-拉伸1 ~ 4 | **`ICE`** | 1 | 3 | 0 |

★★ **「切除-拉伸」的本机类型名是 `ICE`** —— 不是 `Cut`、不是 `CutExtrude`。
若凭印象写，判据会漏掉全部 4 个孔特征。

`tests/test_acceptance_e3_real_machine.py` 有一条测试专门钉这个：
词表里必须有 `ICE`，且**不得**出现 `Cut` / `CutExtrude` / `Extrude` / `Sketch`
这些凭印象的名字。

## 三、★ 一个关键区分：改已有尺寸 ≠ 新建尺寸

第 14 轮查明（`known-facts.md` 事实 560）：

| 动作 | 状态 |
|---|---|
| **新建**尺寸（`AddDimension2` / `AddHorizontalDimension2`） | ❌ 本机把 SolidWorks 弄崩 |
| **改已有**尺寸（`update_dimension_mm` → `SetSystemValue3`） | ✅ 通 |

⇒ E3 要求的「实际编辑前序」走的是**改已有尺寸**，**不受那条退化影响**。
  这也是 E3 能在本轮推进的原因。

## 四、有没有落到「替代品」上

E3 的替代品栏写着「特征数大于零、STEP 可打开」—— 这两个都**不是** E3。
本轮的判据里：

- ❌ 没有把「特征数 > 0」当通过条件（判定器第一句就是
  「特征数 > 0 **不是** E3 的判据」）
- ✅ 用的是「**原生**特征 > 0」+ 零悬空 + 零错误 + **前序可改且下游跟随**

## 五、还没验的（如实）

| 项 | 说明 |
|---|---|
| ~~导入死实体负例（真机）~~ | ✅ **第 16 轮已补**，见第七节 |
| 悬空引用负例（真机） | 同上，只有离线测试 |
| 「目标对象漂移」负例 | 未验 |
| 多配置下的编辑 | 未验（只在默认配置上做了） |
| 编辑**草图以外的**前序（如拉伸深度） | 未验；本轮改的是草图尺寸 `D1@草图1` |

★ 其中最值得补的是**导入死实体**那条 —— 它是 E3 最典型的伪造手法，
  而本轮只验了判定器「会被骗」的反面（判定器写得对），没验「真机能造出那种情形」。

## 六、可重跑

```powershell
# 前置：交付件要在（第 11 轮生成）
python -B tools\sw_guard.py --timeout 300 -- python tools\probe_s3_e3_feature_tree.py
```

证据：`output/s3-e3-feature-tree.json`（`output/` 在 `.gitignore` 里，
关键读数已抄进本文件）。

## 七、真机负例：导入死实体（第 16 轮补上）

第 15 轮只验了正面 + 离线负例。本轮在真机上把负例造出来了。

### 做法

```
交付件副本 ──导出──> STEP（ok=True）──作为新文档导入──> 导入体零件
```

### 真机读数

导入后的零件特征树（`tools/probe_s3_e3_imported_solid_negative.py`）：

| 特征 | `GetTypeName2` 实测值 | 面数 |
|---|---|---:|
| 前视基准面 | `RefPlane` | 0 |
| 上视基准面 | `RefPlane` | 0 |
| 右视基准面 | `RefPlane` | 0 |
| 原点 | `OriginProfileFeature` | 0 |
| Tables | `ConfigTableFolder` | 0 |
| **`板1_rev-1.step<1>`** | **`MBimport`** | 14 |

```
原生 0 · 非原生 6
④ 判定器：fail（★ 没有任何原生特征 ⇒ 只有导入实体，没有可编辑历史）
★ 负例成立
```

### ★★ 两个必须实测、不能猜的类型名

| 特征 | 实测值 | 容易猜错成 |
|---|---|---|
| 切除-拉伸 | **`ICE`** | `Cut` / `CutExtrude` |
| **导入的 STEP 实体** | **`MBimport`** | `Import` / `Imported` |

### ★★★ 一个关键陷阱：基准面不能算「原生」

导入的 STEP 零件**也带**三个基准面、原点和 Tables —— 实测 6 个特征里 **5 个**是这类。

⇒ 若把基准面算成「原生特征」，`native_features` 就不是 0，
  判定器会跳过「没有原生特征」那条，**「导入死实体冒充原生」就会被判 pass** ——
  而那正是 E3 明令要拒的伪造手法。

⇒ 已把这套分类收成**单一真源** `scripts/engineering/acceptance/e3_feature_types.py`：

| 组 | 类型（全部实测） | 算不算可编辑历史 |
|---|---|---|
| `NATIVE_GEOMETRY_TYPES` | `ProfileFeature` · `Extrusion` · `ICE` | **算** |
| `INFRA_TYPES` | `RefPlane` · `OriginProfileFeature` · `ConfigTableFolder` | 不算 |
| `IMPORT_TYPES` | `MBimport` | 不算，且是负例 |

遇到没量过的类型，`classify()` 回 **`unknown`** 并单独列出 ——
**不猜**（铁律 5），漏计会让伪造手法混过去。

`tests/test_acceptance_e3_feature_types.py`（19 条）钉住：
交付件分对（原生 10 / 基础设施 5）、导入体分对（原生 0 / 基础设施 5 / 导入 1）、
基准面不算原生、凭印象的名字（`Cut`/`Import`/`Sketch`…）**不得**入表、未收录类型可被看见。

## 八、★ 孤儿文档问题：查到根因并修好（第 17 轮）

### 问题

第 16 轮改完词表后想复跑负面探针，`sw_guard` 预检拒绝：

```
[预检 第1次] ★ 不放行 · 读到文档 1 个 · 非我方 1 个 · 未保存 1 个
⇒ ★ 会话里有 1 个不是我们打开的文档 ⇒ 拒绝开始
```

孤儿特征：`path=''`（从未保存）、`GetSaveFlag` 为真。

### 为什么删不掉

| 尝试 | 结果 |
|---|---|
| `CloseDoc(title)` | 会弹「是否保存」框（有脏标记）⇒ 护栏不点 ⇒ 调用**永久等待** |
| `SetSaveFlag()` | ❌ 官方逐字「**Flags the document as dirty**」—— 它是**标脏**，不是清脏 |
| `close_orphan_plate_doc.py`（三重判据） | ✅ **正确地拒绝了**（有脏标记 ⇒ 怕丢数据） |

### ★ 官方给的正式出口

`types/ISldWorks/CloseAllDocuments.md` 逐字：

> `System.bool CloseAllDocuments( System.bool IncludeUnsaved )`
> - **True = Close all documents, including dirty documents**

⇒ `CloseAllDocuments(True)` 就是「含脏文档一并关掉」，**不弹保存框**。

它是**关全部**，所以 `tools/discard_orphan_via_closeall.py` 在调用前做**三项硬前置**：

1. 打开文档数**恰好 1**
2. 其 `GetPathName()` 为**空串**（从未保存 ⇒ 磁盘上没有会丢的版本）
3. 其 `GetTitle()` 以 `板1_rev-1` 开头（本次作业的底名）

任一条不满足 ⇒ **只报告不关**。两次都用这个出口干净关掉了（读数：`1 → 0`）。

### ★★★ 根因：探针只调 `CloseDoc`，从不核对文档数

留孤儿的真因不是「关不掉」，而是**关完没检查**：

```python
try:
    sw.CloseDoc(doc.GetTitle())   # ← 返回 None，失败也看不出来
except Exception:
    pass
```

`CloseDoc` 的返回值是 `None`，所以「调用成功」与「文档真的关了」是两件事。
（与第 14 轮那条教训同族：`save_document` 报 True 却没落盘。）

### 修法：关闭之后**回读文档数**

探针新增 `_close_doc()`：关前数一次、关后数一次，把 `1 → 0` 记为 `closed: True`；
收尾再数一次，**非零就当场报出来**，不再留到下一轮才发现。

修后真机读数：

```
关源副本:   title='板1_rev-1_src__2.SLDPRT' · 1 → 0 · closed True
关导入文档: title='板1_rev-1__2.SLDPRT'      · 1 → 0 · closed True
收尾后剩余文档数：0
```

★ 顺带查明一个反直觉事实：导入 STEP 之后，SolidWorks 把文档标题命名成
  **`板1_rev-1__2.SLDPRT`**（源零件名 + 沙盒序号），**不是** `xxx.step`。
  靠「猜标题」去关必然关错 —— 这也是必须回读文档数的原因。

### 复跑结果（用共用词表）

```
③ 导入体特征 6 个 · 类型词表 ['ConfigTableFolder', 'MBimport', 'OriginProfileFeature', 'RefPlane']
   分类：{'native': 0, 'infra': 5, 'import': 1, 'unknown': 0, 'unknown_types': []}
④ 判定器：fail（★ 没有任何原生特征 ⇒ 只有导入实体，没有可编辑历史）
★ 负例成立
```

⇒ 第 16 轮那个「真机复跑搁置」的缺口**已补齐**，且分类口径与离线测试一致。
