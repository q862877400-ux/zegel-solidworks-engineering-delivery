# Zegel-SWE · SolidWorks 工程交付系统

[中文](README.md) · [English](README.en.md)

用一句自然语言指令驱动 SolidWorks，产出机械工程师敢拿去用的模型与图纸。底层是一个本地 MCP 服务，把 SolidWorks COM 接口按白名单封装成 544 个工具，并配了一套针对中国机械设计习惯的检查能力。

## 一、交付到什么程度算合格

这个项目对"做完了"的定义不是"模型建出来了"，而是下面七条同时成立：

| # | 标准 | 合格的样子 |
|---|---|---|
| E1 | 草图全约束 | 求解器状态是完全定义，没有欠约束实体；位置、形状、大小由几何约束加尺寸约束驱动，不是靠坐标硬拽 |
| E2 | 参数化可重建 | 在交付件的副本上改主参数后重建，关键尺寸和下游关系正确联动，存盘重开仍然成立 |
| E3 | 特征树可编辑 | 特征树没有错误和警告，没有悬空引用；能改前序草图或参数并验证后续 |
| E4 | 装配自由度闭合 | 配合对象与剩余运动可回读，目标自由度符合设计意图，干涉为 0，关键间隙合规 |
| E5 | 图样合规 | 标注清单由功能、制造、检验要求生成，逐项绑定到真实图纸对象，并核对数值、基准、所指几何与版本 |
| E6 | 工艺可行 | 从实际几何和工艺输入检查已确认工艺路线的适用项：刀具可达、孔深、壁厚余量、装夹空间 |
| E7 | 结论可溯源 | 每条工程判断都能解析到有效证据或可复算依据，含原文或算法、适用条件、版本与产物绑定 |

## 二、环境要求

| 项 | 要求 |
|---|---|
| 操作系统 | Windows（SolidWorks 是 Windows 桌面 COM 应用） |
| CAD | SolidWorks 2024 或 2026 SP01.1（这两个是回归过的版本）；AutoCAD 2024 用于二维部分 |
| Python | 3.10 以上，64 位，与 SolidWorks 位数一致 |

## 三、安装与自检

```powershell
# 1. 依赖
pip install -r mcp-server\requirements.txt

# 2. 环境自检：缺什么、影响哪个格式、怎么装，一次列出来
python scripts\cad_doctor.py
```

自检通过后，把 MCP 服务加进你的客户端（以 DSH 为例，Claude Code / Cursor 同理，路径换成你的克隆位置）：

```json
{
  "mcpServers": {
    "solidworks": {
      "command": "python",
      "args": ["D:/path/to/this/repo/mcp-server/server.py"]
    }
  }
}
```

连上之后先调一次 `solidworks_health_check`，确认本机连得上 SolidWorks。

**同一个机器上不要同时起多个 SolidWorks MCP。** 服务内部用全局锁串行执行 COM 调用，多进程抢同一个 COM 连接会死锁。

## 四、四种用法

| 入口 | 适合什么 | 怎么开始 |
|---|---|---|
| MCP Server | 你已经在用支持 MCP 的客户端，想让模型直接操作 SolidWorks | `python mcp-server\server.py`，由客户端作为子进程拉起 |
| Skill | 客户端支持导入 skill 包 | 把仓库根目录作为一个 skill 加载，见 [SKILL.md](SKILL.md) |
| 桌面端 | 想要图形界面：项目、任务队列、评审、预览、交付包 | [apps/workbench-ui](apps/workbench-ui)（React + Tauri，正式客户端，自带 Rust 后端 23 个命令；需自行 `npm install` 与 `cargo build`）· [apps/desktop](apps/desktop)（PySide6 原型，CAD 执行是 mock，只用来看界面设计） |
| DSH preset | 用 DSH，且希望一个会话里直接拿到全部 544 个工具 | `python -B tools\dsh-preset\install_preset.py --apply`，见 [docs/dsh-preset-sw-engineer.md](docs/dsh-preset-sw-engineer.md) |

> 桌面端的任务执行走它自己的本地 worker（通过 `codex` 命令行），**不经过 MCP Server**，两条路是并行的入口。想用同一套能力跑批处理，走 MCP；想要界面管理任务与交付包，走桌面端。

### 从零试一个零件

```text
1. 起 MCP 服务，客户端里确认能列出 solidworks_* 工具
2. 让模型先跑 solidworks_read_document_units，确认文档单位
3. 建草图 → 加约束 → 拉伸 → 回读体积和包围盒
4. 需要图纸时再建视图与标注
```

每一步的返回值里都带读数（体积、包围盒、实体数、草图约束状态）。看读数，不要只看调用成功。

## 五、能力范围与边界

`capabilities.yaml` 是能力的唯一真源，每条都标了等级：

| 等级 | 含义 | 当前 |
|---|---|---|
| `verified` | 有本机真机运行证据 | 100 条 |
| `stitched` | 实现按官方签名写好，缺自有运行证据 | 38 条 |
| `not_implemented` | 明确没做 | 2 条 |

受控 `pilot` 的域（配置族、钣金 U 型轮廓法兰与展开 DXF、HSS 矩形焊接框架与切割清单、Simulation/FEA、Routing、复杂曲面、模具）在清单里逐条标注，不当作原生完整交付。`stitched` 的条目能用，但结果需要你自己复核。

