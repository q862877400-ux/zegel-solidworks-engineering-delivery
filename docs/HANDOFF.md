# 交接文档 —— SolidWorks 工具栏「不能项」攻关（★ 给接手的**新对话**）

> ★ 本文写给**接手这个仓库的下一个新会话**。★ 目标是让接手者**不必重走我已经走过的弯路**。
> ★ 生成时间：2026-10-03 · 仓库 `D:\AI\SW` · 起点提交 `df399ff` · 共 **776** 个提交。

---

## 〇、一句话现状

> ★ 在攻 **SolidWorks 工具栏里当前「不能」的功能**（特征 / 草图 / 草图尺寸与关系 / 曲面 四个工具条，约 75 项）。
> ★ **进度：台账 119 条 ⇒ 已能 82 · 可攻关 4 · 待查 20 · 待验证 6 · 后端到不了 7**。
> ★ 手法固定为：**查官方三源 → 按六条铁律立柱 → 实现包装 → 真机实测 → 加静态门禁**。

| 指标 | 当前值 |
|---|---|
| 提交数 | **776** |
| `capabilities.yaml` | **109** 条（`verified` **96** · `stitched` **12** · `not_implemented` **1**） |
| `docs/known-facts.md` | **481** 行（★ 编号已到 **483**，中间有跳号） |
| `docs/toolbar-ledger.json` | **119** 条 |
| release 门禁 | **24** 道（★ 分类表 `docs/gate-classification.json` **29** 条） |
| 真机证据 | `output/` 下 **361** 个 `.json` |

---

## 一、★ 先读这五份（顺序别换）

```
① D:\AI\SW\AGENTS.md                        ← ★ 常驻纪律（六条铁律 / 验收标准 / 红线）
② docs/known-facts.md                       ← ★ 事实表（481 条；★ 遇事先查它，别重走）
③ docs/dead-ends.md                         ← ★ 走死的路（由 gen_dead_ends.py 生成，别手改）
④ docs/toolbar-ledger-verified.json         ← ★ 台账（★ 每条带 tier + note，★ note 里常写着"下一步"）
⑤ docs/toolbar-gaps-backend-limits.md       ← ★ 后端到不了的**依据**集中在这（§二/§2.2.1/§2.3/§三）
```

★ 另有 **`~/.dsh/AGENTS.md`**（用户全局层，每轮自动注入）与 **`~/.dsh/纪律/`**（纪律正文）。

---

## 二、★★★ 环境陷阱（★ 这一节最值钱 —— 都是**实测踩出来的**）

### 2.1 ★ SolidWorks 相关（★ 违反会浪费好几轮）

| 陷阱 | 事实编号 | 正确做法 |
|---|---|---|
| **实体（边/面）按坐标选**（`SelectByID2("","EDGE",x,y,z,…)`）**选不中** | 32 / 482 / 483 | ★ 用 **`IEntity.Select4`（按对象选）**；本仓封装：`sw_selection_spec.entities_on_body` + `select_object` |
| ★ **`Select4` 没有 `mark` 参数** | — | ★ 选完用 **`ISelectionMgr.SetSelectedObjectMark(i, mark, -1)`** 补设 |
| ★ **发射线前不 `ClearSelection2(True)` 会留残留对象** | 479 | ★ 发射线前**先清选区** |
| ★ **官方 `## Examples` 段给的是"调用序"** —— 签名与 Remarks 都给不出 | 480 / 482 | ★ **读例子**（★ 例子里常有"两遍选边""收尾 `InsertSketch`"这种关键步骤） |
| ★ **台账/文档里 `api` 名可能是已废弃的旧入口** | 433 / 476 | ★ **读那个 md 头顶那句 `Obsolete`** —— 继任者名字就在那句里 |
| ★ 能力层**回 `False` / `None` 不等于失败** | 482 | ★ 例：`SketchOffsetOnSurface` 回 `False` 是**正常的**（★ 还要 `InsertSketch` 收尾） |
| ★ **跑真机一律走护栏** | — | ★ `python tools/sw_guard.py --timeout N -- python <脚本>`（★ 绝不要裸跑） |

### 2.2 ★ 工具/操作相关（★ 它们反复咬我）

