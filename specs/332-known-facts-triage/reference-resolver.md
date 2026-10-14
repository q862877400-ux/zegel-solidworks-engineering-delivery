# ★★★★★★ Reference Resolver —— **语义引用 → 稳定选择器**

**来源**：`C:\Users\Zegel\.agents\skills\mech-design\知识库\10-零件建模\ReferenceResolver语义引用与稳定选择器.md`
（★ 该篇自述：「**我 30+ 轮踩坑的总答案**」）

**★ 它借鉴自**：`github.com/eyfel/mcp-server-solidworks`（355★ · **AGPL-3.0 · 只读借鉴**）
★ **不抄代码、只读思想**（★ 本仓铁律 6）。

---

## §1 ★★★ 它解决的是**我这几轮反复踩的病**

**症状（★ 与我的完全一样）**：
```
add_edge_feature 选错边（★ 加完体积反而变大）
extrude up_to_face_index 选到错误的面
圆角/阵列/切除 时「传了索引但不是我想要的那个」
```

**★★★ 病根（★ 逐字）**：

> 我的工具全是**扁平的一次一动作**，调用方（我）必须**手工算出「该传哪个 index」**
> —— ★ **而这个 index 是不稳定的**。

**★ 它的一句话定位**：

> Reference resolution (**the hard, make-or-break part**): turn semantic references —
> `top_face`, `center`, `concentric to edge X` — into concrete coordinates/selectors
> against the **live B-rep state**.

---

## §2 ★★★ 核心思路：**语义引用 + 几何锚点**

### ① v0 语义选择器（★ 确定性，不依赖建模方向）

| 语义 | 判据 |
|---|---|
| `top_face` | ★ **PLANAR 面中法向 `+Y >= 0.9` 者，取质心 Y 最大的那个** |
| `center` | ★ **包围盒以模型原点为中心** ⇒ 原点投影到 top_face 平面正好是面心 ⇒ 草图 2D 原点就在 `(0,0)` |

**★★★ `top_face` 判据的价值（★ 逐字）**：

> 它用**几何事实**（法向 + 质心位置），
> **而不是「我以为的拉伸方向」** ⇒ ★ **不会被 SolidWorks 的方向怪癖骗到**。

### ② ★★ v0.5 几何锚点（★ 跨重建稳定 —— ★ 这是核心）

```
face 锚点（'near' 落在目标面上）：
    ★ 平面包含匹配 —— 法向与 'near' 一致、且 'near' 到该平面的距离 <= _PLANE_TOL
    ★ 若多个【不同】平面都匹配 ⇒ REFERENCE_AMBIGUOUS
    （共面面之间对 up-to-surface 是等价的 ⇒ 取最近的代表点）

edge 锚点（'near' 落在目标边中点）：
    ★ 容差球内最近中点匹配 —— 必须【恰好一条】边中点在 _EDGE_TOL 内
    ★ 否则 ⇒ REFERENCE_UNRESOLVED / REFERENCE_AMBIGUOUS
```

---

## §3 ★★★ 三个必须知道的**诚实限制**（★ 逐字）

| 限制 | 原文 |
|---|---|
| **索引不跨编辑保持** | 「Anchors are exact for **fresh-doc replay**… but **NOT durable across edits**」 |
| **不要用 hint** | 「The optional `hint` field is **NEVER read** here」 |
| **v0 只支持单体** | 「v0 has a single body, so 'the top face of node n' == the body's top face」 |

**★★★ 工程含义**：

> **改完模型后，之前算出来的 face/edge index 全部作废，必须重查。**

**★★ 这正好解释了我「先分析再修改」时索引失效的现象** ——
★ 与我这两轮学到的**事实 556/557** 同族：
★ **「索引/返回值」不等于「几何现状」**。

---

## §4 ★★★ 接口设计（★ 直接可借鉴）

> 「the resolver returns face/edge **INDICES** that
> `create_sketch(on_face, face_index)` / `extrude_feature(up_to_face_index)` /
> `add_edge_feature(edge_indices)` select directly — **no fragile coordinate pick**」

**★★★ 关键的架构判断（★ 逐字）**：

> ★ **它的工具接口设计与我一致**（`face_index` / `up_to_face_index` / `edge_indices`），
> **区别在于它在上层多了一个 resolver 把语义翻译成索引**。
> ⇒ ★★ **我缺的不是工具参数，是上面那一层「谁来算这个 index」**。

**★★★★★ 这句话点破了我的一个结构性缺口** ——
★ 本仓有 `solidworks_select_face_selector`（★ `+z` / `-z` 这种**声明式选择器**），
★ 而它**正是这一层的雏形** —— ★ 但**只有 6 个固定方向**，
★ 而 `ReferenceResolver` 支持**任意语义**（`top_face` · `center` ·
`concentric to edge X`）+ **几何锚点**。

---

## §5 ★★ 它自己承认的**失败模式**（★ 该抄进我的决策树）

```
REFERENCE_AMBIGUOUS   多个候选面/边 ⇒ ★ 必须由上层消歧（不要猜）
REFERENCE_UNRESOLVED  容差球内找不到 ⇒ ★ 必须报，不要退化到坐标选取
```

**★★★ 这两个码正是「三档决策」在**选择层**的对应** ——
★ `AMBIGUOUS` = 该问 · `UNRESOLVED` = 该拒。

---

## §6 ★★ 与我的 L3 语料的关系（★ 该吸收什么）

| # | 知识 | 命中我的哪条 |
|---|---|---|
| **1** | ★★★ **`top_face` 用几何事实判（法向 + 质心），不用「我以为的方向」** | ★ **全部有面选择的** |
| **2** | ★★★ **索引不跨编辑保持** ⇒ 改完必须重查 | ★ **全部有「先分析再改」的** |
| **3** | ★★ **`AMBIGUOUS` ⇒ 上层消歧（不要猜）** | ★ 全部 |
| **4** | ★★ **`UNRESOLVED` ⇒ 必须报，不要退化到坐标选取** | ★ 全部 |
| **5** | ★ **`center` = 包围盒以原点为中心 ⇒ 草图 2D 原点就在 (0,0)** | ★ **全部有草图的** |
| **6** | ★ **`hint` 字段不被读** ⇒ 不要指望它 | ★ 全部 |

---

## §7 ★★ 另一篇高密度文档（★ 同批发现）

`10-零件建模/轮廓可行性判据.md`（★ 90 行 · **12 条规范句**）——
★ 判「轮廓能不能建」⇒ ★ 与本仓 `check_sketch_definition` **互补**
（★ 我判「写没写清」，它判「能不能建出来」）。

**★ 10-零件建模 的其余篇**（★ 该继续读）：
★ 该目录下还有多篇（★ 本批只精读了 2 篇）。
