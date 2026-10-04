# T4-1 逐条核（机械部分）：25 条冲突的成员，我们用了没、用在哪

> 生成物 —— 由 tools/t4_member_crosscheck.py 产出，不要手改。
> 输入：c4-merged.json（只读复用）+ 本仓 scripts/ mcp-server/ tools/。

## 一 · 口径

| 项 | 值 |
|---|---|
| 冲突条目 | **25**（unit_diff 15 + mark_diff 10）|
| 涉及成员 | **19** |
| ★ 我们用了的成员 | **8** |
| ★ 我们没用到的成员 | **11** |

本表不算什么：

- ★ 不判我们调得对不对 —— 它只说用没用、用在哪（判对错要读那一行代码加官方页）；
- ★ 没用到的成员不等于无影响 —— 若将来实现同一能力，该冲突届时才触发；
- ★ 匹配有三种写法（get_com_member / 属性访问 / 字符串字面量），
  第三种会把注释与文档里的提及也算进来，可能高估用了没。

## 二 · 我们用了的（8 个，需要人核的那批）

| 成员 | 引用处 | 方式 |
|---|---|---|
| `AutoDimension2` | `scripts\sw_part.py:805` | get_com_member |
| `AutoDimension2` | `mcp-server\tool_specs_batch55.py:15` | attr_access |
| `AutoDimension2` | `tools\probe_autodimension_successor.py:1` | attr_access |
| `AutoDimension2` | `tools\probe_fullydefinesketch.py:71` | get_com_member |
| `AutoDimension2` | `tools\probe_getsystemvalue_successor.py:69` | attr_access |
| `AutoDimension2` | `tools\prove_part_read_and_dimension.py:9` | attr_access |
| `FeatureCircularPattern4` | `scripts\sw_part.py:1441` | attr_access |
| `FeatureCircularPattern4` | `tools\probe_pattern5.py:114` | get_com_member |
| `FeatureCircularPattern4` | `tools\probe_pattern_generations.py:129` | literal |
| `FeatureCircularPattern4` | `tools\prove_linear_pattern_generations.py:10` | attr_access |
| `FeatureCircularPattern4` | `tools\prove_pattern_members.py:42` | literal |
| `FeatureLinearPattern4` | `tools\probe_linear_pattern_baseline.py:115` | get_com_member |
| `FeatureLinearPattern4` | `tools\probe_linearpattern4.py:112` | literal |
| `FeatureLinearPattern4` | `tools\prove_linear_pattern_generations.py:93` | literal |
| `FeatureLinearPattern4` | `tools\prove_pattern_members.py:41` | literal |
| `InsertProtrusionBlend2` | `scripts\sw_loft.py:87` | get_com_member |
| `InsertProtrusionBlend2` | `mcp-server\tool_specs_batch47.py:54` | attr_access |
| `InsertProtrusionBlend2` | `tools\audit_gap_implementations.py:40` | literal |
| `InsertProtrusionBlend2` | `tools\prove_pattern_members.py:43` | literal |
| `InsertSewRefSurface` | `scripts\sw_surface_features.py:263` | get_com_member |
| `InsertSewRefSurface` | `mcp-server\tool_specs_batch45.py:75` | attr_access |
| `InsertWeldmentTrimFeature2` | `tools\probe_t302_four_families.py:181` | literal |
| `InsertWeldmentTrimFeature2` | `tools\probe_t302_four_families_v2.py:190` | get_com_member |
| `SetSystemValue3` | `scripts\sw_document_data.py:4` | attr_access |
| `SetSystemValue3` | `tools\probe_getsystemvalue_on_existing.py:14` | attr_access |
| `SetupSheet6` | `scripts\sw_drawing_expose.py:18` | attr_access |
| `SetupSheet6` | `mcp-server\tool_specs_batch75.py:39` | attr_access |
| `SetupSheet6` | `tools\probe_datum_tag_selfcontained2.py:9` | attr_access |
| `SetupSheet6` | `tools\probe_drawing_tools_e2e.py:19` | attr_access |
| `SetupSheet6` | `tools\prove_drawing_batch.py:1023` | attr_access |

## 三 · 我们没用到的（11 个）

- `ConeParams`
- `EditMate3`
- `FeatureExtruRefSurface2`
- `FieldOfViewAngle`
- `GetEnvironment`
- `GetMergeDistance`
- `GetRowHeight`
- `InsertCutSwept5`
- `InsertMoveCopyBody2`
- `IsTolerant`
- `MaxValueForGapRange`

## 四 · 下一步

★ 对第二节那 8 个成员逐条：读我们那一行代码加官方页 Remarks，判我们用的是示例写法还是 Remarks 写法；有证据的才改。

---

## 五 · ★★ 修正（★ 2026-10-04 第 12 轮）：上一轮的「用了」口径**高估了**

★ 触发：判读第一条（`AutoDimension2`）时发现 7 处命中里 **6 处是注释/docstring 里的提及** ⇒
★ 即上一轮判据的第三种写法（字符串字面量）**把提及也算成了使用** —— ★ 那正是上一轮
「本表不算什么」第 ③ 条**预告过的风险**，现在**实测确认它发生了** ✓

★★ 本轮改用 `ast` 精确判：**真调用**只有两种形态 ——
`get_com_member(<任意>, "member")` 的**第二实参**、或 `<任意>.member` 的**属性访问**；
★ 其余（docstring / 注释 / 散文里的字符串）**一律算提及** ✓

| 口径 | 「用了」的成员数 |
|---|---|
| 上一轮（文本匹配）| **8** |
| ★★ 本轮（`ast` 精确）| **7** |
| ⇒ 高估 | **1** 个 |

### 5.1 ★ 真调用（`ast` 判 · 需要人核的那批）

| 成员 | 引用处 | 方式 |
|---|---|---|
| `AutoDimension2` | `scripts\sw_part.py:805` | get_com_member |
| `AutoDimension2` | `tools\probe_fullydefinesketch.py:71` | get_com_member |
| `FeatureCircularPattern4` | `scripts\sw_part.py:1441` | attr_access |
| `FeatureCircularPattern4` | `tools\probe_pattern5.py:114` | get_com_member |
| `FeatureLinearPattern4` | `tools\probe_linear_pattern_baseline.py:115` | get_com_member |
| `FeatureLinearPattern4` | `tools\prove_linear_pattern_generations.py:94` | get_com_member |
| `InsertProtrusionBlend2` | `scripts\sw_loft.py:87` | get_com_member |
| `InsertSewRefSurface` | `scripts\sw_surface_features.py:263` | get_com_member |
| `InsertWeldmentTrimFeature2` | `tools\probe_t302_four_families_v2.py:190` | get_com_member |
| `SetSystemValue3` | `scripts\sw_document_data.py:365` | attr_access |

### 5.2 ★ 只出现在文本里（提及，非调用）—— 上一轮被误算成「用了」的

- `SetupSheet6`（文本命中 2 处，真调用 0 处）

### 5.3 完全没出现

- `ConeParams`
- `EditMate3`
- `FeatureExtruRefSurface2`
- `FieldOfViewAngle`
- `GetEnvironment`
- `GetMergeDistance`
- `GetRowHeight`
- `InsertCutSwept5`
- `InsertMoveCopyBody2`
- `IsTolerant`
- `MaxValueForGapRange`

★ **口径**：本轮判据的否定面已写明（提及不算）；
★ 但它仍有边界：`getattr(obj, "member")` 这类**动态取用**不在两种形态里 ⇒ 会漏 ✓
★ 另有冲突类 mark_diff/unit_diff 的成员分布见 `conflicts-25.md` ✓