| 陷阱 | 症状 | 正确做法 |
|---|---|---|
| ★ **`edit` 的 `old_string` 不匹配** | 明明文件里有那行 | ★ 文件里存的可能是**字面转义文本**（`return "\u5f85\u67e5"` 而不是 `return "待查"`）⇒ ★ **按磁盘上的真实形态匹配** |
| ★ **heredoc 反复被 mangle** | `IndentationError: unexpected indent` / 引号被吃 | ★ **长内容先写成独立文件**（`write` 工具），再用最短脚本搬运（★ 事实 48 定则①） |
| ★ **脚本语法错 ⇒ 内容没落盘，而 `git commit` 照跑** | 「假提交」 | ★ 批量脚本跑完**必须回读目标文件**（★ 不能只看 stdout） |
| ★ **`python tools\gen_level_audit.py` 路径错** | 门禁报"与最新数据不一致"却不知怎么办 | ★ 它在 **`scripts/`** 下：`python scripts/gen_level_audit.py` |
| ★ **`Path("D:")` 不是盘根** | 路径缺反斜杠 | ★ 用 `Path("D:/")`（★ 事实 59） |

---

## 三、★ 每轮的标准动作（★ 照抄即可）

```powershell
# ① 收尾链（★ 一条命令搞定：生成器 + release_check + 聚焦测试）
pwsh -File D:\AI\SW\tools\round_chain.ps1 -Tests tests\<改过的>.py

# ② 真机探针（★ 一律带护栏）
python -u tools\sw_guard.py --timeout 900 -- python tools\<探针>.py

# ③ 提交（★ 一律用文件，不要 -m）
& git -c user.name='DSH Lead' -c user.email='dsh@local' commit -F '<消息文件>.txt'
```

★ **全量 pytest 只在两种情况跑**：① 发布前；② 改了 `sw_connect.py` 或门禁本体（★ 它要 ~160 s）。

★ **改了门禁之后必须**：
1. ★ 接进 `release_check.py` —— **三处**：`_run_xxx_gate` 函数 + 调用 + **进返回体**
2. ★ 登记 `docs/gate-classification.json`（★ 否则 `check_gate_wiring.py` 会拦）
3. ★ 写**负例测试**（★ 事实 62：★ 门禁"写了"不等于"有效"）

---

## 四、★ 当前剩下的活

### 4.1 「可攻关」4 条（★ 而**每条都已带 `note` 写明卡在哪**）

| 工具栏项 | api | note 里写的下一步 |
|---|---|---|
| 曲线-分割线 | `InsertSplitLineProject` | ★ 官方 `## Remarks` **已给 mark = 4（草图）/ 1（面）**；★ 例子 `Create_Projection_Split_Line_Example_VB.md` **未读** |
| 对称线性直径尺寸 | `AddSymmetricDimension` | ★ 前置链已按官方例子备齐 ⇒ ★ **返回的 `CDispatch` 七成员全 `AttributeError`**（★ 空壳，事实 463） |
| 侧影实体 | `SketchUseEdge3` | ★ **事实 483**：★ 按对象选面后仍回 `False`、段数 0→0 ⇒ ★ **下一步造一个"面带内环"的板**（`InnerLoops=True` 要内环） |
| 自由样式 | `InsertFreeform2` | ★ **已结论**（事实 481）：★ 十格矩阵全 `None` 而不报错 ⇒ ★ **这条后端上不产出特征** |

### 4.2 「后端到不了」7 条（★ 依据都已写明、**别重复攻**）

```
线性阵列 · 曲线驱动的阵列 · 表格驱动的阵列 · 填充阵列 · 草图驱动的阵列
扫描曲面 · 曲线-投影曲线
★ 共同依据：那些 `*FeatureData` **带 `AccessSelections`**（★ 指针族）
★ 而 `AccessSelections` 的**第 2 参四种形态全到不了**（★ 事实 474，★ 有真机错误码）
★ 依据集中处：docs/toolbar-gaps-backend-limits.md · docs/backend-limited-items.json（12 条）
```

### 4.3 「待查」20 · 「待验证」6

★ 都在台账里（`tier` 字段）。★ **待验证**的意思是「**有真入口、但还没真机试过**」。

