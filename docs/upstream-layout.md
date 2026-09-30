# 上游仓库结构（对照参考）

> 来源：工作副本 `C:\swprojects\sw-skill-fork\`（remote `wzyn20051216/solidworks-automation-skill`，390 个上游文件，MIT）；只读对照克隆在 `C:\swprojects\sw-automation-skill\`（395 文件）。

```
solidworks-automation-skill/
├─ SKILL.md                    ← 主技能入口
├─ capabilities.yaml           ← 能力真源：原子操作 → 后端映射，每条带 level / provenance
├─ golden-workflows.yaml       ← 黄金工作流
├─ agents/  ai_team/           ← 智能体定义
├─ apps/desktop/               ← 桌面工作台（cad_workbench/）
├─ docs/                       ← 说明与生成物：union-conventions.md / union-coverage-matrix.md
│                                / capability-matrix.md / gap-analysis.md / signature-audit.md
│                                / harvest-report.md
├─ mcp-server/server.py        ← MCP 服务
├─ references/                 ← 知识文档（language-backend-routing / troubleshooting / export …）
├─ scripts/                    ← 能力实现主战场，命名 sw_<域>.py
├─ subskills/                  ← autocad / 工程图 / 圆角倒角 CNC / 螺纹孔 / vibecad
├─ tests/                      ← 80+ 测试
├─ tools/                      ← 来源与地图构建：build_union_sources.py / build_union_map.py
│                                / union-sources.json
└─ requirements{,-mesh,-occt,-pdf}.txt
```

`scripts/` 已有能力模块（补全前先看是否已存在）：`sw_connect sw_preflight sw_session sw_part sw_assembly sw_drawing sw_motion sw_sheet_metal sw_weldment sw_export sw_gear sw_hole_features sw_appearance sw_delivery sw_review sw_document_data sw_entity_reference sw_import_mesh_reference sw_macro_guard sw_diagnostics sw_addin_host sw_capability_probe backend_router capabilities fea_analysis fea_convergence advanced_geometry advanced_geometry_ocp advanced_surface_ocp headless_cad_writer headless_occt_service dxf_preview_scene dfm_review dfm_profiles drawing_spec routing_review cad_studio cad_doctor cad_diagnostics cad_installation stability_regression release_check`。

新增模块的落位参考（约束来源是 AGENTS.md 铁律 3 的顶层白名单）：

- 命名 `sw_<功能域>.py`，与既有并列；顶部 docstring 写清能力域、对应官方接口族、移植来源、许可。
- 顶部 import 照抄 `sw_connect.py` 的依赖解析模式（`try: from .x import / except ImportError: from x import`）。
- 涉及选中的操作，一律复用 `sw_part._select_by_id` / `sw_connect.get_com_member`，不裸写 `SelectByID2`，不裸写 `getattr(obj, name)()`。
- 补 `tests/test_<模块名>.py`（静态可跑：mock adapter，不连 SolidWorks）。
