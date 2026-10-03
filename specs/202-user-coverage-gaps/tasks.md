# Tasks: 用户视角能力覆盖 · 缺口攻关

**Branch**: `202-user-coverage-gaps` ｜ 规格 `spec.md` ｜ 计划 `plan.md`

> 每条格式：**任务** → 验收（★ **一条能跑出绿的命令**，宪法 §V）。
> ★ 状态：`[ ]` 未做 · `[~]` 进行中 · `[x]` 完成 · `[-]` 已判不做（**带依据**）。

## T000 前置：规格与侦察

- [x] **T001** 立规格三件（spec / plan / tasks）
  → 验收: `python -c "import pathlib as p;[print(f) for f in ['spec.md','plan.md','tasks.md'] if (p.Path(r'D:\AI\SW\specs\202-user-coverage-gaps')/f).is_file()]"` 输出三行
- [x] **T002** 用**便宜模型助手并行**侦察 6 个域，产物写 `specs/202-user-coverage-gaps/recon/<域>.md`（六列表）
  → 验收: `python -c "import pathlib as p;d=p.Path(r'D:\AI\SW\specs\202-user-coverage-gaps\recon');print(len(list(d.glob('*.md'))))"` ≥ 1（★ 有几份算几份，失败的要写明）
  ★ 实况：**bunny 8 路并发**产出 **7/8 份**（`feature.md` 未产出）；★ 而 `surface.md` / `sheetmetal.md` 等已落盘
  ⚠ 教训：★ **本地模型不可并发**（曾被业主当场打断）⇒ 机械活给 bunny、判断活给本地模型**串行**（事实 489）
- [ ] **T003** 逐条**拿官方原文抽查**侦察结论（宪法 §III：**专挑最容易编造处**）
  → 验收: `python -c "import pathlib as p,re;t=''.join(f.read_text(encoding='utf-8') for f in p.Path(r'D:\AI\SW\specs\202-user-coverage-gaps\recon').glob('*.md'));print('官方没写:',t.count('官方没写'))"` 且 `docs/` 下留抽查记录
  ★ 已开始：★ 我**自己**用 `tools/audit_gap_implementations.py`（AST）独立量了「本仓现状」那一列作为交叉印证
- [x] **T004** 侦察结论落 `specs/202-user-coverage-gaps/research.md`（分诊表：建成 / 到不了 / 查不到）
  → 验收: `python -c "import pathlib as p;print((p.Path(r'D:\AI\SW\specs\202-user-coverage-gaps')/'research.md').is_file())"` 输出 `True`
  ★ 实况：分诊为 **A 已建成 3 · B 有实现未暴露 2 · C 候选直入法 19 · D 到不了 1 · E 待查 2**；
  ★★ 并记下**本轮最关键的一条定则**：**侦察说"官方没写" ≠ 官方没有**（它只在我给的候选名里查）
  ⇒ ★ 钣金/焊件 6 处"未命中"**是我的候选名写错了**，真名已回查确认（`InsertSheetMetalMiterFlange` 等）

## T100 工程图（P1 · 13 项）

- [ ] **T101** 视图族：逐项核官方入口（投影/剖面/局部/断裂/辅助）
  → 验收: `python -c "import pathlib as p;print(len(list(p.Path(r'C:\swapi\types').rglob('Create*View*.md'))))"` > 0
- [~] **T102** 标注族：逐项核官方入口（注释/基准符号/表面粗糙度/中心符号线/气泡序号/孔表/修订表）
  → 验收: `python -c "import pathlib as p,re;n=[f.name for f in p.Path(r'C:\swapi\types').rglob('*.md') if re.search(r'(SurfaceFinish|DatumTag|Note|CenterMark|BOMBalloon|HoleTable|RevisionTable)',f.name)];print(len(n))"` > 0
  ★ 实况：侦察已确认 **8/8 命中官方入口**（`recon/drawing_anno.md`）⇒ ★ 下一步是**实现**（C 类）
- [ ] **T103** 实现包装（`scripts/sw_drawing_views.py` 等）+ ToolSpec
  → 验收: `python -c "import ast,pathlib as p;ast.parse(p.Path(r'D:\AI\SW\scripts\sw_drawing_views.py').read_text(encoding='utf-8'));print('ok')"`
- [ ] **T104** 真机探针（★ 走护栏）逐项 1 格
  → 验收: `python tools\audit_gap_implementations.py`（★ AST 重扫）且
    `python -c "import io,re;t=io.open('docs/user-feature-coverage.md',encoding='utf-8').read();print(int(re.search(r'本仓库\*\* \| (\d+)/145',t).group(1))>=105)"` 输出 `True`
  ★ 命令**只用仓库内已有的东西**（★ 门禁 `check_spec_acceptance_paths` 会拦不存在的路径与仓外脚本）
- [ ] **T105** 建成项登记 `capabilities.yaml`（`level: verified` + `evidence`）
  → 验收: `python scripts\release_check.py` 退出 0（内含 A4「verified 必须带 evidence」门禁）

## T200 特征与曲面（P2 · 9 项）

- [x] **T201** ★ **把已 `verified` 而未挂工具的能力补上入口**（旋转曲面等）
  → 验收: `python -c "import sys;sys.path.insert(0,r'D:\AI\SW\mcp-server');import register_capabilities as r;print(len([s for s in r.all_specs() if 'revolve' in s.name.lower()]))"` > 0
  ★ 实况：工具 **253 → 256**；`solidworks_create_revolved_surface` 已注册且真机建成（`曲面-旋转1` · 曲面体 0→1）
- [ ] **T202** 组合/相交 · 缩放/变形 · 边界凸台 · 加厚：逐项核入口并分诊
  → 验收: `python -c "import pathlib as p,re;n=[f.name for f in p.Path(r'C:\swapi\types').rglob('*.md') if re.search(r'(InsertCombine|Scale|InsertProtrusionBlend|Thicken)',f.name)];print(len(n))"` > 0
