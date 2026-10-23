# cadquery-llm-skill

<!-- survey: class=I; repr=code; orchestration=none; verify=none; deliver=none; evidence=读码 -->

| 字段 | 值 |
|---|---|
| 仓库 / 主页 | https://github.com/jmwright/cadquery-llm-skill （无独立主页——API 里 `"homepage": null`；来源：https://api.github.com/repos/jmwright/cadquery-llm-skill ） |
| 许可 | Apache-2.0（读克隆内 `LICENSE` 原文首行「Apache License / Version 2.0, January 2004」；仓库内**无** NOTICE 文件）→ **可借鉴**（保留版权声明；另见 §7 关于 `docs/` 快照的许可） |
| 元数据 | stars 11 · 最近推送 2026-05-19T13:04:26Z · 语言 Python（来源：https://api.github.com/repos/jmwright/cadquery-llm-skill ，取数日 2026-10-23） |
| 克隆 | D:\ai3d-survey\repos\jmwright__cadquery-llm-skill （HEAD `270c94be`，末次提交 2026-05-19T09:04:23-04:00，工作树干净） |
| 证据等级 | 读码 |

## 1. 一句话定位

**纯提示词/知识资产仓库**（不含执行器、不含服务）：一份给 LLM 读的 CadQuery 技能包，用"决策 + 反模式"改写模型的默认反射——它要治的病写得很直白：LLM 老把 CadQuery 当 CSG 用、乱用选择器、在全局坐标里建模、能用工作平面特征却去 `.union()`/`.cut()`（`README.md:1-8`）。

## 2. 技术路径（输入 → 中间表示 → 生成 → 编排 → 执行 → 验证 → 交付）

1. **输入**：任意 CadQuery 题面/提示。仓库通过四条注入路径把技能塞进上下文：一次性 `@` 引用、项目 `CLAUDE.md`、全局 `~/.claude/CLAUDE.md`、Ollama `Modelfile`（`README.md:30-95`）。
2. **中间表示**：**不是几何 IR，是决策与心智模型**——先判用 fluent（Workplane）还是 Free Function API（两套不许混用），再把 CSG 反射换成 BRep 反射（`SKILL.md:8-35`、`SKILL.md:39-58`）。
3. **生成**：用具体规则把 LLM 的输出收窄：选择器语法表、tag 优于索引选择器、`centerOption` 必须显式、wire 必须先 `.close()`、tag 上下文后要 `.end()`（`SKILL.md:96-128`、`SKILL.md:132-168`）。
4. **编排**：三层阅读顺序（速查 `SKILL.md` → `concepts/`+`patterns/` → `examples/`+`docs/`），并给出可执行的检索动作——`grep -rn "\.shell\(" examples/`、`grep -n "def loft" docs/free-func.rst`（`SKILL.md:247-264`、`README.md:97-114`）。
5. **执行**：**本仓不含执行器**；代码在宿主的 Python 里跑，仓库只提供知识（`README.md:10-18` 的清单里没有 runner）。
6. **验证**：唯一机制是人工纪律——"每个片段提交前都要跑过"、"不许加未验证但看着对的模式"（`CONTRIBUTING.md:16-26`）；仓库内无 CI（实测克隆顶层无 `.github/`）、无测试目录。
7. **交付**：两份 prompt 产物——手工优化的 `Modelfile`（Ollama 预载 SYSTEM）与一个从 Markdown 生成"全量内容版 Modelfile"的生成器（`Modelfile:1-7`、`scripts/build_ollama_modelfile.py:15-41`）。

## 3. 技术方案要点（可迁移的机制）

