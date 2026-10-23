# Multi-Agent-CAD / MAC（Pan-Chera）

| 字段 | 值 |
|---|---|
| 仓库 / 主页 | https://github.com/Pan-Chera/Multi-Agent-CAD · 中文 README `README_cn.md` · 单零件/装配各有子说明（`multi_agent_cad/README.md`、`mac_assembly/README.md`） |
| 许可 | **MIT** —— 读仓库内 `LICENSE` 原文：第 1 行 `MIT License`，第 3 行 `Copyright (c) 2026 Tsinghua University · IEI Lab`；`pyproject.toml` 的 `license = { text = "MIT" }` ⇒ **可借鉴**。★另有**第二份**许可：内嵌运行时 `packages/cadpy` 是 MIT 派生件（`packages/cadpy/LICENSE:1-3` = `Copyright (c) 2026 earthtojake`，`README.md:353-356`）⇒ 引入时要同时保留两份声明 |
| 元数据 | stars **1046**、forks 99、open issues 1、主语言 Python、许可 MIT、最近推送 **2026-10-17T08:24:25Z**（来源：`gh api repos/Pan-Chera/Multi-Agent-CAD`，取数日 2026-10-23）；克隆 HEAD `git log -1` = 2026-10-17 16:24:21 +0800（`7e4cf4b`） |
| 克隆 | D:\ai3d-survey\repos\Pan-Chera__Multi-Agent-CAD |
| 证据等级 | **读码**（读 README / 子 README / WORKFLOW.md / 评测报告 / prompts / Python 源码 + `gh api` 元数据；**未**建 conda 环境、未跑 `python -m multi_agent_cad.graph`） |

## 1. 一句话定位

把「自然语言 → 可编辑 STEP」拆成**只传紧凑结构化状态的解耦多智能体流水线**：Spec Planner → Geometric Architect → 确定性代码翻译器（Aider 兜底）→ 双引擎 QA + 独立 Judge + 有界修复；并用十题 **141** 个二元特征的自评基准把「省 token」当成一等指标（`multi_agent_cad/README.md:136-147`、`docs/quantified_quality.md:26-31`）。

## 2. 技术路径（输入 → 中间表示 → 生成 → 编排 → 执行 → 验证 → 交付）

**① 输入**：自然语言设计需求，另有可选参考图目录 `user_input_images/`（`multi_agent_cad/README.md:132`）；请求写在 `multi_agent_cad/config.py:234`（`USER_REQUEST`），装配走 `MAC_ASSEMBLY_REQUEST` 环境变量（`README.md:296-305`）。模型接口是 OpenAI 兼容，可逐阶段（SPEC_PLANNER_/ARCHITECT_/CODER_/REPAIR_/AIDER_）配不同模型、温度与 token 上限（`multi_agent_cad/README.md:73`）。

**② 中间表示 = 两层紧凑 JSON（核心设计）**：`CADBrief`（Spec Planner 产出；只声明 3 类验证目标 `overall_dimension` / `single_body` / `water_tightness`，见 `multi_agent_cad/WORKFLOW.md:71`、`:625-628`）→ `ArchitectPlan`（Geometric Architect 产出；含 `sketches`/`steps`/`selector_map`/`key_dimensions`，`WORKFLOW.md:73`）。数据结构在 `multi_agent_cad/schemas.py`。★**要点不是「有 4 个 agent」，而是 agent 之间只传结构化状态、不传任何对话原文**（`WORKFLOW.md:39-41`）。

**③ 生成**：**确定性翻译器优先**——`_plan_to_code` 覆盖拉伸、旋转、孔、布尔、阵列、镜像、圆角、倒角、抽壳这些常见操作，**不额外花一次代码生成模型调用**；不支持的计划步留 `TODO_AIDER` 标记再交模型补（`multi_agent_cad/README.md:145`、`WORKFLOW.md:578-620`）。五个提示词各管一段：`multi_agent_cad/prompts/` 下的 `spec_planner.md`、`geometric_architect.md`、`python_coder.md`、`qa_judge.md`、`repair.md`。产物是 `temp_design_*.py` → 执行并导出 STEP/STL（`multi_agent_cad/README.md:102-107`）。

**④ 编排**：LangGraph 状态图，拓扑是 `planner → architect → coder → autonomous_skill_loop → END`（`multi_agent_cad/graph.py:8-10`）。★所有改 bug 的动作都发生在 `autonomous_skill_loop` **这个超级节点内部**的「Aider + 双 QA」while 循环里；LangGraph 在 coder 之后**不再**做错误路由（`graph.py:16-20`）。装配另有一张图，把失败按归属分四路（`mac_assembly/graph_assembly.py:334-360`）。

