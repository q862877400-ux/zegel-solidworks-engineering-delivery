# 步骤做法矩阵（由 `scripts/gen_survey_matrix.py` 生成，勿手改）

分母：`31` 张已带 tag 的卡片（来源：同目录 `architecture-matrix.md`）。

### 编排（E4/E7）

| 做法 | 项目数 | 谁 |
|---|---|---|
| single | 20 | cad-coder, cad-recode, cadrille, deepcad, drawing2cad, flexcad, freecad-mcp, fusion360-mcp-server, hunyuan3d-2, img2cad, instantmesh, plankassembly, sky-001, spar3d, stable-fast-3d, step1x-3d, text2cad, trellis, triposg, triposr |
| loop | 8 | agentcad, amagine3d, blender-mcp, build123d-mcp, cad-assistant, cadam, earthtojake-text-to-cad, mcp-cadquery |
| none | 2 | autocad-mcp, cadquery-llm-skill |
| multi-agent | 1 | multi-agent-cad |

### 验证（E6）

| 做法 | 项目数 | 谁 |
|---|---|---|
| visual | 13 | blender-mcp, cad-assistant, cadam, freecad-mcp, hunyuan3d-2, instantmesh, multi-agent-cad, spar3d, stable-fast-3d, step1x-3d, trellis, triposg, triposr |
| numeric | 11 | agentcad, cad-coder, cad-recode, cadrille, deepcad, drawing2cad, flexcad, fusion360-mcp-server, img2cad, sky-001, text2cad |
| run-only | 3 | autocad-mcp, build123d-mcp, mcp-cadquery |
| dfm-rules | 1 | earthtojake-text-to-cad |
| export-readback | 1 | amagine3d |
| geometry-gate | 1 | plankassembly |
| none | 1 | cadquery-llm-skill |

### 交付（E8）

| 做法 | 项目数 | 谁 |
|---|---|---|
| mesh | 13 | blender-mcp, cadam, cadrille, hunyuan3d-2, img2cad, instantmesh, plankassembly, spar3d, stable-fast-3d, step1x-3d, trellis, triposg, triposr |
| STEP | 10 | agentcad, amagine3d, build123d-mcp, cad-assistant, cad-coder, cad-recode, earthtojake-text-to-cad, fusion360-mcp-server, mcp-cadquery, multi-agent-cad |
| none | 4 | cadquery-llm-skill, drawing2cad, freecad-mcp, sky-001 |
| sequence | 3 | deepcad, flexcad, text2cad |
| drawing | 1 | autocad-mcp |

### 中间表示（E2）

| 做法 | 项目数 | 谁 |
|---|---|---|
| code | 13 | agentcad, amagine3d, blender-mcp, build123d-mcp, cad-assistant, cad-coder, cad-recode, cadam, cadquery-llm-skill, cadrille, earthtojake-text-to-cad, mcp-cadquery, multi-agent-cad |
| mesh | 8 | hunyuan3d-2, instantmesh, spar3d, stable-fast-3d, step1x-3d, trellis, triposg, triposr |
| sequence | 8 | autocad-mcp, deepcad, drawing2cad, flexcad, img2cad, plankassembly, sky-001, text2cad |
| feature-tree | 2 | freecad-mcp, fusion360-mcp-server |

