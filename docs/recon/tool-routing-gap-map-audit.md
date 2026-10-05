# 目录缺口地图复核 —— 规格 207 路由研究 §五 的更正

> ★ **一句话**：那份研究报告 §五 的「该补哪些工具」表**不能直接当待办用** ——
> 它把「**已经写好包装、只差登记**」当成「**缺能力**」，
> ★ 并且它列出的官方成员名里**有 5 个经复核不存在**
> （其中 `InsertBoundarySurface` 是**界面命令枚举**，不是 API 入口）。
> 逐条复核 14 行后：★ **属于「官方源里查不到」的只有 1 行**。
>
> ★ 本文件不含行号。★ 每个数带口径。★ **只报不动** —— 未改任何既有实现或声明。

---

## 〇 · 为什么值得复核（不是找茬）

| 理由 | 依据 |
|---|---|
| §五 是那份报告**唯一可直接行动的产出** | 报告「结论与建议」第 3 条「去补 §五 的 10 个缺口」**全靠这张表** |
| ★ 报告**自己**标了未复核 | §五 逐字「★ **未做真机复核**」· §6.5「★ **需真机复核才能当结论**」 |
| ★★ 交接文档**主动邀请**复核 | 其开篇逐字「里面的『建议/下一步』是我当时的判断，**请自行复核再采信**」 |
| ★★ 而且**同源同错**已能指认 | 报告那一栏与 `scripts/sw_surface_ref_ops.py` 的「查不到」段结论一致 —— 因为**两次搜索都只搜了 `C:\swapi\types\`** |

---

## 一 · 复核方法（三条命令可复跑）

★ 与那次搜索的**唯一差别**：按**词根**搜**三处**，而不是按**猜的成员名**搜一处。

| 源 | 路径 | 它管什么 |
|---|---|---|
| ① 成员页 | `C:\swapi\types\**` | 精确签名 · arity · mark |
| ② **官方示例** | `C:\swapi\examples\*.md` | ★ **调用序**（签名与 Remarks 都给不出 —— 本仓第 0 步的第 ③ 样） |
| ③ 枚举 | `C:\swapi\enums\*.md` | 取值 · **界面命令号** |

```powershell
# ① 这个名字到底存不存在（文件名精确匹配，不是文本匹配）
Get-ChildItem 'C:\swapi' -Recurse -File | Where-Object { $_.BaseName -eq 'InsertBoundarySurface' }

# ② 按【词根】找入口（★ 不要按猜的名字找）
Get-ChildItem 'C:\swapi\types\IFeatureManager' -File |
  Where-Object { $_.Name -match 'Boundary|NetBlend|Scale|Combine|Draft|Freeform' }

# ③ 官方示例（★ 答案常常在这里，而不是在 types\）
Get-ChildItem 'C:\swapi\examples' -File |
  Where-Object { $_.Name -match 'Boundary|Scale|Combine|Draft' }