**⑤ 执行**：生成的 Python 以子进程执行，超时 `CAD_SCRIPT_TIMEOUT = 180` 秒（`multi_agent_cad/config.py:74`）。同一阶段内还有**白盒插桩**：在布尔合并**之前**测量每个特征的真实尺寸、写 `temp_measurements_{iter}.json`，且该数据**不参与 QA 判据，只传给修复代理**（`WORKFLOW.md:630`、`:738-742`）。

**⑥ 验证（双引擎 + 独立 Judge）**：
- **Engine A — `packages/cadpy` 的 STEP 拓扑分析**：测量优先级是「选择器匹配 > 白盒插桩 > STEP 拓扑」，并有统一的**特征关键词守卫**（lug/rib/cutout/boss/flange/gusset/… 共数十个词）防止把孔误当特征（`WORKFLOW.md:634-646`）。
- **Engine B — `check_mesh.py` 的 STL 网格分析**：尺寸、孔径、壁厚、结构，外加**用 Union-Find 在面邻接图上做连通性致命检查**——显著分量 ≥2（微小碎块按 < 总体积 0.1% 过滤）即 `is_fatal=True` 走 TOPOLOGY（`WORKFLOW.md:648-659`）。主引擎超时/崩溃/非零退出/JSON 解析失败四条路径都会触发 nodes.py 内部的**独立 Union-Find 兜底**（`WORKFLOW.md:661-665`）。
- **如实表达「判不了」**：引擎自身失败时合成报告用 `body_count=None`，**不再是 99 哨兵**，`single_body` 的 `measured_value` 也返回 `None`（`WORKFLOW.md:667-668`）。
- **合并路由**：RULE 0 双引擎故障→FATAL、单引擎故障→DIMENSION；RULE 1 连通性失败→TOPOLOGY；RULE 2 非水密→TOPOLOGY；RULE 3 真实尺寸失败→DIMENSION；RULE 4/5 强度<40、严重悬垂或悬臂→TOPOLOGY（`WORKFLOW.md:670-678`）。
- **独立 Judge**（`node_judge_qa`）出三决策 ACCEPT / REPAIR / HALT：ACCEPT、HALT 都不调用 Aider，只有 REPAIR 才把 Judge 的 `reason`+`evidence` 前置注入修复提示最前面；`DEFENSIVE CORRECTION:` 前缀表示这是**物理合理性修正**（例如给悬空处加安全搭接、加壁厚），要求 Aider 当作「防御性覆盖」执行——官方称这是「单 agent 时代隐式防御性修正的显式化、可审计化版本」（`WORKFLOW.md:714-721`、`docs/quantified_quality.md:140`）。

**⑦ 交付**：STEP / STL / GLB；装配额外给 URDF 交接（`README.md:10-11`、`:145-146`），产物落在 `assembly_jobs/job_<timestamp>/`，含分件几何、装配体、manifest 与 QA 记录（`README.md:307-308`）；单零件 CLI 另留 `temp_measurements_*.json`（实测特征）与 `temp_missed_*.json`（漏检诊断）（`multi_agent_cad/README.md:106-107`）。

## 3. 技术方案要点（可迁移的机制）

