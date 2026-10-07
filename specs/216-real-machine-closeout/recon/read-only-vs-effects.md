# 规格 216 · 发现：**`read_only` 与效应体系的不一致**（★ 一族，不是一条）

> **来源**：★ 本轮做 T-216-06a（读台账第一现场）时**顺手撞到**的 ✓
> **不是**本规格原定的三件事之一，★ 但按纪律**必须记档**（★ 要么修、要么写明为什么先不修）✓

## 一、病灶：判序第一是"显式声明"，★ 而它**没有门禁**

`mcp-server/tool_registry.py` 的 `effective_read_only` 逐字：

```python
explicit = getattr(spec, "read_only", None)
if explicit is not None:
    return bool(explicit)          # ★ 显式声明优先（人判 / 真机实证）
writes = effective_writes(spec)
return writes == ()
```

⇒ ★★ 显式 `read_only` **直接覆盖**派生值 ⇒ ★ 于是「**效应体系说它有写 / 台账裁定它不许标只读**」
只要 ToolSpec 里写着 `True`，**下游一律当真** ✗
★★ 而我实测确认：**没有任何门禁**比对「显式 `read_only`」与「台账裁定」或「`writes`」✗

## 二、已修 1 条（★ 有台账**明文裁定**，故有据可依）

| 项 | 值 |
|---|---|
| 工具 | `solidworks_section_properties` |
| 原 | ★ ToolSpec `read_only=True` ＋ 文档写"**只读**" |
| 台账裁定（逐字） | 「★★ **有副作用**：★ 官方写「**This method clears the selection set**」＋「objects in the `Sections` parameter **are added to** the current selection set」⇒ ★★ **它清空并重写选择集** ⇒ ★ 按**规格 210** 的效应声明体系，★ **它不许被标 `read_only`**」 |
| 为什么效应表没抓到 | ★ 它是**生成物**（表头 `★ 不要手改`），静态判据**只用「动词这一路」**（其 `_limitations` 自述）⇒ ★★ **看不见只写在官方 `## Remarks` 里的副作用**（"clears the selection set" 不是动词写）⇒ 表里那条 `writes: []` 是**欠近似** |
| 修法 | ★ **人判显式覆盖**：`read_only=False` ＋ 把「⚠ 不是只读」提到**文档首句**（★ lean 只保首句 —— 规格 215 的纪律）✓ |
| 验证 | ★ `effective_read_only(spec)` 由 `True` → **`False`** ✓ · ★ 相关测试 **33 passed** ✓ |

★ ⚠ `state_classes` **本来就含 `selection`** ⇒ ★ 这条副作用**在体系的语义之内**，
  ★ 只是**静态判据那一路上看不见** ⇒ ★ 不是"体系没设计"、★ 是"这一路看不见" ✓

## 三、**未修 6 条**（★ 同一族，★ 但**没有裁定**⇒ 不擅改）

★ 实测（`effective_writes(spec)` 非空、而显式写着 `read_only=True`）：

| 工具 | `writes` |
|---|---|
| `solidworks_current_selection` | `('document',)` |
| `solidworks_collect_appearance_evidence` | `('document',)` |
| `solidworks_collect_assembly_bom` | `('document',)` |
| `solidworks_selection_count` | `('document',)` |
| `solidworks_selection_point` | `('document',)` |
| `solidworks_resolve_entity` | `('document',)` |

★ 观察：★ 其中 `selection_count` / `selection_point` / `resolve_entity` / `current_selection`
**确实是"会动选区"的工具** ⇒ 它们被判 `writes=('document',)` 而不是 `('selection',)`
**本身可能就是又一次分类欠准**（★ 与 `section_properties` 同一路问题）✓

★★ **为什么先不修**（★ 如实写）：
1. ★ **没有裁定** —— 台账里这 6 条**没有**「不许标只读」那类明文 ⇒ ★ 改它们就是**我替项目定政策** ✗
2. ★ **需要先回答一个规范问题**：★ **「只动选区、不动几何」算不算"只读"？**
   ★ 体系里 `selection` 是状态类之一 ⇒ 按体系逻辑**不算**；
   ★ 而"只读"在 MCP 那边的语义是 `readOnlyHint`（★ 客户端据此判断能否自动重放）⇒
   ★★ **两者的口径不一致**，★ 这要一次**规范级决定**，★ 不是 6 处改布尔 ✓
3. ★ 且★ 若判"算写"★ 则这 6 条要一起改（★ 一致地改），★ 而它们的 `writes` 分类**也该同时订正** ✓

⇒ ★ **列为待决项**（★ next：要么在规格 216 里立一个 T，要么另立规格）✓

## 四、可机械化的那一半（★ 建议，★ 本轮未做）

★ 可以做、且**零假阳性**的判据（★ 已量过形态）：
> **凡台账某条目的 `limitations` 里出现「不许被标 `read_only`」⇒ 该条目 `mcp_tools` 里的工具
>   必须 `effective_read_only` 为假** ✓

⚠ 但**本轮不建**：★ 台账的 `limitations` 与**具体工具名**之间**没有直接映射**
（★ 一条 limitation 常覆盖一族工具）⇒ ★ 要建就得先**在台账里给这条裁定标注它管哪个工具**
（★ 否则门禁只能靠文本邻近猜 ⇒ ★ 那正是我这几轮反复踩的"判据过宽/过窄"坑）✓
