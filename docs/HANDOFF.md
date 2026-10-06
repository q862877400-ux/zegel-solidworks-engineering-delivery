# 交接文档 —— SolidWorks 自动化仓库（★ 给接手的**新对话**）

> ★ 本文写给**接手这个仓库的下一个新会话**。★ 目标是让接手者**不必重走我已经走过的弯路**。
> ★ 本版更新时间：**2026-10-06** · 仓库 `D:\AI\SW` · ★ **本版新增：规格 209 **全部 15 件活收口完毕****
> ★ 上一版（2026-10-05）讲规格 206/207 的收口与环境陷阱 ⇒ ★ **其内容原样保留在本文后半（见「上一版内容」），本版在最前面**。
> ★ 本版主结论：★★ **规格 209（18 条采纳候选 → 15 件活）15/15 全部收口** ——
> ★ 其中一部分 **verified**、一部分 **stitched**（★ 都是**如实记的负结论 / 半程结论**，不是没做），
> ★ 逐条判据与证据见 [../specs/209-union-adopt-18/tasks.md](../specs/209-union-adopt-18/tasks.md)
> 与 `capabilities.yaml`（★ 每条带 `level` / `evidence` / `limitations`）。
> ★★ **接下来可做的**：① 补规格 209 里**如实记下的「未验 / 未接」分支**（★ 每条都在 `limitations` 里写死了下一步）；
> ② 补 idx 30 `AutoInsertCenterMarks2` 批量路的**单独真机验证**（★ 裁决书 §一 第 2 条点名的缺口）。

---

# ★★ 本版（2026-10-06）：规格 209 **全部收口**

★ **15 件活的全貌**（★ 详细读数与证据在 `specs/209-union-adopt-18/tasks.md` 各条下）：

| 批次 | 条 | 结果 | 一句话 |
|---|---|---|---|
| B1 | `rebuild_report` / `sketch_set_construction_geometry` / 显示状态 / 依赖 / `move_copy_body` 等 5 件 | **verified** | 真机建成并回读 |
| B2-1 | idx 336 `unfold` | **verified** | 建出 `展开1`；★ 事实：**`mark 4` 不是必需的**（官方示例让它看着像必需） |
| B2-2 | idx 34 `balloon` | **verified** | ★★ **定案**：装配图上**有没有 BOM 表都插得进去**（各 Δ=1）⇒ 两家外部项目的论断都**不该照抄** |
| B2-3 | idx 52 `centerline` | **stitched** | ★ 选区回读 **1**、而 `InsertCenterLine2` 回 `None`、中心线数 **Δ=0** ⇒ 「选中了也没产出」 |
| B2-4 | idx 175 `blank_sketch` | **verified** | ★ 双向验过（隐藏 / 显示），回读用 `IFeature::Visible` |
| B3-1 | idx 115+145 `edges/faces` | **verified** | ★ 合并成**一条**工具（按裁决书），并用 **Euler `V−E+F=2`** 回读校验 |
| B4-1 | idx 211 `macro_recording` | **stitched** | ★★ 真机证明**返回值不可用**（未开录制 `RecordLine` 也回 `True`）⇒ 只到「成对调用可达」 |
| B4-2 | idx 173 `hem` | **stitched** | ★ 五种形态**全回 `None`** ⇒ 如实记负结论 + 下一步 |
| B4-3 | idx 181 `intersect` | **verified** | ★★ 建出 `相交1`；**布尔 SafeArray 包装双向证实**（排除唯一实体 ⇒ 回 `None`） |
| B4-4 | idx 155 `fold` | **verified** | 建出 `折叠1` |
| B4-5 | idx 205 `model_annotations` | **stitched** | ★ 调用可达 + 回读可用，但★ **夹具里没有可插的标注**（数据相关，不是后端到不了） |

★★★ **本批最值得接手者读的三条**（★ 都是「看起来该成、实际不成」或反之的）：
1. **返回值不可信**：`RecordLine` **未开录制也回 `True`**（B4-1）· `SelectByID2` / `Select4` 的布尔不可信（**事实 8**）
   ⇒ ★ **判据一律用回读**（★ 本批 15 件每一件都这么做的）。
2. **官方示例的 `Preconditions` 是「例子的环境」，不是「API 的契约」**（B2-2 定案）——
   ★ 我据此假设过「没有 BOM 表就静默无效」，**被真机否证** ⇒ 已记 `spec.md` §五 第 12 条。
3. **空 Dispatch 形参不能传 Python `None`**（**事实 33**）—— ★ 我在 B2-3 **又踩一次**
   （`GetVisibleEntities2` 的组件形参传 `None` ⇒ 四种类型全报「类型不匹配」，
   ★ **看着像「读不到」、实际是我传错了**）⇒ ★ 一律 `create_empty_dispatch_variant()`。

★ **本版新增的工具**（★ 以后都该用）：
- `tools/fix_cjk_quotes.py` —— ★ 把「中文散文里的 ASCII 引号」批量换成「」（★ 我在本规格里**手改了 6 次以上**）。
  ⚠ ★ 它对「引号当字符串分隔符」的形态**会误伤** ⇒ ★ 内置了「**改完语法不过就不写盘**」的安全阀；
  ★★ 更稳的做法是**事实 48**：**长文本先写成独立文件（`.json` / `.md`），再用最短脚本搬运**
  （★ 本版最后一次就是这么做的：`_s209_b4f_caps.json` + 十来行搬运脚本）。