- [ ] **T203** 建成项实现 + 真机探针 + 登记
  → 验收: `python tools\audit_gap_implementations.py` 且
    `python -c "import io,re;t=io.open('docs/user-feature-coverage.md',encoding='utf-8').read();print(int(re.search(r'本仓库\*\* \| (\d+)/145',t).group(1))>=104)"` 输出 `True`
- [ ] **T204** 到不了项写进 `docs/backend-limited-items.json`（★ 每条带依据）
  → 验收: `python scripts\check_backend_limited_completeness.py` 退出 0

## T300 钣金与焊件（P3 · 8 项）

- [ ] **T301** 逐项核官方入口（斜接法兰/闭合角/转折/褶边/展开/平板型式 · 裁剪延伸焊件/顶端盖/角撑板/焊接符号）
  → 验收: `python -c "import pathlib as p,re;n=[f.name for f in p.Path(r'C:\swapi\types').rglob('*.md') if re.search(r'(Miter|ClosedCorner|Jog|Hem|EndCap|WeldSymbol|Gusset)',f.name)];print(len(n))"` > 0
- [ ] **T302** ★ 有 `AccessSelections` 的**先判指针族**再决定做不做（事实 47/474）
  → 验收: `python -c "import pathlib as p;print(sum(1 for f in p.Path(r'C:\swapi\types').rglob('*.md') if 'AccessSelections' in f.read_text(encoding='utf-8',errors='replace')))"` 且分诊表写明判据
- [ ] **T303** 到不了项进 `docs/backend-limited-items.json`；建成项实现+验证+登记
  → 验收: `python scripts\check_backend_limited_completeness.py` 退出 0

## T400 草图/装配/其他（P4 · 5 项）

- [~] **T401** 样条曲线 + 完全定义检查：核入口并实现
  → 验收: `python -c "import pathlib as p;print((p.Path(r'C:\swapi\types\ISketchManager\CreateSpline.md')).is_file())"` 输出 `True`
  ★ 实况：**完全定义检查 done**（`sw_sketch_status.get_constrained_status` + 工具 `…_fully_defined_status`，真机 2/3 有区分度）；
  ★★ **样条曲线判 `[-] 到不了`**：`CreateSpline2` 回 `None`、后继 `CreateSpline3` 末参 **BYREF `Object&`**（事实 47/68/141）
  ⇒ 已登记 `docs/backend-limited-items.json`（12 → 13 条）；★ **不接成工具**（不假装做到）
- [ ] **T402** 爆炸视图 + 宏/VBA：核入口并实现
  → 验收: `python -c "import pathlib as p;print((p.Path(r'C:\swapi\types\ISldWorks\RunMacro.md')).is_file())"` 输出 `True`
- [ ] **T403** PDM 项：判 `[-] 不做` 或做（★ 带依据）
  → 验收: `python -c "import pathlib as p;t=p.Path(r'D:\AI\SW\specs\202-user-coverage-gaps\research.md').read_text(encoding='utf-8');print('PDM' in t)"` 输出 `True`
- [ ] **T404** 真机探针逐项 1 格（★ 走护栏）
  → 验收: `python tools\audit_gap_implementations.py` 且
    `python -c "import io,re;t=io.open('docs/user-feature-coverage.md',encoding='utf-8').read();print(int(re.search(r'本仓库\*\* \| (\d+)/145',t).group(1))>=104)"` 输出 `True`

## T900 收敛

- [ ] **T901** `capabilities.yaml` 逐条标级（★ `verified` 必须有我们自己的运行证据）
  → 验收: `python scripts\release_check.py` 退出 0
- [ ] **T902** `docs/known-facts.md` 追加本轮事实（★ 含"下一步"与否证）
  → 验收: `python -c "import pathlib as p;print(p.Path(r'D:\AI\SW\docs\known-facts.md').read_text(encoding='utf-8').count('| 49'))"` ≥ 1（★ 编号已过 487）
- [ ] **T903** ★ **回读覆盖率**（★ 只靠补真入口，**不许改生成物**）
  → 验收: `python -c "import io,re;t=io.open('docs/user-feature-coverage.md',encoding='utf-8').read();print(re.search(r'本仓库\*\* \| (\d+)/145',t).group(1))"` 输出 ≥ `110`（SC-001）
  ★ 现读数为 **99**（96 → 99，本轮 +3）⇒ ★ **尚未达标**，★ 目标 110 由后续批次补
  ⚠ 覆盖率**生成器刻意不在本仓库**（`D:\SW-coverage-tool\`）⇒ ★ 验收**只读它的产物**，★ **不调那个脚本**（否则验收命令不可移植）
- [ ] **T904** `docs/toolbar-ledger.json` 里相关行的 `note` 更新为结论（★ 结论挂在被结论所指的记录上）
  → 验收: `python tools\build_toolbar_ledger.py` 退出 0
- [x] **T905** 收尾链
  → 验收: `pwsh -File tools\round_chain.ps1 -Tests tests\test_official_md_claims_gate.py` 输出「release_check: 第 1 轮 OK」
  ★ 实况：同上（★ 收尾链同时跑生成器 + `release_check` + 聚焦测试）
- [ ] **T906** 提交（★ 只 `git add` 自己改的路径；不用 `-A`）
  → 验收: `git status --porcelain` 输出为空

## 依赖与顺序

```
T001 → T002 →（T003 抽查）→ T004
T100 / T200 / T300 / T400  ★ 彼此独立，可并行推进
       ↓（各自建成后）
T900 收敛（★ 必须等前面各域的**真机证据**都落盘）
```
