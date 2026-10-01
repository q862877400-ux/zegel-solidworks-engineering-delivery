import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")

P = Path(r"C:\swprojects\sw-skill-fork\docs\union-gap-triage-sample.md")
t = P.read_text(encoding="utf-8")

ADD = """

---

# 追加：132 条「真缺」的反向核样（轮 103）

## 为什么要核这一档
前三轮都在核「**别名 / 后缀候选**」三档（它们会把"其实没有"记成"有"）。
「真缺」132 条**方向相反**：它是"**连 `scripts/` 里也没有同名函数**"⇒
⚠ 可能把"**其实我们以别的名字实现了**"记成缺。轮 98 就撞到一例：
`tooling_split` 在真缺里，而我们**早有** `sw_mold.insert_core_cavity_solids`。

⇒ 核样：**每 6 取 1**（与轮 101 同规则）⇒ **22 条**。

## ⚠⚠ 我的自动检查这一轮**连续错三次**（必须记下来）
| 次 | 我写的判据 | 错在哪 |
|---|---|---|
| 1 | 在 `scripts/sw_*.py` 里找关键词 | 命中的是 `sw_api_sldworks.py` —— **API 名登记表，不是实现** |
| 2 | 再排除 `sw_api_*` | `save_as` 命中的是 `sw_com_traps.py` —— **COM 陷阱表**；`gdt` 命中的是 `sw_api_swdimxpert.py` |
| 3 | 再排除 `sw_com_traps` | `equation` 命中的是**参数名**；`export_vba` 命中的是 `sw_automation_knowledge`（**知识表**）|

★ **⇒ 结论：按名字做的自动检查在这个问题上「两个方向都不可靠」**：
* 前三轮：把**没有**的记成**有**（假阳性）；
* 这一轮：把**有**的（换名实现）记成**没有**，同时又把**参数名/知识表**当成实现（**又是假阳性**）。

⇒ **⇒ 唯一站得住的做法是逐条人工判**（下面就是）。

## 22 条逐条判定

| # | 缺口操作 | 我们其实有吗 | 判定 | 说明 |
|---|---|---|---|---|
| 1 | `activate_sheet` | 无 | ❌ 没有 | 只有 `activate_configuration` / `_activate_model_document` |
| 2 | `assembly_mates` | `collect_mate_feature_summary` | ⚠ 部分 | 有**配合摘要**，不是"列配合" |
| 3 | `batch_operations` | `batch_export` | ⚠ 部分 | 只有**批量导出**，不是通用批量操作 |
| 4 | `check_drawing_compliance` | 无 | ❌ 没有 | |
| 5 | `convert_entities` | 无（`SketchUseEdge` 只登记未实现）| ❌ 没有 | |
| 6 | `drawing_dimensions` | 无 | ❌ 没有 | `review_drawing_layout` 是复核布局，不是尺寸 |
| 7 | `equation` | 无（命中的是**参数名**）| ❌ 没有 | ⚠ 自动检查在这里**假阳性** |
| 8 | `export_vba` | 无（命中的是**知识表**）| ❌ 没有 | ⚠ 同上 |
| 9 | `gdt` | 无 | ❌ 没有 | 形位公差 |
| 10 | `generate_vba_file_operations` | 无 | ❌ 没有 | |
| 11 | `helix` | 无 | ❌ 没有 | 螺旋线 |
| 12 | `jog` | 无 | ❌ 没有 | 折弯 |
| 13 | `measure` | **`collect_geometry_measurements`** | ✅ **有** | 几何测量收集 |
| 14 | `pattern_component_circular` | **`circular_pattern`（`sw_part`）** | ✅ **有** | ⚠ 但那是**特征**圆周阵列，不是**零部件**阵列 —— **口径存疑** |
| 15 | `recording` | 无 | ❌ 没有 | 宏录制 |
| 16 | `save_as` | **`SaveAs`（`sw_connect` / `sw_export`）** | ✅ **有** | 另存为 |
| 17 | `sheets` | `sheet_names`（`sw_export`）| ⚠ 部分 | 只是导出用的辅助，不是"图纸"操作 |
| 18 | `sketch_chamfer` | 无 | ❌ 没有 | 草图倒角 |
| 19 | `sketch_mirror` | 无 | ❌ 没有 | 草图镜像 |
| 20 | `stop_native_macro_recording` | 无 | ❌ 没有 | |
| 21 | `tooling_split` | **`insert_core_cavity_solids`** | ✅ **有** | **轮 98 已确认**（能力在、未暴露）|
| 22 | `validate_drawing_completeness` | 无 | ❌ 没有 | |

```
✅ 确实有 **4**  ·  ⚠ 部分 **2**  ·  ❌ 没有 **16**
⇒ 反向错误率 ≈ 4/22 ≈ **18%**（含"部分"则 27%）
```

## ★★ 四轮合并后的估算
```
              条数   真    来源
别名（强）      26     7    轮 102 全核
别名（弱）      37     6    轮 102 全核
后缀候选       144    36    轮 101 抽样外推
真缺           132    24    轮 103 抽样（132 × 18%）
----------------------------------------
真匹配 ≈ 73   ⇒   真实缺口 ≈ 338 − 73 ≈ **265**
```

## ⚠ 这个数字的限度（比前几轮更多）
* **后缀候选**（144）与**真缺**（132）都是**抽样外推**（24/144 · 22/132）；
* 「部分」共 **18** 条口径未定 ⇒ 真匹配区间约 **73~95** ⇒ **真实缺口约 245~265**；
* `pattern_component_circular` 那条**口径存疑**（特征阵列 ≠ 零部件阵列）——
  按严格口径它不算"有"，那真匹配降到 72、缺口升到 266。

## ★ 本轮的**方法**收获（比数字重要）
> **按名字做的自动检查，在这个问题上两个方向都靠不住。**

它既会把"没有"记成"有"（前三轮），也会把"有"记成"没有"，
**还会把参数名和知识表当成实现**。
⇒ **四轮下来唯一站得住的动作都是同一件：把每条拿出来人工看一眼。**
"""