---

# ★★ 上一版（2026-10-06）：规格 209 · B1 批收口

## 〇 · 一句话现状 + 三条自查命令

```powershell
python -c "import sys;sys.path.insert(0,'mcp-server');import register_capabilities as rc;print(len(rc.all_specs()))"   # ⇒ 439
python -m pytest tests\test_tool_specs_batch92.py -q                                                                    # ⇒ 25 passed
(Select-String -Path specs\209-union-adopt-18\tasks.md -Pattern '^\s*-\s*\[ \]').Count                                  # ⇒ 10（B2 4 + B3 1 + B4 5）
```

## 一 · 这一版干了什么

按上一版 §二「下一件该干的活：实现那 18 条」**起了规格 209**，并把裁决书列的 **B1 批**做完：

| idx | op | 落点 | 真机判据（**全是回读**） |
|---|---|---|---|
| 235+236 | `rebuild` | `scripts/sw_session.py` | 三档都 `ok=True` · `needs_rebuild 0→0` · 树 7→7 · 包围盒前后逐位相同 |
| 79 | `construction_geometry` | `scripts/sw_sketch_edit_ops.py` | 置位/复位双向 `ok=True`；★★ **定死"连调两次 = 置位（幂等）"** |
| 97 | `display_states` | `scripts/sw_render_material.py` | 建第二条 → 激活另一条 ⇒ `changed=True`；负例不猜 |
| 244 | `referenced_documents` | `scripts/sw_document_data.py` | 自建 1 零件 + 1 装配 ⇒ `count=1` · `raw_len=2` |
| 209 | `move_body` | `scripts/sw_body_ops.py`（新） | 移动 25 mm ⇒ x `-30/30→-5/55`；复制 ⇒ 实体 1→2 |

★ 6 个新工具（`register_capabilities.all_specs()` 433 → **439**），`capabilities.yaml` **117 条**。
★ 证据：`output/union-adopt-b1-evidence.json`（★ `output/` 被 gitignore ⇒ 重跑那条命令即可复现）。

## 二 · ★★ 本版最值钱的东西：**6 处「官方文档与真机读数不一致」**（照文档写会静默错）

`specs/209-union-adopt-18/spec.md` §五 逐条记账，这里列**最要命的三条**：

1. ★★★ **`InsertMoveCopyBody2` 的长度参数是「文档长度单位」（mm），不是米** ——
   官方页**没写单位**。★ 套「COM 惯例=米」换算传 `0.025` ⇒ **只挪了 0.025 mm**，
   ★★ 而那是个**静默的 1000× 错误**，**而且它能过「包围盒变了」那条判据** ⇒ 谁都发现不了。
   ★★ 定则：**本仓的"米"惯例不能套到没写单位的成员上** —— 逐接口实测。
2. ★★ **`EditRebuild3` 是方法，而 pywin32 下「读」就等于「调」** ——
   三家外部项目都当**属性**读（`_get(doc,'EditRebuild3')`）⇒ 读到的是**返回值 `bool`**、**恒为真**
   ⇒ 拿它当判据**永远为真**（★ 注意：**不是**裁决书写的"bound method"，本仓按真机读数改了口径）。
3. ★★ **`InsertMoveCopyBody2` 的参数名与实际作用轴 X↔Z 互换**（`RotAngleX` 实际绕 Z、`RotAngleZ` 实际绕 X）
   ★ 判据用「只给一个角、看**哪一轴跨度不变**」三格互证定出；★ 补偿后 `rotate_angle_z_deg=30`
   得到跨度 `71.9615 = 60cos30+40sin30` **逐位吻合** ⇒ 单位与轴同时被几何证实。

另三条：只读信息串真机回 `"FALSE"`（官方例子是**空串**，★ 按"非空即只读"会判反）·
`CreateConstructionGeometry` 实测是**置位**不是 toggle · 「第一个名字即活动显示状态」**装配里不成立**。

## 三 · ★★ 本版抓到的**我自己的**错（★ 记下来，因为不记就会被当成"本来就是对的"）

★★ **`rebuild_report` 的包围盒判据是空转的**：`sw_part.get_bounding_box` 回的是**字典**，
而我按可迭代对象写 ⇒ `float("min")` 抛异常**被 `except` 吞掉** ⇒ 回 `None`
⇒ **`bbox_changed` 永远 `False`** —— ★★ **判据看着在、其实没在判** ✓
⇒ ★ 修法：① 取对字段；② 返回值里**显式给 `bbox_comparable`**（**`None`「读不到」与 `False`「没变」必须分得开**）；
③ 加回归测试。★ 同批还修了探针自己的两处错判据（负例以为会抛异常；用"本来就是活动的"那条去验变化）。

⇒ ★★ **可复用的手法**：★ **凡"没读到"与"没变化"落到同一个值上，判据就废了** ——
一律拆成两个字段（**能不能读** / **读到了什么**）✓ 见 `spec.md` §六 全表。

## 四 · ★ 这一版留下的（未处置）

