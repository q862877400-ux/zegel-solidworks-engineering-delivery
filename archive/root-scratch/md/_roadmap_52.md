            52 🔴🔴 **输入异常根因定位：**是我自己的测试在全量回归时真的按 Ctrl+A****（轮 63）：
               用户两次报告「鼠标键盘忽然被影响（全选蓝底/回车/Ctrl）」，
               **第二次发生在我跑全量回归的时刻** ⇒ 逐环查证：
               ```
               tests/test_sw_gui_input.py L212/L233  assert gi.type_text(ctl,"195")
                 → scripts/sw_gui_input.py L236 type_text()
                 → L56 "input_api": "type_keys"   ← **默认逐键真输入**
                 → L62 "clear_with": "ctrl_a"     ← **默认清空策略 = Ctrl+A**
                 → L211 _tap_ctrl(ord("A"))       ← **真的发 Ctrl+A = 全选**
                 → L130 → win32api.keybd_event
               该测试文件 **monkeypatch 出现 0 次** ⇒ 零 mock
               仓库 **没有任何 conftest.py** ⇒ 零全局保护
               ```
               **⇒ 跑一次全量回归 = 在真实桌面按一次 Ctrl+A。**
               ⚠ **也解释了「为什么重启没用」**：重启后一跑回归，它又发生。
               ⚠ **两个 bug 叠加**才长成用户看到的样子：上一提交给 `keybd_event` 加了
                 `finally` 保证抬起 ⇒ 所以是「**一阵一阵**」而非持续卡死。
               ⇒ **止血**（`a09d4f0`）：新增 `tests/conftest.py` 的 **`autouse`** 拦截器，
                 把 `keybd_event`/`mouse_event`/`SetCursorPos` 换成**记录器**。
                 ⚠ **必须 autouse**：本次事故正是「漏一个文件就等于没保护」。
                 **三层验证**：① `test_sw_gui_input.py` 17 passed（拦截下仍通过）
                 ② 临时探针证明只进账本不真按（断言 `len(log)==2` 通过，探针已删）
                 ③ 回归后 14 个修饰键**全抬起**
            53 ⚠ **同轮我修掉 7 处「修饰键/回车卡在按下态」的真缺陷**（`8ad2dfb`）：
               形态一律 `keybd_event(按下) → sleep → 抬起`，而 **`sleep` 可被中断**
               ⇒ **抬起到不了** ⇒ Ctrl/Alt/Enter 卡住（按 A 变全选、菜单被激活、忽然回车）。
               ⚠ **它不需要周期性** —— 一次事故就够。
               修处：`sw_gui_input`（新增异常安全原语 `_press`/`_hold`）·
               **`sw_gui_modal`（每轮发 Enter+Esc、最多 5 轮 ⇒ 「忽然回车」最强来源）**·
               `sw_gui_focus` · `sw_jlcfa_locate` · `sw_jlcfa_fill` · `sw_jlcfa_select` · `sw_jlcfa_search`
               ⇒ 并新增**门禁检查④**（AST 判据 + 负例证明有牙齿）。
            54 ⚠ **我此前的误判（如实记）**：① 「我走 COM 不注入键鼠」→ **错**（有 55 处注入 / 12 文件）；
               ② 「`.pyc` 时间戳证明凌晨 1 点后没跑」→ 对，但**漏了「pytest 会 import 它们」这一路**；
               ③ 「此刻修饰键全抬起 ⇒ 不是我的代码」→ 对，但**推不出**该结论（是**瞬时**注入）。
               ★ **教训：把「某条路径走不通」写成「不是我干的」，与把「没搜到的词」写成
                 「官方没有这个成员」是同一类错误 —— 都是该查全而没查全就下结论。**
            55 🔴 **修掉 `scripts/sw_motion.py` 的真 bug**：`import` 区**没有 `from pathlib import Path`**，
               而 `_motion_typelib_candidates()` 用了 `Path(executable)` ⇒ **`NameError`**
               ⇒ **整条 Motion 路径在真机上根本走不通**。
               ⚠ 它能活这么久，是因为 `tests/test_sw_motion_audit.py` 把
                 `get_motion_study_manager` / `ensure_motion_type_library` **两个入口整个 monkeypatch 掉了**
                 ⇒ **入口零覆盖** ⇒ 契约测试已补「入口可调用且不抛 NameError」的断言。
            56 🎯🎯 **护城河第三域「动画导出 AVI」找到确切 API**（**我此前写「尚未查证到」是错的**）：
               ```
               Boolean      IMotionStudy::SaveToAVI(String, AVIParameter)   ← 2 参
               AVIParameter IMotionStudyManager::CreateAVIParameter()       ← 零参（工厂在 manager 上）
               IAVIParameter 15 个属性（反射里是 get_/set_）
               swapi 原文: "Saves the animation to a .avi, .bmp, or .tga file."
               ⚠ 而 `scripts/sw_api_swmotionstudy.py` **早就登记了** `'SaveToAVI': 2`
                 ⇒ **答案一直躺在仓库里，只是没人去实现它**
               ```
               ★ **错因：我只搜了 `SaveAnimation`/`SaveMovie`/`PlayAnimation`，没搜 `SaveToAVI`。**
               ★★ **教训：把「没搜到的词」写成「官方没有这个成员」，是铁律 5 最危险的误用** ——
                 铁律 5 允许「查不到」，但**不允许「没查全就说查不到」**。
               **真机验证（SW 2026 SP4.1）**：`ensure_motion_type_library()` ⇒ 找到 `.tlb`；
               `GetMotionStudyManager`/`CreateMotionStudy` ⇒ 非 None（`GetDuration`=4.0）；
               `CreateAVIParameter` ⇒ 非 None（默认值可读 `FramePerSecond=7.5`）；
               `configure_avi_parameter(FramePerSecond=12)` ⇒ **回读 12.0**（写入生效）。
               🔴 **导出需要真实动画**：空装配体上 ——**不 `Calculate` 时返回 `True` 而文件 0 字节**
                 （**「返回码撒谎」的又一例**）；`Calculate` 后**返回 `False`、文件不存在**
                 ⇒ **判据不看返回值，只看「文件存在且大小 > 0」**。
               ⇒ `animation_export`：**`not_implemented` → `stitched`**（**没有**「导出非零文件」的证据
                 ⇒ evidence 如实留空，**不升 verified**）；`motion_study.verified_versions`
                 从 `['2024']` 改 **`['2026']`**（本机 2026，**2024 从未验过**）。
               ⇒ 新增 `scripts/sw_motion.py` 三函数 + `tests/test_sw_motion_avi_contract.py`（11 条）
            57 ⚠ **同一处连修 ≥3 次要回退**（**事实 53 重演**）：我在 `check_env_pitfalls.py` 上
               **连续 4 次 edit 把两行粘成一行** ⇒ `git checkout --` **回退整个文件**
               （检查③ 在 HEAD 里已有，不会丢），再**分 3 步重做、每步验证**。
               **根因**：`old_string` 以换行结尾而 `new_string` 不以它结尾 ⇒ **并掉一个换行**。
               ⇒ **定则：`edit` 的两边要严格对称地处理行尾。**
            58 ⚠ **一个来源块覆盖不到下面多个定义单元**（**同一坑踩两次**：`verify_costing_e2e.py`
               与 `sw_motion.py`）⇒ `check_provenance` 报「N 行没有可追溯的出处」
               ⇒ **每个定义单元前都要有足够近的来源块**。
