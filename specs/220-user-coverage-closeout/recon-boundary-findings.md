# 规格 220 · 边界特征（`InsertNetBlend`）的真机发现集（★ 11 轮实测攒下）

> ★ 本文只收**真机读数**（★ 每条都带"哪一轮 / 什么读数"），★ 供后续复用 ——
> ★ 比"再猜一遍"便宜得多 ✓

## 一、★★★ 四条已定案的真机发现

### 1. ★ `GetFeatureCount` 在本绑定里是**属性**，不是方法

★ 读数（第 1 轮）：★ 调 `model.GetFeatureCount()` ⇒
`TypeError: 'int' object is not callable` ✗
★ 处置：★ 用 `getattr` 兼容两种形态（★ `scripts/sw_net_blend.py` 的 `_feature_count` ✓）

### 2. ★★ **迟到绑定的成员要走 `get_com_member`**，直接点属性会报「没有这个成员」

★ 读数（第 2 轮）：★ `body.GetFaces` ⇒ 逐字「**没有这个成员**」✗
★ 而 `model.GetBodies2` **是方法**（`<bound method …>` ✓）且 **`bodies_len = 1`**（取体成功 ✓）
⇒ ★★ **元组里装的不是"可直接点属性的 body"** ✗ ⇒ ★ 正解：★ **走 `get_com_member(obj, "Name")`** ✓
★ 本仓**已验证**的取面路径（`sw_part.select_face_by_index_mark1`，★ 规格 216 T-216-06b）用的就是它 ✓

### 3. ★★★ **选面：`SelectByID2` 按点会失败，必须走 `IEntity.Select4`**

★ 读数（第 9 轮 · 双臂判别探针 `tools/probe_spec220_append_arms.py`）：

| ★ 臂 | ★ 步骤 | ★ 回读计数 |
|---|---|---|
| `SelectByID2` 按点 | 选 0 号面（`Append=False`）| ★ **0** ✗ |
| | 再选 1 号面（`Append=True`）| 1 |
| | 选 0 号面（`Append=True`）| ★ **0** ✗ |
| ★★ `IEntity.Select4` | `A.Select4(False)` | ★★ **[True, 1]** ✓ |
| | `B.Select4(True)` | ★★ **[True, 2]** ✓ |

⇒ ★★ **0 号面（盒中心 `[0.0, 30.0, -0.01]`）按点永远选不上** ✗（★ 两次都是 0）
⇒ ★★★ **而 `Select4` 对同一个面一次就成、且 `Append=True` 正确累加** ✓✓
★ 这与本仓**事实 32**（★ 实体没有可用名字 ⇒ ① 按点选 · ★ ② **按对象 `IEntity.Select4(Append, Callout)`**）**完全一致** ✓
★ 处置：★ `scripts/sw_net_blend.py` 的选面**已换成 `face.Select4(bool(append), callout)`** ✓
★★ **教训**：★ 计数停在 1 时，★ **先排除"其中一个面根本选不上"**，★ 再去怀疑 `Append` 语义 ✗（★ 我误判过一轮 ✓）

### 4. ★★★ **试件：官方示例是"两个拉伸 → 各取一个面"**

★ 官方 `Insert_Boundary_Feature_Example_VB.htm` 的 `Postconditions` **逐字**：
  「② **Creates two boss-extrude features.** ③ **Selects a face on each boss-extrude feature.**
   ④ Creates a boundary feature using the selected faces.」✓
★ 官方示例的调用行**逐字**（第 74 行）：★ `InsertNetBlend **1, 2, 0**, False, 0.0001, …`
  ⇒ ★ `Type=1`（Boss）· ★ `NCurvesDir1=1` · ★ **`NCurvesDir2=2`** ✓
★★ 而**同一块板的两个面**（我的试件）⇒ ★ 读数（第 10 轮）：★ **选面已成功、流程走到 `InsertNetBlend`、
  但它回 `None`、特征树 20 → 20** ✗ ⇒ ★★ **很可能是"试件不合法"**（★ 不是"API 调不动"）✓

## 二、★ 由此得到的下一步（★ 照官方示例）

1. ★ **建两个拉伸**（★ 两个体/两个特征）⇒ ★ **每个体各取一个面**
   ★ 本仓 `sw_selection_spec.entities_on_body(model, "FACE", body_index=…)` **已带 `body_index`** ✓
2. ★ 调用参数照官方：★ `Type`（1 凸台 / 2 曲面）· ★ `NCurvesDir1=1` · ★ **`NCurvesDir2=2`**
   ★ 已改成这些默认值 ✓
3. ★ 判据：★ **特征树增量 ≥ 1**（★ 事实 8）⇒ ★ 过了才提台账 `level` ✓

## 三、★ 本规格的真机纪律（★ 全程照做）

★ 一律 `python tools/sw_guard.py --timeout 600 -- python <探针>.py` ✓
★ 每次读数都记：★ `seconds` · `dialogs` · `sw_alive` · ★ 以及**探针自己的判据读数** ✓
★ 真机**用完关文档**（★ 护栏也会代关，★ 探针里也显式做一遍 ✓）✓
★ 探针产物落 `output/spec220-*.json`（★ gitignored，★ 但结论已抄进本条与目标栏 ✓）
