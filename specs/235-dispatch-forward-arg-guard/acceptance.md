# acceptance 235 —— 分发口**调用点**的非字面量实参门禁

> 离线切片（**未调 COM / 未碰真机**）· 未提交 · 未部署 · 未删任何文件 · 未派任何成员。
> ★ 本文件是 spec 235 的**验收记录**，与 `output/AUTO_RUN_2026-10-09-1251.md` 一致。

## 一、交付物

| 件 | 路径 | 动作 |
|---|---|---|
| 门禁 | `scripts/check_dispatch_forward_arg_guard.py` | **新增** |
| 判据 | `tests/test_dispatch_forward_arg_guard.py` | **新增**（19 例） |
| 声明 | `scripts/sw_drawing_create_missing.py` · `scripts/sw_drawing_view.py` · `scripts/sw_simulation_study_options.py` | **纯插入 4 行**（零删除） |
| 接线 | `scripts/release_check.py` | 改（`_run_dispatch_forward_arg_gate` + fail 判据 + `_gate_results`） |
| 登记 | `docs/gate-classification.json` | 改（44 → **45**） |
| 量测 | `output/_probe235_gap.py` · `_probe235_gap2.py` · `_reg235_gate.py` | 一次性（**不进仓库代码**） |
| 状态 | `docs/ROADMAP.md` §一 · `.specify/feature.json` · `memory/2026-10-09.md` · `output/AUTO_HANDOFF.md` | 更新 |

## 二、判据读数

| 判据 | 读数 |
|---|---|
| 门禁本体（真树） | `非字面量 8 · 可枚举 4 · 候选值 distinct 12 · 表态 upstream 3 / dynamic 1 · 违规 0 · [PASS] · exit 0` |
| **红基线**（改实现前） | `[FAIL] 违规 4 处 = [undeclared] ×4` · **exit 1** |
| **变异检验**（短路 `judge`） | `Ran 19 tests · FAILED (failures=6)` ★ 判据不是空判据 |
| 新判据 | **Ran 19 tests · OK**（18.7 s） |
| 229–235 合并回归 | **Ran 92 tests · OK**（157.2 s）★ 73 → 92，证明没碰坏 |
| 收尾链 `round_chain.ps1` | `release_check: 第 1 轮 OK` · `19 passed in 23.81s` |
| **门禁全套** @**3.14.7** | `EXIT 0` · `status pass` · `missing []` · `gates` 43 → **44** · `dispatch_forward_arg_guard: pass` |
| 登记条目 | `classification` 44 → **45**（★ 两套口径**都 +1**） |

## 三、★★★ 核心事实：**「被计数」不等于「被审」——最后 8 个点**

`check_dispatch_entry_guard.resolution()` 从 spec 230 起就报 `partial 3 · unresolved 4 ·
no-callers 12`，**连着五轮**（230–234）**没有人去问「这些入口的调用点到底长什么样」**。
本轮**先量**（`output/_probe235_gap.py`）⇒ 缺口**只有 8 个调用点**：

| # | 位置 | 形态 | 处置 |
|---|---|---|---|
| 1 | `sw_assembly_doc.py:398` | `IfExp`（`"HideComponent" if hidden else "ShowComponent"`） | **可枚举**（两支并集，全官方） |
| 2 | `sw_drawing_create_missing.py:286` | `Name` = 包围 `def` 的形参 | `upstream _sum_over_views` |
| 3 | `sw_drawing_view.py:391` | `Name` = 包围 `def` 的形参 | `upstream call_view_no_args` |
| 4 | `sw_part.py:851` | `Name` = `for` 目标（字面量容器 2 候选） | **可枚举**（全官方） |
| 5 | `sw_preference_guard.py:108` | `Subscript _GET[kind]`（模块级 dict） | **可枚举**（取**值**） |
| 6 | `sw_preference_guard.py:115` | `Subscript _SET[kind]`（模块级 dict） | **可枚举**（取**值**） |
| 7 | `sw_simulation_study_options.py:664` | `Name` = `for` 目标 over **形参 dict** | `dynamic`（键在静态范围外） |
| 8 | `sw_simulation_study_options.py:904` | `Name` = 包围 `def` 的形参 | `upstream set_study_option_report` |