## 六、目录结构

| 路径 | 内容 |
|---|---|
| `mcp-server/` | MCP 服务与工具声明（`server.py`、`tool_registry.py`、`tool_specs_batch*.py`） |
| `scripts/` | 能力实现，一个域一个模块（`sw_part.py`、`sw_assembly.py`、`sw_drawing.py` 等） |
| `tools/` | 命令行工具：真机护栏 `guard_run.py`、各种探针与生成器 |
| `docs/` | 知识库与说明文档 |
| `tests/` | 测试 |
| `apps/` | 桌面端 |
| `references/`、`subskills/`、`examples/` | 参考资料、子技能、示例 |
| `AI Solidworks/` | 本机官方文档、模型、截图工作区（不入库） |

## 七、参考与致谢

项目起步时通读过一批公开的 SolidWorks 自动化项目，读它们的接口封装、测试分层、错误处理和对官方 API 的理解，用来判断哪些路走得通、哪些是死路。下面按用途列出调研过的项目。许可一栏是 2026-11 逐个读各仓库里的 `LICENSE` 文件核出来的，不是看 README 徽章。

**用到了代码或设计**

| 项目 | 许可 | 参考了什么 |
|---|---|---|
| `wzyn20051216/solidworks-automation-skill` | MIT | 本项目的最初来源。`mcp-server/server.py` 原样保留（45 个工具实现），49 个 `scripts/*.py` 模块与 `subskills/` 在此基础上继续做 |
| `microsoft/UFO` | MIT | 配置驱动的 GUI 输入层设计（`input_text_api`、`input_text_enter`、`input_text_inter_key_pause`），用于 `sw_gui_input.py` 与 `sw_jlcfa_fill.py`。模式借自它，代码是自己写的 |
| `Eduardof0nt/Solidworks-MCP-Server` | MIT | 模具域该有哪两个动作（分型线、补孔面）。它的方法名在官方类型库里查不到，所以只取思路，实现照官方签名写 |

**评估过、未并入代码**

| 项目 | 许可 | 参考了什么 |
|---|---|---|
| `andrewbartels1/SolidworksMCP-python` | MIT | 工具分组与参数组织的对照 |
| `vespo92/SolidworksMCP-TS` | MIT | `mock-solidworks-adapter` 的测试分层、macro-generator、若干 `.vba` 样例 |
| `Slacker-LLC/solidworks-mcp` | Apache-2.0 | 工具覆盖范围的对照。未并入，故其 NOTICE 义务尚未触发 |

**调研与交叉验证**

| 项目 | 许可 | 参考了什么 |
|---|---|---|
| `xarial/codestack` | MIT | 建视图、文档操作、装配、导入导出，以及故障分类 |
| `angelsix/solidworks-api` | MIT | SolidDNA 模板思路（免弹模板设置） |
| `deloarts/pyswx` | MIT | 类型库封装的组织方式 |
| `painezeng/CSharpAndSolidWorks` | MIT | 几何算法（自交、凸性、面积）与测试件 |
| `alisamsam/Solidworks-MCP` | MIT | 27 个 `.vbs` 语料，用于核对 VBScript 侧写法 |
| `delancy827/solidworks-skills` | MIT | 参数个数的独立交叉验证 |
| `djlex83/solidworks-automation-skill` | MIT | `VARIANT(VT_DISPATCH, None)` 的简洁写法 |
| `Sakikooooo/solidworks-auto-modeling` | MIT | `Nothing`（标量 Dispatch）与 `Empty`（Variant）的区分 |
| `Mochaxgcc/solidworks-ai-bridge` | MIT | 位置参数传递方式的佐证 |
| `guoleizhen717/solidworks-api-skill` | MIT | 反例：它说的「参数超过 12 个会失败」不成立 |
| `ZiChen-Ni/solidworks-com-automation-skill` | MIT | 最小 COM 封装与 Windows 安装脚本 |
| `just1step/solidworks-mcp` | MIT | 工具覆盖范围的对照 |
| `Cai-aa/CAD-Agent-Hub` | MIT | Agent 与 CAD 协作的组织方式 |
| `kalyanpi4/pySW` | GPL-2.0 | 只读思想，未抄代码 |
| `eyfel/mcp-server-solidworks`（SolidPilot） | AGPL | 只读思想，未抄代码。其分支 `Bennyco86/q3ds-solidworks-mcp` 同为 AGPL |
| `pedropaulovc/offline-solidworks-api-docs` | 无许可 | 只读流水线思路。本机官方文档库的整理方式受其启发，产物不随本仓库分发 |
| `pengxiaoan/solidworks-build-mechanical-models` | 无许可 | 只读思想 |
| `walterkken/doc-driven-engineering-software-skills` | 全版权保留 | 只借鉴「文档驱动目录结构」这一条方法论 |

SolidWorks API 帮助与官方示例是日常依据，用来核对签名、Remarks 和调用顺序。它们不是开源项目，这里只作说明。

以上项目的作者和维护者让这些经验可以被读到，这个项目因此少走了不少弯路，在此致谢。若上表的许可判定或归属有误，请提 issue，会按实际情况改正。

## 八、许可

MIT，见 [LICENSE](LICENSE)。第三方代码与许可义务见 [THIRD-PARTY-NOTICES.md](THIRD-PARTY-NOTICES.md)。