| 机制 | 说明 | 证据 |
|---|---|---|
| **信息压缩，而非单纯多 agent** | 4 个 agent 只互传几十~几百字段的结构化状态，不传对话历史；官方把「省 token」当成架构目标本身 | `multi_agent_cad/WORKFLOW.md:39-63` |
| **确定性翻译器优先 + `TODO_AIDER` 兜底** | 常见 CAD 操作走确定性翻译，不花代码生成调用；只有不支持的步才交模型 | `multi_agent_cad/README.md:145` |
| **双引擎互补 QA** | Engine A 精确 BRep 拓扑 + Engine B 网格连通性；两条腿互相兜底 | `WORKFLOW.md:632-668` |
| **白盒插桩与 QA 职责分离** | 插桩数据只喂修复代理、**不进 QA 判据** ⇒ 避免「自己量的数给自己判分」 | `WORKFLOW.md:630`、`:738-742` |
| **「判不了」写成 `None` 而非哨兵** | 引擎失败时 `body_count=None`，不再用 99 假装测到了 | `WORKFLOW.md:667-668` |
| **独立 Judge + 三决策** | ACCEPT/REPAIR/HALT 由 Judge 判，Aider 只执行不重新判断；判定理由前置进修复提示 | `WORKFLOW.md:705`、`:714-721` |
| **防御性修正显式化** | 物理合理性修正带 `DEFENSIVE CORRECTION:` 前缀，可审计而非隐式 | `WORKFLOW.md:717`、`docs/quantified_quality.md:140` |
| **失败按归属路由** | 装配把失败分给四类：`recompose`(分解错) / `remate`(配合错) / `remodel`(零件几何错) / `repair assembly`(脚本缺陷) | `mac_assembly/README.md:184-189` |
| **选择器缺失先探测再归属** | 路由前拿当前 STEP 探测选择器，避免把「计划幻觉」误判成「几何缺失」 | `mac_assembly/README.md:191-194` |
| **重试耗尽就显式停** | 认证/依赖/反复超时无进展/预算耗尽 → 显式 incomplete，不无限重试；零件耗尽仍留可用 STEP 则标 `degraded` 而非静默成功 | `mac_assembly/README.md:193-199` |
| **fillet 半径四档自动降级** | `_safe_fillet` 试 R → R/2 → R/4 → R/8，任一档成功即返回并记 `FILLET_DEGRADED`；全失败则输出边 bbox 诊断 | `WORKFLOW.md:752-757` |
| **语义边选择器** | `_infer_edge_filter` 生成基于 `e.length()` 的 list comprehension，避免把硬编码坐标交给 Aider | `WORKFLOW.md:33`、`:759` |
| **可复用/镜像件而不是重新生成** | `reuses_part_id` 指向源几何；`reuse_mirror_plane` 产出真正的手性镜像 STEP；`spec_fingerprint` 在源规格变化时让复用失效 | `mac_assembly/README.md:126-135` |
| **按需构建器注册表** | `builders.py` 注册表装 29 个参数化构建器，专攻易错结构（水平孔、叉耳、连杆、板、衬套、轭、桁架臂、传感器壳）；官方声明「以源码注册表为准」 | `mac_assembly/README.md:119-124` |

## 4. 运行条件与依赖

- **Python 3.11.\***（`environment.yml:8`）；`pyproject.toml` 写 `requires-python = ">=3.11"`，但 classifiers 只列 3.11/3.12。
- 装法是 **conda**：`conda env create -f environment.yml` + `conda activate multi_agent_cad`（`README.md:168-169`）。
- 关键依赖：`build123d>=0.8,<0.13`（`environment.yml`）、`langgraph>=0.2,<0.3`、`langgraph-checkpoint>=2.0,<3.0`、`pydantic>=2.5`、`openai>=1.20.0`、`anthropic>=0.30`；网格侧 `trimesh>=4.0` + `rtree>=1.1` 走 conda-forge 预编译（`environment.yml`）。
- ★**版本天花板有理由**：bundled 的 cadpy 运行时需要 OCP 7.x，而 build123d 0.13 换 OCP 8 会加载不了当前 STEP 运行时 ⇒ 必须把 build123d 夹在 `<0.13`（`README.md:182-185`）。
- ★**aider-chat 必须手动装**：`pip install --no-deps "aider-chat==0.82.3"` —— 它硬 pin `numpy==1.26.4`，与 build123d 的 `numpy>=2` 冲突，故不进 `environment.yml`，用 `--no-deps` 绕过（`README.md:174-176`、`environment.yml` 内注释）。
- 需要 key：`export DASHSCOPE_API_KEY="..."`（`README.md:171`）——该变量名是历史命名，实际承载所选 provider 的 key（`multi_agent_cad/README.md:87`）。
- **本机（Windows / 16GB 显存 / Python 3.14.7）能不能跑**：不需要 GPU（几何与网格检查都是 CPU）。Windows 官方说 conda 流程可行，但**明说 Windows 不在 CI**（`README.md:208`）；本机 Python 3.14.7 不满足 `python=3.11.*`（来源：本机 `python --version` 实测），须先建 conda 环境、且有外部 LLM key。⇒ 判断「需建 3.11 conda 环境 + 配 key 才可能跑」，**本卡未实测**。

## 5. 失败模式与已知坑

