# Implementation Plan: P3 · 并入模板定型（焊件域）

**Feature**: `002-merge-weldment` · **Spec**: [spec.md](spec.md) · **Created**: 2026-10-01

## Summary

把焊件域按**官方签名**实现进本仓库，并借此**定型 P3 的并入模板**。
来源的 4/5 个方法名在官方反射里查不到 ⇒ **引用思路、用官方签名实现**。

## Technical Context

| 项 | 值 |
|---|---|
| 语言 / 运行时 | Python 3.14 + pywin32（迟到绑定） |
| 代码落点 | `C:\swprojects\sw-skill-fork\scripts\sw_weldment.py`（**新模块**） |
| 测试落点 | `C:\swprojects\sw-skill-fork\tests\test_sw_weldment_contract.py`（**新文件**） |
| 能力登记 | `C:\swprojects\sw-skill-fork\capabilities.yaml`（**新增条目，或并入既有焊件条目**） |
| 来源 | `Eduardof0nt/Solidworks-MCP-Server`（MIT，`server.py` + `sw_client.py`） |
| 签名真源 | `D:\AI\SW\_raw\topo-sldworks\iface_sldworks.txt`（1032 接口 / 20627 成员） |
| 缺口地图 | `C:\swprojects\sw-skill-fork\docs\union-coverage-matrix.md` §五 的焊件节 |

**⚠ 本特性最大的风险不是技术，是**来源不可信**：它 0 测试文件、未声明验证环境，
  且 4/5 个方法名写错。⇒ **每一步都要回到反射核对**，不得「来源这么写就这么搬」。**

## Constitution Check

| 宪法条款 | 本特性如何满足 |
|---|---|
| §I 缝合优先 | 来源是**思路**的来源；实现照官方签名，不照来源的错名 |
| §II 签名三源互证 | 逐成员核 `iface_sldworks.txt` + `sw_api_sldworks.py` + CHM；已发现并记录 4 处冲突 |
| §III 查不到就写查不到 | `InsertGussetFeature` 的 `Int16` 参数语义查不到 ⇒ 标注不猜 |
| §IV 许可红线 | MIT ⇒ 保留版权声明（`Copyright (c) 2026 Eduardo Font Cruz`）；在 NOTICE 里登记 |
| §V 验收可跑 | SC-001..005 各给命令 |
| SDD 接口表 | tasks 每条带 `→ 验收:`；`level` 只能 `stitched` |

**一处需要注意**：本特性会让 `THIRD-PARTY-NOTICES.md` 里的这条发生变化 ——
四家从「**已评估但尚未并入**」变成「**已并入**」（至少 Eduardof0nt 一家）。
**必须同批更新该文件**（MIT 的版权声明义务）。

## Project Structure

```
C:\swprojects\sw-skill-fork\
├── scripts\sw_weldment.py                    ← 新增
├── tests\test_sw_weldment_contract.py        ← 新增
├── capabilities.yaml                         ← 改（新增/更新焊件条目）
├── THIRD-PARTY-NOTICES.md                    ← 改（四家从「未并入」迁到「已包含」）
└── docs\union-coverage-matrix.md             ← 改（焊件节标为已并入）

D:\AI\SW\
├── specs\002-merge-weldment\                 ← 本特性制品
└── _raw\source-defects\                      ← 新增：来源缺陷记录（可复核）
```

## 实施顺序

```
1. 逐成员核反射，定出「官方签名表」            ← 已完成（见 spec 的背景表）
2. 写 scripts\sw_weldment.py（照官方签名 + 项目既有模式 + 来源头注释）
3. 写契约测试（断言官方 arity 与参数类型）
4. 记录来源缺陷（可复核：来源写的 / 官方真名 / 核对命令）
5. 更新 capabilities.yaml + THIRD-PARTY-NOTICES.md + 缺口地图
6. 五项门禁 + 全量回归 + 两仓库 commit
```

## Complexity Tracking

| 决策 | 为什么不更简单 |
|---|---|
| **新建 `sw_weldment.py`** 而不是塞进 `sw_part.py` | 焊件是一个独立域（有自己的 ProfilePath / CutList / Gusset/EndCap 一族）；塞进零件模块会让它变成杂物间 |
| 选 `InsertStructuralWeldment` 而非带后缀版本 | 无后缀是最小签名（3 参），其余是它的扩展；先做最小面，扩展留待有需求时 |
| 来源缺陷单独记一份文件 | 后面 15 个域都会撞同类问题；把它做成**可复核的记录**，比每次重新发现便宜 |
| `level` 标 `stitched` 不标 `verified` | 来源未声明验证 + 我们未实测 ⇒ A7 禁止写成 verified |