| # | 事项 | 为什么我没动 |
|---|---|---|
| 1 | **B2/B3/B4 共 10 件活未做** | ★ 本轮做到 B1 收口；★ 每件的**硬约束已在 `tasks.md` 逐条写好**（含 B2 的"官方没给 mark"、B4-1 的"StopMacro 会弹 Save As"） |
| 2 | **既有的一处 release_check 红**：`tools/verify_union_349.py:112` 的变换未自证 | ★ 该文件自 `38bd4f3c` 起**未改过**，**不是我造成的**；★ 而本仓红线写着「tools/ 的探针/证据脚本**只报不动**」⇒ **未处置，留给该文件的作者** |
| 3 | `docs/*.md` 的几个生成物**在我开工前就是脏的**（另一条线留下的） | ★ 遵循「两个对话同仓 ⇒ 只写自己那一个文件」⇒ **没有顺手扫进我的提交** |
| 4 | 上一版 §六 的 6 条（273 缓办 · recon-206 漂移 · `RunMacro2` Remarks · `auto_center_marks` · SW 归属 · 逐字复述 2 处） | ★ 全部**原样未动**（★ 仍是业主待决项） |

## 五 · 本版提交（可 `git log` 复核；两次收尾链均绿，聚焦测试 25 passed）

```
3384c8b  规格 209 · B1 批收口：idx 209 move_body 落地 + 修掉我自己写的一处「静默空转判据」
8c868a4  规格 209 · B1 批：把规格 207 的 4 件采纳候选落地（真机全过 + 抓到 2 处官方与真机不一致）
```

---

# ★★ 本版（2026-10-05）：规格 206 / 207 收口

## 〇 · 一句话现状 + 三条自查命令

```powershell
python tools\close_spec207.py      # ⇒ verify 273/273 · deep 76/76 ⇒ 349/349；SC 全绿 exit 0
python tools\list_adoptable.py     # ⇒ 采纳 18 · 缓办 11 · 不做 47
(Select-String -Path specs\206-c1c6-harvest\tasks.md -Pattern '^\s*-\s*\[ \]').Count   # ⇒ 0
```

## 一 · 规格 207 干了什么，结论是什么

**把一份 349 条的「四家外部项目有、我们可能没有」缺口清单逐条核实。**

| 口径 | 值 |
|---|---|
| 分类器**自述**（不是实测） | 273/349 = **78.2%** 打成「①已有等价物」 |
| **逐条实测**（273/273 全覆盖） | 确认已有 **208** · 其实没有 **62** · 查不到 **3** |
| ★★ 「已有」这一标的**错判率** | **62/270 = 23.0%**，**100% 单向乐观**（反向 0） |
| deep 档 76 条逐条读完 | **采纳 18** · 缓办 11 · **不做 47** |

**三条主结论**（见 `docs/recon-207/union-verify-summary.md`，已写成**事实 559**）：
1. **词面覆盖率（`best_cov`）没有判别力**：① 档错法是**乐观**、②③ 档错法是**悲观**，还有**第三种**——
   `cov=0.0` 把**抽取噪声**判成强候选（`217` 是别家 demo 参数字典的键名 · `221` 是文档类型字符串）。★ **调阈值救不了**。
2. **「缺口清单的长度」几乎是噪声**：349 条的清单，真实待办 **18 条（5%）**。
3. **深调（bunny 逐条读官方）的价值高于分类器**：它逼人去读官方**做同一件事的别的入口**。
   ★ 实例：我曾断言「宏录制成员零命中 ⇒ 别家幻觉」，**只对一半** —— 名字确实不存在，
   但能力可达（真入口 `RecordLine` + `RunCommand` + 事件通知，三样都在官方源里）。

**交付物**：`specs/207-union-gap-verify/` · `docs/recon-207/adjudication.md`（**九节五批**逐条裁决 + 三条横向纪律）·
`docs/recon-207/union-verify-summary.md` · 事实 **559** · 工具 `close_spec207.py` / `check_spec207_sc.py` /
`build_union_verify_349.py` / `list_adoptable.py` / `verify_union_349.py` / `report_false_positive_rate.py` / `audit_bunny_routing.py`。

## 二 · ★★ 下一件该干的活：实现那 18 条

`docs/recon-207/adjudication.md` 每条都有：官方成员（**逐字签名**）· mark 表 · 建议工具名与落点模块 · 验证判据 ·
**风险（含"本机 pywin32 后端能不能到"）**。**排活顺序裁决书已给**：

| 批 | 条目 | 为什么这个顺序 |
|---|---|---|
| **B1**（最干净） | `209 move_body` · `97 display_states` · `79 construction_geometry` · `235+236 rebuild`（**合并成一条三档 mode**）· `244 referenced_documents` | 官方页最全（`209` 有 signature + 逐字 mark 表 1/2/4/8 + 示例调用序）；零参或普通 COM；落点都是**已有模块** |
| **B2**（须真机定前置） | `336 unfold` · `34 balloon` · `52 centerline` | 官方**没给 mark** 或**两家结论矛盾** ⇒ 必须先真机定出可建形态 |
| **B3**（先小验证） | `115 edges` + `145 faces`（**一条工具**，FACE/EDGE/VERTEX） | ★ 本会话**已真机确证** `IBody2::GetEdges` / `GetFaces` **可用**（欧拉公式 `V−E+F=2` 成立）⇒ 可动手 |

