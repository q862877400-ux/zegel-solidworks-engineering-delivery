# LTGOz/solidworks-agent-skill

<!-- survey: class=D; repr=dsl; orchestration=template; verify=numeric; deliver=STEP; evidence=读码 -->

| 字段 | 值 |
|---|---|
| 仓库 / 主页 | `LTGOz/solidworks-agent-skill` · https://github.com/LTGOz/solidworks-agent-skill |
| 许可 | **MIT**（`LICENSE`，1083 B；README badge 逐字 `License-MIT-yellow`）⇒ 可并入，保留版权声明 |
| 元数据 | stars **3** · created **2026-09-02** · pushed **2026-09-04** · 语言 Python · 仓库约 126 KB（来源：`gh api repos/LTGOz/solidworks-agent-skill`，2026-11-02 取；体积见 `D:\swagent-2026Q4\dup-report.md` §3）|
| 克隆 | `D:\swagent-2026Q4\repos\LTGOz__solidworks-agent-skill`（`--depth 1`）|
| 证据等级 | **读码**（未运行：要活的 SolidWorks 2023；`sw_bridge.py` 41,308 B 已通读其 verify 与 op 分派）|

## 1. 一句话定位

**本批唯一把「LLM 只写 JSON 配方、执行器确定性执行、再用 trimesh 对导出的 STL 做几何断言，断言不过就当整条配方失败」做完整闭环的 skill 包**；它给出一个明确的成本账——「LLM 直接调 COM API 只有约 54% 成功率（引 Query2CAD）」，因此不让模型碰 API。附带一份 12 节、12.8 KB 的 COM 坑手册。（来源：`README.md` 与 `sw_bridge.py:645-690`，见本卡 §8）

## 2. 技术路径（输入 → 中间表示 → 生成 → 编排 → 执行 → 验证 → 交付）

**输入**：自然语言 → agent 按 `SKILL.md` 加载技能 → **LLM 只产出一条 JSON 配方**（`recipes/*.json` 共 9 条样例：`recipe_tube_bracket.json`、`recipe_asm_test.json`、`recipe_step_test.json` 等）。
**中间表示**：**JSON op 序列**（`repr=dsl`）。op 种类从 `sw_bridge.py` 的 `--demo` 与 README 用例子可见：`new_part` / `sketch` / `rect` / `extrude` / `revolve` / `cut` / `fillet` / `chamfer` / `export` / `verify`。
**生成**：不生成代码——`sw_bridge.py` 按 op 确定性执行（这是它与我方「工具一动词一调用」的核心差异：模型产出的是**一条配方**，不是 N 次工具调用）。
**编排**：`template`（配方模板 + 确定性解释器）；`--demo block` 是一条内置的完整闭环。
**执行**：pywin32 COM，**要求 SolidWorks 2023 正在运行**（README 明写「不是无头 CAD 服务」）。
**验证**（本卡重点）：`sw_bridge.py` 的 `verify(self, path, volume=None, bbox=None, tol=0.01, golden=None, golden_iou=0.99, require_watertight=True)` —— trimesh 断言层，检查四件：
1. **水密性**（`mesh.is_watertight`，`require_watertight=True` 时不水密直接失败）；
2. **体积**（mm³，`Δ%` 与 `tol` 比，**单位自动探测 mm/米**，见 `sw_bridge.py` 的 `scale` 分支）；
3. **包围盒**（mm，按 STL 轴序逐轴比）；
4. **可选 golden STL 的 IoU**（`golden_iou=0.99`，用 `mesh.intersection(g).volume` 算交并）。
   ⇒ **断言不过 = 配方失败**，README 逐字：「a failed assertion fails the whole recipe, so no silent scrap parts」。
另附 **ASCII STL 切片器**（`stl_slicer.py`，6,120 B）做截面检查；`dfm_check.py`（10,262 B）做 DFM 规则；`rules/dfm_injection.json` / `rules/dfm_proto.json` 是规则包。
**交付**：STL / STEP / 工程视角 PNG。

## 3. 技术方案要点（可迁移的机制）

### 3.1 ★★★ 「模型不碰 API」的量化理由

