# 全仓逐文件诊断报告 · 2026-11-02

> **业主指令**：「先全面自我诊断一下我们这个项目，一个文件一个文件地诊断，看看现在做到什么程度了、能实现什么功能。你按照多轮自动进行，而且要多轮带机械门禁地自动进行。不然你就容易骗我说『我看完了』，实际上根本就没看。」
>
> **本报告的每个数字都可复现**；「看完了」由门禁证明，不由我自述。

---

## 0 · 一句话结论

**这不是一个「工具很多但没人验证过」的项目，也不是一个「能端到端交付零件」的项目。**
它是一个**底座扎实、门禁极严、但验收面积远小于工具面积**的项目：

| 维度 | 实测 | 判断 |
|---|---|---|
| 入库文件 | **8,670** 个（入册 4,872 / 出册 3,798） | 入册文件 **100%** 逐条有裁决与证据 |
| 能力台账 | **140** 条：`verified` **100** / `stitched` **38** / `not_implemented` **2** | 已验证面积 71% |
| 工具面 | **544** 个（**499** 声明式 + **45** 手写） | 工具数量 ≠ 验收面积 |
| 测试 | **557** 文件 / **4,929** 用例可收集 | 收集失败 **0** |
| 门禁 | **66** 道（全部接线，元门禁 PASS） | `release_check` **EXIT=0** |
| 结论 | — | **可推 GitHub（私有）；公开前需清史与剔除第三方 salvage** |

---

## 1 · 怎么做的：机械门禁（防「嘴上说看完了」）

### 1.1 三件新工具（本轮新增，已接进 `release_check`）

| 文件 | 作用 |
|---|---|
| `scripts/gen_file_audit.py` | 枚举 `git ls-files`，为每个文件产**机械事实**（字节/行数/能否编译/AST 函数类数/空壳函数/告警数/自述用途），写 `docs/state/file-audit.jsonl`；**幂等**，内容 sha 未变时保留既有裁决 |
| `scripts/check_file_audit.py` | **门禁**：入册文件零 `pending`；`verdict` 在枚举内；`evidence` ≥12 字符；`reviewed` 必须以 `deep:`/`skim:` 开头并带 `round`+`checked_by`；**自带负例自证**（三条坏行必须被抓出） |
| `scripts/audit_bulk.py` / `scripts/merge_audit_patches.py` | 机械裁决（仅限文档/规格/数据类）；人工审阅补丁合并（并行审阅者不互相覆盖） |

### 1.2 覆盖率（流水账，每轮都跑门禁）

| 轮次 | 动作 | 覆盖 |
|---|---|---|
| 起点 | 建台账，全部 pending | 0 / 4,872（门禁红，负例自证通过）|
| R1 | 文档/规格/参考/示例/元数据/配置 按「文本结构」机械裁决 | 3,029（62.2%）|
| R2 | `tools/` 703 个按「Python 机械」裁决 + 三路并行审阅 | 3,732（76.6%）|
| R3 | 三路补丁合并（scripts 292 / mcp+subskills 194 / apps 79 / tests 557） | 4,834（99.2%）|
| R3b | 剩余 37 个 `.ps1`/`.cjs`/`.cs`/`.json` 由我逐文件看内容后裁决 | 4,872（100%）|
| R4-R5 | 我改过的文件内容变了 ⇒ 自动回退 pending，逐条重裁并写明改了什么 | **4,872（100%）** |

**最终**：`[PASS] 入册 4872 个文件全部有裁决与证据（4872/4872）`。

### 1.3 裁决口径（不同文件用不同标准，写死在门禁里）

| 类别 | 标准 | 允许的 verdict |
|---|---|---|
| 产品代码（`scripts`/`mcp-server`/`apps`/`subskills`） | **必须逐文件读** | 只许 `reviewed`（`deep:` 或 `skim:`）；机械批量**被禁止**（`audit_bulk.py` 直接拒收这四类）|
| `tools/`（门禁与辅助脚本） | 可编译 + 可解析 + 有自述 | `derived-verified` |
| 文档 / 规格 / 参考 / 示例 / 元数据 / 配置 | 结构完整 + 有自述用途 | `derived-verified` |
| 测试 | `pytest --collect-only` 实收集结果 | `derived-verified` |
| 归档 / 产物 / 第三方 salvage / 二进制 | 按铁律 3 出册 | `frozen` / `generated` / `excluded` / `binary-asset` |