**★ 三条只有裁判能加的硬约束（照做，否则会做出静默错的东西）**：
1. `235/236`：`EditRebuild3` 是**方法不是属性** —— 别家都当属性读，照抄会拿到 bound method，**拿它当判据会永远为真**。
2. `97`：官方逐字——「多个显示状态同时活动」时那条"第一个名字即活动"的规则**不成立** ⇒ 输出必须带 `ambiguous`，不许替调用方猜。
3. `244`：官方逐字——**Library features 不会返回** ⇒ doc 必须写明这个盲区。

**★ 一条危险项（不许当普通缺口补）**：`execute_workflow`（idx 123）—— 别家是**空壳 + 自标 simulated**，
而它字面承诺的 "parallel execution" **正面撞上事实 24**（单实例 COM 并发会死锁）。

## 三 · 规格 206：7 项全收口

★ **其中 5 项是「交付物早已存在、只缺机械核一遍」**（T5-1 · T5-2 · T5-3 · T3-2 · T4-3）—— 每项都带**可复跑证据**：
- **T5-1**：`scripts/check_fact_single_home.py`（告警级 exit 0）**且已真正接进 `release_check.py`**
  （**5 处**：helper + 调用点 + `_gate_results` + 返回体 + `docs/gate-classification.json`）
  ⇒ 元门禁 `[PASS] 30 个门禁全部已接线`。
- **T3-2**：★ 证据最硬 —— `tools/t3_2_spelling_pairs.py` **复跑**输出「真名 1529 · spelling 554 · 配对 130」
  与文档**逐字吻合**。
- **T5-2 / T5-3 / T4-3**：提交号 / 文件字节数 / `AGENTS.md` 行号可核。

**T2-6 真机验证**（本会话新做）：①②③④ **真机确认**（判据 = **回读计数**或**几何预期**，不是返回值）：
`GetEdges` 回 **12** 条边 · `GetBodies2` 前置成立 · `GetSelectedObject6` 选中→回读 **1** ·
`ClearSelection2` 清空后回读 **0** · 且满足**欧拉公式** `V−E+F = 8−12+6 = 2`。
★ ⑤ `AccessSelections` **不重跑** —— `probe_access_selections.py` 与**事实 47** 已给真机结果
（`0x80010105` 同码 · **20+ 形态穷尽**）；★ 重跑正违反本仓规矩「不要再用『换个参数试试』的方式继续试」。

## 四 · ★ 怎么干活（照这个来，别自创）

```powershell
# 每轮收尾（一条命令）
pwsh -File D:\AI\SW\tools\round_chain.ps1 -Tests tests\<改过的>.py
# ★ 全量 pytest 只在两种情况下跑：发布前 · 改了 sw_connect.py 或门禁本体

# 提交（★ 纪律，别绕）
git reset -q                                        # ★ 先清索引，见 §五 trap 1
python tools\commit_mine.py -m <信息文件> <路径…>     # ★ 信息先写成文件

# 真机（★ 2026-10-05 授权已变更：可自行拉起、用完必须关闭）
$env:PYTHONIOENCODING='utf-8'                       # ★ 不加会因 GBK 打印 ✓/✗ 而崩
python tools\reclaim_solidworks.py --restart        # 起（自带安全判定：有别人的文档就拒绝）
python tools\reclaim_solidworks.py --close          # 关（★ 只关归属标记是自己启动的那个）

# 派活（★ 必须走 bunny）+ 实证路由
python tools\audit_bunny_routing.py --marker <你这批产物路径关键词>   # ⇒ 期望「合规 N · 异常 0」
```

**派活形状（★ 用事故换来的）**：一片 **≤8 条** · ★ **「每判完一条就立刻写文件」写成硬约束** ·
★ **「查不到」是合法交付不是失败**，并明确**不许为了凑数而猜**（只差几条时压力最大，最容易发生）。

## 五 · ★★ 本版新增的 4 个陷阱（照单避开）

1. ★★★ **`round_chain.ps1` 里有三处 `git add -A`**（L84/L117/L142）⇒ 跑完链，**索引里会塞进几百个别线的文件**
   （`specs/203-*`、`specs/204-*`、`docs/recon/*`、生成物…）。**直接 `git commit` 会全扫进去**。
   ⇒ ★ **永远先 `git reset -q`，再 `git add <只你自己的路径>`**。`commit_mine.py` 的**删除守卫**会拦；
   ★ **那是守卫在尽职** —— 别用 `--allow-deletions` 糊过去，**先看清那 N 行是不是你的**。
2. ★★ **`.git/index.lock` 会变陈旧锁**（我遇到 0 字节残留）⇒ `reset/add/commit` **全部静默失败**
   （只报 "Another git process seems to be running"）。**先确认没有 git 进程，再删锁**。
3. ★★ **「0 个新文件」≠「空转」** —— 我因此**误杀过两个 bunny**（其中一个正在写）。
   ★ 正确判据是**最后写入时间**：
   `Get-ChildItem output\<目录> -Filter *.json | Sort-Object LastWriteTime -Descending | Select -First 3`。
   ★ 且 **`wait_agent` 只在成员状态/信箱变化时唤醒，写文件不触发** ⇒ 超时**不代表**没进展。