```

★★ **本轮证明第 ② 处与第 ③ 处是关键**：
`InsertBoundaryBoss` / `InsertBoundarySurface` 在 `types\` 里**确实一个都没有**，
而**真名 `InsertNetBlend` / `InsertNetBlend2` 就在 `types\IFeatureManager\` 里**；
**官方示例把这条路的调用序写全了**。

---

## 二 · ★★ 原表引用的 5 个官方名，经复核**不存在**

口径 = 在 `C:\swapi` 全树下按**文件名精确匹配**（不是文本包含）。

| 原 §五 写的名字 | 文件命中 | 真相 |
|---|---|---|
| `CreateBossByBoundary` | **0** | 不存在 ⇒ 真名 `IFeatureManager.InsertNetBlend` / `InsertNetBlend2` |
| `InsertBoundaryBoss` | **0** | 不存在（同上）—— ★ 这条**也被写进了本仓代码注释**，见 §四 |
| `InsertBoundarySurface` | **0** | ★ 全树**只有 1 处文本命中**，且它在 `enums\swCommands_e.md`：`swCommands_InsertBoundarySurface` —— ★★ **那是界面命令号（菜单 > 曲面 > 边界曲面），不是 API 入口** |
| `InsertTrimSurface` · `TrimRefSurface` | **0 · 0** | 不存在 ⇒ 真名是**两段式** `IFeatureManager.PreTrimSurface` + `PostTrimSurface` |
| `InsertScaleFeature2` | **0** | 不存在 ⇒ 真名 `IFeatureManager.InsertScale` |

★ **对照（真名全部命中）**：
`InsertNetBlend`(1) · `InsertNetBlend2`(1) · `InsertScale`(2) · `InsertCombineFeature`(1) ·
`InsertMultiFaceDraft`(1) · `InsertFreeform`(1) · `PreTrimSurface`(2) · `PostTrimSurface`(2) · `InsertSweepSurface3`(1)。

⇒ ★★★ **这正是本仓 `docs/HANDOFF.md` 那条纪律的实例**：
**「『查不到』≠『我搜的名不对』—— 先按词根搜目录，再说查不到」。**

---

## 三 · ★★★ 结论表（原表 14 行 → 4 类）

**读法**：`A` = 已实现、只差登记 · `B` = 官方有入口、本仓未实现（可建）·
`C` = 本仓**已记「后端到不了」**（死路，别再加工具）· `D` = 官方源里查不到。

| # | 原 §五 判 | 原 §五 写的「缺什么」 | ★ 复核后的官方真名 | ★ 本仓现状（模块 / 函数） | 类 |
|---|---|---|---|---|---|
| 1 | no | 边界凸台 ① —— 无 `CreateBossByBoundary` 入口 | `IFeatureManager.InsertNetBlend` / `InsertNetBlend2` | 未实现（`NetBlend` 全仓**只在生成的签名索引里**） | **B** |
| 2 | no | 边界凸台 ② —— 同上 | 同上 | 同上 | **B** |
| 3 | no | 曲面 · 边界曲面 ① —— 曲面族齐全，唯独没有 | 同上（`IBoundaryBossFeatureData`，**37 个成员**） | 未实现 | **B** |
| 4 | no | 曲面 · 边界曲面 ② —— 同上 | ★ 官方示例 `Insert_Solid_Body_Boundary_Surface_Feature_Example_*` 建出 **`Boundary-Surface1`**，走 **`InsertNetBlend2`** | 未实现 | **B** |
| 5 | no | 特征 · 拔模 —— 只有 `sheet_metal_create_draft` 沾边 | `IFeatureManager.InsertMultiFaceDraft` + `DraftXpertChange` / `DraftXpertRemove`（官方示例 `Get_Faces_Affected_by_Draft_Feature_*`） | 未实现（只有**模具拔模分析**与**钣金拔模**） | **B** |
| 6 | no | 特征 · 缩放 —— 没有任何 Scale | `IFeatureManager.InsertScale` + `IScaleFeatureData`（官方示例调用序：`InsertScale(swScaleAboutOrigin, True, 3, 3, 3)`） | 未实现（`solidworks_sketch_scale_entities` 是**草图级**，不是特征级） | **B** |
| 7 | no | 特征 · 变形 —— 没有任何 Deform | `IFeatureManager.InsertFreeform` / `InsertFreeform2` + `SetFreeformCurveData` / `SetFreeformPointData` | 未实现 | **B** |
| 8 | no | 特征 · 组合/相交 —— 没有对已有实体做布尔组合的入口 | `IFeatureManager.InsertCombineFeature` + `ICombineBodiesFeatureData`（官方示例：两块实体各 **mark = 2**） | 未实现 | **B** |
| 9 | no | 特征 · 曲线驱动阵列 —— 只有圆形阵列与草图级线性阵列 | — | ✅ **已实现** `scripts/sw_pattern.py::configure_curve_driven_pattern`；★ `sw_pattern` 在 `mcp-server\` **0 命中** | **A** |
| 10 | no | 曲面 · 剪裁曲面 —— 缺 `InsertTrimSurface` / `TrimRefSurface` | ★ **那两个名字都不存在**；真名 `IFeatureManager.PreTrimSurface` + `PostTrimSurface` | ✅ **已实现** `scripts/sw_surface_features.py::trim_surface_report`；未登记 | **A** |
| 11 | partial | 分割线 / 投影曲线 —— 只有组合曲线 | `InsertSplitLineProject` / `InsertSplitLineSil` | ✅ **已实现且真机两条都建成**（`PLine` · 面数 +1）；未登记，卡在**声明式选择器层** | **A** |
| 12 | partial | 扫描曲面 —— 只有实体扫描 | `IFeatureManager.InsertSweepSurface` / `2` / `3` | ✅ **已实现** `scripts/sw_sweep.py::create_sweep_surface_report`（`swFmRefSurface = 62`）；未登记 | **A** |
| 13 | partial | 特征级线性阵列 —— 只有草图级 | `FeatureLinearPattern3`（10 参）/ `5` | ★★ **本仓已判定「pywin32 后端到不了建成」**（三层论证 ⇒ `docs/dead-ends.md` + 事实 369） | **C** |
| 14 | partial | 3D 草图 —— 只有读状态 | 写侧 `Insert3DSketch` / `Insert3DSketch2` | ★★ **写侧已记「本机回 `None`」**（前置不通 ⇒ 交叉曲线也因此未验成） | **C** |
| 15 | no | 特征 · 特征识别 / Instant3D —— 无 | ★ `C:\swapi` **全树 0 命中**（`Recogniz` / `FeatureWorks` / `Instant`） | 未实现 | **D** |

**口径说明**：原表正文写「判 `no` 的 10 条 + `partial` 5 条」，★ 而 `partial` 实际只列了 **4 条**
⇒ 原表 **14 行**；本表把原第 4 行的「缩放/变形」**拆成两行**（它们是两个不同的官方入口）⇒ **15 行**。

### 3.1 四类计数

| 类 | 行数 | 含义 | 判据 |
|---|---|---|---|
| **A · 已实现，只差登记** | **4** | ★ **挂柜台队列**，不是建能力 | `scripts\` 里有函数，且 `mcp-server\` 里 0 命中 |
| **B · 官方有入口，本仓未实现** | **8** | ★ **可建**，且入口已定位到逐字成员名 | `types\` 或 `examples\` 有，`scripts\` 非索引文件 0 命中 |
| **C · 本仓已记后端到不了** | **2** | ★ **死路，别再加工具** | `docs/dead-ends.md` / `capabilities.yaml` limitations 有逐字记录 |
| **D · 官方源里查不到** | **1** | 按铁律 5 写「查不到」 | 全树 0 命中 |

⇒ ★★★ **「官方没有入口」只占 1/15。**
⇒ ★★ **另 14 行的动作完全不同**：4 行是**登记**（便宜）、8 行是**建**（有官方示例给调用序）、
2 行是**别做**（已证死路）。

---

## 四 · ★ 三类错法的根因（都可复用）

| # | 错法 | 实例 | 正解 |
|---|---|---|---|
| **1** | ★★ **把「未登记」当成「缺能力」** | 曲线驱动阵列 / 剪裁曲面 / 分割线 / 扫描曲面 —— 四条**包装早就写好了**，只是没挂成工具 | ★ 本仓的账要**分开记**：**实现 / 登记 / 暴露 / 验证** 是四笔账（「挂柜台」这件事本身就是一条 initiative） |
| **2** | ★★★ **按猜的名字搜，而不是按词根搜** | `CreateBossByBoundary` / `InsertBoundaryBoss` / `InsertTrimSurface` / `InsertScaleFeature2` 全不存在；真名是 `InsertNetBlend` / `{Pre,Post}TrimSurface` / `InsertScale` | ★ 按**词根**搜，**三处**都搜（`types` + **`examples`** + `enums`） |
| **3** | ★★ **搜到了名字却不知道它是哪一类** | `InsertBoundarySurface` 命中的是 **`swCommands_e` 的界面命令号** —— ★ 名字是真的，★ **但它不是 API 入口** | ★ 命中后先**看它在哪个文件里**：`enums\` 里的多半是**命令号 / 取值**，不是可调用的成员 |

★ **第 1 条还有一个反向证据**：报告 §五 把 `sheet_metal_create_draft` 标成「沾边，
**且它自陈真机未通过**」—— ★ 那是**读了工具描述里的 limitations**（对的做法）——
★ 而它**没有对其它 9 条做同一件事**。★ **若对 15 条全做一遍，第 13、14 行（两条死路）当场就会掉出来**。

---

## 五 · ★★ 对原结论的影响

| 原结论 | 复核后 |
|---|---|
| 「去补 §五 的 **10 个缺口**」 | ★★ **要拆成三件事**：**登记 4 条**（A）· **建 8 条**（B）· **别做 2 条**（C） |
| 「曲面族齐全，**唯独**没有边界曲面」 | ★ **官方有入口**（`InsertNetBlend{,2}`），★ 且有**官方示例给全调用序** ⇒ **不是「没有」，是「我们没写」** |
| 「414 个工具里**没有任何** Scale 或 Deform」 | ★ **面这件事是对的**；★ 但**官方入口存在**（`InsertScale` / `InsertFreeform`）⇒ **「目录缺」≠「API 缺」** |
| —— | ★★ **新增一条**：**C 类 2 行不该进待办** —— 它们已在本仓 `dead-ends` / `limitations` 里被证死；★ 再加工具会**静默失败**（回 `None` 或树无增量），**重复走死路是本仓 AGENTS.md 的头号禁令** |

★ **不变的部分**（复核**没有**推翻的）：
全目录 `p_can_do >= p_doable` · 砍 W 掉点 · 任务源是病根（官方示例 `## Description` 不是用户请求） ——
这些都**不依赖 §五那张表**，★ **本条更正不动它们**。