if "132 条「真缺」的反向核样" not in t:
    t = t.rstrip() + ADD
    t = t.replace(
        "* **132 条「真缺」**未核 —— ⚠ 但也要防它**反向出错**（把\"其实我们有\"的记成缺），本轮未查。",
        "* **132 条「真缺」**已在**轮 103** 抽样核过（22 条）⇒ 反向错误率 ≈ **18%**，见文末。")
    P.write_text(t, encoding="utf-8")
    print("  ok sample 文档已追加真缺反向核样")
else:
    print("  已有")

# 更新 triage 顶部
Q = Path(r"C:\swprojects\sw-skill-fork\docs\union-gap-triage.md")
tq = Q.read_text(encoding="utf-8")
anchor = "> ⚠ 限度：别名两档是全核，后缀候选是抽样 ⇒ 结论应表述为「**真实缺口约 270~290**」。"
add2 = (anchor + "\n"
        "> ⚠⚠ **轮 103 追加**：**「真缺」132 条也反向核了**（每 6 取 1 ⇒ 22 条）。\n"
        "> 反向错误率 ≈ **18%**（4/22 其实我们有，如 `tooling_split`、`save_as`、`measure`）。\n"
        "> ⇒ 四轮合并：真匹配 ≈ **73** ⇒ **真实缺口 ≈ 265**（区间约 **245~265**）。")
if "轮 103 追加" not in tq:
    assert anchor in tq, "锚点不符"
    Q.write_text(tq.replace(anchor, add2, 1), encoding="utf-8")
    print("  ok triage 顶部已更新（轮 103）")
else:
    print("  triage 已有轮 103 提示")
