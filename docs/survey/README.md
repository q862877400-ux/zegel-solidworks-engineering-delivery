# AI 自动建模调研 · 交接与索引（**新接手者从这里开始**）

> **这个文件是给「完全没有任何记忆」的接手者看的**：先读它，再读 `docs/ai-3d-survey-plan.md`（计划与判据）。
> 更新时间 **2026-10-23**（每轮必须更新本文件末尾的「变更日志」）。

---

## 0. 一句话现状

做「AI 自动建模」（文字/图 → 3D 与 CAD）的**逐项目**技术路径调研：**40 个仓库已全部克隆完成**，正在逐项目产出分析卡片（`docs/survey/cards/*.md`），最终要汇总出「架构分类矩阵 + 步骤做法矩阵」，并把总论报告更新到 v3。

| 阶段 | 状态 |
|---|---|
| R1 基建 + 情报专项（SKY-001）| ✅ **完成** |
| R2 逐项目卡片（T1 代码路线 12 张）| ⏳ **进行中**（4 路并行，卡片陆续落盘）|
| R3–R7 | ⬜ 未开始，步骤见 §4 |

---

## 1. 接手第一件事（照抄这三条）

```powershell
cd D:\Agent-Studio\Deepseek-Harness\DSH-Data\workspace\SW
python scripts\check_survey_cards.py          # 看卡片有没有过验收判据
Get-ChildItem docs\survey\cards               # 看已产出的卡片
```

再读两个文件，就能完全接手：
- `docs/survey/state.json` —— **机器可读状态**（已完成/进行中/待办、路径、下一步动作）
- `docs/ai-3d-survey-plan.md` —— 分档（T1/T2/T3）、卡片模板、验收判据、分批计划

---

## 2. 目录地图（东西都在哪）