- **反模式优先、先错后对**：新增反模式的规定格式是"先写错误版本、再写正确版本、再解释为什么错"，并明确"**静默错的几何比报错更值得标**"（`CONTRIBUTING.md:61-67`）。
- **明文写下模型能力门槛**：README 直接声明"开放模型至少要 14b 参数才跟得住 BRep 约束，更小的模型不管系统提示怎么写都会退回 CSG/布尔"，默认基座是 `qwen2.5-coder:14b`（`README.md:87-91`、`Modelfile:1`）。这是"提示词能修到什么程度"的现实边界声明，而不是营销话术。
- **两份 prompt 产物、分工明确**：`Modelfile` 是手工优化版、刻意不从 Markdown 生成；需要"全量内容版"就用生成器另造一份（`README.md:93-95`、`CONTRIBUTING.md:95-105`）。签入的 `Modelfile` 第 1 行直接是 `FROM`，没有生成器 HEADER，与"手工"说法一致（`Modelfile:1`、`scripts/build_ollama_modelfile.py:8-13`）。
- **生成器自带失效提示**：拼出的 SYSTEM 文本里若含三引号，就往 stderr 打警告——那会破坏 Modelfile 的 `SYSTEM """` 块（`scripts/build_ollama_modelfile.py:51-55`）。
- **离线文档快照 + 先 grep 再写**：`docs/` 是 CadQuery 官方 RST 的本地快照，用法是"不确定签名就去 grep"，把"猜 API"换成"查 API"（`README.md:97-114`、`SKILL.md:260-264`）。
- **分层上下文预算**：速查常驻、细节按需——`SKILL.md` 是 dense quick-reference，深内容拆进 `concepts/`，避免一次灌满上下文（`README.md:10-18`）。
- **把"几何语义"写成表而不是散文**：反模式里用"别用 X 用 Y"的对照表（`.cut(cylinder)` → `.faces(...).hole(d)`、`.cut(shell_solid)` → `.shell(thickness)`），比讲原理更容易改变模型行为（`SKILL.md:135-141`、`Modelfile:80-88`）。
- **性能取向的写法也被教**：优先用 `addHole()`/`replace()` 这类"不靠布尔加特征"的写法（`SKILL.md:219-227`）。
- **稳定性优先于可达性**：tag 选择优于索引选择器，理由写明"加个圆角就会改变实体数量、索引会漂"（`SKILL.md:114-128`、`SKILL.md:152-153`）。
- **自由函数 API 的运算符语义被单独交代**：`+` 并、`-` 差、`*` 交、`/` 分割；放置用 `moved`（返回新对象）与 `move`（就地）区分，`moved` 传多个位置返回 compound（`SKILL.md:205-219`）。
- **对内核报错给成因清单而非一句"参数不对"**：`BREP_API command not done` 列了四种成因（相邻圆角半径过大/重叠、自交剖面、扫掠剖面超路径曲率、抽壳超局部曲率），并指到展开版 `patterns/anti-patterns.md` 第 14 节（`SKILL.md:161-168`、`patterns/anti-patterns.md:297`）。
- **定位是"教怎么想"而不是给成品模板**：规定示例 5–10 行、一个概念一个片段，避免模型照抄整件（`CONTRIBUTING.md:29-31`）。

## 4. 运行条件与依赖

- 本仓**自身无任何运行时依赖**：只有 Markdown、4 个概念文件（`concepts/brep-mindset.md`、`concepts/workplanes.md`、`concepts/selectors.md`、`concepts/free-function-api.md`）、2 个示例脚本（`examples/brep_thinking.py`、`examples/fillet_and_chamfer_challenges.py`）和 1 个生成脚本；无 `pyproject.toml`/`package.json`、无测试、无 CI（实测克隆顶层无 `.github/`）。
- 要跑示例才需要外部条件：装 CadQuery；`examples/fillet_and_chamfer_challenges.py` 演示半径刚好接触时抛 `BRep_API: command not done`（`Modelfile:155-191`）。
- 要跑 Modelfile 需要 Ollama，基座 `qwen2.5-coder:14b`、`temperature 0.2`（`Modelfile:1-3`）。
- 本机判断（Windows + 默认 Python 3.14.7；实测 `cadquery` 未安装）：**技能文本任何机器都能用**（纯文件读取，与解释器无关）；要跑示例得先装 CadQuery；按题面本机 16GB 显存足以承载 14b 级本地模型，但本次**未跑、未实测**（来源：本任务题面）。
- GPU：技能本身不需要；只有本地跑 Modelfile 才用到显存（`README.md:87-91`）。

## 5. 失败模式与已知坑

- **没有机器兜底**：验证全靠贡献者自觉手跑（`CONTRIBUTING.md:16-26`），克隆内无 CI（实测无 `.github/`）——"示例都验证过"是人为承诺，不是可复算的事实。
- **承诺的元数据没落地**：`CONTRIBUTING.md:86-93` 要求把 CadQuery 版本写进 `docs/VERSION`，但克隆内**不存在**该文件（实测 `docs/` 下无 `VERSION*`）⇒ 快照对应哪个 CadQuery 版本**查不到**。
- 文档快照只带一句说明"应由 sphinxdoc 生成"，没有版本与生成时间，新鲜度无法判断（`docs/README:1-2`）。
- **开放模型边界**：作者声明小于 14b 的模型会退回 CSG，提示词救不回来（`README.md:87-91`）；CPU 上响应可能要好几分钟（`README.md:90-91`）。
- **时效性**：内容写死了 CadQuery 的 selector/workplane 语义，CadQuery 一改语义就要人工复审（`CONTRIBUTING.md:86-93`）。
- **两份产物会漂移**：`Modelfile` 与 Markdown 刻意独立（`CONTRIBUTING.md:95-105`）⇒ 同一知识有两份真源，靠人同步。
- **覆盖面窄**：可直接跑的示例只有 `examples/brep_thinking.py` 与 `examples/fillet_and_chamfer_challenges.py` 两个；概念文件 4 个，最深的一份是 `concepts/selectors.md`（实测 `examples/`、`concepts/` 目录）。