4. ★★ **判据会静默读过时产物** —— 我的 SC 检查器曾报「330/349」而逐条实为 335。
   ★ 修法：**先算生数、与产物里的数比对，不一致就大声报**。
   ★ 同类：**会喊狼的守卫会被无视**（三例：`list_agents` 对 inactive 误报 · 审计器把 Lead 自己报成违规 ·
   我的 SC-8 判据把**"防它的文档"**报成违规）⇒ ★ 修法：**排除自身 + 把"引用"与"断言"分开**，
   并把判据的**已知边界写进输出**。

## 六 · ★ 我留下、需要你决定的（未处置）

| # | 事项 | 为什么我没动 |
|---|---|---|
| 1 | **18 条采纳候选未实现** | 规格 207 只做「核实」不做「实现」⇒ **该起新规格** |
| 2 | `docs/recon-206/more-specific-audit.md` 的 **7+/8− 漂移** | 两条路都要业主定：接受重新生成的版本 / 把那句人工结论写进生成器模板 |
| 3 | `RunMacro2` 的官方页**有** Remarks，而 `capabilities.yaml` 写着"是空的" | 按铁律 4 应以官方源为准更正，但那是**别处的清单**，我只记录 |
| 4 | `auto_center_marks` 的**批量路 `AutoInsertCenterMarks2` 从未单独真机验证** | 现有 `verified` 标签**覆盖不到那条路** |
| 5 | SolidWorks **此刻可能在跑**（重启后 `PID=38500`） | ★ **归属证不出来** ⇒ 按纪律「**证不出归属就不动**」**我没关它** |
| 6 | `check_fact_single_home.py` 认出 **2 处逐字复述**（`docs/dead-ends.md` 复述事实 230 · `specs/202-*/.../vd50-A-surface.md` 复述事实 303） | 两处都在**别人的规格目录/生成物**里，写盘边界不由我改 |

## 七 · 本版提交（可 `git log` 复核；链均绿 8 passed）

```
10e55dee 补齐本会话产出但一直未入库的 5 个工具
4b6dbe3a spec 206 · T2-6 收口：5 条前置全部有判据
d386839a spec 206 · T2-6 第二批真机结果（③④ 成立）
5d9411db spec 206 · T2-6 第一批真机结果 + 按授权改纪律
683410f5 spec 207 · 收尾措辞：把"部分/未定案"改成定案值
788a19f  spec 207 · 收尾：deep 76/76 ⇒ SC 全绿 + 第五批裁决
2359e9b  spec 207 · 新增收尾链 tools/close_spec207.py
623a63d  spec 207 · SC 检查器退出码语义：只有"全绿"才 exit 0
c1b1af4  spec 207 · V7-1b 聚合件（SC-1/SC-5 的落地件）
086303e  spec 206 · T5-1 接线完成（5 处全落地，元门禁放行）
```

## 八 · 一句话给接手的人

**别信"清单长度"，信逐条读数；别信返回值，信回读；别信别家的名字，信官方页；
别信"我记得做了"，信一条能重跑的命令。** —— ★ 这四句是本会话每一次翻车的根因。

---

# 上一版内容（2026-10-04 · ★ 原样保留）

> ⚠ 下面是上一版交接（24h 三阶段主线 / 环境陷阱 / 工具栏台账）。★ 它讲的两条线（`specs/202-user-coverage-gaps`
> 等）**与本版不是同一批活** ⇒ 若你要接的是那些线，读下面这段；★ 若接的是规格 206/207，**读上面的本版即可**。

---

## 〇、一句话现状

> ★ 仓库同时在跑**两条线**：
> ★ **线 A · 工具栏「不能项」攻关** —— 台账 **119** 条 ⇒ 已能 **83** · 可攻关 **3** · 待查 20 · 待验证 6 · 后端到不了 7。
> ★ **线 B · 24h 三阶段主线**（`specs/202-user-coverage-gaps`）—— **先把「已完成」核真 → 再把「没核过的」核全 → 最后才补新能力**。
> ★ 手法固定为：**查官方三源 → 按六条铁律立柱 → 实现包装 → 真机实测 → 加静态门禁**。

| 指标 | 当前值（★ 2026-10-04 实测） |
|---|---|
| 提交数 | **998** |
| `capabilities.yaml` | **110** 条（`verified` **97** · `stitched` **11** · `not_implemented` **2**） |
| `docs/known-facts.md` | **4138** 行 · 编号最大 **515** · 条目 **513** |
| `docs/toolbar-ledger.json` | **119** 条 |
| `release_check.py` 的 `_run_*gate` 函数 | **30** 个 |
| 真机证据 | `output/` 下 **481** 个 `.json` |
| 测试文件 | `tests/test_*.py` **249** 个 |

★ **线 B 的三阶段结论**（详见 `docs/final-report-24h.md`，那边每轮刷新）：
① 收口核对：判据 A 可疑 **0 条**、判据 B 证据路径覆盖 **96/96 = 100%**；
② 废弃成员：真命中 **37**（生产 **6**，**全部已处置 ⇒ 生产侧待办 = 0**）；
③ 缺口地图三条收敛判据**全达标**（无处可放率 **7.85%** ≤ 20 · 空格率 **19.33%** ≤ 60 · 双源一致率 **44.42%** ≥ 30）。
⚠ ③ 的 ①② 是**轮 99「补词」**做的，**不是**近期做的 —— 别把功劳算错。

---

## 一、★ 先读这六份（顺序别换）

