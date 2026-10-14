# ★★★★★★ `AI建模操作手册` —— **本仓最该先读的一份**

**位置**：`AI Solidworks/手册/AI建模操作手册.md`
**★ 它是**：`AI Solidworks/README.md` 自称的「**主入口**」

> 「官方 API 参数真相 · **草图关系词汇表** · **完全定义的自由度会计** ·
>   装配体三步顺序 · 命名规范 · **本机工具能力边界**」

**★★★ 为什么这是最该先读的一份**：
★ 它**逐条回答**了我这几轮（规格 315 / 330 / 332 / 334）在摸索的东西 ——
★ 而它**早就写好了**（★ 建立 2026-09-27）。

---

## §1 ★★★★★ 草图「完全定义」：**自由度会计**（★ 逐字）

> **一条线 4 个自由度；一个圆 3 个（cx, cy, r）。完全定义 = 自由度恰好为 0。**

**★ 矩形（4 条线，16 DoF）**：

| 动作 | 消掉 | 剩余 |
|---|---|---|
| 4 个端点自动重合（或手动 4 个 `sgCOINCIDENT`） | 8 | 8 |
| 2 个 `sgHORIZONTAL2D` + 2 个 `sgVERTICAL2D` | 4 | 4 |
| 宽尺寸 + 高尺寸 | 2 | 2 |
| 一个角点 `sgCOINCIDENT` 到 `Point1@Origin` | 2 | **0** ✅ |

**★ 圆（3 DoF）**：
- 圆心 `sgCOINCIDENT` 到原点 → 2
- 直径尺寸 → 1
- 合计 **0** ✅

**★★★ 判据（★ 逐字）**：

> **状态栏必须显示「草图已完全定义」，
> 欠定义数字哪怕只有 1 个就是没做完。**

**★★★ 这正好印证并超越了我这两轮做的**：
- ★ 我的 `sketch_relations_gen` 用**数值求秩**算自由度 ⇒ ★ **它用「每类关系消掉几个」**
- ★★ **两者给同一个答案**（★ 我的矩形 = 2 个尺寸 ✓ ★ 它的矩形也剩 2 → 加 2 个尺寸 = 0 ✓）
- ★★★ **而它更早、更直白**（★ 逐项列出来，★ 一眼能懂）

---

## §2 ★★★★★ 一次性完全定义：**官方有现成方法**（★ 逐字）

> `ISketchManager.FullyDefineSketch` —— 官方示例（Fully Define Underdefined Sketch）

```vb
lMarkHorizontal = 2 : lMarkVertical = 4
swModelExtension.SelectByID2("Point1@Origin", "EXTSKETCHPOINT", 0,0,0, False, _
                             lMarkHorizontal Or lMarkVertical, Nothing, 0)
lStatus = swSketchManager.FullyDefineSketch( _
    True, True, _
    swSketchFullyDefineRelationType_Vertical Or swSketchFullyDefineRelationType_Horizontal, _
    True, 1, Nothing, 1, Nothing, 1, 1)
```

**★★★★★ 判据（★ 逐字，★ 这句最关键）**：

> **优先用这个，而不是手写一长串关系 ——
> 它会自己补齐缺的、去掉冗余的。**

**★★★ 这与我 A 阶段的发现完全一致** ——
★ 我在 A 阶段独立查到 `FullyDefineSketch`（★ 规格 330 补），
★ **而这份手册早就写了「优先用这个」**。

---

## §3 ★★★★★ 建线顺序（★ 「AI 特有坑」，★ 逐字）

> **必须「建一条线 → 立刻给它加 H/V → 再建下一条」。**

**★★★ 原因（★ 逐字）**：

> 因为关系工具靠「**离 (px,py) 最近的图元**」选目标：
> 先批量画 12 条再回头批量加关系，在密集轮廓上**会选错线**
> （**实测：6 条水平只成 3 条、6 条垂直 0 条全错**，相邻台阶径向只差 1 mm）。

**★★★ 这是「批处理 vs 逐条」的硬判据** ——
★ 而我这两轮写的做法**都是「先画完再标」** ✗ ⇒ ★ **这条要改**。

---

## §4 ★★★★ 三个必须先记住的陷阱（★ 逐字）

### 陷阱 1：方向是 `Dir`，不是 `Reverse`

★ `FeatureExtrusion3` / `FeatureCut4` 的方向开关**叫 `Dir`**。

### 陷阱 2：切除边界靠 `T0` + `StartOffset`，不靠 `D1`

### 陷阱 3：草图关系**不是自动的**

---

## §5 ★★★★ `swEndConditions_e` **完整枚举**（★ 逐字）

