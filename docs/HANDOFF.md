# 交接文档 —— SolidWorks 自动化仓库（★ 给接手的**新对话**）

> ★ 本文写给**接手这个仓库的下一个新会话**。★ 目标是让接手者**不必重走我已经走过的弯路**。
> ★ 本版更新时间：**2026-10-04** · 仓库 `D:\AI\SW` · 起点提交 `df399ff` · 共 **998** 个提交。
> ★ 上一版（2026-10-03）只讲工具栏台账；本版补上 **24h 三阶段主线**与**这一轮实测出来的环境陷阱**。

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