```
① D:\AI\SW\AGENTS.md                        ← ★ 常驻纪律（六条铁律 / 验收标准 / 红线）
② docs/known-facts.md                       ← ★ 事实表（513 条；★ 遇事先查它，别重走）
③ docs/dead-ends.md                         ← ★ 走死的路（由 gen_dead_ends.py 生成，别手改）
④ docs/toolbar-ledger-verified.json         ← ★ 台账（★ 每条带 tier + note，★ note 里常写着"下一步"）
⑤ docs/toolbar-gaps-backend-limits.md       ← ★ 后端到不了的**依据**集中在这
⑥ docs/final-report-24h.md                  ← ★ 线 B 的收口报告（做成了 / 没做成 / 为什么 / 下一步）
```

★ 另有 **`~/.dsh/AGENTS.md`**（用户全局层，每轮自动注入）与 **`~/.dsh/纪律/`**（纪律正文，含**资源与环境**）。
★ 另有 **[`docs/team-roles.md`](team-roles.md)** —— ★ 怎么派便宜模型助手（★ 含本轮的实测坑）。
★ 另有 **[`docs/kickoff-bunny-sideline.md`](kickoff-bunny-sideline.md)** —— ★ 给**支线对话**的第一句话模板（批量辅助活全派 Bunny）。
★ 另有 **[`docs/recon/`](recon/)** —— ★ 批量产物落点（含 `README.md` 记着判据与待决断）。

---

## 二、★★★ 环境陷阱（★ 这一节最值钱 —— 都是**实测踩出来的**）

### 2.1 ★ SolidWorks 相关

| 陷阱 | 事实编号 | 正确做法 |
|---|---|---|
| **实体（边/面）按坐标选**（`SelectByID2("","EDGE",x,y,z,…)`）**选不中** | 32 / 482 / 483 | ★ 用 **`IEntity.Select4`（按对象选）**；本仓封装：`sw_selection_spec.entities_on_body` + `select_object` |
| ★ **`Select4` 没有 `mark` 参数** | — | ★ 选完用 **`ISelectionMgr.SetSelectedObjectMark(i, mark, -1)`** 补设 |
| ★ **发射线前不 `ClearSelection2(True)` 会留残留对象** | 479 | ★ 发射线前**先清选区** |
| ★ **官方 `## Examples` 段给的是"调用序"** | 480 / 482 | ★ **读例子**（签名与 Remarks 都给不出调用序） |
| ★ **台账/文档里 `api` 名可能是已废弃的旧入口** | 433 / 476 | ★ **读那个 md 头顶那句 `Obsolete`** —— 继任者名字就在那句里 |
| ★ 能力层**回 `False` / `None` 不等于失败** | 482 | ★ 例：`SketchOffsetOnSurface` 回 `False` 是**正常的** |
| ★ **跑真机一律走护栏** | — | ★ `python tools/sw_guard.py --timeout N -- python <脚本>` |

### 2.2 ★★ 资源与环境（★ 本轮业主当场点破两件事）

| 陷阱 | 正确做法 |
|---|---|
| ★ **用完了不关 SolidWorks** | ★ 纪律逐字：**「一轮真机活收尾时它是关着的」**、**「跨轮不许留 —— 收尾链跑完就关」**。★ 本轮实测代价：`cwbcbfmesh` 一度涨到 **24.6 GB**（纪律记的另一例是 8286 MB）⇒ **"我会记得"不是机制** |
| ★ **关的时候误杀别的会话** | ★ **只关自己启动的**。正解：`sw_connect` 在**它自己启动**实例那一刻把 PID 落进 `output/.sw-started-by-us.json`；`tools/reclaim_solidworks.py --close` **只认那个标记**，没有标记就**拒绝关闭** |
| ★ **`--restart` 不能当"关"用** | ★ 它是"停完**重连**" ⇒ **重连又把它拉起来**（实测：kill 掉 28539 MB 那 9 个进程后几秒它回来、PID 全新） |
| ★ **`_OURS = (零件\|Part)\d+\|^MCP_` 这种按文档名的判据分不出是谁的** | ★ 别人的会话也多半开着 `零件N`；★ 而**若别人没开文档** ⇒ 判据通过 ⇒ 照样误杀 |

### 2.3 ★★ 工具/操作相关（★ 它们反复咬我）

