# 40路准备——调度、兼容与证据测试规约

日期：2026-10-08。当前仅准备；不授权业务实现或真机。

## 1. 已结束的1＋1测试

| 项 | DS | HY |
|---|---|---|
| 已有自定义类型 | ds-flash-worker | hy4-conc-worker |
| 定义配置的显示名 | Deepseek-V4.1-Flash | Hy4 preview |
| 重启后成员 | restart-ds-test | restart-hy-test |
| 本次任务ID | agent-f1391bb2563d4545 | agent-619534d380364bb2 |
| 有效回报 | DSFLASH_OK: restart-ds-test 已启动 | HY4_OK: restart-hy-test 已启动 |
| 消息链路 | 通过 | 通过 |

DS回报确实来自restart-ds-test，不是重启前的preflight-ds-custom。主代理曾错误否认这条回报，现更正。用户已确认两个测试成功。

此结果只证明配置类型可启动并返回消息。不自证真实后端权重，不证明工程任务执行、文件写入、测试运行或长期稳定性。测试成员没有授权读取/修改项目或执行COM。

不再重复查模式、配置或模型身份。用户给出的单模型35路测试作为规划输入；保持40，不扩到60，不继续压测。新派任务出现异常立即停止该批调度，向用户报具体异常，不自行研究平台故障或循环重试。

## 2. 名册语义

- `source_roster`为旧职责来源；新名册不覆盖原包，不直接执行原dispatch_prompt。
- 每个槽位必须继承 `policy.slot_state_inheritance`：not_started、未指派、dispatch_allowed=false、当前业务/产物写范围空、COM禁止。
- `inputs`是候选最小读范围；实际派发前验证路径可读。不存在就记录缺项，不猜相似路径、不盲导入。
- `phase1`是未来获准后的独立源码/草案初审；当前只有名册，不代表已启动。
- `phase2_deps`是规范化槽位ID数组。原COM令牌不当作槽位，转独立权限门；旧业主界面/模型身份调查不继续执行。
- 原R/F/S保存在source_class作为出处，不是当前权限；S类本轮只设计验收，不能真机。
- HY第一阶段不等DS，独立设计反例；第二阶段缺依赖产物不称“正在复核”。
- `engineering_agent_type=null`表示尚未选用实际工程角色，不是模型路由未知。不能用启动型代理冒充业务角色。

## 3. 正式派发前判据

```text
派发就绪 = 本阶段明确授权
         AND 角色工具能力匹配
         AND 输入可读且目标文件基线一致
         AND 本阶段依赖产物齐备并已审计
         AND 独立候选写区已确认（若需要写业务代码）
```

COM额外要求真机授权、单执行责任人、跨进程互斥证据、文档/会话所有权和护栏。当前均不派COM任务。编码授权不等于COM或部署授权。

公共源码仅唯一合并执行人修改。主代理只审计；发现问题退回实施人。无独立候选区时只交补丁文本，不先改共享文件再导出diff。操作超时且可能有非幂等效应时进入uncertain，核效果前不重放。

## 4. 每路最小交付契约（仅格式提案）

```json
{
  "slot_id": "DS-03",
  "phase": "source_review",
  "baseline_head": "<派发时实际HEAD>",
  "input_sha256": {},
  "findings": [
    {
      "status": "pass|fail|unknown",
      "source_path": "<真实路径>",
      "location": "<函数或行段>",
      "claim": "<可核对结论>",
      "evidence": "<实际文本/读数来源>",
      "compatibility_impact": "<影响的旧契约>",
      "proposed_action": "<最小处理，不自行扩大任务>"
    }
  ],
  "commands_executed": [],
  "files_changed": [],
  "com_executed": false,
  "unresolved": []
}
```

占位文本只能用于格式说明；实际交付不得留未替换占位。`commands_executed=[]`表示未运行，不能把计划命令写成通过。样例失败须区别工具bug、调用契约错误、量具不可用和环境缺项。

## 5. 兼容测试分层

| 层 | 内容 | 当前状态 |
|---|---|---|
| 准备结构 | 40唯一ID、20＋20、依赖可解析且无环、全部不派发、模型无回退 | 本组文件静态检查 |
| 旧契约离线 | Param/Pydantic、注入关键字、派生覆盖拒绝、JSON/Markdown、三态 | 仅列现有测试参考，未运行 |
| 工程硬义务 | 单位边界、上下文授权、引用歧义、效果unknown、非幂等uncertain | 需正式任务及正负例；未实现 |
| 真机效果 | 关系/几何/自由度、参数扰动、保存重开、计数和量具校准 | 禁止，未测 |
| 生产交付 | 首个工程闭环与标准条款证据、发布批准 | 未到此阶段 |

不得把这些阶段共享一个“success”。API返回True、任务completed、结构自检OK都不替代实际效果与工程验收。

## 6. 已核原自检的证明边界

只读执行：

```bash
"C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe" -B "D:/AI/SW/output/make_roster.py" --check
```

已读取脚本：带 `--check` 只走check，未走默认写JSON的build路径。检查7件文件非空、槽位数/唯一ID、业务写范围空、not_started、若干字段及有限敏感串模式。退出0、`DELIVERABLE OK`。

它没有核模型分组、依赖就绪、DAG无环、read_scope与inputs匹配、dispatch_prompt安全、隔离真实性、COM权限或工程契约正确性。有限正则未命中只能叫“未命中所用模式”，不能叫完整安全审计。

## 7. 必须失败的负例（未来实施，不假装已测试）

1. DS槽位绑定Hy4或默认glm：拒绝；同理HY不能绑默认writer模型。
2. 单槽显式允许派发覆盖准备锁：拒绝，不能绕全局授权。
3. HY复核阶段上游产物不存在：blocked，不是running。
4. 未提交文件不同但HEAD相同：拒绝自动应用patch。
5. writes=None被当空元组：失败，不可宣称只读/可重试。
6. 旧草图入口与脚本边界都除1000：失败；须成员级单位证据。
7. 把预检放行直接改为旧全局失败关闭：兼容检查失败；新工程硬义务走单独分层。
8. 输出ExecutionOutcome对象替换旧str：旧客户端契约失败。
9. display指纹不可用被当无变化：证据检查失败。
10. class=S取得COM权限或自动关用户SolidWorks：权限检查失败。
11. 执行round_chain作为纯只读检查：失败，已知有暂存/资源处置副作用。
12. AddRelation返回True但几何/关系不生效：效果失败，不能提升verified。

本文件是规约，不是这些测试的执行记录。
