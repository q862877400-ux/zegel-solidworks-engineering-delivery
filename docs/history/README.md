# 历史归档

> **本目录不再维护，只作追溯。** 里面的文件是过去的交接、计划、报告与一次性产物；
> 它们记录「当时怎么想的」，不是「现在该做什么」。
>
> 当前项目定义看 [`../PROJECT-CHARTER.md`](../PROJECT-CHARTER.md)；
> 路线与施工顺序看 [`../ENGINEERING-PATH.md`](../ENGINEERING-PATH.md)；
> 现状读数看 [`../state/INDEX.md`](../state/INDEX.md)。

---

## 为什么归档

2026-10 的文档梳理把 `docs/` 根目录从 137 个文件收敛到 67 个。
归档判据（四类互斥，按此顺序判定）：

1. **GENERATED**：有生成器、且被新鲜度门禁守着 —— 留在 `docs/`。
2. **LIVE**：被 `AGENTS.md` 链接 / 被代码实际 `read_text` 读取 / 是门禁判据来源 /
   承载当前项目定义 —— 留在 `docs/`。
3. **DATA**：纯机器读数且无人读内容 —— 留在 `docs/`。
4. **HISTORY**：只被别的历史文档引用，或只被代码注释提一句当出处，或内容已并入别的文档
   —— 进本目录。

分类结果与逐条判据见 [`../state/facts/R-engineering-path.md`](../state/facts/R-engineering-path.md) R-17。

## 目录结构

| 子目录 | 内容 |
|---|---|
| `./` | 旧交接（`HANDOFF-*`、`AGENTS-*`）· 旧计划（`plan-*`）· 旧报告（`milestone-*`、`final-*`、`weekly-*`）· 旧提案与调研（`proposal-*`、`research-*`、`market-*`）· 一次性盘点（`spec2xx-*`、`t003-*`） |
| `engineering/` | 2026-10-08 那一批工程系统施工方案：原架构方案、EC00–EC12 施工总计划、P0 五份草案、40 路并行准备三份 |

## 引用约定

- 归档文件**仍可被引用**，但引用路径要写成 `docs/history/<file>`。
- 归档文件里的数字与结论**不随仓库演进**，不得当作当前读数使用。
- 需要「当时为什么这么决定」时读这里；需要「现在是什么状态」时读 `../state/`。

## 明确不归档的内容

`docs/state/`（实测台账）、`docs/survey/`（外部调研与卡片）、`docs/recon/`、
`docs/recon-206/`、`docs/recon-207/` 是**取证数据集**，被门禁与来源块逐行引用，
删了会断链，整块保留。
