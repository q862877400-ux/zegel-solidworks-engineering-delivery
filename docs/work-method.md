# 工作方法

> 从 `AGENTS.md` 搬出。根指令文件只留摘要 + 链接。

## 一、施工顺序：S0–S6，判据先行

逐条定义、完成标准与停线条件见 [`ENGINEERING-PATH.md`](ENGINEERING-PATH.md) 第六节。要点：

| 步 | 一句话 |
|---|---|
| **S0** | 恢复首件所需的正式通路，冻结可复现基线 |
| **S1** | 先做 E1–E7 的验收规范与坏样件，再谈新能力 |
| **S2** | 冻结首件需求和最小规则包，把知识变成执行义务 |
| **S3** | 做成原生可编辑的板件参数族，真过 E1–E3 |
| **S4** | 把装配、图样与工艺接上，完成首个 E1–E7 交付包 |
| **S5** | 真实 DeepSeek 端到端、修改与中断试验 |
| **S6** | 限定发布、重复验证，再扩展交付族 |

同一时刻只展开一个交付族；所有真机工作串行。

## 二、开工三问

每个任务开工前必须回答：

1. 服务哪个首件要求？
2. 改善哪条 E（E1–E7）？
3. 增加哪个可重复试验？

答不出就不进当前迭代。

## 三、方法包的内部五步

扩展一个方法包时的动作：

1. **建全景与对差**：`sw_know.py domain --list` 拿 14 个域，`swdoc.ps1` + 反射补
   `cosworks`/Routing/Costing/PDM，对照上游 `capabilities.yaml` + `scripts/` + `subskills/`
   建 [`capability-matrix.md`](capability-matrix.md) 与 [`gap-analysis.md`](gap-analysis.md)
   （从零建表，不预设缺口结论）。
2. **找来源**：按优先级取素材——上游相邻模块 > MIT 项目现成实现 > MIT 项目文档/示例 >
   Apache-2.0 项目实现（带 NOTICE）> 只读思想（AGPL/GPL/无许可，绝不抄文本）> 照官方签名自建。
3. **归一**：按「并入六条规则」改造，命名/单位/选择/验证等级/出处五统一。
4. **标等级与出处**：`capabilities.yaml` 每条给 `level`（五级）与
   `provenance{repo, license, files, upstream_verified}`。
5. **门禁与实测**：`check_union_conventions.py` → `python -m compileall -q scripts subskills` →
   逐 COM 调用与官方签名对齐（[`signature-audit.md`](signature-audit.md)）→ 本机实测；
   缺我们自己的运行证据的条目留在 `stitched`。

## 四、判据优先去开源项目里找

先去四家找现成判据，找不到再自己搓。见 [`evidence-first.md`](evidence-first.md)。

## 五、产出落点

| 产出 | 落点 |
|---|---|
| 规则包 | `scripts/engineering/rules.py` · `manufacturing_rules.py` · `rule_service.py` |
| 方法包 | `scripts/engineering/compiler.py` · `registry.py` · `expand.py` · 各 `sw_*.py` 实现 |
| 验收包 | `scripts/engineering/drawing_obligations.py` · `compliance.py` · 新增的 E1–E7 检查器 |
| 现状读数 | `docs/state/facts/` + `docs/state/inventory-*.json` |
| 历史归档 | `docs/history/`（不再维护，只作追溯） |
