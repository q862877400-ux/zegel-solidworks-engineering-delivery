# solidpilot-salvage —— 从 SolidPilot 目录抢救出的自有成果

> **这不是 SolidPilot 项目本身。** 是 2026-10-01 从
> `C:\Users\Zegel\solidpilot-mcp\` 里**抢救出来的、属于我们自己的工作**。
> 原目录**未删除**，仍在原处当备份。

## 为什么有这个目录

`C:\Users\Zegel\solidpilot-mcp\` 是 `eyfel/mcp-server-solidworks`（SolidPilot，AGPL-3.0）
的克隆，被当作 DSH 的 SolidWorks MCP 用过一段时间。但它里面**混进了大量我们自己的成果** ——
因为那段时间所有会话的工作目录都在那儿。

2026-10-01 决定把 DSH 的 SolidWorks MCP 换成上游自带的那个（MIT），
于是要处置这个目录。**删除前清点时发现里面有不可再生的东西**，所以先抢救。

## 这里面是什么

| 目录/文件 | 是什么 | 独有性 |
|---|---|---|
| `官方文档/` | ★ **`拓扑优化_官方做法.md`** —— 拓扑优化正是我们要建的三个护城河域之一 | 独有 |
| `官方文档/` | `Simulation载荷夹具API签名全表.md` | 独有 |
| `loose/` | ★ **`问题交接2_DISPPARAMS已通卡E_INVALIDARG.md`** —— COM byref 的实操记录 | 独有 |
| `loose/` | `问题交接_Simulation夹具API调不通.md` · `文档查询地图.md` | 独有 |
| `loose/` | `主轴壳体_静力学分析结果_20260928.md` —— 带真实求解结果 | 独有 |
| `loose/` | `设计评审_BT30_ATC_20260928.csv` · `装配体检_*.md` · `新会话启动_*.md` | 独有 |
| `loose/` | `swdoc.ps1` / `swdoc2.ps1` —— 官方文档检索工具（AGENTS.md §4.1 引用） | 独有 |
| `loose/` | `_handoff_prompt.txt` | 独有 |
| `loose/` | `api_scan_*.csv` ×8 · `api_products.csv` · `api_silent_audit.csv` · `product_availability.csv` | 独有 |
| `loose/` | `param_combos*.csv` ×4 · `cnc_unique_parts.json` · `write_ops_verify.csv` | 独有 |
| `loose/` | 一批 `.py`：`run_bracket_*.py` `run_pulley.py` `render_bracket.py` `gen_gt3_profile.py` `probe_*.py` `apply_materials.py` … | 独有 |
| `loose/` | `dsh-solidworks.cordis.yml` —— 当时的 DSH 配置 | 独有 |
| `调研/` | `各interopDLL接口统计.csv` · `官方API全量清单.csv` · `全接口可用性扫描.csv` | 独有 |
| `调研/Wenmao/` | 25 文件 | 独有 |
| `tools/` | 79 文件 | 独有 |
| `cs-patches/` | ★ **C# 执行层的 14 个 `.cs`**（6 个改上游 + 8 个新增）+ `_MANIFEST.tsv` 标明哪个是哪种 | 独有 |
| `backup-20260927/` | 8.1 MB，C# 执行层备份（含 `SolidworksExecution.exe.bak`） | 独有 |
| `backup-20260927-132009/` | 0.3 MB，同上 | 独有 |

## 刻意**没有**搬的（可重新取得，或不该碰）

| 项 | 为什么不搬 |
|---|---|
| `知识库/`（148 文件 / 0.7 MB） | **与 `~/.agents/skills/mech-design/知识库/` 是同一份** —— 实测「solidpilot 独有 0 个」 |
| `调研/GitHub项目/`（4,077 文件 / 140 MB） | 10 个 **git 克隆**（codestack / solidworks-api / …），可重新 clone；**且含 `SolidWorks-CAD`（破解投递页，铁律 2 红线：零接触）** |
| `调研/repos/` | 空目录 |
| `.venv/` `bin/` `obj/` | 构建产物与虚拟环境，可重建 |
| SolidPilot 本体（`adapters/` `cad-planner/` `compiler/` `execution/` 等） | **AGPL-3.0** —— 按铁律 6 只读思想，不作为运行时依赖；且原目录未删，随时可查 |

## 原目录的状态

```
C:\Users\Zegel\solidpilot-mcp\      ← 未删除，仍在原处
  · DSH 里的 MCP 注册已移除（cordis.patch.yml 的 preset-solidworks）
    备份: ~/.dsh/profiles/web/cordis.patch.yml.bak-20261001-solidworks
  · 即：**已停用，未删除**
```

## 给未来自己的提醒

1. **这里的东西是「当时的工作记录」，不是「可直接复用的库」。** 要用先读、再按
   `docs/union-conventions.md` 的规则归一。
2. **`cs-patches/` 是 C# 层的改动** —— 那是另一条技术路线（进程内 add-in），
   与本项目的 Python COM 路线不同源。读它的**思想**，不要直接搬代码。
3. **`官方文档/拓扑优化_官方做法.md` 直接关系到 A9（护城河要可跑的实现）** ——
   做到拓扑优化时**先读它**。