**深度分布**（`docs/state/file-audit.jsonl` 可核）：`deep:` **≥180**（三路合计 177 + 我本人标注的若干）· `skim:` 其余入册代码 · 机械核 2,000+。

---

## 2 · 现在能做什么（能力盘点，每个数字有出处）

### 2.1 能力台账：140 条

出处：`capabilities.yaml`（`schema_version: 2.0`），以及生成物 `docs/union-level-audit.md`。

| 等级 | 条数 | 含义 |
|---|---:|---|
| `verified` | **100** | 有我们自己的**真机运行证据** |
| `stitched` | **38** | 实现按官方签名写好、**缺自有运行证据**（不许冒充 verified）|
| `not_implemented` | **2** | `autocad_basic_drafting`（无真机回归）· `pdm`（需另装许可产品，判「不做」）|

**分布**（`gen_level_audit.py` 实测）：`source` = `original` 110 / `upstream` 18 / `mixed` 11 / `undetermined` 1。

### 2.2 工具面：544 个

| 项 | 数值 | 出处 |
|---|---:|---|
| 声明式 `ToolSpec` | **499** | `register_capabilities.all_specs()` |
| 手写 `@mcp.tool` | **45** | `mcp-server/server.py` |
| **合计唯一工具** | **544** | `check_tool_official_claims.py` 实测（524 已核官方依据，基线 20 待收敛）|
| 声明层校验 | **0 问题** | `check_param_binding.py` / `probe_all_specs.py` |

⚠ **台账里的 501/497 是旧读数**（`docs/metrics.md` 的 498/45/543 才是对的；本轮再 +1 ⇒ 499/45/544）。

### 2.3 测试：557 文件 / 4,929 用例

出处：三路并行 `pytest --collect-only` 逐文件实测。

- 收集成功 **537** 个文件、**4,929** 个用例；**收集失败 0、超时 0**。
- 收集到 0 用例 **19** 个：18 个设计如此（conftest / helper / 独立脚本）+ **1 个真失效**（`tests/test_headless_occt_service.py` 因未装 OCP/trimesh，CI 里同样 0 用例）。
- **需真机 SolidWorks 的只有 15 个文件、0 个 pytest 用例**；其余 **542 文件 / 4,929 用例可离线**（靠 64 个 monkeypatch + 30 个假 COM）。

### 2.4 桌面端

| 端 | 状态 |
|---|---|
| `apps/workbench-ui`（React19 + Tauri2 **0.3.4**） | **正式客户端**：有 CI、SQLite、19 个 Rust `#[test]` |
| `apps/desktop`（PySide6 **0.1.0**） | 旧原型：mock 执行、无 CI、无测试 |

---

## 3 · 现在**不能**做什么（如实列）

### 3.1 等级为 `stitched` 的 38 条（实现有、运行证据没有）

按域归类（逐条见 `docs/union-level-audit.md`）：

- **工程图**：模型标注插入（本轮补）、中心线、截面属性（面积单位未确证：侧面读 0.4 vs 应为 400）
- **钣金**：折边（五种形态全回 `None`）、创建族六个
- **焊件**：裁剪/延伸（试死）、角撑板、圆角焊缝
- **模具**：分型几何（`insert_shut_off_surface` 三次都回 true 而树不变）
- **曲面**：加厚、剪裁曲面取消剪裁
- **装配/运动**：`AddComponent5` 真机回 `None`、旋转马达、动画导出
- **其它**：宏录制（返回值不可用）、Routing、需求分析/规划、C# Add-in 宿主、配置与设计表、DFM 复核、Pack and Go、无 CAD 开放格式写入

### 3.2 三个「结构性缺口」（不是 bug，是边界）

1. **`view`(22) 与 `review`(12) 两域共 34 个工具，一条 `verified` 都没有**；
2. **16 条 `verified` 能力仍零工具**（能力在，但模型够不到）；
3. **543 工具里只有 293 个被能力条目认领**，250 个无归属。

### 3.3 真实机脚本大多没有自动门禁

12 个真机 CAD 脚本里只有 3 个被引用，且所在 workflow **仅手动 `workflow_dispatch`**；**9 个在任何 CI/脚本/文档里 0 引用**。

---

## 4 · 本轮修了什么（都是门禁能证明的）

