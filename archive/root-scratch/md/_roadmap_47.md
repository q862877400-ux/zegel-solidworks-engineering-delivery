            ㊼ ★★ **护城河 `costing` 升 `verified`**（轮 61）—— 交接的「优先 1」：
               `costing` 是护城河三域里**唯一有实现却停在 `stitched`** 的（无测试、无运行证据）
               ★ **真机完整闭环跑通**（SW 2026 SP4.1；验收命令 `python tools/verify_costing_e2e.py`）：
               ```
               Extension.GetCostingManager() ⇒ **非 None**      ← 入口打通
               GetTemplateCount(0/1) ⇒ 2 / 2；4 条 .sldctc/.sldcts 模板路径
               GetMaterialName(0) ⇒ '普通碳钢' · GetMaterialClass(0) ⇒ '钢'
               **total_to_manufacture = 3.2714499345031918（USD）** · costing_type = 0
               ⇒ verdict: **pass**
               ```
            ㊽ 🔴 **修掉一个真缺陷（真机抓到）**：`read_cost_analysis` 等 **7 处**写 `int(x or -1)`
               ⇒ `CostingType` 真值 **`0`** 被吞成 **`-1`**（把「机加工」误报成「未知」）
               ⇒ 改用 `_num()`（**只有 `None` 才回落**）。**修复由真机证明**：修前 -1、修后 **0**
               ⚠ 与本项目**早已记录**的「`bool(0)` 为 False ⇒ 不要用真假值判」是**同一族**
            ㊾ 🔴 **那段来源块写着一个**错误结论**（正是缺口成因）**：旧文说
               「CostManager 由 **Composer** 给出…**本机没装 Composer**，ProgID 查不到 ⇒ 接收调用方传入」
               **两条硬证据推翻**：① 反射里**有** `IModelDocExtension::GetCostingManager()`；
               ② 注册表里**有** `swcCostingAddin.SwcAddin`（`.34`）等 8 个 ProgID ⇒ **本机装了**
               ⓘ「4 个 ProgID 全返 None」这个观察**对**，但结论「所以拿不到」**错**
               ★ **教训：把「某条路走不通」写成「对象拿不到」，会让模块放弃唯一的正解**
               ⇒ 新增 `get_costing_manager(model)`（此前 24 个公开入口里**没有入口**）
            ㊿ ★ **新增防增长门禁：`x or <默认值>` 吞掉合法的 0**（`check_env_pitfalls.py` 检查③）
               · 判据：**只有「默认值 ≠ 该类型的 falsy 值」才有害**（`or 0`/`or 0.0` 幂等）
                 ⚠ 我第一版把 `or 0.0` 也标有害 ⇒ **假阳性**（门禁首跑要用真实数据核对 —— 这次是我自己撞上）
               · **基线记账 42 条 / 45 处（13 个模块）**，新增即红；已修的必须从基线删
               · ⚠ 检查③ **不扫 `tests/`**（负例夹具里必须有那串字面量 ⇒ 否则抓到自己的夹具）
               · ⚠ 匹配前**去注释** ⇒ 否则门禁**抓到解释这个坑的注释本身**；
                 **改注释让它变绿 = 把判据改坏去迁就实现**（红线）
               · 剩 **38 处存量未改**（如实记录：`sw_simulation_loadprops` 14 · `sw_simulation` 6 · …）
            51 △ **护城河三域现状**：`topology_optimization` **verified** · `costing` **verified** ·
               `animation_export` **not_implemented**（唯一剩下的空缺，见游标 ㊹）