⇒ ★★ **可枚举 4 / 需表态 4**。★ 与 234 的 `local` 桶（46 处）**零重叠**（实测，防重复判罪）。

★★ 通用教训：**「入口被分类计数」≠「调用点被审」** —— 分类是**入口级**的，
而盲区在**调用点级**。与 225「分类不是判据」、232「一个数被反复引用而没人守它」同族。

## 四、★ 本轮的两个设计决定（都写成了形态规则，不写散文）

1. ★★ **二级转发只「要求声明」不「递归解析」**（交接单 §③ 的处置）。
   追下去会变成**会移动的靶子**（`_sum_over_views` 的调用方又可能有调用方）；
   而「登记在案 + 自证」已能保证盲区**不会被悄悄扩大**。
2. ★★ **`upstream` 声明必须自证**：实参**必须**是包围 `def` 的形参，且包围 `def` 名
   **必须**等于声明的 caller 名 ⇒ 抄错名字 / 拿它给局部变量躺平都**会红**
   （判据：`test_upstream_with_wrong_caller_name_is_red` · `test_upstream_on_non_parameter_is_red`）。

## 五、★ 口径不变量（**独立于本门禁的取点**）

凡带非字面量调用点的入口，`resolution()` 的分类**必须**是 `partial` / `unresolved`
（`resolved` 的定义就是「**全部**调用点的成员名都是字面量」）⇒ 不符即 `[class-mismatch]` 红。
★ 这条**不依赖**本门禁自己的取点实现，是**两个独立口径的交叉断言**（spec 233 的教训：
一个数被反复引用而没人守它 ⇒ 先量它的口径）。

## 六、★ 源隔离（spec 234 的坑，本轮**按设计**避开）

234 踩过：新门禁内部 import 别的门禁时，那个门禁读的是**它自己的** `DSH_*_ROOT`。
本轮的做法：取点走**显式** `cdeg.scan(root=ROOT)`；官方源走**本门禁自己的**
`DSH_DISPATCH_FWD_DUMPS` / `_SWAPI`（在调 `official_members()` **之前**覆盖它的模块级路径）
⇒ 合成树**天然隔离**。★ 并加一条判据钉住它：
`test_synthetic_tree_does_not_read_real_sources`（断言只看到 3 个合成名、不含真树的 18460）。

## 七、★ 本轮自己踩到的坑

1. ★★ 首版 `judge()` 把「`probe` + 候选值**全部**查得到」**漏判成绿**（该红）——
   原因是「候选值存在性」写在 `main()` 的循环里、而「code 自证」写在 `judge()` 里，
   两边**各判一半** ⇒ 覆盖不到。修法：把 `uncovered` **传进** `judge()`，
   **自证条件集中在一处**（唯一一个判罪入口）。★ 同族教训：**判罪逻辑不许分居两处**。
2. ★ 真树首跑 **4 处 `[undeclared]`** 就是红基线 ⇒ **先证能红**才动手插声明（未跳步）。
3. ★ 变异检验（短路 `judge`）⇒ 6 例转红 ⇒ 恢复；★ 这条是「判据本身也要有能红的判据」。

## 八、未过门 / 未完成

1. **候选值的接口归属**不判（属 `check_interface_member_ownership.py`，映射表有洞）。
2. `dynamic` / `upstream` 只做**形态**自证，**不验候选值本身对不对**（**需真机**）。
3. **二级转发的上游**（`_sum_over_views` / `call_view_no_args` / `set_study_option_report`
   各自的调用方）**未纳入守卫** —— 本切片**有意**只要求声明。
4. `no-callers 12`（`sw_api_*.py::call_index`）**无调用点** ⇒ 无靶子（只登记）。
5. 16 条 arity 定罪 / `HEM_POSITIONS` 真机复核 —— **需业主另行授权 COM**。
6. 223 的 8 条 `HEAD` 即红既有失败 —— 权属未确认。
7. 真机未验；未提交未部署。
