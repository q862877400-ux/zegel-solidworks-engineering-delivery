import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")

# ① 判定表（可复算：抽样规则写死在文件里）
SAMPLE = """# 「后缀候选」144 条的人工核样（2026-10-01 轮 101）

## 为什么要核
`docs/union-gap-triage.md` 把 **144 条**（占缺口 42%）归为
「**能力在、未暴露** —— `scripts/sw_*.py` 里有同名函数，只是没暴露成 MCP 工具」。
⚠ 该归类来自**字符串匹配**（后缀相同）。抽查一眼就觉得不对：
```
arc           -> sketch_arc          ✅ 同一操作
assembly      -> dissolve_assembly   ❌ 「分解装配体」不是「装配」
broken_view   -> call_view           ❌ 「断裂视图」不是「调用视图」
apply_template-> find_template       ❌ 「应用模板」不是「查找模板」
```
⇒ **人工核样，定出真实命中率。**

## 抽样规则（**可复算**）
对 `union-gap-triage.md` 的「后缀候选」表**每 6 条取 1**，得 **24** 条。

## 判定（三种：真 / 部分 / 假）

| # | 缺口操作 | 我们的候选 | 判定 | 理由 |
|---|---|---|---|---|
| 1 | `3d_sketch` | `auto_dimension_sketch, end_sketch` | ❌ 假 | 3D 草图 ≠ 自动标注/结束草图 |
| 2 | `analyze_macro` | `is_swp_macro, validate_vba_macro` | ❌ 假 | 判断/校验 ≠ 分析 |
| 3 | `assembly_components` | `get_components` | ✅ 真 | 就是取装配体零件 |
| 4 | `bodies` | `get_bodies` | ✅ 真 | 同名 |
| 5 | `check_drawing_standards` | `get_hole_standards, list_standards` | ❌ 假 | 查标准 ≠ 检查图纸标准 |
| 6 | `close_model` | `_comtypes_active_model, _extract_comtypes_model` | ❌ 假 | **下划线内部函数**，且是取模型不是关模型 |
| 7 | `convert_text_to_native_macro` | `is_swp_macro, validate_vba_macro` | ❌ 假 | 转换 ≠ 判断 |
| 8 | `detail_view` | `activate_view, call_view` | ❌ 假 | 详图视图 ≠ 激活视图 |
| 9 | `drawing_sheet_size` | `_read_bmp_size, set_default_lot_size` | ❌ 假 | **内部函数** + 装箱尺寸 |
| 10 | `execute_macro` | `is_swp_macro, validate_vba_macro` | ❌ 假 | 执行 ≠ 校验 |
| 11 | `export_iges` | `export_to_iges` | ✅ 真 | 同一操作 |
| 12 | `extract_template` | `find_template, get_default_template` | ❌ 假 | 提取 ≠ 查找 |
| 13 | `flat_pattern_info` | `_file_info` | ❌ 假 | 钣金展开 ≠ 文件信息 |
| 14 | `hole_table` | `get_fastener_table` | ❌ 假 | 孔表 ≠ 紧固件表 |
| 15 | `manage_file_properties` | `apply_visual_properties, set_custom_properties` | ⚠ 部分 | `set_custom_properties` 是其中一种 |
| 16 | `model_view` | `activate_view, call_view` | ❌ 假 | 模型视图 ≠ 激活视图 |
| 17 | `point` | `click_point, first_result_point` | ❌ 假 | 草图点 ≠ 点击坐标 |
| 18 | `relation` | `add_sketch_relation` | ✅ 真 | 加草图关系 = relation 操作 |
| 19 | `run_vba_macro` | `is_swp_macro, validate_vba_macro` | ❌ 假 | 运行 ≠ 校验 |
| 20 | `scale_body` | `create_deformed_body, entities_on_body` | ❌ 假 | 缩放 ≠ 变形 |
| 21 | `sketch` | `auto_dimension_sketch, end_sketch` | ❌ 假 | 草图 ≠ 自动标注 |
| 22 | `sketch_polygon` | `sketch_polygon` | ✅ 真 | **完全同名** |
| 23 | `slot` | `create_semicircular_slot, sketch_slot` | ✅ 真 | 同一操作 |
| 24 | `template_custom_properties` | `apply_visual_properties, set_custom_properties` | ⚠ 部分 | 同上 |

## 结果
```
24 条抽样：✅ 真 **6** · ⚠ 部分 **2** · ❌ 假 **16**
⇒ 真实命中率 ≈ 6/24 = **25%**（⚠ 24 个样本，95% 区间约 12%~43%）
```

## ★★ 结论：**「144 = 能力在、未暴露」这个说法高估了**
```
原分档：能力在未暴露 144（42%） · 真缺 132（39%）
按 25% 命中率折算：
   真匹配 ≈ 144 × 25% ≈ **36**   ⇒ 仍在「已实现但没暴露」
   假匹配 ≈ **108**              ⇒ 应当归进「真缺」
⇒ 真缺 ≈ 132 + 108 ≈ **240**（不是 132）
```

## ★ 为什么匹配器会错这么多
它按**后缀词**匹配（`sketch` / `view` / `template` / `macro`），
而这些词在 SolidWorks 里是**高频通用词** ⇒ 一个 `*_view` 就能配上几十个操作。
⚠ **这与已知事实 52（名字是弱信号）同源**，且与事实 53（启发式连续修补就该停）相邻：
**这一档不该由字符串匹配给出结论，只能人工核。**

## ⚠ 未查证
* 只核了 **24/144**（抽样），**剩余 120 条未逐条核**；
* 「部分」那 2 条算不算命中，**口径未定**（本表按不计入"真"处理）。
"""

P = Path(r"C:\swprojects\sw-skill-fork\docs\union-gap-triage-sample.md")
P.write_text(SAMPLE, encoding="utf-8")
print("  ok 已写 docs/union-gap-triage-sample.md")

# ② 在生成的 triage 文档里挂上修正（⚠ 不能改生成器逻辑，只加提示）
Q = Path(r"C:\swprojects\sw-skill-fork\docs\union-gap-triage.md")
t = Q.read_text(encoding="utf-8")
NOTE = """> ⚠⚠ **2026-10-01 轮 101 修正**：本表「**能力在、未暴露 144（42%）**」这一档
> **高估了**。人工核样 24 条（每 6 取 1）⇒ **真 6 · 部分 2 · 假 16** ⇒ **真实命中率 ≈ 25%**。
> ⇒ 真缺应约 **240**（= 132 + 144×75%），不是 132。
> 证据与逐条判定见 [`docs/union-gap-triage-sample.md`](union-gap-triage-sample.md)。
> ★ **根因**：该档来自**后缀词**匹配，而 `sketch` / `view` / `template` / `macro` 是高频通用词
> ⇒ **这一档不该由字符串匹配给结论，只能人工核**。
"""
if "轮 101 修正" not in t:
    lines = t.splitlines(keepends=True)
    ins = 1
    for k, l in enumerate(lines):
        if l.startswith("#"):
            ins = k + 1
            break
    Q.write_text("".join(lines[:ins]) + "\n" + NOTE + "".join(lines[ins:]), encoding="utf-8")
    print("  ok triage 文档已挂修正提示")
else:
    print("  triage 已有修正提示")