| # | 修复 | 证据 |
|---|---|---|
| 1 | **`drawing_dimension_insertion` 从 `not_implemented` 修正为 `stitched`** | 原记录理由是「实现层没有对应函数」——**那是搜错成员名**：真正干活的是 `IDrawingDoc::InsertModelAnnotations4`（8 参），子技能 `drawing_workflow.insert_dimensions` 早已实现，缺的只是**工具层暴露**。本轮补 `scripts/sw_drawing_annotations.py` + 工具 `solidworks_drawing_insert_model_annotations` + 7 条离线契约测试 |
| 2 | **服务起不来（导入期崩溃）** | `check_specs` 只捕 `GateError`，非 GateError 异常穿透 ⇒ `import server` 崩、`check_param_binding` 与 `probe_all_specs` 跟着崩。改为「任何异常记成该 spec 的问题」⇒ 三条链路恢复；`tests/test_check_specs_robustness.py` 三条负例锁死 |
| 3 | **6 个文件 / 8 处无效转义**（未来 Python 会变硬错误） | `sw_part.py`×3、`sw_export.py`、`sw_drawing_expose.py`、`test_source_verification_conclusions.py`、`probe_dialog_guard_selftest.py`；`check_python_syntax.py` 原先只捕 `SyntaxError` ⇒ **补上 SyntaxWarning 判据**（两个负例验证） |
| 4 | **恒真断言** | `test_tool_specs_batch17.py` 的 `assert "" is not None` 换成真反例（归一化失效时真的会红） |
| 5 | **接线守卫长期失效** | `test_server_wiring.py` 钉死 480，而实际早已 498 ⇒ 一次对齐到 499 并写明「每加批次必须改这个数」 |
| 6 | **成员归属歧义** | 我的 `_iter_views` 与另两文件同名 ⇒ `FunctionIndex` 按函数名索引导致 **10 条假 `member-uncited`**；改名 `_annot_iter_views` |
| 7 | **`claim` 必须逐字等于 doc 首句** | 建 `docs/tool-official-claims/B9.json`，10 个成员的锚点逐字取自官方页 |
| 8 | **凭据入库** | `docs/history/research-misumi-api.md` 里 2 处真实 API key 已脱敏（★ 历史提交里仍在，公开前须清史） |

**门禁结果**：`release_check` **EXIT=0**；`check_file_audit` 4,872/4,872 PASS；`check_gate_wiring` 66 道全接。

---

## 5 · 还没修的（具名，不藏）

1. `sw_part.py:2167 hole_wizard()` 是 `pass` 空壳（真实现在 `sw_hole_features`，调用方拿 `None` 不报错）；
2. 7 个模块缺 docstring（`sw_loft`/`sw_measure`/`sw_sensor`/`sw_surface_features`/`sw_sweep`/`sw_units`/`sw_wrap`）；
3. `sw_sketch_dimensions.py:1` 自述「两个入口被怀疑会弄崩 SolidWorks —— 见下」，**全文没有那一节**，而它被暴露 6 个工具；
4. `DxfViewport.tsx` 缩放后点选错位（CSS `scale` 与 `getBoundingClientRect` 口径不一致）；
5. `styles.css` 两套皮肤并存：110 个选择器重复定义；
6. `tests/test_headless_occt_service.py` 永不执行（CI 也不装 `requirements-occt.txt`）；
7. `scripts/jlcfa_index.json` 单文件 **11.2 MB**、`assets/star-history.svg` 与 `-dark.svg` **完全相同**（都是 2026-09-28 的 1010 星旧图）。

---

## 6 · 复现命令（每个数字都能重算）

```powershell
$env:PYTHONIOENCODING="utf-8"      # ★ GBK 控制台下多个门禁会假红
python -B scripts\gen_file_audit.py        # 重建台账
python -B scripts\check_file_audit.py      # 覆盖率门禁（含负例自证）
python -B scripts\release_check.py         # 全量 66 道门禁
python -B scripts\check_gate_wiring.py     # 门禁接线元门禁
python -B scripts\check_tool_official_claims.py
python -B scripts\check_python_syntax.py
python -B docs\state\probes\probe_all_specs.py
python -B scripts\gen_level_audit.py       # 能力等级审计（生成物）
```

**台账**：`docs/state/file-audit.jsonl`（8,670 行，每行一个入库文件 + 机械事实 + 裁决 + 证据）。
