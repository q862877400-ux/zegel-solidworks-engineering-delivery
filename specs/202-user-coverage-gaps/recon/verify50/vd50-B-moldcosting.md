# vd50-B-moldcosting · 核对「域 08-mold-costing · 置信度=高」条目

**范围**：`audit-vs-official/` 下与 moldcosting 有关的 `audit-08-mold-costing-{A,B,C}.md`，**只核置信度为「高」的条目**。
**高置信共 5 条**：A#1 · B#1 · B#3 · C#1 · C#2（B#2 置信度为「中」，按指令**未核**）。
**每条核两件事**：①「官方的原文」真的存在于官方文档（`C:\swapi`）；②「我们的原文」真的在仓内文件里且片段对得上。

## 判据来源（先说清楚，避免把「文件在」当成「原文对」）

| 源 | 路径 | 状态 |
|---|---|---|
| 我方文件 | `D:\AI\SW\scripts\sw_mold.py`（21960 B） | 存在 |
| 我方文件 | `D:\AI\SW\scripts\sw_measure.py`（8456 B） | 存在 |
| 官方 | `C:\swapi\types\IMeasure\Calculate.md` | 存在（904 B） |
| 官方 | `C:\swapi\types\IFeatureManager\InsertMoldPartingLine.md` | 存在（1032 B） |
| 官方 | `C:\swapi\types\IFeatureManager\InsertMoldCoreCavitySolids.md` | 存在（2019 B） |
| 官方 | `C:\swapi\types\IFeatureManager\MoldUndercutDetect.md` | 存在（739 B） |
| 官方 | `C:\swapi\types\IFeatureManager\MoldUndercutDetect2.md` | 存在（1906 B） |
| 官方 | `C:\swapi\types\IFeatureManager\InsertMoldPartingSurface.md` | 存在（2015 B） |
| 官方 | `C:\swapi\enums\swPartingSurfaceSmoothingType_e.md` | 存在（446 B） |

⚠ **同名单副本已排除**：`apps\workbench-ui\src-tauri\resources\skill\scripts\sw_mold.py` 存在，但 SHA256 与 `scripts\sw_mold.py` **完全相同**（`0E50A52C6FB1C677…`）⇒ 是 `sync_bundled_skill.py` 的构建产物快照（已知事实 55），**不是另一份会漂移的源**，故以 `scripts/` 为准。

---

## 逐条结果

### 1️⃣ A#1 · `IMeasure.Calculate` 实参个数 0 ≠ 官方形参个数 1 —— **成立**

**我们的原文**（`D:\AI\SW\scripts\sw_measure.py`）：

```python
        ok_calc = _get(m, "Calculate")
```
（`_get` 的绑定已回读确认：`from sw_connect import get_com_member as _get` ⇒ 确系 `get_com_member`，且此处**未传任何实参**。同行上一段注释亦为：
`#: ★★★ 2026-10-01（轮 311）**真机：`Calculate` 必须无参调**（★ 事实 227）——`）

**官方的原文**（`C:\swapi\types\IMeasure\Calculate.md`）：

```
**Signature**: `System.bool Calculate( System.object Entities )`

## Parameters
- **Entities**: Array of entities to measure; if NULL, then this method measures the selected entities
```

旁证（`C:\swapi\examples\Measure_Selected_Entities_Example_CSharp.md`）：`status = swMeasure.Calculate(null);`

**官方原文在不在**：**在**（签名 + 参数说明 + 官方示例，三处一致）
**我们的原文在不在**：**在**（片段逐字一致）
**判定**：**成立**
**一句话依据**：官方签名声明 1 个形参 `Entities`，我们这一行以 0 个实参调用 —— 实参个数与形参个数确实对不上，两侧原文都能逐字 grep 到。

---

### 2️⃣ B#1 · `InsertMoldPartingLine` 的 mark 前置只落了一半 —— **成立**

**我们的原文**（`D:\AI\SW\scripts\sw_mold.py`）：

```python
    调用前须由调用方选好**拔模方向参考**（边线/基准面/轴）——
    官方在未选时会返回 None。
```
```python
            "InsertMoldPartingLine 返回 None —— 常见原因：未选拔模方向参考"
```

