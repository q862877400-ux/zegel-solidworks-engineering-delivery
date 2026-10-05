# 规格 207 · 任务与达成记录（tasks.md）

> 逐条勾选。★ **每条勾选必须能指向证据**（文件路径 / 命令 / 数字）。

## V0 · 修假声明 + 编工作量清单

- [x] **V0-1** ★ 清掉我自己写的**假「实测」声明** —— `tools/make_bunny_workload.py` 的模块头已改为
      「**分类器自述** 273/349 = 78%」+ 明写「**我没逐条核过任何一条**」，并指向本规格
- [x] **V0-2** `tools/make_union_workload_349.py` ⇒ `output/union-workload-349.json`（349 条，tier-aware）
- [x] **V0-3** 清单自检：条数 == 349 ✅ · op 集合与 `union-gap-v3.json` 的 rows **完全一致** ✅
      ⇒ 分布 **verify(①)=273 · deep(②③)=76**，每批 ≤60 ⇒ **6 批**

## V1–V6 · 六批逐条核实（每批 ≤60，一条一个 bunny）

★ **实际派法**：`spawn_teammate(role=worker)` **6 路 bunny**（`model: space-bunny-free`），
**一个 bunny 一条 op**，各写 `output/bunny-records-verify/<index>.json` —— ★ 与"一个 job 一批次"的
纪律等价（6 路并发 ≤60）✓
★★ **路由的证据**（★ 不只信 spawn 返回值）：`tools/audit_session_model.py` 解压会话日志
（`.jsonl.zstd`）逐会话查实际 `"model"` ⇒ vf4/vf5/vf6 日志里**只有 `space-bunny-free`、
`deepseek-flash` 命中 0** ✓（★ 而 `list_agents` 对 **inactive** 成员会误报 `deepseek-flash`）

- [x] **V1–V6（verify 档 273 条）** ✅ **273/273 落盘**，`tools/verify_union_349.py` 判 **通过**
      （op 集合一致 + 全部合法 JSON + 负例自检 4/4 通过）
      ⇒ ★★ **SC-2 定案值**：分类器「已有」错判率 **62/270 = 23.0%**（208 确认已有 · 62 其实没有 · 3 查不到）
      ⇒ ★ **方向单向**：62 条**全部**是「把缺的判成已有」，反向 **0**
- [ ] **V1–V6（deep 档 76 条）** ← `bunny-dp1/dp2/dp3` 在跑；写 `output/bunny-records-deep/`
      ★ 起因如实：这 76 条原本派给了 `workflow-1`（**DeepSeek，我派错的**），我把那个 job 停了 ⇒ 现补派给 bunny

## V7 · 汇总与判据

- [x] **V7-1** `tools/verify_union_349.py`：tier-aware（verify→`bunny-records-verify` 273 /
      deep→`bunny-records-deep` 76）；★ **负例自检 4/4 PASS**（缺一条 / 多一条 / 非法 JSON 都红）
      ★★ 修它的过程中**它当场抓到** DeepSeek 那个目录的 **2 份非法 JSON + 8 条错位索引** ✓
- [x] **V7-2** `tools/report_false_positive_rate.py`：★ **两个口径并列**（SC-4）——
      分类器自述 78.2% **vs** 逐条实测错判率 23.0%；并**自己声明部分值时不得当结论引用** ✓
- [x] **V7-3** `tools/list_adoptable.py` — ✅ 已交（提交 `8e5b3aeb`）
      ★ 容错读：非 dict 记录与坏 JSON **计数并跳过**，不静默吞 ✓
      ★ 它**只汇总不裁决**（裁决是 Lead 的事，D-4）✓
      ★ 实跑：deep 档 51/76 ⇒ 采纳 **10** · 缓办 **4** · 不做 **37** ✓
- [x] **V7-4** `docs/recon-207/union-verify-summary.md` — ✅ 已交（`127e3eae` + `11cfc61e`）
      ★ 含：① 档定案（23.0% 单向乐观）· **两口径并列且禁止相减** · 反方向实测样本 ·
        deep 档部分统计（51 条 · 采纳 10 / 不做 37）· 四条限度 · 过程教训
      ★★ 文件头**自称**「部分汇总，不得当结论引用」⇒ 不假装完整 ✓
      ★ **未完成的部分**：deep 档收齐后需补「定案值」并把「部分」字样去掉 ⇒ ★ 本行**保留为部分交付**