README 英文段逐字引用了一个成功率数字：「LLMs calling the COM API directly succeed only **~54%** of the time (Query2CAD), so this skill has the LLM write a **JSON recipe** instead」。（来源：`README.md` 英文段，见本卡 §8）
⇒ 这是一份**把「为什么不让模型调 API」写成数字**的样本。我方 439 个工具正是「让模型逐个调 API」的极端形态，这条对我方路线的挑战最直接。（来源：`docs/state/INDEX.md` 的工具数口径）
⚠【转述】该 54% 引自 Query2CAD，本卡未核原论文。（来源：本卡 §9 未确认事项）

### 3.2 ★★★ 断言层用**导出物**而不是内存读数

`verify` 的输入是 `path`（导出的 STL），它 `trimesh.load(p, force="mesh")` 后算水密/体积/包围盒。⇒ 判据的对象是**落到磁盘的交付物**，不是 COM 返回值。这与 SolidCraft 的「每件导出 STEP 再读回」是同一原则的两种实现，而它更省（用 STL + trimesh，不引 OCCT）。
★ 关键细节：**单位自动探测**（mm/米）——因为 STL 无单位。这一步不写就会差 1000 倍，正是我方单位事故的同型问题。（来源：`sw_bridge.py:645-690` 的 `scale` 分支，见本卡 §8）

### 3.3 断言必须带容差且逐轴

`tol=0.01`（1%）用于体积；包围盒逐轴比（`bbox[%d]=%.2f vs %g OK/FAIL`）。⇒ 与 SolidCraft 的 0.2% / 0.05 mm 同构，但这里是**离散率 1%**，量级更宽——说明它是「防报废」而非「防 0.1% 漂移」。

### 3.4 ★★ golden STL + IoU：形状判据

`golden_iou=0.99`，用 `mesh.intersection(g).volume / union` 算 IoU。⇒ 这是**「形状对不对」**的判据，补上体积/包围盒抓不到的情形（等体积但形状错）。我方目前缺这类判据。

### 3.5 12 节 COM 坑手册（`references/api-pitfalls.md`，12,832 B）

节标题逐字可见：`## 2. 类型库签名不可信，以录宏为准` · `## 3. 晚绑定 VARIANT 三规则` · `## 5. 中文本地化名称（英文系统名不同）` · `## 10. 兜底大招：录宏回放` · `## 12. 圆角/倒角（2026-08 实测打通）` · `### 12.2 选边（本次最大坑区）` · `## 13. COM 启动的 SW 实例附着不上（ROT 陷阱）` · `## 14. 性能包裹与 PNG 导出的互斥`。
⇒ 与 A 线从 `infei12306` 与 `forge_ai` 抽出的坑表**高度重合**（类型库签名、VARIANT、ROT、中文本地化名），三处独立来源指向同一批事实 ⇒ 交叉验证价值高。

### 3.6 `--demo block` 是一条可跑的验收样例

README 贴出真实输出：`verify OK: watertight=True; volume=32000.0 OK; bbox 80/40/10 OK`。⇒ 给了一个**可复现的最小判据**（80×40×10 方块 = 32,000 mm³），我方可以拿同一条判据去校准自己的验证链。

## 4. 运行条件与依赖

- Windows + **SolidWorks 2023 正在运行**（README「环境要求」；不支持无头）。
- Python 3.10+（`requirements.txt`，60 B）。
- 验证层需要 `trimesh` + `manifold3d`（`sw_bridge.py` 的 verify 分支报错信息逐字：「verify 需要 trimesh：pip install trimesh manifold3d」）。
- 三个 SKILL.md：根 `SKILL.md`（5,773 B）+ `skills/sw-dfm-injection/SKILL.md` + `skills/sw-dfm-proto/SKILL.md`。

## 5. 失败模式与已知坑