| # | 坑 | 来源 |
|---|---|---|
| 1 | ★**重试预算文档与代码不一致**：文档说 5 次（`multi_agent_cad/WORKFLOW.md:29`、`docs/quantified_quality.md:128`）、官方默认值也是 5（`multi_agent_cad/_config_defaults.py:75`），但克隆里的现行 `multi_agent_cad/config.py:49` 是 **3** ⇒ 实际行为取决于哪个文件胜出，读文档会读错 | `_config_defaults.py:75` vs `config.py:49` |
| 2 | **缓存只查文件在不在、不比对内容**：换一个模型前必须删 `pipeline_cache/cad_brief.json` 与 `architect_plan.json`，否则会复用上一个需求的规划 | `multi_agent_cad/README.md:122-128` |
| 3 | `temp_design_*.py` **故意不进 .gitignore**（Aider 修复阶段要它）；迭代号不一定是 `0`，要看最新一次而不是假定固定文件名 | `.gitignore:51-53`、`multi_agent_cad/README.md:109` |
| 4 | CLI 每轮 QA 开一个 **10 秒** checkpoint（1 自动迭代 / 2 注入新需求 / 3 停止保留）；超时按「自动迭代」处理 | `multi_agent_cad/README.md:92-94`、`config.py:78` |
| 5 | **Web UI 目前只会自动迭代**，不暴露 CLI 的 checkpoint | `multi_agent_cad/README.md:115` |
| 6 | Web UI 用**调用者账号权限**执行生成的 Python，官方明说不是沙箱、不要暴露到不可信网络；随意目录拷贝默认禁用（需 `MAC_WEB_ALLOW_DEST_PATH=1` + `MAC_WEB_DEST_ROOT`） | `README.md:238-241`、`:272-275` |
| 7 | 自定义 provider endpoint 默认关闭，须 `MAC_WEB_ALLOW_CUSTOM_ENDPOINT=1`；否则 host 必须落在 allowlist 内 | `README.md:265-271` |
| 8 | 已知唯一基准失败是 **fillet 代码冲突**（P8 第 13 项）：代码里有该特征，但 build123d 在该几何上圆角生成冲突，连续重试修不掉后放行 | `docs/quantified_quality.md:128-130` |
| 9 | 装配是**技术预览**：画廊是精选产出、**不是**测得的成功率，官方不主张优于 CAD-agent skill；用前必须自己看几何与关节 | `README.md:27-31`、`mac_assembly/README.md:15-17` |
| 10 | 基准**不可外推**：作者明说两边实现除架构外还有编排/工具上下文/修复行为/缓存口径等差异，此对照不证明架构是唯一因果变量 | `docs/quantified_quality.md:12-14` |
| 11 | 装配缺变换时按**不可核验**报告，不用世界对齐包围盒近似 | `mac_assembly/README.md:160-163` |
| 12 | 装配的视觉判定分轨：只有 Judge 真的看过渲染视图才用 `verified`/`failed`，无图像能力的 provider 安全退化为 `unverified` 且不阻塞几何上有效的产物 | `mac_assembly/README.md:176-180` |

## 6. 对我方目标的可用处（机制层面）

我方目标：让**普通模型**也能建出**能用、规范**的模型（SolidWorks 自动化）。

1. **「信息压缩而非多 agent」是这张卡最该拿走的一条**：普通模型真正的瓶颈是上下文膨胀——本仓用「只传几十~几百字段的结构化状态、绝不传对话原文」把 141 项特征跑到了 **140/141** 的通过率（`来源：docs/quantified_quality.md:26-27`，自评）。我方可照此把「需求 → 特征计划 → 调用序列 → 检查报告」各段都压成 JSON。
2. **确定性翻译器优先、模型只补不支持的步**：与我方「能静态比对就不靠模型」同向，而且留了一个显式标记（`TODO_AIDER`）来**报告**哪些步没被覆盖——这正是「查不到就说查不到」的工程化写法。
3. **白盒插桩与 QA 职责分离**：自己量的数不进自己的判分。这条可直接写成我方验证等级规则：插桩/诊断数据只能用于定位，不能作为通过依据。
4. **双引擎 + `None` 而非哨兵**：引擎崩了就如实报「判不了」，并给一个独立兜底判据。哨兵值（如 99）会把「没测到」伪装成「测到了」——这是「失败的计算不是通过」的具体实现形态。
5. **失败按归属路由**（分解错 / 配合错 / 零件几何错 / 脚本缺陷）：把失败发给真正能修它的那一层，比「整段重新生成」省一个数量级，也避免在错误的层反复打补丁。
6. **`degraded` 状态**：重试耗尽仍留可用产物时如实标 degraded 而非当干净成功——与我方「不许把 stitched 写成 verified」同构，可直接借其词汇。
7. **`packages/cadpy` 的 vendored 路线**：把上游运行时内嵌并在自己包里带一份原版权（`packages/cadpy/LICENSE:1-3`），是「借用别人内核但不整体继承其结构」的一个可参照做法。
8. **不适合照搬的**：它是 build123d/OCP + LangGraph + Aider 的 Python 栈，没有 COM、没有特征历史树、没有装配配合与工程图语义；其「装配」只是 STEP 里多实体 + URDF 交接，不构成 SolidWorks 装配的等价物。

