# 工程能力系统——交接接收与40路准备审计

日期：2026-10-08。审计状态：`PREPARATION_DELIVERED / BUILD_NOT_AUTHORIZED`。

## 1. 结论

**双模型启动测试通过；旧工作已接续；40路准备包已经形成。业务尚未开工，工程验收尚未通过。**

采用20个 `Deepseek-V4.1-Flash` 槽位、20个 `Hy4 preview` 槽位。不增加到60，不拿旧DSH默认模型替代，不再研究受限模式、配额或模型身份。主代理继续只审计监督，不写业务代码。

原7件交接保留不改。旧Agent的源码事实、未解决问题、来源索引可用；其6路上限、默认glm/gemini、忽略目录即隔离、class=S隐含COM授权和用完关闭SolidWorks等决定不采用。

## 2. 两个启动测试的真实记录

| 配置类型 | 重启后成员 | 本次可见消息 | 判定 |
|---|---|---|---|
| ds-flash-worker | restart-ds-test | DSFLASH_OK: restart-ds-test 已启动 | 启动/消息通过 |
| hy4-conc-worker | restart-hy-test | HY4_OK: restart-hy-test 已启动 | 启动/消息通过 |

主代理曾在HY回报后说“DeepSeek尚未回报”，这是记录错误：restart-ds-test已先回报，不是重启前的旧消息。现已更正，用户也确认两个成功。

这不认证服务端实际权重、不证明业务写入/桩测试/长期稳定。用户提供单模型35路测试作为规划输入，本轮不再重测并发。重启前那次HY曾发回消息后又有空流失败通知，不能拿它当本次稳定性结论；不再调查该平台问题。

## 3. 接收与只读核验

### 3.1 原7件交接

已接收：入口、决策、交接说明、现有契约JSON、槽位草案、槽位JSON及生成/自检脚本。

实际JSON解析得到19条契约、10条旧宿主路由、40唯一槽位，DS20/HY20。原479个all_specs是原Agent反射报告，本次没有导入执行，不视作完整MCP总数。

读取 `make_roster.py` 后，仅执行 `--check` 分支，退出0：

```text
槽位 40（A=22 B=12 C=6；今天并行上限=6；COM 串行=1）
文件齐全 7/7 · 无密钥样式串 · 业务写范围全空 · 全部未启动
DELIVERABLE OK
```

上面“6路”是旧JSON字段，不是本次采用的上限；“无密钥样式串”只说明所用有限正则没有命中，不能叫完整安全审计。检查通过也不证明原dispatch_prompt可安全派发。

### 3.2 当前代码基线

本次实际HEAD：`d072d0c79985f87e9d1f6278241b18fc1f26d713`，分支master。

仅核六个关键路径状态：`scripts/sw_part.py`已修改，`scripts/sw_sketch_relations.py`未跟踪；其余查询路径无状态输出。未进行全仓权属普查，旧交接“264条”不作为当前计数。

六个关键文件SHA-256及原名册哈希已记录到新名册，并在文档制作后重新比对一致。保留旧改动，不提交、不覆盖、不把他人工作认领为本轮。

`.specify/feature.json`本次仍指 `specs/003-topology-closed-loop`。207重号/221缺目录是旧交接提供的历史问题，本次不重复遍历全仓，也不擅自改编号。

### 3.3 直接核查的契约

- `tool_registry.py:576-631`：默认JSON；预检异常/unchecked/关闭开关放行，NotApplicable才返回拒绝载荷。
- `tool_registry.py:660-699`：注入→预检→pre_call→derived_args→目标函数→run_locked；派生参数冲突拒绝；旧返回字符串。
- `tool_registry.py:754-812`：写域显式→实证→静态→未知，read_only显式优先，三态注解。
- `tool_registry.py:835-867`：声明全套校验后再注册，不注册半套。
- `register_capabilities.py`解析器：实际不只model/sw_app/study，对象语义与关键字都需对齐。
- `sw_fingerprint.py:29-55`：九类廉价状态及display不可用桶，不是完整模型revision。
- `round_chain.ps1`：当前确有git add -A与reclaim --close，因此不是纯只读自测入口；未执行。

官方API成员尚未重新探测。本轮没有为AddRelation试参数，也没有裸跑COM。

## 4. 原包的具体错误及接续办法