| 成员 | 值 | 备注 |
|---|---|---|
| `swEndCondBlind` | 0 | 盲端，用 D1/D2 |
| `swEndCondThroughAll` | **1** | ★ **单向通孔** |
| `swEndCondThroughNext` | 2 | 穿透下一个实体 |
| `swEndCondUpToVertex` | 3 | ⚠️ **官方标 "Do not use"** |
| `swEndCondUpToSurface` | 4 | ⚠️ **官方标 "Do not use"** |
| `swEndCondOffsetFromSurface` | 5 | 相对面偏移 |
| `swEndCondMidPlane` | **6** | ★ **对称，D1 是总宽**（★ 不是单边） |
| `swEndCondUpToBody` | 7 | 到指定实体 |
| `swEndCondThroughAllBoth` | **9** | ★ **双向通孔** |
| `swEndCondUpToSelection` | **10** | ★ **切到指定选择面 ← 官方推荐** |
| `swEndCondUpToNext` | 11 | 到下一个面 |

**★★★ 判据（★ 逐字）**：

> **不要**用 `UpToSurface(4)` / `UpToVertex(3)` —— **官方已标 "Do not use"**。

**★ 且**：「切穿整个实体 ⇒ `T1=swEndCondThroughAll(1)`，**`D1` 随便给个非零值**
（★ **官方示例给 0.01**）」
⇒ ★ **这与我在批次①吸收的事实 10 完全一致** ✓

---

## §6 ★★★ 关系名对照（★ `SketchAddConstraints` 字符串）

| 关系 | API 字符串 | 选择类型 |
|---|---|---|
| 重合 | `sgCOINCIDENT` | `swSketchRelationEntityType_Point`×2 |
| 水平 | **`sgHORIZONTAL2D`** | `..._Line` |
| 竖直 | **`sgVERTICAL2D`** | `..._Line` |
| 中点 | `sgATMIDDLE` | Point + Line |
| 共线 | `sgCOLINEAR` | Line×2 |
| 垂直 | `sgPERPENDICULAR` | Line×2 |
| 平行 | `sgPARALLEL` | Line×2 |
| 相切 | `sgTANGENT` | Line/Arc×2 |
| 等长 | **`sgSAMECURVELENGTH`** | Line/Arc×2 |
| 同心 | `sgCONCENTRIC` | Arc×2 |
| 共径 | `sgCORADIAL` | Arc×2 |
| 固定 | `sgFIXED` | 任意 · ★ **慎用**（放弃参数化） |

**★★★ 关键警告（★ 逐字）**：

> ⚠️ **选关系目标时用的类型是 `swSketchRelationEntityType_Point`（=2），
> 不是字符串 `"SKETCHPOINT"`**。两者在不同接口上不通用
> （`SelectByID2` 收字符串，`SketchRelationManager.AddRelation` 收枚举）。
> **混淆这两者是「关系加不上」的头号原因。**

**★★ 注意三处与本仓的差异**（★ 要核实）：
- ★ 它写 **`sgHORIZONTAL2D`** / `sgVERTICAL2D`（★ 带 `2D`）
- ★ 它写 **`sgSAMECURVELENGTH`**（★ 本仓 `references/part-modeling.md` 写的是 `sgSAMELENGTH`）
- ★ **两者必有一个错** ⇒ ★ **要核实**（★ 铁律 4：三源互证）

---

## §7 ★★ `AddComponent5` 的 `x/y/z` 是**零件中心**，不是原点

> ⚠️ `AddComponent5` 的 x/y/z 是**零件中心**，不是原点

---

## §8 ★★★ 其它（★ 该继续读的章节）

| 章 | 内容 |
|---|---|
| §5 | ★ 选择集：名字与类型 |
| §7 | ★★ **验证闭环（不验证 = 没做完）** |
| §8 | ★★ **本机 MCP 工具的能力边界**（可用 ✅ / 不可用 ❌ / 绕行方案） |
| §9 | ★★ **零件建模标准作业流程（SOP）** |
| §10.5 | ★ `swMateType_e` 实测 **26 种**，MCP 只暴露 **8** 种 |
| §10.9 | ★ 嘉立创 3D 库：对机械装配**价值≈0**（实测） |
| §12 | ★★ 拓扑优化与仿真（含反射签名 + 枚举） |

---

## §9 ★★★ 本仓该做的（★ 三条）

| # | 动作 | 依据 |
|---|---|---|
| **1** | ★★★ **把「自由度会计」写进 `sketch-definition-protocol.md`** —— ★ 它比我的数值求秩**更直白**，★ 两者互为验证 | §1 |
| **2** | ★★★★★ **把「建一条线 → 立刻加 H/V → 再建下一条」写进做法** —— ★ 我的做法**都是先画完再标** ✗ | §3 |
| **3** | ★★ **核实 `sgHORIZONTAL2D` vs `sgHORIZONTAL`**（★ 与 `sgSAMECURVELENGTH` vs `sgSAMELENGTH`） | §6 |
