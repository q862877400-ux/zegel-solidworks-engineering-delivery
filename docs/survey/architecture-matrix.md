# 架构分类矩阵（由 `scripts/gen_survey_matrix.py` 生成，勿手改）

卡片 31 张：带机读 tag 31 张 · 待补 0 张。

| 项目 | 类 | 表示 | 编排 | 验证 | 交付 | 证据 | 卡片（出处）|
|---|---|---|---|---|---|---|---|
| agentcad | B | code | loop | numeric | STEP | 读码 | `docs/survey/cards/agentcad.md` |
| Amagine3D（amagine-ai） | B | code | loop | export-readback | STEP | 读码 | `docs/survey/cards/amagine3d.md` |
| CAD-Assistant | B | code | loop | visual | STEP | 读码 | `docs/survey/cards/cad-assistant.md` |
| CADAM | B | code | loop | visual | mesh | 实测 | `docs/survey/cards/cadam.md` |
| text-to-cad（earthtojake） | B | code | loop | dfm-rules | STEP | 读码 | `docs/survey/cards/earthtojake-text-to-cad.md` |
| mcp-cadquery | B | code | loop | run-only | STEP | 读码 | `docs/survey/cards/mcp-cadquery.md` |
| Multi-Agent-CAD / MAC（Pan-Chera） | C | code | multi-agent | visual | STEP | 读码 | `docs/survey/cards/multi-agent-cad.md` |
| DeepCAD | D | sequence | single | numeric | sequence | 读码 | `docs/survey/cards/deepcad.md` |
| Drawing2CAD | D | sequence | single | numeric | none | 读码 | `docs/survey/cards/drawing2cad.md` |
| FlexCAD | D | sequence | single | numeric | sequence | 读码 | `docs/survey/cards/flexcad.md` |
| PlankAssembly | D | sequence | single | geometry-gate | mesh | 读码 | `docs/survey/cards/plankassembly.md` |
| Text2CAD | D | sequence | single | numeric | sequence | 读码 | `docs/survey/cards/text2cad.md` |
| Hunyuan3D-2 | E | mesh | single | visual | mesh | 读码 | `docs/survey/cards/hunyuan3d-2.md` |
| InstantMesh | E | mesh | single | visual | mesh | 读码 | `docs/survey/cards/instantmesh.md` |
| SPAR3D | E | mesh | single | visual | mesh | 读码 | `docs/survey/cards/spar3d.md` |
| Stable Fast 3D | E | mesh | single | visual | mesh | 读码 | `docs/survey/cards/stable-fast-3d.md` |
| Step1X-3D | E | mesh | single | visual | mesh | 读码 | `docs/survey/cards/step1x-3d.md` |
| TRELLIS | E | mesh | single | visual | mesh | 读码 | `docs/survey/cards/trellis.md` |
| TripoSG | E | mesh | single | visual | mesh | 读码 | `docs/survey/cards/triposg.md` |
| TripoSR | E | mesh | single | visual | mesh | 读码 | `docs/survey/cards/triposr.md` |
| CAD-Coder（`anniedoris/CAD-Coder`） | F | code | single | numeric | STEP | 读码 | `docs/survey/cards/cad-coder.md` |
| CAD-Recode（`filaPro/cad-recode`） | F | code | single | numeric | STEP | 读码 | `docs/survey/cards/cad-recode.md` |
| cadrille（`AIRI-Institute/cadrille`） | F | code | single | numeric | mesh | 读码 | `docs/survey/cards/cadrille.md` |
| Img2CAD | F | sequence | single | numeric | mesh | 读码 | `docs/survey/cards/img2cad.md` |
| autocad-mcp（puran-water/autocad-mcp） | H | sequence | none | run-only | drawing | 读码 | `docs/survey/cards/autocad-mcp.md` |
| mcp-for-blender（原名 blender-mcp） | H | code | loop | visual | mesh | 读码 | `docs/survey/cards/blender-mcp.md` |
| build123d-mcp | H | code | loop | run-only | STEP | 读码 | `docs/survey/cards/build123d-mcp.md` |
| FreeCAD MCP（neka-nat/freecad-mcp） | H | feature-tree | single | visual | none | 读码 | `docs/survey/cards/freecad-mcp.md` |
| faust-machines/fusion360-mcp-server | H | feature-tree | single | numeric | STEP | 实测 | `docs/survey/cards/fusion360-mcp-server.md` |
| cadquery-llm-skill | I | code | none | none | none | 读码 | `docs/survey/cards/cadquery-llm-skill.md` |
| SKY-001（Skyfall AI） | J | sequence | single | numeric | none | 元数据 | `docs/survey/cards/sky-001.md` |

## 类的口径

- **A**：代码单发（写脚本 → 执行一次）
- **B**：代码回环（写 → 执行 → 读错 → 重写）
- **C**：多智能体编排
- **D**：序列 / DSL 专模
- **E**：生成式网格
- **F**：逆向（图 / 点云 / 图纸 → 代码）
- **G**：模板 + 参数 + 规则
- **H**：GUI / API 代理（改既有模型）
- **I**：知识 / 检索助手（不出几何）
- **J**：世界模型 / 几何状态预测