| 路径 | 是什么 |
|---|---|
| `docs/survey/README.md` | **本文件**：交接与索引 |
| `docs/survey/state.json` | 机器可读状态（每轮更新）|
| `docs/survey/cards/*.md` | **逐项目卡片**（核心产出，每项目一张）|
| `docs/survey/architecture-matrix.md` | 架构分类汇总（**由脚本生成，不许手写**；R7 出）|
| `docs/survey/step-matrix.md` | 步骤做法矩阵（**由脚本生成**；R7 出）|
| `docs/ai-3d-survey-plan.md` | 调研计划：分档判据、卡片模板、验收判据、R1–R7 分批 |
| `docs/ai-cad-landscape-report.md` | 总论报告（v2，九类架构 + E1–E9 环节 + 数字索引；R7 更新为 v3）|
| `scripts/check_survey_cards.py` | 卡片门禁（结构 + 出处检查）|
| `scripts/gen_survey_matrix.py` | 汇总矩阵生成器（R7 写，**尚未创建**）|
| `D:\ai3d-survey\repos\` | **40 个克隆**（`<owner>__<name>` 命名，总 1.0 GB）|
| `D:\ai3d-survey\repos.txt` | 克隆清单（40 行，owner/repo）|
| `D:\ai3d-survey\logs\clone-log.tsv` | 克隆日志（repo / status / 秒 / MB）|
| `D:\ai3d-survey\clone.py` | 克隆脚本（幂等，可重跑：已存在的目录跳过）|

---

## 3. 已完成（可直接引用，不需重做）

### 3.1 克隆：40/40 全部成功（2026-10-23，`--depth 1`）

清单见 `D:\ai3d-survey\repos.txt`，逐条状态见 `D:\ai3d-survey\logs\clone-log.tsv`。分档：
- **T1（深挖）**：text-to-cad、Amagine3D、Multi-Agent-CAD、agentcad、CADAM、cadquery-llm-skill、build123d-mcp、mcp-cadquery、cadquery、build123d、cadquery-contrib、fusion360-mcp-server、freecad-mcp、mcp-for-blender、RhinoAI、autocad-mcp、OpenSCAD-MCP-Server、slvsx-cli、freecad-ai、vcad、ai-cad、anvilate
- **T2（复现架构）**：cad-recode、cadrille、CAD-Coder、FlexCAD、Text2CAD、DeepCAD、Img2CAD、CAD-Assistant、Hunyuan3D-2、TRELLIS、TripoSG、TripoSR、InstantMesh、stable-fast-3d、stable-point-aware-3d、Step1X-3D、PlankAssembly、Drawing2CAD

### 3.2 情报专项：**SKY-001 已查清**

结论卡片：`docs/survey/cards/sky-001.md`。要点：**它不是 LLM，是「工程世界模型」**（预测几何状态序列，不是文本 token）；出品方 Skyfall AI，**2026-10-19 发布、闭源、waitlist**；自测 CAD IoU 79.7%/3.9 秒/¥0.005 对比 GPT-6 Astra 79.1%/199 秒；**无第三方复现**，且官方承认「生成的还不是可编辑参数化 CAD 历史」「演示中 2D 草图会与 3D 状态不一致」。
★ 该专项**新增了第 10 类架构 `J=世界模型/几何状态`**（原九类 A–I 见总论报告），R7 汇总时要写进 v3 并说明改动理由。

### 3.3 同期发现的三条非 LLM 路线（情报，待并入 v3）

| 模型 | 公司 | 关键点 | 来源 |
|---|---|---|---|
| Tripo P1.0 | VAST | **放弃序列化/next-token**，改「统一概率空间宏观坍缩」，2 秒出模型 | https://www.36kr.com/p/3709872081023369 |
| Lux3D | 群核科技 | Mesh+PBR+3D 高斯「大一统」，极速版 20 秒，**Harness 模式可集成进编码工具与 Blender** | https://tech.cnr.cn/techph/20260827/t20260827_527794661.shtml |
| MoWorld-3D | 魔芯 + 华为昇腾 | 28B MoE 交互式三维世界模型 | https://www.toutiao.com/article/7670848816454648320/ |

### 3.4 基础设施

- 卡片门禁 `scripts/check_survey_cards.py`：四条判据（字段齐全 / 量化断言有出处 / 证据等级在枚举内 / 有未确认段）。
- 资源实测：**D 盘剩 2,763 GB**（克隆放 D）；**RTX 4080 SUPER / 16 GB 显存**；Python 3.14.7；`git` 可连 GitHub。

---

## 4. 未完成（接手就照这个干）

### R2（进行中）：T1 代码路线 12 张卡

已派 4 路并行，分别负责：
1. `text-to-cad-earthtojake` / `amagine3d` / `multi-agent-cad`
2. `agentcad` / `cadquery-llm-skill` / `build123d-mcp`
3. `mcp-cadquery` / `cadam` / `fusion360-mcp-server`
4. `freecad-mcp` / `blender-mcp` / `autocad-mcp`

**若某张卡缺失**：按 `docs/ai-3d-survey-plan.md` §4 的模板补写；克隆在 `D:\ai3d-survey\repos\<owner>__<name>`。

### R3：桥接层其余（已克隆，未写卡）

`RhinoAI`、`OpenSCAD-MCP-Server`、`slvsx-cli`、`freecad-ai`、`mcp-cadquery`（若 R2 未完成）+ **本仓自带克隆的 4 家 SW MCP**（在 `C:\swprojects\`，不在 `D:\ai3d-survey\repos`：`Eduardof0nt` / `andrewbartels1` / `SolidworksMCP-TS` / `Slacker-LLC`）。

### R4：学术 10 张卡

`cad-recode` / `cadrille` / `CAD-Coder` / `FlexCAD` / `Text2CAD` / `DeepCAD` / `Img2CAD` / `CAD-Assistant` / `PlankAssembly` / `Drawing2CAD`（全部已克隆）。★ 注意 `cad-recode` 与 `Text2CAD` 是 **CC BY-NC 非商用**，卡片必须写「只读思想」。

### R5：网格 8 张卡（含实测）

`Hunyuan3D-2` / `TRELLIS` / `TripoSG` / `TripoSR` / `InstantMesh` / `stable-fast-3d` / `stable-point-aware-3d` / `Step1X-3D`（全部已克隆）。
★ 16 GB 显存内**能试跑**：TripoSR(~6G)、TripoSG(≥8G)、SF3D(~6G)、SPAR3D 低显存(~7G)、Hunyuan3D-2 形状(6G)；**跑不了**：TRELLIS.2(≥24G)、Hunyuan3D-2.1(29G) ⇒ 跑不了就写「未实测」。
★ Python 3.14 对 torch 支持有限，**要单独建 venv/conda 再试**，不要污染本仓环境。

### R6：商业与情报 13 张卡（T3，无源码）

Zoo / Fusion / Onshape / NX / Creo / Adam / Backflip / DriveWorks / Meshy / Rodin / Tripo / Spline / Leo。
★ 只能做黑盒分析（官方文档 + API 文档 + 公开案例），**标【宣称】/【事实】**。

### R7：汇总（**不许手写**）

1. 先写 `scripts/gen_survey_matrix.py`：扫 `docs/survey/cards/*.md`，生成 `architecture-matrix.md` 与 `step-matrix.md`；
2. 卡片里要能机读：**在 H1 下加一行**（R2 已派活的没要求到，需要人工/脚本补）：

```html
<!-- survey: class=B; repr=code; orchestration=loop; verify=geometry-gate; deliver=STEP; evidence=读码 -->
```

枚举：`class`=A 代码单发 · B 代码回环 · C 多智能体 · D 序列/DSL · E 网格 · F 逆向 · G 模板+规则 · H GUI/API 代理 · I 知识助手 · **J 世界模型**；`repr`=code·sequence·dsl·feature-tree·mesh·constraint·params；`orchestration`=single·loop·multi-agent·template·human-approve·none；`verify`=none·run-only·geometry-gate·numeric·visual·solver·dfm-rules·export-readback；`deliver`=STEP·mesh·drawing·gcode·none；`evidence`=实测·读码·元数据。

3. 更新 `docs/ai-cad-landscape-report.md` 到 v3，**每处改动逐条写明理由**（不留暗改）。

---

## 5. 硬约束与易踩的坑（接手前必读）

| # | 约束 / 坑 |
|---|---|
| 1 | **许可红线**：无 LICENSE / CC BY-NC / GPL/AGPL 的仓库**可以克隆只读，但禁止把代码复制进本仓**。已知非商用：`cad-recode`(CC BY-NC 4.0)、`Text2CAD`(CC BY-NC-SA 4.0)、`CADAM`(GPL-3.0)、`freecad-ai`(LGPL-2.1)、`slvsx-cli`(GPLv3)、CraftsMan3D(无 LICENSE) |
| 2 | **`docs/*.md` 有出处门禁**（`scripts/check_fact_provenance.py`，在 `release_check` 里）：凡「N 个/条/处/次/行/秒/MB/GB/%/倍」这类量化断言，**那一行必须自带可追溯指向**（`` `文件:行` `` / 反引号路径 / markdown 链接 / `来源：`）⇒ 卡片写法必须照此，否则 `python scripts\release_check.py` 会红 |
| 3 | **`subagent` 子代理不是 teammate**：`send_message` 找不到它们（本轮实测报 `active teammate not found`）。要补要求只能在派活时一次写清，或事后自己改文件 |
| 4 | **不许把 README 宣称当事实**：跑不动的写「未实测」；官方未验证的数字标【宣称】|
| 5 | 16 GB 显存 / Windows / Python 3.14 是硬环境；ML 依赖要独立环境 |
| 6 | 克隆**幂等**：重跑 `D:\ai3d-survey\clone.py` 会跳过已存在目录 |

---

## 6. 变更日志（每轮追加一行）

| 轮次 | 日期 | 做了什么 |
|---|---|---|
| R1 | 2026-10-23 | 立计划（`ai-3d-survey-plan.md`）；40 仓库全部克隆成功（1.0 GB）；SKY-001 情报专项查清并出卡；写卡片门禁 `check_survey_cards.py`；写本交接文档与 `state.json`；派 4 路写 R2 的 12 张卡 |
| R2（部分）| 2026-10-24 | 卡片落盘 **3 张**：`sky-001` / `earthtojake-text-to-cad` / `amagine3d`；★ 4 路 subagent 在会话中断后只剩 2 张（其余 9 张需重派）；★ 修门禁三处：新脚本补 §十八 来源块（统一化体检 ③ 归零）、`gate-wiring-exemptions.json` 登记 `check_survey_cards.py` 的暂缓接线（附 R7 到期条件）、派生文档重生成链跑完 ⇒ **`release_check` EXIT=0** |
| R2 收口 | 2026-10-24 | **13 张卡片全部过门禁**（R2 的 12 张 + sky-001；其中 blender/autocad/freecad 属 R3 提前做完）；两次提交 `d0aba63c`、`3139788b`；**上线汇总生成器** `scripts/gen_survey_matrix.py` ⇒ 生成 `architecture-matrix.md`（13 行）与 `step-matrix.md`（四维计数）；门禁判据放宽一处：出处形态改「任意扩展名 + 可选行号」（`.lsp:1216` 原先不认，误报 16 处）；freecad 卡三处数据纠错（证据等级降读码、`include_screenshot` 7→8、tag 改 feature-tree/single/visual）|
| R4 | 2026-10-24 | 派 3 路写学术批次 10 张：cad-recode / cadrille / CAD-Coder / FlexCAD / Text2CAD / DeepCAD / Img2CAD / CAD-Assistant / PlankAssembly / Drawing2CAD（全部已克隆）|