| 问题 | 接续决定 |
|---|---|
| 旧DSH配置找不到模型被写成模型不存在 | WorkBuddy已有配置类型且双回报成功，不再索要provider ID |
| 原model_ref按职责落到glm/gemini | 新名册按DS/HY侧绑定两种用户指定模型 |
| 人为6路上限 | 保持40目标，不扩大60、不保证每时刻40个均运行 |
| A级被直接allowed_now，忽略11个带依赖槽位 | 初审独立读源码，第二阶段按DAG等实际产物 |
| 原草案11/9/20与实际22/12/6统计矛盾 | 以解析数据22/12/6作原分类；分类不是授权 |
| output被忽略即“零风险” | 不成立；正式编码要独立候选区＋唯一合并人 |
| 裸HEAD工作区当接续基线 | 会漏掉未提交修复；受控HEAD加明确归属覆盖层 |
| COM文件存在性当互斥证明 | 不采用；当前禁止，未来串行执行并验证互斥 |
| S类提示词默认COM/自动关SW | 不采用；真机另授权，资源所有权不明拒关闭 |
| 所有人跑round_chain | 不采用；副作用拆分由唯一责任人提案并审计 |
| fixed=False等于装配合格 | 不成立；具体任务核配合、自由度、干涉、运动及持久性 |
| 旧预检直接改成失败关闭 | 不采用无版本全局改变；工程入口分层硬义务 |

## 5. 新40槽位准备包与检查结果

新名册复用原40职责，并调整为：DS初审事实/最小提案，HY先独立读对应源码设计反例，再对DS实际产物复核。原HY-15/16模型配置调查改为工程依赖就绪/证据分层，不继续平台研究。

每槽包含最小输入、独立初审职责、规范化第二阶段依赖、EC00桥接和唯一合并角色。权限由全局slot_state_inheritance继承：全部not_started、未指派、不允许派发、当前业务/产物写范围空、COM禁止。

本次静态校验退出0：

```text
PREPARATION STRUCTURE OK:
40 unique slots; DS20/HY20; dependency DAG valid;
no dispatch/write/COM authorization; intended model groups;
six baseline files and source roster unchanged
```

证据范围：JSON结构、唯一ID、20＋20、依赖存在/无环、准备锁、模型分组、必需职责字段、关键源文件未改变。未验证所有候选输入文件可读、工程角色实际工具、候选区OS权限、COM互斥或工程正负例。

40个准备/审计职责不是40个已获批可直接编码包。正式业务任务仍按Spec Kit来源→计划→任务→可执行验收落到真实文件，不为人数强拆共享文件。

## 6. 开工前仍要完成什么

1. **EC00正式化**：逐FR来源/许可/官方依据，逐任务 `→ 验收:` 可运行命令，FR→任务→验收证据对齐。现有32项仍未执行。
2. **兼容决定**：旧标量/字符串/预检保持，新工程硬义务、unknown与uncertain分层；不能由40人各选解释。
3. **拟改路径权属**：只核拟改文件原差异；未知冻结，不要求用户逐项处理全仓无关改动。
4. **实施角色与基线候选区**：工程角色能力匹配、受控dirty基线、独立候选写区、唯一合并执行人。启动型代理不当业务coder。
5. **明确开工授权**：当前仍仅准备。编码、COM、部署分别确定权限，不隐含授权。

不再把模型provider ID、6路限制或重复烟雾测试当阻塞。下一批应服务EC00规格与验收，不回到无止境的工具普查。

## 7. 交付与修改范围

- 更新 `output/ENGINEERING_PARALLEL_PREFLIGHT.md`：本轮事实、兼容C01～C16、纠错、受控基线/隔离及开工门。
- 新建 `output/ENGINEERING_PARALLEL_ROSTER.json`：40槽位准备数据，非直接执行脚本。
- 新建 `output/ENGINEERING_PARALLEL_TEST_PROTOCOL.md`：双回报记录、名册语义、正负例及证据边界。
- 新建本报告：`output/ENGINEERING_PARALLEL_READINESS_AUDIT.md`。

原7件交接、业务源码、测试、正式Spec、宿主配置均未修改。未运行工程测试、COM/CAE、整条收尾链、暂存/提交或部署。准备产物交付完成不等于产品工程验收通过。
