# T006 官方签名核验 —— 草图关系族

**Feature**: `specs/302-ec00-trustworthy-tool-base/`
**日期**: 2026-10-10
**对应任务**: **T006**（★ 逐字：对关系调用和回读核对官方签名、Remarks、Example、冲突索引与对应 limitations；★ 必要时设计限定探针但**不先运行**）
**上游**: `research.md` §二（★ 本文件是它的**逐字核验补全**）

---

## 一、★★★★★ 官方签名（★ 逐字 · ★ `C:\swapi\types\ISketchRelationManager\AddRelation.md`）

```
type: ISketchRelationManager
member: AddRelation
kind: method
assembly: SolidWorks.Interop.sldworks
category: Sketch
```

★ **Signature** 逐字：

```
SketchRelation AddRelation( System.object Entities, System.int RelationType )
```

★ **Parameters** 逐字：
- ★ **`Entities`**：★ **Array of entities to which add the relation**
- ★ **`RelationType`**：★ **Type of relation as defined by `swConstraintType_e`**

★★★ **Returns** 逐字：★ **`[[Sketch relation]]`**

---

## 二、★★★★ `## Remarks` 逐字（★ 这是**前置**）

> ★ **A sketch must be active for this method to have any effect.** Use `[[IModelDoc2::GetActiveSketch2]]`
> or `[[IModelDoc2::IGetActiveSketch2]]` to determine if a sketch is active.

★★★ **⇒ 官方明写的**唯一前置** = **必须有一个活动草图**（★ 否则**没有任何效果**）。
★★ **官方**没有**说「需要预先选择实体」** ⇒ ★★ 与 `HoleWizard` 那类（★ 官方明写 mark 表）**不同**。

---

## 三、★★★★★ 指针变体（★ 同名不同签名 —— ★ **这是关键区分**）

★ `C:\swapi\types\ISketchRelationManager\IAddRelation.md` 逐字：

```
SketchRelation IAddRelation( System.int NumEntities, ref System.object EntityArray, System.int RelationType )
```

| ★ 项 | ★ `AddRelation` | ★ `IAddRelation` |
|---|---|---|
| ★ 形参个数 | ★ **2** | ★ **3** |
| ★ 第 1 参 | ★ `object Entities` | ★ `int NumEntities` |
| ★ 第 2 参 | ★ `int RelationType` | ★ **`ref object EntityArray`** |
| ★ 第 3 参 | ★ — | ★ `int RelationType` |

★★★ **⇒ 两者**不可混用****（★ 传错个数 ⇒ `0x8002000E`「参数个数不正确」—— ★ 那正是**历史记录里第 20 轮**踩的坑）。

---

## 四、★★★★ `swConstraintType_e`（★ 关系类型枚举 · ★ 86 个成员）

★ `C:\swapi\enums\swConstraintType_e.md` 逐字：★ `enum_member_count: 86` · ★ `assembly: SolidWorks.Interop.swconst`。

★ **抽样逐字**（★ 与草图关系相关的常见值）：

| ★ 成员 | ★ 值 | ★ 成员 | ★ 值 |
|---|---|---|---|
| ★ `swConstraintType_ANGLE` | ★ **2** | ★ `swConstraintType_ATMIDDLE` | ★ **12** |
| ★ `swConstraintType_ATINTERSECT` | ★ **13** | ★ `swConstraintType_ATPIERCE` | ★ **40** |
| ★ `swConstraintType_ALONGX` | ★ **48** | ★ `swConstraintType_ALONGY` | ★ **49** |
| ★ `swConstraintType_ARCANG90` | ★ **18** | ★ `swConstraintType_ARCLENGTH` | ★ **44** |

★★ **注意**：★ 官方枚举名是 **`swConstraintType_*`**（★ 而**不是** `sg*`）——
★★★ **`sg*` 是 `SketchAddConstraints` 的字符串口径**（★ 两个**不同入口**、**两套命名**）。

---

## 五、★★★★ 回读判据的官方依据

