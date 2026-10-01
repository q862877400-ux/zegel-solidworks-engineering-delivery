            ㉝ ★ **`probe_results_api_surface.py` 已收进 `tools/`**（轮 56）—— 001 的 **SC-001** 点名它，
               而它原先**只在工作区根** `D:\AI\SW\` ⇒ **换机器 / CI 跑不了**
               （与 `capability_gap.py` 同类，这是**第 2 例**，两例都已闭）
               · `sys.path.insert(0, r"C:\swprojects\sw-skill-fork")` → `Path(__file__).resolve().parents[1]`
               · 来源块更新到新位置；**业务逻辑与搬移前逐行相同**
                 （用 `difflib` 核过：差异**只在来源块与路径处理**）
               · 001 的 `spec.md` / `plan.md` / `tasks.md` / `converge.md` 四处引用**全部改成仓库内路径**
            ㉞ 🔴 **`check_report_freshness.py` 的口径被**实测打回两次**（轮 56）—— 两次都是**可用性**问题**：
               ```
               ① 量 HEAD ⇒ 有**未提交改动**时，按门禁给的数去写、**提交后必然又红一位**
                  （实测：门禁报 178/+126589，而未提交的探针再加 1 文件/+153 行 ⇒ 提交后 179/+126742）
               ② `dirty = bool(files or untracked)` ⇒ **错**：`files` 是**相对 origin 的总漂移**（179，
                  **永远 > 0**）⇒ `commits` **永远 +1** ⇒ 提交后立刻又红
               ⇒ **正解（现在实现的）**：`files/add/delete` 量**工作树 + 未跟踪文件**（= 提交后会变成什么），
                 `commits` = HEAD 的计数 **+（`git status --porcelain` 非空 ? 1 : 0）**
               ```
               ⚠ **它不会引入循环**：改报告只改**行内容**、不改**行数** ⇒ 计数稳定
                 ⇒ **同长度替换一次写对即自洽**（实证：提交后 `[PASS] 四个字段逐项相符`，树干净）
               ★ **固有代价（如实记）**：**每次改代码都要顺带更新那一行** ——
                 因为「提交后状态」本身会变。门禁的输出已经把它写成**可直接粘贴的修法行**
                 ⇒ 摩擦被压到「复制一行」。**这是「报告保持新鲜」的必然成本，不是缺陷。**
               ⚠ 契约测试同步改到新语义（`test_actual_drift_measures_the_state_that_will_be_committed`），
                 并把**两次踩坑**都写进它的 docstring —— **下一个人不用再踩**
