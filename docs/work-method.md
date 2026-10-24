# 工作方法（并入五步）

> 从 `AGENTS.md` §五 搬出（2026-10-24），逐字保留。

1. 建全景与对差：`sw_know.py domain --list`拿 14个域，`swdoc.ps1` + 反射补`cosworks`/Routing/Costing/PDM，对照上游`capabilities.yaml` + `scripts/` + `subskills/`建`docs/capability-matrix.md`与`docs/gap-analysis.md`（从零建表，不预设缺口结论）。
2. 找来源：按优先级取素材——上游相邻模块 > MIT 项目现成实现 > MIT 项目文档/示例 > Apache-2.0 项目实现（带 NOTICE）> 只读思想（AGPL/GPL/无许可，绝不抄文本）> 照官方签名自建。
3. 归一：按「并入六条规则」改造，命名/单位/选择/验证等级/出处五统一。
4. 标等级与出处：`capabilities.yaml`每条给`level`（五级）与`provenance{repo, license, files, upstream_verified}`。
5. 门禁与实测：`check_union_conventions.py` → `python -m compileall -q scripts subskills` → 逐 COM 调用与官方签名对齐（`docs/signature-audit.md`）→ 本机实测；缺我们自己的运行证据的条目留在`stitched`。

产出：`docs/capability-matrix.md`、`docs/gap-analysis.md`、`docs/signature-audit.md`、`docs/union-coverage-matrix.md`、`docs/harvest-report.md`。判据优先去开源项目里找（先去四家找现成判据，找不到再自己搓）见 [docs/evidence-first.md](docs/evidence-first.md)。
