# 规格 208 · 计划（顺序 / 依赖 / 写盘边界）

> `spec.md` 定判据（SC）与决策（D）；本文件定**顺序**与**谁写哪里**；`tasks.md` 是 checklist。

## 一 · 阶段

| 阶段 | 做什么 | 出口判据 |
|---|---|---|
| **P0** | 沙盒复制收尾（代码已同提交）+ 记生产基线指纹 | SC-1 的「开工指纹」 |
| **P1** | ★ 落地 `mode: 'lean'`（11 个站点） | SC-2 · SC-3 · SC-4 |
| **P2** | 组装真工具目录（N ≥ 500） | SC-6 |
| **P3** | 造题（复用 207 的 145 项 + 自写冷门题） | 题集落盘且有 `task\expected_hint` |
| **P4** | 跑 5 条件对照 | SC-5 · SC-7 · SC-12 |
| **P5** | 我逐条判「能不能干活」 | SC-8 · SC-9 |
| **P6** | 报告交业主裁定 | SC-10 · SC-11 |
| **P7** | ★ **仅在业主判「合格」后**：日常 preset + 生产补丁 | 业主一句话 |

## 二 · ★★ 11 个站点清单（P1 的作业表，行号是**参考**不是约束）

`packages\core\tools\src\index.ts`：

| # | 站点 | 改成 |
|---|---|---|
| 1 | `ToolPresentationMode` 联合类型 | 加 `'lean'` |
| 2 | `Config` 的 zod union | 加 `'lean'` |
| 3 | 构造函数 `if (defaultMode !== 'native')` 注册两段 | lean 也注册（但要注册**目录段**而非 SDK 段） |
| 4 | `collapseSection()` 的 `=== 'ptc' ? … : ''` | lean 渲染空（**不变**，但要写注释说明为何空） |
| 5 | `sdkSection()`：`if (mode === 'native') return ''` + `requirePtcRuntime` | lean **分流**到新的 `catalogSection()`（**不**取 runtime） |
| 6 | 新增 `catalogSection()` | 渲染紧凑签名目录（新渲染器，见站点 10） |
| 7 | `presentAs()` 的 `if (mode !== 'native')` 加两段 | lean 加 **catalog 段 + 无 collapse 段** |
| 8 | `wireSchemas()`：`if (mode === 'native')` 与 `requirePtcRuntime(mode)` | lean **跳过** runtime 检查；返回**骨架投影**的全集 |
| 9 | `wireSchemas()` 的 `if (mode === 'ptc')` 尾部 | lean 走新分支：全部工具（骨架）+ **不**加 `run_code` |
| 10 | `schemaOf()` / 新增 `leanSchemaOf()` | 骨架投影：只留 `name\description(一句)\parameters{type:object,additionalProperties:true}` |
| 11 | `view()` 的 `if (modeFor(scope) !== 'native')` 注入 `run_code` | 改成 `=== 'ptc' \|\| === 'both'`（lean **不**注入） |

`packages\core\tools\src\ts-types.ts`（或新文件）：新增 `renderToolCatalog()` —— 紧凑签名目录。

★ **负例测试是必须的**（事实 62）：未知模式字面量被拒 + lean 下 `run_code` 不可见 + lean 不取 runtime。

## 三 · 写盘边界

| 允许写 | 禁止写 |
|---|---|
| `D:\AI\DSH-sandbox\**`（沙盒 harness 与 sandbox home） | ★ `D:\AI\DSH\deepseek-harness\**`（生产实例） |
| `D:\AI\SW\specs\208-lean-tool-surface\**` | ★ `C:\Users\Zegel\.dsh\**`（生产 home） |
| `D:\AI\SW\output\lean-tool-surface\**` | `D:\AI\SW` 的 `capabilities.yaml\scripts\tests\tools\门禁` |
| `D:\AI\SW\docs\recon\lean-tool-surface*.md` | 207 那两个规格目录的文件 |

## 四 · 依赖

```
P0 ─→ P1 ─→ P2 ─→ P3 ─→ P4 ─→ P5 ─→ P6 ─→ (业主判定) ─→ P7
              ↑
        P2 可与 P1 并行（目录只读，不依赖新模式）
```