---

## 五、★★ 方法论（★ 本会话血泪换来的）

1. ★ **官方文档是第 0 步，不是"试不出来再去查"**（★ 顺序：官方页 → `dead-ends.md` → 该能力 `limitations` → `known-facts.md` → 动手）
2. ★ **官方材料的排序**：★ **`## Examples` > `## Remarks` > 签名**（★ 只有例子给得出**调用序**）
3. ★ **"一个探针全面失败时，先看错误信息写的是谁的名字"** —— ★ 写着自己函数名的就是我的错
4. ★ **失败几乎总是我这边**（★ 本会话至少 **11 次**：420 · 431 · 440 · 441 · 447 · 452 · 456 · 460 · 462 · 470 · 472 · 483）
5. ★ **两格都回同一对象时，"回了对象"不是判据** ⇒ ★ 去读**那个对象自己的成员**（★ 空壳 vs 真对象）
6. ★ **"十格全 `None` 而全不报错"是有信息量的否证** —— ★ 它把结论从「参数可能不对」推进到「**这条路不产出**」
7. ★ **给门禁加一条"提示"，等于给自己加一个"待办生成器"**
8. ★ **排除一个候选因，就是一步进展** —— ★ 而不只有"建成"才算进展
9. ★ **把结论挂在被结论所指的那条记录上**（★ 台账那行的 `note`）—— ★ 因为下一个人先看台账

---

## 六、★ 红线（★ 任何模式都不豁免）

```
· ★ 不 git push（任何远端）· 不建目标远端仓库 · 不发 release
· ★ 不删用户数据 · 不动注册表 / 系统环境变量
· ★ 破解相关零接触
· ★ `origin` 故意留空（★ 防裸 push 误推上游）；上游叫 `upstream`（★ 只登记未 fetch）
· ★ 提交一律 `git commit -F <文件>`
· ★ 不手改生成物：docs/toolbar-ledger.json / -verified.json / -verified.json / dead-ends.md
   （★ 都由 tools/ 下生成器产出）
```

---

## 七、★ 团队（Agent Teams）现状 —— ★ **接手前先知道**

```
★ 名额上限 **8**，★ 而当前被占满：
   · 6 个 `failed`（★ 病因写在诊断里：`tools.restrict() names unknown global tool "bash"`）
   · 2 个 `inactive`（dom12 / simscan）
★ 而**没有"移除成员"的工具**（★ `interrupt_agent` 只中断、不移除）
⇒ ★ `spawn_teammate` **当前会报 `Team member limit 8 reached`** ⚠

★ 而 `verify_rollout` 也不可用：`no adapter registered for provider "stepfun"` ⚠

★ **可用的替代**：**`subagent`**（★ 普通子智能体、**不占团队成员名额**）✓
   ★ 而实测（★ 事实 483）：★ 派**纯静态的"读官方页 → 出调用序清单"**这类活
     ⇒ ★ **零编造、还能答出台账上挂着的待办** ⇒ ★ **净收益为正** ✓
   ★★ 而**核的方式必须是"拿官方原文逐条比"**（★ 不是"读一遍觉得对"）
```

---

## 八、★ 一条可复制的"攻关单元"模板

```
① ★ 从台账里挑一条 `tier == "可攻关"`（★ 先读它的 `note` —— 常常已写明卡在哪）
② ★ 读官方页三样：签名 + `## Remarks` + **`## Examples`**（★ 例子优先）
③ ★ 若 `api` 是旧入口 ⇒ ★ 读 md 头顶的 `Obsolete` 找继任者
④ ★ 写探针（★ 带来源块：六字段 + 写明读的是哪一页/哪个例子）
⑤ ★ 真机跑（★ `sw_guard.py`），★ **判据 = 特征树增量 / 段数增量**（★ 规则 6）
⑥ ★ 成 ⇒ 登记 `capabilities.yaml`（★ `level: verified` + `evidence` + `limitations`）；
      ★ 不成 ⇒ 记 `known-facts.md`（★ **含"下一步"**）
⑦ ★ 更新台账那行的 `note`（★ 把它从"待重查"改成结论）
⑧ ★ 收尾链 + 提交
```