| 陷阱 | 症状 | 正确做法 |
|---|---|---|
| ★★ **`git add -A` 放进索引的东西，后续 `git add <路径>` 撤不出来** | 只想加自己的 6 个文件，暂存区里却有别人的在途件 | ★ 先 **`git reset`**（只清索引、不动工作树），再按路径 add |
| ★★ **`git checkout -- <file>` 的源是**索引**、不是 HEAD** | 已 `git add` 过坏内容 ⇒ 恢复不掉 | ★ 用 **`git checkout HEAD -- <file>`** |
| ★★ **两个对话同仓，作者名分不开** | 最近提交作者全写 `DSH Lead` | ★ **只用显式路径 add**；★ **临时文件名带自己前缀**（本轮差点覆盖别人同名的 `_commit_msg_810.txt`，是文件系统"先读再写"策略挡住的） |
| ★★ **job 返回通道会截断** | 175 KB 的批量结果**被截在 60,159 字节丢了** | ★ **大批量产物落成文件**，返回通道只传摘要 |
| ★ **`edit` 的 `old_string` 不匹配** | 明明文件里有那行 | ★ 文件里存的可能是**字面转义文本** ⇒ **按磁盘上的真实形态匹配** |
| ★ **长内容内联进 Python 源码** | 引号被吃 / `IndentationError` | ★ **先写成独立文件**，再用最短脚本搬运（★ 事实 48） |
| ★ **脚本语法错 ⇒ 内容没落盘，而 `git commit` 照跑** | 「假提交」 | ★ 批量脚本跑完**必须回读目标文件** |
| ★ **`Path("D:")` 不是盘根** | 路径缺反斜杠 | ★ 用 `Path("D:/")`（★ 事实 59） |
| ★ **PowerShell 把单元素数组拆成标量** | 取 `$parts[0]` 得到的是**第一个字符** | ★ 用 `@()` 兜住（★ 本轮 Bunny 自己发现并记下） |
| ★ **`python -c` 里带引号/反引号的中文串** | `SyntaxError: unterminated string literal` | ★ 写文件，别写 `-c` |

---

## 三、★ 每轮的标准动作（★ 照抄即可）

```powershell
# ① 收尾链（★ 一条命令：生成器 + release_check 18 道门禁 + 聚焦测试 + ★ 关 SolidWorks）
pwsh -File D:\AI\SW\tools\round_chain.ps1 -Tests tests\<改过的>.py

# ② 真机探针（★ 一律带护栏）
python -u tools\sw_guard.py --timeout 900 -- python tools\<探针>.py

# ③ 提交（★ 一律用文件；★ 先 git reset 再按路径 add）
git reset; git add <我改过的那几个路径>; git add <消息文件>.txt
& git -c user.name='DSH Lead' -c user.email='dsh@local' commit -F '<消息文件>.txt'
```

★ **全量 pytest 只在两种情况跑**：① 发布前；② 改了 `sw_connect.py` 或门禁本体（★ ~160 s）。
★ **改了门禁之后必须**：接进 `release_check.py`（三处）+ 登记 `docs/gate-classification.json` + 写**负例测试**（★ 事实 62）。

---

## 四、★★ 团队与批量扇出（★ 本版**大改** —— 上一版这一节已过期）

```
★ `spawn_teammate` 有名额上限 **8**（实测报 `Team member limit 8 reached`），且**没有"移除成员"的工具**。
★ 要规模 ⇒ 用 **`workflow`**：写一段 JS，`parallel(thunks)` 或 `pipeline(items, 阶)` 把活扇出到任意多子代理。
   ★★ 实测已跑过 **100 路**（`parallel`），回 99 路、失败 1 路，**逐路失败名单可读**。

★★ 三条实测坑（不写会重踩）：
   ① **`agent()` 的 opts 里 `provider` 与 `model` 必须成对写。**
      只写 `model: "space-bunny-free"` ⇒ **整批静默失败**：`{requested:100, returned:0, rows:[]}`，
      **返回值里没有任何错误信息**。正解：`provider: "opencode-zen", model: "space-bunny-free"`。
   ② **并发默认只放 16 路，其余排队**（不是失败）。
      源码 `packages/workflow/workflow-ptc/src/index.ts` 逐字：
        maxConcurrentAgents: this.config.maxConcurrentAgents === 0
          ? Math.min(16, Math.max(1, availableParallelism() - 2)) : this.config.maxConcurrentAgents
      ★ **`min(16, …)` 是硬上限**（本机 28 核 ⇒ 16），且**与模型无关** —— 别把它当成"Bunny 比较慢"。
      ★ 要突破：在 `~/.dsh/profiles/web/cordis.patch.yml` 的**两个** `workflow-ptc` 块的 `config:` 下加
        `maxConcurrentAgents: <N>`（缩进 18 空格），**重启 DSH 才生效**。
   ③ **先跑 2–3 路"判据探针"再铺全量** —— 挑**极端形态**的样本（全属性族 / 全 `ISet*` 族），
      不是随机挑。★ 本轮就是漏了这步：先验了"管子通不通"，没验"水流出来干不干净"。

★ **模型必须选 Bunny**（业主明确：DeepSeek 做子代理**太贵**）。
   `role="artist"` 路由到 `space-bunny-free`；`$DSH_HOME/team-roles.yaml` 里 `worker`/`reviewer`/`researcher`
   也已指向 Bunny。★ workflow 里则显式写 `provider` + `model`。
```

---

## 五、★★★ 一条**本轮最值钱**的方法论（★ 比任何单个能力都值钱）

**把判据交出去批量执行，能得到我自己逐个读发现不了的样本量。**
本轮 100 路同时指出我给的判据有**四个洞**（详见 `docs/recon/family-scan-100-criteria-defects.md`）：
① **指针串常常不在 `## Returns` 段**（`IMacroFeatureData` 17 个全在 `## Parameters` ⇒ 报 0）；
② **废弃标记有变体**（`INote` 严格 13 vs 宽松 **31**）；
③ **「零参可读」把属性也算进去**（`IDSPBRMaterial` **52 = 52 个属性** ⇒ 该列退化成成员总数）；
④ **官方原文有笔误**（`in-porcess`）。
⇒ **四条都在 8 个以上的族里独立复现** —— 人工抽读永远发现不了。