1. **只支持 SolidWorks 2023**（README badge 逐字 `SolidWorks-2023-red`）⇒ 我方 2026 环境不能直接跑。
2. **3 星、两天即停更**（created 2026-09-02 / pushed 2026-09-04）：外部验证为零，作者自述的实战案例（`docs/case_mcp1085_box.md`）无法复核。
3. **trimesh 是从 STL 反推几何**：STL 是三角化近似 ⇒ 对曲面件体积会有系统偏差（我方 D 线实测同类偏差 **-0.30%**，见 `docs/survey/cards/sw-d-blussyya-solidworks-converters.md` §3.1 的网格 vs 精确对照）。⇒ **1% 容差正好盖住这个偏差，但也意味着它抓不到 0.3% 级的问题。**
4. **配方是封闭 op 集合**：扩展需要改 `sw_bridge.py`，不是改提示词。
5. **未运行**：本卡结论止于读码。

## 6. 对我方目标的可用处（能学 / 不能学）

**能学（四件）**：
1. **★★★ 断言的对象是导出物**：`verify` 读 STL 而非 COM 读数。我方「导出 STEP → 回读」已是同路，但可借它**更省的 STL+trimesh 档**做快速门。
2. **★★★ golden STL + IoU 形状判据**：补我方缺的「形状对不对」一维（体积对但形状错抓不到）。
3. **★★ 单位自动探测**：STL 无单位，它做 mm/米探测。这正是我方「米/毫米反复出错」的同型问题的**现成解法样本**。
4. **★★ 失败即整条配方失败**（fail-closed）：与我方 A 线看到的 `forge_ai` 教义同向。

**不能学**：
- **封闭 op 集合 + 只能 SW2023**：覆盖面与版本都不够。
- **1% 容差 + STL 近似**：精度到不了我方 E 判据需要的量级。（来源：本卡 §5 失败模式）
- **把「模型只写 JSON」当教义**：它的 54% 引文值得读，但我方 439 工具里已有大量结构化参数，退化到封闭 DSL 会丢能力。（来源：`README.md` 英文段；工具数见 `docs/state/INDEX.md`）

## 7. 许可与红线

**MIT**（`LICENSE`，1083 B）⇒ 可并入。`THIRD_PARTY_NOTICES.md`（703 B）存在，并入时应一并保留。
⚠ 它引用的 Query2CAD 成功率数字属**转述**，引用时必须标出处与「未核原文」。

## 8. 证据清单

- `D:\swagent-2026Q4\repos\LTGOz__solidworks-agent-skill\sw_bridge.py:645-690`（`verify` 的签名、参数默认值、水密/体积/包围盒/IoU 四段判据）
- `D:\swagent-2026Q4\repos\LTGOz__solidworks-agent-skill\sw_bridge.py` 的 `--demo` op 序列（`:834` 附近 `{"op":"verify","path":"demo_block.STL","volume":32000,"bbox":[80,40,10]}`）
- `D:\swagent-2026Q4\repos\LTGOz__solidworks-agent-skill\references\api-pitfalls.md`（12 节标题，12,832 B）
- `D:\swagent-2026Q4\repos\LTGOz__solidworks-agent-skill\README.md`（英文段的 54% 引文与「no silent scrap parts」；`--demo block` 的输出）
- `D:\swagent-2026Q4\repos\LTGOz__solidworks-agent-skill\recipes\`（9 条配方样例）· `rules\dfm_injection.json` / `rules\dfm_proto.json` · `stl_slicer.py` / `dfm_check.py`
- `D:\swagent-2026Q4\repos\LTGOz__solidworks-agent-skill\LICENSE`（1083 B）· `THIRD_PARTY_NOTICES.md`（703 B）· `requirements.txt`（60 B）
- 元数据：`gh api repos/LTGOz/solidworks-agent-skill`（2026-11-02）；体积见 `D:\swagent-2026Q4\dup-report.md` §3

## 9. 未确认事项

1. **未运行**：`verify` 是否真按 1% 判、单位探测在真实 STL 上是否可靠，**均未实测**。（来源：本卡 §9 未确认事项）
2. **54% 的原始出处（Query2CAD）未核**：只读到本仓 `README.md` 的转述（来源：本卡 §8 证据清单）。
3. **golden IoU 的实际实现**（`mesh.intersection` 在非 manifold 网格上的行为）未验。
4. **只有 SW2023**：是否真的在 2026 上会断，未测。
5. **3 星项目的实战案例**（`docs/case_mcp1085_box.md`）无法复核。