## 7. 许可与红线

**MIT**（`LICENSE:1-3`：`MIT License` / `Copyright (c) 2026 Tsinghua University · IEI Lab`；`pyproject.toml` 的 `license = { text = "MIT" }`）。⇒ 可读、可抄、可改、可商用，**保留版权声明**。★**第二条版权线**：内嵌的 `packages/cadpy` STEP/GLB 运行时派生自 earthtojake/text-to-cad，按原 MIT 再分发（`README.md:353-356`、`packages/cadpy/LICENSE:1-3` = `Copyright (c) 2026 earthtojake`）⇒ 引入这份代码必须**同时保留两份**版权声明。仓库内未见 AGPL/GPL。红线：Web UI 以调用者权限执行生成代码、官方明说非沙箱（`README.md:238-241`）。

## 8. 证据清单

| 证据 | 出处 |
|---|---|
| 主体许可与版权 | `LICENSE:1-3`、`pyproject.toml`（`license` 字段） |
| vendored 运行时的第二份许可 | `packages/cadpy/LICENSE:1-3`、`README.md:353-356` |
| 项目定位与装配预览口径 | `README.md:13-31`、`README.md:94-105` |
| 单零件基准表与官方否认外推 | `README.md:107-132`、`multi_agent_cad/README.md:37-63` |
| 「信息压缩」架构论点 | `multi_agent_cad/WORKFLOW.md:37-64` |
| 四阶段流水线 | `multi_agent_cad/README.md:136-147` |
| 白盒插桩与职责分离 | `multi_agent_cad/WORKFLOW.md:623-630`、`:738-742` |
| 双引擎 QA 与连通性兜底 | `multi_agent_cad/WORKFLOW.md:632-678` |
| Judge 三决策与防御性修正 | `multi_agent_cad/WORKFLOW.md:701-732` |
| 有界修复路由与 degraded | `mac_assembly/README.md:165-199` |
| 复用/镜像/构建器 | `mac_assembly/README.md:110-135` |
| 装配图与反馈环 | `mac_assembly/graph_assembly.py:8-17`、`:334-360` |
| LangGraph 拓扑 | `multi_agent_cad/graph.py:1-25` |
| 提示词五件套 | `multi_agent_cad/prompts/{spec_planner,geometric_architect,python_coder,qa_judge,repair}.md` |
| 超时与重试预算 | `multi_agent_cad/config.py:49-78`、`multi_agent_cad/_config_defaults.py:75` |
| 评测方法与失败分析 | `docs/quantified_quality.md:26-31`、`:112-154` |
| 环境与依赖约束 | `environment.yml`、`pyproject.toml`、`README.md:174-185`、`README.md:208` |
| 仓库元数据 | `gh api repos/Pan-Chera/Multi-Agent-CAD`（2026-10-23 取数） |

## 9. 未确认事项

1. **未实测运行**：没建 conda 环境、没跑 `python -m multi_agent_cad.graph`、没装 `aider-chat==0.82.3` ⇒ 全卡为**读码结论**；`build123d>=0.8,<0.13` 在 Python 3.11 下的实际可装性未验证；
2. **★重试预算到底几次未确认**：`config.py:49` = 3、`_config_defaults.py:75` = 5、文档说 5，三者不一致的原因我没查（`config.py` 是可直接编辑的用户配置文件，克隆里可能已被改过）；
3. **基准数字无法复核**：141 项特征、`140/141`、`116×` token、`13×` 成本都是作者自报（`docs/quantified_quality.md`），原始判题脚本我没找到，**不可独立复核**；作者自己也否认这是因果证明（`docs/quantified_quality.md:12-14`）；
4. **装配质量未验证**：官方只给精选画廊、明确不给成功率（`mac_assembly/README.md:40-42`），我无法评其可靠度；
5. 元数据（stars 1046、推送 2026-10-17）是取数日快照——README 正文写「nearly 1,000 stars」（`README.md:19`），与当前 1046 已不一致，属正常漂移；
6. `nodes.py` 单文件 **439365** 字节，我只读了其被 WORKFLOW.md 指名的关键函数，未逐行审全文（`来源：Get-ChildItem multi_agent_cad -Recurse`）；
7. `mac_assembly/README.md` 提到的 `assembly_selector_audit.json` 我只在文档里看到，未确认其实际落盘位置与字段。