**⇒ 两条定则**：
- ★★ **判据里"合并"是危险的**：把「方法」与「属性」合成一个"零参可读"、把「Returns 段命中」与
  「别处命中」合成一个"指针"，**列名在两族里就会含义不同 ⇒ 不能跨族比较**。能拆就拆。
- ★★ **凡"结果要能完整落盘"的批量活，产出必须落成文件** —— 返回通道只传摘要。

---

## 六、★ 剩下的活

### 6.1 线 A（工具栏）
- **可攻关 3 条**（★ 每条 `note` 里已写明卡在哪）；**待查 20 · 待验证 6**（★ 都在台账 `tier` 字段里）；
- **后端到不了 7 条**（★ 共同依据：那些 `*FeatureData` 带 `AccessSelections`，★ 而它第 2 参四种形态全到不了，★ 事实 474）⇒ ★ **别重复攻**。

### 6.2 线 B（24h 主线，★ 详见 `docs/final-report-24h.md`）
- ★ **未定案三条**：`rib` 在真机建不成（★ 连试 6 次、换 4 个变量 ⇒ **按事实 53 结题**，别再无变量地重试）·
  `ISweepFeatureData` 一族里仍有部分口径待定 · 阶段 4「补 `api-pre` 缺的两域」只开了头。
- ★ **工程图读侧**已做两批（注释族 + 折弯线/螺纹/基准/中心线四个计数），★ **`IView` 的零参可读候选还有约 200 个**。
- ★ **判据的洞要修，但别擅改已发布的数字**：修法建议是**拆列**（见 §五），不是就地改判据。

---

## 七、★★ 方法论（★ 上一版的血泪 + 本轮新增）

1. ★ **官方文档是第 0 步，不是"试不出来再去查"**（★ 顺序：官方页 → `dead-ends.md` → 该能力 `limitations` → `known-facts.md` → 动手）
2. ★ **官方材料的排序**：★ **`## Examples` > `## Remarks` > 签名**（★ 只有例子给得出**调用序**）
3. ★ **"一个探针全面失败时，先看错误信息写的是谁的名字"** —— ★ 写着自己函数名的就是我的错
4. ★ **失败几乎总是我这边**
5. ★ **两格都回同一对象时，"回了对象"不是判据** ⇒ ★ 去读**那个对象自己的成员**（★ 空壳 vs 真对象）
6. ★ **"十格全 `None` 而全不报错"是有信息量的否证**
7. ★ **排除一个候选因，就是一步进展**
8. ★ **把结论挂在被结论所指的那条记录上**（★ 台账那行的 `note`）
9. ★★ **本轮新增 · 「查不到」≠「我搜的名不对」** —— 目录名可能带 `I` 前缀（`SketchManager` vs `ISketchManager`）；
   ★ **先按词根搜目录，再说查不到**。
10. ★★ **本轮新增 · 读别人的产物前先把它打出来**（`type` + `len` + 第一项）—— ★ 本轮**同一天三次**取错字段/猜错形状，
    其中**两次直接把结论拉反**。
11. ★★ **本轮新增 · 收尾链报红时，先看红的是不是我改的东西** —— 本仓有并行对话，门禁有**竞态窗口**。
12. ★★ **本轮新增 · "我会记得"不是机制** —— 该每轮做的事（关 SolidWorks / 清理 / 计数同步）都要**接进收尾链**。

---

## 八、★ 红线（★ 任何模式都不豁免）

```
· ★ 不 git push（任何远端）· 不建目标远端仓库 · 不发 release
· ★ 不删用户数据 · 不动注册表 / 系统环境变量（★ 只改用户级 $DSH_HOME）
· ★ 破解相关零接触
· ★ `origin` 故意留空（★ 防裸 push 误推上游）；上游叫 `upstream`（★ 只登记未 fetch）
· ★ 提交一律 `git commit -F <文件>`；★ 且先 `git reset` 再按路径 add
· ★ 不手改生成物：docs/toolbar-ledger.json / -verified.json / dead-ends.md（★ 都由 tools/ 下生成器产出）
· ★ 探针/证据脚本（tools/）**只报不动**（★ 改了会破坏"证据不可变"）
· ★ 两个对话同仓 ⇒ **只写自己那一个文件**，不要顺手整理、不要批量重排
```

---

## 九、★ 一条可复制的"攻关单元"模板

```
① ★ 从台账里挑一条 tier == "可攻关"（★ 先读它的 note —— 常常已写明卡在哪）
② ★ 读官方页三样：签名 + ## Remarks + ## **Examples**（★ 例子优先）
③ ★ 若 api 是旧入口 ⇒ ★ 读 md 头顶的 Obsolete 找继任者
④ ★ 写探针（★ 带来源块：六字段 + 写明读的是哪一页/哪个例子）
⑤ ★ 真机跑（★ sw_guard.py），★ 判据 = 特征树增量 / 段数增量（★ 规则 6）
⑥ ★ 成 ⇒ 登记 capabilities.yaml（★ level: verified + evidence + limitations）；
      ★ 不成 ⇒ 记 known-facts.md（★ **含"下一步"**）
⑦ ★ 更新台账那行的 note
⑧ ★ 收尾链 + 提交
⑨ ★★ **收工关 SolidWorks**（★ `python tools/reclaim_solidworks.py --close` —— 只关自己启动的）
```