| ★ 成员 | ★ 官方页 | ★ 用途 |
|---|---|---|
| ★ `ISketchSegment::GetRelationsCount` | ★ 逐字（★ 见 `sw_sketch_relations.py:16` 的来源块） | ★★ **真判据**（★ 关系数**真的 +1**） |
| ★ `ISketch::GetConstrainedStatus` | ★ 返回 `swConstrainedStatus_e` | ★ 前态（★ `1 swUnknownConstraint` · ★ **`2 swUnderConstrained`**） |
| ★ `ISketchRelationManager::GetRelationsCount` | ★ `## See Also` 逐字列出 | ★ 管理器级计数 |

---

## 六、★★★★★ 本仓实现的**一致性核对**（★ 逐行读源码，★ **不猜**）

★ 实现：`scripts/sw_sketch_relations.py` · ★ 调用点：**L350-357**。

| ★ 检查项 | ★ 本仓实现 | ★ 官方 | ★ 一致？ |
|---|---|---|---|
| ★ 入口 | ★ `mgr.AddRelation`（★ 先 `getattr` 取，★ **调用前选定路线**） | ★ `ISketchRelationManager::AddRelation` | ✅ |
| ★ **形参个数** | ★ `add_relation(payload, RELATION_TYPES[kind])` ⇒ **2 个** | ★ **2 个** | ✅ |
| ★ 第 1 参（实体数组） | ★ `_dispatch_array([segs[i] for i in idx])` | ★ `object Entities` = **Array of entities** | ✅ |
| ★ 第 2 参（关系类型） | ★ `RELATION_TYPES[kind]`（★ **数值**） | ★ `int RelationType`（★ `swConstraintType_e`） | ✅ |
| ★ **前置**（活动草图） | ★ **L197-201**：`sk = _active(model)` ⇒ ★ **`if sk is None: return {"ok": False, "error": "没有活动草图 ⇒ 先 sketch_start"}`** | ★ **「A sketch must be active」** | ✅ **一致** |
| ★ 回读判据 | ★ `_rel_count(model, segs[idx[0]])`（★ before/after） | ★ `ISketchSegment::GetRelationsCount` | ✅ |
| ★ 兜底路线 | ★ `model.SketchAddConstraints("sg" + kind)`（★ **调用前选定**） | ★ 另一入口（★ `sg*` 字符串口径） | ✅ **命名对得上** |
| ★ 防过定义 | ★ `_status(model)`（★ 完全定义则**整批拒加**） | ★ ★ **官方 Remarks 没有这一条** | ✅ **本仓**加强**（★ 不是缺口） |

★★★ **⇒ 全部一致**（★ 2026-10-10 **逐行复核**）。

⚠ **订正记录**：★ 本文件**初版**曾写「★ 本仓**没有**显式查「活动草图」（★ 只在更外层隐含）」
⇒ ★★ **那是**错的** —— ★ 逐行读 `scripts/sw_sketch_relations.py:196-201` 后确认：
★★ **本仓**确实**查了**（★ `sk = _active(model)` + ★ `if sk is None` 早返回）。
★★★ **⇒ 已订正**（★ 依据 `MEMORY.md` 规则 28：「改实现前先搜『有没有测试钉住旧行为』」的同族纪律：
★ **说实现之前先读实现**）。

---

## 七、★★★ 结论与待办

| # | ★ 结论 | ★ 状态 |
|---|---|---|
| ① | ★ 官方签名**逐字到手**（★ 2 参 · `object` + `int`） | ✅ **完成** |
| ② | ★ 指针变体 `IAddRelation`（★ 3 参）**已区分** | ✅ **完成** |
| ③ | ★ `## Remarks` 的**唯一前置**（★ 活动草图）**已逐字核** | ✅ **完成** |
| ④ | ★ 本仓调用的**形参个数与类型**与官方**一致** | ✅ **完成** |
| ⑤ | ★ **本仓确实查了「活动草图」**（★ `L197-201`）—— ★★ **初版记录写错、已订正** | ✅ **完成**（★ 无缺口） |
| ⑥ | ★ 枚举名 `swConstraintType_*` 与 `sg*` **两套口径**已澄清 | ✅ **完成** |
| ⑦ | ★ 本仓**额外**做了「防过定义」（★ 官方 Remarks **没有**这一条） | ✅ **本仓加强** |

★★★ **⇒ T006 **全部核验完成**，★ **未发现未闭合的缺口**。
★★ **⇒ T017 的输入 = 「关系实现已对，★ 只差**正式注册**」**（★ 实测：0 个 ToolSpec）。
