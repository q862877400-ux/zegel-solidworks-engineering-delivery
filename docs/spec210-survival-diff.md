# 规格 210 · 存活普查**总表**（B3 的全量读数 · 448 个工具）

> ★ 由 `tools/gen_survival_diff.py --group all` 生成 —— **不要手改**。
> ★★ 本规格的判据：★「**声明只读却观察到指纹变化**」= **0 或逐条定性** ✓

· ★ `empty`：**47** 条 ⇒ agree **35** · missed **2** · undecided **10** · ★ 硬红 **2** 条
· ★ `nonempty`：**135** 条 ⇒ conservative **71** · undecided **64** · ★ 硬红 **0** 条
· ★ `null`：**266** 条 ⇒ undecided **266** · ★ 硬红 **0** 条

## 全局

★★ 合计 **448** 条
★★ 四类：★ agree **35** · conservative **71** · missed **2** · undecided **340**

★★★ **硬红门禁（声明只读却观察到指纹变化）：2 条** ⇒ ★ **已逐条定性**（★ 每条都进了**实证覆盖层**、★ 且已不再是只读）✓

★ 逐条：

· `solidworks_assembly_check_interference`
· `solidworks_motion_create_study`

