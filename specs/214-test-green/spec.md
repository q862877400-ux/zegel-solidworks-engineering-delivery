# 规格 214 · 全仓测试归零（18 failed → 0）

> **来源（铁律 1 的四种合法来源，逐条指认）**：
> ① **用户指令**（2026-10-07）：「**按照 spec 规范自动进行，设置好目标，我给你替我拍板的授权**」✓
> ② **本仓实测读数**（同一轮）：`python -m pytest tests -q --no-header -p no:cacheprovider`
>    ⇒ ★ **18 failed / 2374 passed / 20 skipped**（8.5 min）✓ —— ★ 这是本规格的**唯一缺口地图** ✓
> ③ **本项目既有模式**：`docs/ROADMAP.md` §一 ⓪bis「**注册 ≠ 能跑**」质量线的收口读数就是
>    「**全量 pytest 0 failed**」（该线 2026-10-03 曾把 15 failed 修到 1456 passed / 0 failed）✓
> ④ **本项目既有模式**：`specs/202-user-coverage-gaps/recon/` 那套「先分诊、再动手」的工法 ✓

## 一、要解决什么（★ 先分清两类，它们的**修法完全不同**）

★ 同一轮里，我把这 18 条**逐条单独跑了一遍**（判据：`pytest <单文件>`）⇒ 分出两类：

| 类 | 条数 | 判据 | 含义 |
|---|---|---|---|
| **A1 · 稳定红** | ★ **9** | ★ **单独跑也红** | 真缺陷 / 真过期 ⇒ ★ **逐条修** |
| **A2 · 顺序污染** | ★ **9** | ★ **单独跑绿、全量红** | 测试之间在互相污染 ⇒ ★ **要从机制上消掉，不是逐条改** ✗ |

**A1 的九条（★ 每条都给了现成判据）**

| # | 测试 | 现成判据（我量到的原文） |
|---|---|---|
| A1-1 | `test_mcp_protocol_layer` | 断言写着「两条路径合计 **504** 条，而本测试上次实测 **339** 条」⇒ ★ **钉死数过期**；★ **504 是真值**（`tools/probe_mcp_stdio_handshake.py` 真 JSON-RPC + `all_specs()` 459 + `server.py` 装饰器 45）✓ |
| A1-2 | `test_effect_declarations` | 「★ 效应表过期 ⇒ 跑 `python tools/gen_effect_declarations.py`」（★ 生成物与真源分叉）|
| A1-3 | `test_sw_connect_open_document` | ★ **真 bug**：`AttributeError: 'bool' object has no attribute 'get'` @ `scripts/sw_connect.py:896` |
| A1-4 | `test_registry_wiring` | 「RESOLVERS 有这些没被用：**`['sketch']`** ⇒ 要么补上、要么删掉说明」|
| A1-5 | `test_com_member_helpers` | 「**注入与导入不一致**」 |
| A1-6 | `test_no_bare_byref_args` | 「裸 byref 传 **1** 个」 |
| A1-7 | `test_sketch_slot_params` | `CreateSketchSlot` 相关判据 |
| A1-8 | `test_real_gap_triage_contract` | `[sw_simulation-get_study_manager]` 档位与台账不符 |
| A1-9 | `test_tool_specs_batch79` | 「十七条工具」没全到 `all_specs()`（★ 实测差集里是 `solidworks_macro_*` 一族）|

**A2 的九条（受害者已知，污染源只找到一半）**

★ 受害者：`test_rule3_declarative_selection_is_enforced`（3）· `test_spec212_rule2b_gate`（1）·
`test_sw_part_sketch_selection::BBoxTests`（2）· `test_tool_specs_batch92`（2）·
`test_com_member_helpers` 的第 2 条（1）✓

★★ **已确证并已修的一条通路**（本规格立起**之前**就修掉了，作为 A2 的样板）：
`tests/test_sw_part_sketch_selection.py` 把 `sys.modules["sw_connect"]` 装成 `types.SimpleNamespace`
（★ **没有 `__name__`、没有兜底**），而真 `sw_connect` 后来加了 `deg` ⇒ ★ `scripts/sw_body_ops.py` 等
`from sw_connect import deg` 在**收集期**就炸、★ **把后面所有测试一起带坏** ✗
★ 报错逐字 `cannot import name 'deg' from '<unknown module name>'` —— ★★ 那句
**"unknown module name" 正是缺 `__name__` 的后果 ⇒ 错误信息指不到真因** ✓
★ 修法：改用 `types.ModuleType("sw_connect")` + **PEP 562 模块级 `__getattr__` 转发给真模块**
（★ 这是同仓 `tests/test_sw_selection_contract.py` 在轮 470 用过的成熟解法）✓
★ 复现装置（本文件在前、受害者在后）：★ **23 failed → 49 passed** ✓

