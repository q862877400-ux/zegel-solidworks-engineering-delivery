# 规格 216 · 计划（plan）

> 宪法 §II（要查的官方源）/ §III（「应该有」附核查命令）/ §IV（许可）★ 三答复见 §三 ✓

## 一、目标与判定

★ 目标：★ 三件真机活**收口**（③ 台账订正 → ① 预选族 9 条 → ② AVI 取舍）✓
★ 判定：★ 规格 §五 的 C1–C5 全绿 ✓

## 二、技术方案

### 2.1 ③ 台账订正（★ 本轮已做）
```
① 先读该能力的 limitations（★ 第一现场 —— AGENTS.md 开篇的纪律）
② 用**台账自己的**验收命令真机复跑 ⇒ 拿实测读数
③ 只做「追加 + 标注旧条作废」，不删历史
④ 顺带发现的真缺陷（revision 键缺失）在**源头**修：
   scripts/sw_connect.py 复用 get_sw_version()；verifier 加 or ""
⑤ 真机复跑证明修复（修前 '' / 修后 '34.4.1'）
```

### 2.2 ① 预选族 9 条（★ 主要工作量）
```
① 读 docs/preselect-family-baseline.json ⇒ 取「官方前置」那 9 条（含 verdict 与理由）
② 读 mcp-server/tool_specs_batch74.py 的 _select_faces_for ⇒ 照它的形状写 pre_call
   ★ 要点：pre_call 在**注入之后**跑 ⇒ 这时选区已被 RESOLVERS[inj] 清空 ⇒ 必须**重建** ✓
③ 逐条：先真机确认「注入确实清空选区」（可复用已有真机证据 output/selection-lifetime-evidence.json）
④ 每条改完**单独**真机验证：选区计数 > 0 且特征真建成（★ 判据看**特征树**，不看返回值）
⑤ 跑 scripts/check_preselect_family.py ⇒ 未登记的新增必须为 0
```

### 2.3 ② AVI 取舍
```
① 读 scripts/sw_motion.py 的 AVI 来源块 + capabilities.yaml 的 animation_export 条目（★ 第一现场）
② 判 (a) 能否拿到 CosmosMotion 类算例：查本机 Motion 加载项与算例类型可得性
   ★ 注意台账 L3189 已经警告：ensure_motion_type_library 探的是**类型库**、
     **答不了「AVI 能不能导」** ⇒ 不许拿它的 ok 当"能导"的证据 ✗
③ 若 (a) 不成 ⇒ (b)：把**边界**（需 CosmosMotion 类算例）与三条实测事实
   （4 个 ProgID 全 None · 返回码会撒谎 · 判据必须是文件>0）写进 limitations
```

## 三、官方源 / 冲突裁决 / 许可

| 宪法条款 | 本规格的答案 |
|---|---|
| §II 要查的官方源 | ★ **部分适用** —— ★ 预选族与 AVI 都**不新增 COM 签名**（★ 用的是既有成员：`SelectByID2`/`Select4`/`SaveToAVI`/`CreateAVIParameter`）⇒ ★ 只**复核**既有来源块，不新查 ✓ |
| §II 冲突裁决顺序 | ★ 不适用（无新签名冲突）✓ |
| §III 「应该有」的核查命令 | ★ 凡「应该有」**一律换成实跑读数**（★ 例：不信台账的 `partial`，★ 真机复跑取 `pass`）✓ |
| §IV 许可 | ★ 不适用（不引入第三方代码）✓ |

## 四、与既有载体的接口

| SDD 制品 | 接到哪 | 本规格怎么做 |
|---|---|---|
| `plan.md` 的 COM 调用 | `docs/signature-audit.md` | ★ 无新增 COM 调用 ⇒ 不动 ✓ |
| `tasks.md` | `docs/ROADMAP.md` §一 | ★ 接在 ⓪-214 之后 ✓ |
| 实现完成 | `capabilities.yaml` | ★ **本规格就是改它**（★ 订正 + AVI 落档）✓ |

## 五、风险与回退

| 风险 | 处置 |
|---|---|
| ★ 真机复跑出新读数、与台账又一次不符 | ★ 以**实跑**为准（★ 这正是本轮 ③ 的做法），★ 并把旧条标作废 |
| ★ 预选族 9 条逐条真机很慢 | ★ 分批：★ 每条单跑验证 + 每批一次 `round_chain`；★ 中途不跑全量 |
| ★ 改 `scripts/sw_connect.py` 的波及面 | ★ 改动是**给 dict 加一个键**（★ 防御式 try/except）；★ 仍按纪律**跑一次全量**确认无回归 ✓ |
| ★ 与并发会话撞车 | ★ 本轮只碰 `capabilities.yaml` / `sw_connect.py` / `verify_costing_e2e.py` / `specs/216`；★ 提交按路径 ✓ |