## 6. 对我方目标的可用处（机制层面）

- **表格化的"别用 X 用 Y"是改变普通模型行为的最低成本手段**，比讲原理有效（`SKILL.md:135-141`、`Modelfile:80-88`）。
- **按危害排序而不是按报错排序**：把"静默错的几何"放在反模式首位，这条判据可直接用于我们整理 SolidWorks 失败模式（`CONTRIBUTING.md:64-66`）。
- **稳定的心智模型层**（BRep 而非 CSG、选择器优先于硬编码坐标、tag 优先于索引）——SolidWorks 侧对应"按特征/草图语义选实体，而不是按名字/坐标"（`CONTRIBUTING.md:33-38`）。
- **明文写出模型能力门槛**：告诉使用者"哪类模型能跟住哪套约束"，可以照搬到我们的使用说明里，避免把失败归因到工具（`README.md:87-91`）。
- **离线官方文档快照 + 先 grep 再写**，与我们既有纪律"官方文档是第 0 步"同构，可直接借它的组织方式（`README.md:97-114`）。
- **上下文分层**（速查常驻、细节按需）可直接用于我们的 skill/规范文件切分（`README.md:10-18`）。
- **反模式的写作格式**（错例 → 对例 → 原因 → 一行速查摘要）是拿来即用的模板（`CONTRIBUTING.md:61-67`）。

## 7. 许可与红线

- 仓库本体 Apache-2.0：可读、可抄、可改、可商用；保留版权声明即可（克隆内 `LICENSE` 原文；无 NOTICE 文件）。
- **`docs/` 快照要单独看许可**：那是 CadQuery 官方 RST 的副本，搬进我们仓库前必须核 CadQuery 上游许可与本快照的实际范围（本卡未核该点，见 §9）；`docs/_static/` 内还带第三方字体许可文件 `docs/_static/logo/Roboto_Font/LICENSE.txt`（原文同为 Apache-2.0 首行）。
- 我方红线：本次对克隆**只读**（未改任何文件）；搬它的文本要标来源与许可，不把它的示例当"已验证"证据。

## 8. 证据清单

```
D:\ai3d-survey\repos\jmwright__cadquery-llm-skill\README.md:1-8,10-18,30-95,87-91,93-95,97-114,118
...\SKILL.md:3,8-35,39-58,62-93,96-113,114-128,132-168,219-227,247-264
...\Modelfile:1-3,5,80-88,155-191
...\CONTRIBUTING.md:16-26,33-38,61-67,86-93,95-105
...\scripts\build_ollama_modelfile.py:8-13,15-26,29-41,51-55
...\patterns\anti-patterns.md:7-297 （14 个小节，`^## ` 实测）
...\patterns\common-patterns.md:8,162 · concepts\{brep-mindset,workplanes,selectors,free-function-api}.md
...\examples\{brep_thinking,fillet_and_chamfer_challenges}.py · docs\README:1-2
```
- 计数实测：`docs/` 67 个文件、顶层无 `.github/`、无 `docs/VERSION*`（来源：在克隆内用 `Get-ChildItem -Recurse -File` 现场计数）。
- 元数据来源：https://api.github.com/repos/jmwright/cadquery-llm-skill （取数 2026-10-23）。

## 9. 未确认事项

- 未跑任何示例、未建 Modelfile 模型（本机 `cadquery` 未安装）；本卡为读码级，"示例都验证过"是仓库声明（`CONTRIBUTING.md:16-26`），未独立复核。
- `docs/` 快照对应的 CadQuery 版本**查不到**（无 `docs/VERSION`），因此无法判断它与当前 CadQuery 的行为偏差；该快照自身的许可范围也未核。
- Modelfile 的实际效果（尤其"14b 门槛"这条）是作者陈述，未复现（`README.md:87-91`）。
- stars 与推送日期是 API 快照，之后会变。
- 未核 `concepts/*.md` 与 `patterns/common-patterns.md` 的逐条技术断言（本卡只按结构抽样读了 `anti-patterns.md` 的小节标题与 `SKILL.md`/`Modelfile` 全文）。