# 规格 216 · 目标栏（唯一进度字段）

> ★★ **本文件是唯一进度字段** —— 进度只看上面那一行。

**阶段：★ ③ 台账订正**已完成**（含顺带修掉一个真缺陷，真机证明 `solidworks_revision` 空串 → `34.4.1`）· ★ ① 预选族 9 条 / ② AVI 取舍**未开始** · ★ 当前动作 = **T-216-05**（取「官方前置」那 9 条，逐条读目标函数）**

---

## 当前状态

★ **规格 216 立起**（2026-10-07，接手轮），起因是用户订正纪律：

> 「**第 3 点我允许你开，我从没说过不准开啊，纪律是开了用完要关**」

★★ **订正我此前的误读**：★ `AGENTS.md` 规定的是**怎么开**（真机命令一律走 `tools/sw_guard.py`：
弹窗护栏 + 硬超时），★ **不是"不许开"**；★ 而"零真机"是我**自己**写进 `specs/214`/`215` 的额外约束 ✗
★ 规格已提交 ⇒ 按 Flow-forward 不改，★ 订正记在本规格 ✓
★ **本轮已按正确纪律执行**：★ 真机命令走护栏 ✓ · ★ 收尾 `round_chain` 关掉 SolidWorks ✓

### ★★ 本轮实测推翻了两条原前提（★ 都是"没先读台账就下判断"）

| 项 | ★ 原以为 | ★ 实测 |
|---|---|---|
| **③** `costing` | 台账写「`verdict: partial`（5/6），卡在 `list_templates`」 | ★ **`verdict: pass`** · `assertions` **3/3** · `templates` 步拿到真路径（每类 2 条 `.sldctc`）⇒ **旧阻塞点不复现** ✓ |
| **②** AVI | 我写「根因是缺 Motion 加载项」 | ★★ **台账 2026-10-01（轮 285）就已订正过这句**（L1611 逐字：「原写『缺 Motion 加载项』—— ★ 而实测那条**不成立**」）⇒ ★ 真结论在 **L1619**：🔴「`SaveToAVI` 需要 **`CosmosMotion` 类算例**，而本机拿不到」✓ |

★ 本机体检也与之一致：`swmotionstudy.tlb` **存在且 `ready: true`** ⇒ ★ 类型库从来不是阻塞点；
★★ 且台账 **L3189 明确警告**：`ensure_motion_type_library` 探的是**类型库**、**答不了「AVI 能不能导」** ✓

### ✅ ③ 的产出

- ★ 真机复跑（**走护栏**，15.9 s、0 弹窗）⇒ `verdict: pass` · `assertions` 3/3 ✓
- ★★ **顺带发现并修掉一个真缺陷**：`connect_solidworks` 的 `metadata` **从来没有 `revision` 键**，
  而 `tools/verify_costing_e2e.py` 读的正是它 ⇒ ★ 证据里 `solidworks_revision` **恒为空串** ✗
  ⇒ ★ 修法：复用既有 `get_sw_version()` 补键（★ 防御式：失败记 `None`、不拖垮连接）；
  ★ 并给 verifier 加 `or ""`（★ 免得把 `None` 写成字符串 `None`）✓
  ⇒ ★ **真机证明**：修前 `''` · 修后 **`'34.4.1'`** ✓
- ★ 台账订正**两处**（`costing` · `costing_readback`）：★ **一律"追加 + 标注旧条作废"，不删历史** ✓
  ★ `check_union_conventions` ⇒ 退出 **0** ✓
- ⚠ 证据文件结构已变（顶层 6 键、`steps` 7 项），★ 台账旧记的 5 键已作废 ⇒ ★ 也已订正 ✓

---

## 下一个动作（只写一条）

★ **T-216-05**：★ 读 `docs/preselect-family-baseline.json`，★ 取「**官方前置**」那 **9** 条，
★ 逐条**读目标函数体**确认「它确实需要预选、且当前没有入口能选」，
★ 再照 `mcp-server/tool_specs_batch74.py` 的 `_select_faces_for` 形状写 `pre_call` ✓
→ 验收: ★ 9 条清单 + 每条的目标函数落 `specs/216-real-machine-closeout/recon/precall-plan.md`；
★ 然后 `python scripts/check_preselect_family.py` 在改完后须退出 0 ✓