⚠★ **但全量仍是 18** ⇒ ★★ **还有第二个污染源没找到** ✓（本规格 A2 的主要工作）

## 二、本规格做什么（三件）

### ① A1 九条逐条收口

★ 每条的**修法只允许两类**（★ 见 §四 硬约束 2）：★ 桩补齐 / 过期钉死数按**已裁定的真值**更新；
★ 其余一律**先定位真因再改实现**（★ 例 A1-3 是 `sw_connect.py` 的真 bug，★ 不许改测试绕开）✓

### ② A2：找到**第二个污染源**并从机制上消掉

★ 方法**已定**（★ 不盲试单个文件 —— 实测：单跑全绿、配对才红）：
1. ★ 按**收集顺序**取前缀 ⇒ 与已知受害者拼一次运行 ⇒ 看受害者是否变红；
2. ★★ **二分**（★ 一次全量 8.5 min ⇒ 二分约 8 次）；
3. ★ 定位到文件后，判它属于哪一类污染：★ `sys.modules` 装假模块不还原 / 装桩**缺名字** /
   `del sys.modules[...]` 造出**第二个模块身份**；
4. ★★ **修法优先选"不再手维护名字"那一类**（★ PEP 562 转发，照 A2 样板）——
   ★ 因为同一处**已经栽过三次**（轮 145 · 规格 209 · 本轮 `deg`）✓

### ③ 收口

★ 全量 **0 failed** + `release_check` 33 道全绿 + 回写 `docs/ROADMAP.md` §一 游标 ✓

## 三、本规格**不做**什么

- ★ **不碰 `specs/208-*`**（★ 另一个对话正在里面提交，见 ROADMAP §一 的并发说明）✓
- ★★ **不为过测试放宽判据**：★ 断言若要改，必须**写出依据**（★ 例 A1-1 的依据是"504 已被两条独立通路复算"）✓
- ★ **不动 14 条预选族**（★ 那要真机，★ 归另一条线：`docs/preselect-family-baseline.json`）✓
- ★ **不在跑长测试期间编辑它要读的文件**（★ 本轮自己踩过：`test_gate_details_*` 的假红就是这么来的）✓
- ★ **不装不改系统层**（铁律 2）· ★ **不碰 COM**（本规格**全离线**：★ 一条真机命令都不需要）✓

## 四、硬约束

1. ★★ **判据必须"单独跑 + 全量跑"双绿** —— ★ 这正是 A2 那一类的教训（★ 单跑绿不算绿）✓
2. ★ **改测试只允许两类**：① **桩补齐**（★ 镜像真模块，★ 优先用 PEP 562 转发，★ 不再手维护名字）；
   ② **过期钉死数**按**已裁定的真值**更新（★ 依据写进注释）。★ 其余一律改实现 ✓
3. ★ **每处改动配复算命令**；★ 能造负例的造负例（★ 事实 62）✓
4. ★ **收尾走** `pwsh tools/round_chain.ps1`；★ **提交按路径**走 `python tools/commit_mine.py`
   （★ 不许 `git add -A` —— `round_chain` 里有三处，会暂存整个脏树）✓
5. ★ **长文本先落文件再搬运**（事实 48）✓
6. ★ **本规格零真机**：`tools/sw_guard.py` 与 SolidWorks **一次都不启动** ✓

## 五、验收判据

| # | 判据 | 怎么验 |
|---|---|---|
| **C1** | ★★ **全量 pytest 0 failed** | `python -m pytest tests -q --no-header -p no:cacheprovider` ⇒ ★ 尾行 `0 failed` |
| **C2** | ★ `release_check` 33 道全绿 | `python scripts/release_check.py` ⇒ ★ 退出码 0 |
| **C3** | ★ **A1 九条逐条单跑绿** | `python -m pytest tests/test_mcp_protocol_layer.py tests/test_effect_declarations.py tests/test_registry_wiring.py tests/test_com_member_helpers.py tests/test_no_bare_byref_args.py tests/test_sketch_slot_params.py tests/test_real_gap_triage_contract.py tests/test_tool_specs_batch79.py` ⇒ **0 failed** |
| **C4** | ★★ **A2 的复现装置绿** | ★ 已知受害者 + 污染源**同一次运行** ⇒ **0 failed**（★ 单跑绿**不算** —— 见硬约束 1） |
| **C5** | ★ **零放宽** | ★ 逐条 diff：★ 断言若有改动，★ **该处必须带依据注释**；`git diff` 里**不许出现**「删断言 / 把 assert 改成 pass」 |
| **C6** | ★ **零真机** | ★ 全规格**没有**任何一次 `sw_guard.py` / SolidWorks 调用 ✓ |
| **C7** | ★ 收尾链绿 + 按路径提交 | `pwsh tools/round_chain.ps1` ⇒ 首轮 OK；★ `git status` 索引复位为 0 |