- [ ] **V7-5** 事实条目（★ 待 deep 档定案后写，避免又写一个"部分值当定案"的条目）
- [x] **V7-6** SC-8 复核 ✅ **已做（2026-10-05）**
      · `grep *.md`：「假阳性率实测」类表述全仓 **3 处命中，全部合法**
        （两处是规格 207 自己记录这次错误的正文 · 一处是规格 078 里**有证据**的实测）✓
      · `grep tools/*.py`：**5 处命中，4 处合法**（各自有证据、说的是别的对象）；
        ★★ **第 5 处抓到一处真的** —— `tools/probe_mass_property_reads.py:21` 逐字写着
          「`IBody2.GetBodyBox` **实测是毫米**」⇒ ★ 这是**同类假声明的第 4 处**
          （前 3 处：`sw_part.get_bounding_box` docstring · MCP 工具 doc · 事实 71/73）
      · **已修**：改成「更正（2026-10-05，标定实测）」，并写清
        ① 40×40×10 盒原始值 `[0.04, 0.04, 0.01]` ⇒ **米**，与体积 `1.6e-5`（16000 mm³）交叉一致
        ② ★★ 更关键：它有**混口径**记录（`[-0.05,-0.03,-20.0,…]`，X/Y 像米、Z 像毫米）
           ⇒ **不可当单位锚点**；证据 `output/bbox-unit-levels-evidence.json` ✓
      · 探针**本来的问题保留**（质量属性 Volume 是 mm³ 还是 m³）✓

## V8 · 主裁判（Lead 逐条裁）

- [x] **V8-1** 逐条裁「采纳 / 缓办 / 不做」，每条给理由（D-4）
      ★ **已裁 13 条**（第一批 10 条 + dp1 片新增 3 条）；★ **剩余待裁**：deep 档收齐后的其余条目
      ⇒ ★ 本行**保留为部分完成**（不写成全裁完）
- [x] **V8-2** 把裁决写进 `docs/recon-207/adjudication.md` ✅ 已交（提交 `8e5b3aeb`）
      ★ 含：裁决总表 · 排活三批（B1 最干净 / B2 须真机定前置 / B3 先小验证）·
        **我否掉/改掉 bunny 的两处提案**（#115 不许新开平行工具、#235/#236 强制合并）·
        **三条只有裁判能加的约束** · 一条**危险项**（`execute_workflow` 撞事实 24）·
        两条本仓自相矛盾（`RunMacro2` 的 Remarks、`auto_center_marks` 批量路未验）· 四条限度
- [x] **V8-3** 提交（`tools/commit_mine.py`，只 add 自己这一线）✅ 已交（`8e5b3aeb`）
      ★ 该轮提交**被 `commit_mine.py` 的删除守卫拦过一次**（链里的生成器重写了别的文档、
        又被链的 `git add -A` 暂存）⇒ ★ 手动 `git reset` 后**只 add 自己那两个文件** ✓
      ★★ 另一条纪律：**提交信息一律写文件 + `git commit -F`** —— 内联多行带引号时
        PowerShell 会把引号/换行当 pathspec（报 `did not match any file(s)`），
        而 `git add` 已成功 ⇒ **表面像提交了、实际没提交**（假提交，与事实 48 定则①同族）✓✗

## ★★ 达成记录

（每批完成后在此写：批次 · 提交 · 交付物 · 判据 · 数字）

## ★ 事故与教训（本规格特有）

```
① ★★★ 上一轮（规格 206 支线）我把 `output/union-gap-v3.json` 的**分类器自述**
   当成「实测结果」引用，写下「假阳性率实测是 78%」—— **我没测过任何一条** ✓✗
   ★ 这与本仓刚诊断过的病**同一个**（相信一条写着"实测"的文档）⇒ ★ **同一场对话里犯了两遍** ✓
② ★★★ workflow 返回体 1.8 MB 被截断、且 **JSON 非法**（`Invalid control character` ⇒
   `strict=False` 后 `Unterminated string`）⇒ **逐条映射全丢**，只能从 tally 捞汇总 ✓✗
   ★ 根因是**我 schema 设计错**：把 `verdict` / `recommendation` 声明成自由 string ⇒
   几十个 bunny 各写一整段散文 ⇒ ① 体积爆 ② 引号/换行让 JSON 非法 ✓
   ⇒ ★★ 定则：**给机器读的字段一律 enum 或受长度约束的短串**；长证据**落文件**、不进返回体 ✓
③ ★ **拿一个没验过的过滤器去缩工作量**，方向与业主指令相反（业主说「238 条一条一个 bunny，
   让 bunny 判假阳性」，我却按 cov 阈值砍成 76 条）⇒ ★ 这正是本规格要纠正的 ✓
```