**官方的原文**（`C:\swapi\types\IFeatureManager\InsertMoldPartingLine.md`）：

```
## Remarks
Before calling this method, you must select the direction of pull and the edges for the parting line by calling [[IModelDocExtension::SelectByID2]] with the following Marks:

Selection
Mark

Direction of pull
1

Parting line edges
4
```

旁证（CHM 解包页 `…IFeatureManager~InsertMoldPartingLine.html` 去标签后）：
`Before calling this method, you must select the direction of pull and the edges for the parting line by calling IModelDocExtension::SelectByID2 &nbsp;with the following Marks: Selection Mark Direction of pull 1 Parting line edges 4`

**官方原文在不在**：**在**（`C:\swapi` 页与 CHM 页逐字一致，两个选择项与两个 mark 都在）
**我们的原文在不在**：**在**（片段逐字一致）
**判定**：**成立**
**一句话依据**：官方要求**两项**选择（拉拔方向 mark=1 **且** 分型线边 mark=4），我们只把「拔模方向参考」写成唯一前置，`SelectByID2` 与 mark 在整个文件里一个都没有。

**★ 一处对原审计的更正（不改变判定方向，反而更强）**：原条目括号里写「`grep Select\|Mark` 在该文件里只命中这一句散文」；实测 `sw_mold.py` 中 `Select` / `Mark` / `mark` / `select` **各 0 次**（正则全文计数，非行检索）⇒ 原文那句话实际**一处都没命中**。结论方向不变（分型线边 mark=4 在代码里确实完全没有落点），只是原审计对「命中几处」的记数偏松。

---

### 3️⃣ B#3 · `InsertMoldCoreCavitySolids` 的官方前置其实查得到，却被当成查不到 —— **成立**

**我们的原文**（`D:\AI\SW\scripts\sw_mold.py`，模块 docstring 的来源块内）：

```
# ⚠ **多个参数语义查不到**（CHM 无这些方法的独立说明页、`C:\swapi` 未收录、
#   来源也未提供）⇒ 按铁律 5 **不猜**，逐个在 docstring 里标注「未查证」。
```

```python
            "InsertMoldCoreCavitySolids 返回 None —— 常见原因：未先建分型面"
```

**官方的原文**（`C:\swapi\types\IFeatureManager\InsertMoldCoreCavitySolids.md`）：

```
## Remarks
To use this method:

- The Parting Line feature must exist.

- The parting surface must be generated.

- The part must be separated into core and cavity (sheet bodies).

- A sketch describing the outline of the mold block must exist. The sketch must be perpendicular to the pull direction. Usually, the sketch is a rectangle that includes the part (core and cavity).
```

旁证（CHM 解包页 `…IFeatureManager~InsertMoldCoreCavitySolids.html`）：命中 `Parting Line feature must exist` ⇒ **CHM 侧的独立说明页同样存在**。

**官方原文在不在**：**在**（`C:\swapi` 有该成员的独立页且带完整 `## Remarks`；CHM 也有该成员的独立页）
**我们的原文在不在**：**在**（片段逐字一致）
**判定**：**成立**
**一句话依据**：模块 docstring 声明「CHM 无独立说明页、`C:\swapi` 未收录」，但两套官方源**都**有该成员的独立页并写着四条成文前置，我们却只保留了「未建分型面」一条。

---

### 4️⃣ C#1 · `MoldUndercutDetect` 官方双源均标 Obsolete，后继是 9 参 —— **成立**

**我们的原文**（`D:\AI\SW\scripts\sw_mold.py`）：

```python
    """**底切检测**（官方 `IFeatureManager.MoldUndercutDetect`，6 参，返回 `Void`）。
```
```python
    return get_com_member(fm, "MoldUndercutDetect",
                          int(col_undercut), int(col_base), bool(b_coord_input),
                          float(dx), float(dy), float(dz))
```

**官方的原文**（`C:\swapi\types\IFeatureManager\MoldUndercutDetect.md`）：

