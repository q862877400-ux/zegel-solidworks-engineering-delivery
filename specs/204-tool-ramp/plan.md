# 规格 204 · 施工计划（plan）

> 规格：[`spec.md`](spec.md) · 任务：[`tasks.md`](tasks.md)
> 目标：工具数 **296 → ≥400**（SC-001），★ 每批过全门禁 + 附测试 + 逐批提交。

## 一 · 每批的**固定工序**（七步，不跳）

```
① ★ **选域**：从 `output/tool-ramp-plan-data.json` 取下一批（P1 整域未暴露 → P2 域内工具少）
② ★ **核能力层**：读该模块的公开函数（签名 + docstring），逐条判**可暴露性**：
     · 能暴露：全部形参是**标量/字符串**（或可由 `inject`/`derived_args` 补）
     · 需包装：形参含 `model`/`sw_app`/`study`/`manager` ⇒ 用 `inject`（★ 解析器已在 `register_capabilities`）
     · **不做**：含**裸坐标**（FR-003）· 是**基础设施**（FR-007）· **域内已有工具覆盖**（FR-006）
③ ★ **写 ToolSpec**（`mcp-server/tool_specs_batch<NN>.py`）：
     · `name` 用 `solidworks_<域>_<动作>`（FR-005，★ 先查重）
     · 长度 `_mm` / 角度 `_deg`（FR-004）；★ 换算只在 `derived_args` 里做一次
     · `doc` 写**官方依据**（铁律 4）· 文件头写**来源块**（铁律 1 + `check_provenance`）
     · ★ **本批不与哪些既有工具重叠**（SC-004）
④ ★ **注册**：把批次名加进 `register_capabilities.BATCH_MODULES`（★ 并用注释记"本批做什么/为什么"）
⑤ ★ **测试**：`tests/test_tool_specs_batch<NN>.py` —— 注册得到 · 目标函数解析得到 ·
     参数绑定 · 默认值口径 · 本批**不重名**（★ 照批次 78 的样板）
⑥ ★ **改全局计数**：`tests/test_server_wiring.py` 里那处 `len(all_specs()) == N`（★ 它自己写着"加批次必须同时改"）
⑦ ★ **收尾链**：`pwsh -File tools\round_chain.ps1 -Tests tests\test_tool_specs_batch<NN>.py`
     ⇒ ★ 必须看到 `release_check 第 1 轮 OK`；然后 **单独提交**（D-3）
```

## 二 · 真机验证（★ 何时必须）

```
★ 工具"能挂上"由门禁保证；★ 而**能力是否真的能用**要靠真机 —— 两者不是一回事（事实：批次 28 的教训）✓
⇒ 判据（FR-009 + SC-005）：
  · ★ **FR-008 的两块（爆炸视图 / 宏）必须真机跑**（★ 规格 202 的 MUST）⇒ 一正一反两个场景
  · ★ 其余批次：★ **每批抽 1~2 个**做真机 smoke（★ 尤其"读"类：成本低、无副作用）
  · ★ 真机一律走 `python tools/sw_guard.py --timeout N -- python <脚本>`（AGENTS.md 硬要求）
  · ★★ 常驻弹窗监控已在跑（`output/dialog-watch/status.json`）⇒ ★ 真机期间它替我看框
```

## 三 · 风险与对策

| 风险 | 对策 |
|---|---|
| ★ 数量上去了、质量下来（"假数量"） | FR-006 按域去重 · FR-007 禁基础设施 · D-1 目标封 400 · 每批测试断言"不重名" |
| ★ 工具挂上了但能力是坏的（批次 28 的老病） | SC-005/FR-009：真机抽查 + 未验证的**不许**借工具升 level |
| ★ 一批太大、门禁红一片难定位 | 每批 ≤ ~15 个工具；★ 逐批提交、可单独回滚 |
| ★ Bunny 扇出静默失败（实测过） | provider+model **成对写**；★ 先跑 2 路探针再铺量（支线实测） |
| ★ 与另一个对话撞车（同仓两对话） | ★ 只 `git add` 自己的路径、绝不 `-A`（AGENTS.md §七）· 只写自己的批次文件 |

## 四 · 目录与命名约定（本规格新增物）

```
specs/204-tool-ramp/{spec.md,plan.md,tasks.md}      ← 本规格
mcp-server/tool_specs_batch79.py … batch8N.py       ← 每批一个文件（★ 编号接着现有最大号）
tests/test_tool_specs_batch79.py …                  ← 每批一个测试
output/tool-ramp-*.json                             ← 施工数据与每批证据（★ output 已 gitignore）
```