---

## 六 · ⚠ 本次复核**仍然没有**做的事（如实列出）

| # | 没做 | 为什么 | 要补什么才算数 |
|---|---|---|---|
| 1 | ★ **真机复核** | 本轮**只读官方源与仓库**，**一次 SolidWorks 都没碰** | B 类 8 条要真机定 mark / 前置；A 类 4 条要真机跑通登记判据 |
| 2 | ★ **A 类 4 条的「卡点」是否真只差登记** | 只核到「`scripts` 有实现 + `mcp-server` 无引用」 | 分割线那条**逐字写着**卡在声明式选择器；★ 另 3 条**未逐条确认**卡在哪 |
| 3 | ★ **B 类 8 条的 pywin32 可达性** | ★ 本仓有先例：`FeatureLinearPattern*` 官方入口齐全**而本机到不了** | 每条都要走**探针 + 判据（回读/几何）**，★ **不许只看返回值** |
| 4 | ★ **D 类那 1 条是不是真没有** | ★ 只搜了 `C:\swapi`（离线两源之一） | ★ 还要查 **CHM**（`D:\AI\SW\AI Solidworks\官方文档\`）与**出厂类型库反射** —— 铁律 4 是**三源互证** |
| 5 | ★ **与另一条线的 18 条采纳候选对表** | 两份缺口清单来源不同（这份 = 145 项用户功能；那份 = 349 条四家并集） | 交叉去重，★ **避免同一件事立两次项** |

---

## 七 · 建议的下一步（三条，按性价比）

1. ★★★ **先做 A 类 4 条**（登记）—— 包装已写好、判据已写明、代价最小，
   且**立刻把 414 面抬到 418**，★ **可当场用 `tools/list` 核**。
2. ★★ **B 类 8 条按官方示例建** —— ★ **先读 `examples\`**（调用序在那里），
   ★ 每条**先探针定 mark / 前置**，再登记（本仓「攻关单元」模板第 ③ 步）。
3. ★★ **把 C 类 2 行写进 `docs/dead-ends.md` 的对照清单** ——
   ★ 防下一个人再按 §五 去补它们（**这才是这次复核省下来的东西**）。

★ 附：本条复核的**可复用产出**是一条纪律 ——
**「判『缺什么』之前，先按词根在三处官方源里搜，并分清 `enums` 里的名字是命令号不是入口」**；
★ 它的**正确落点是 `docs/known-facts.md`**（本文件只做指认，不越界改主线事实表）。