```
Obsolete. Superseded by [[IFeatureManager::MoldUndercutDetect2]].
```
（CHM 解包页去标签后：`Obsolete. Superseded by IFeatureManager::MoldUndercutDetect2 .`）

后继页 `C:\swapi\types\IFeatureManager\MoldUndercutDetect2.md`：

```
**Signature**: `void MoldUndercutDetect2( System.int ColUndercut1, System.int ColUndercut2, System.int ColOccluded, System.int ColStraddle, System.int ColBase, System.bool BCoordInput, System.double Dx, System.double Dy, System.double Dz )`
```

**官方原文在不在**：**在**（`C:\swapi` 页与 CHM 页都写着 Obsolete + 点名后继；后继页 9 个形参可逐位数）
**我们的原文在不在**：**在**（片段逐字一致）
**判定**：**成立**
**一句话依据**：我们调的成员被两套官方源同时标为 Obsolete，且后继 `MoldUndercutDetect2` 是 5 个颜色 + BCoordInput + Dx/Dy/Dz 共 9 参，与我们仍传的 6 个不是同名同位替换。

---

### 5️⃣ C#2 · `InsertMoldPartingSurface` 第 6 形参是枚举，我们传的 `0` 不在成员表内 —— **成立**

**我们的原文**（`D:\AI\SW\scripts\sw_mold.py`）：

```python
        int(option),            # 6 Int32 未查证
```
（签名默认值 `option: int = 0`，且 docstring 明写 `其余 5 个（`surface_type` / `flip` / `use_trim` / `option` / `alternate`）**语义未查证**`）

**官方的原文**（`C:\swapi\types\IFeatureManager\InsertMoldPartingSurface.md`）：

```
**Signature**: `Feature InsertMoldPartingSurface( System.int Radiate, System.bool ReverseAlignment, System.bool ReverseOffset, System.double OffsetDistance, System.double Angle, System.int Smooth, System.double SmoothDistance, System.bool Knit )`
```
```
- **Smooth**: Smooth mold parting surface as defined by [[swPartingSurfaceSmoothingType_e]]
```
（`C:\swapi\enums\swPartingSurfaceSmoothingType_e.md`）

```
enum_member_count: 2

| Member | Value |
| --- | --- |
| swPartingSurfaceSharp | 1 |
| swPartingSurfaceSmooth | 2 |
```

**官方原文在不在**：**在**（第 6 形参名为 `Smooth`、类型枚举页存在、成员表只有 1 与 2）
**我们的原文在不在**：**在**（片段逐字一致，且传参位序第 6 位确实是 `int(option)`）
**判定**：**成立**
**一句话依据**：官方把第 6 形参明确定义为枚举 `swPartingSurfaceSmoothingType_e`，该枚举成员表只有 1 和 2，我们却把默认值 `0` 写进了这一位。

---

## 汇总

| 条目 | 文件 | 官方原文在不在 | 我们的原文在不在 | 判定 |
|---|---|---|---|---|
| A#1 | `audit-08-mold-costing-A.md` #1 | ✅ 在（swapi + 官方示例） | ✅ 在 | **成立** |
| B#1 | `audit-08-mold-costing-B.md` #1 | ✅ 在（swapi + CHM） | ✅ 在 | **成立** |
| B#3 | `audit-08-mold-costing-B.md` #3 | ✅ 在（swapi + CHM） | ✅ 在 | **成立** |
| C#1 | `audit-08-mold-costing-C.md` #1 | ✅ 在（swapi + CHM + 后继页） | ✅ 在 | **成立** |
| C#2 | `audit-08-mold-costing-C.md` #2 | ✅ 在（swapi + 枚举页） | ✅ 在 | **成立** |

**核了 5 处 · 判定成立 5 · 不成立 0 · 存疑 0 · 对不上 0。**

**「查不到」记录**：无 —— 5 条的两侧原文全部命中，无一条需用相似名字顶替。

**本轮唯一对原审计的修正**：B#1 括号里「`grep Select\|Mark` 只命中这一句散文」不准确（实测 0 命中），已在上文逐条注明；**不改变该条判定**。
**未核**：B#2（置信度为「中」，按指令不碰）。