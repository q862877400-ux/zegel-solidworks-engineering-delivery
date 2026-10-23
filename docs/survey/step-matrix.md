# 步骤做法矩阵（由 `scripts/gen_survey_matrix.py` 生成，勿手改）

分母：`50` 张已带 tag 的卡片（来源：同目录 `architecture-matrix.md`）。

### 编排（E4/E7）

| 做法 | 项目数 | 谁 |
|---|---|---|
| single | 28 | cad-coder, cad-recode, cadrille, deepcad, drawing2cad, flexcad, freecad-mcp, fusion360-mcp-server, hunyuan3d-2, img2cad, instantmesh, meshy, openscad-mcp-server, plankassembly, rodin, sky-001, spar3d, stable-fast-3d, step1x-3d, sw-andrewbartels1, sw-eduardof0nt, sw-slacker-llc, sw-vespo92, text2cad, trellis, tripo, triposg, triposr |
| loop | 13 | agentcad, amagine3d, blender-mcp, build123d-mcp, cad-assistant, cadam, earthtojake-text-to-cad, freecad-ai, leo-ai, mcp-cadquery, rhinoai, slvsx-cli, zoo-text-to-cad |
| none | 4 | autocad-mcp, cadquery-llm-skill, onshape-ai-advisor, siemens-nx-ai |
| human-approve | 3 | adam-cad-copilot, fusion-assistant, spline-ai |
| multi-agent | 1 | multi-agent-cad |
| template | 1 | ptc-creo-generative |

### 验证（E6）

| 做法 | 项目数 | 谁 |
|---|---|---|
| visual | 20 | blender-mcp, cad-assistant, cadam, freecad-mcp, fusion-assistant, hunyuan3d-2, instantmesh, meshy, multi-agent-cad, rhinoai, rodin, spar3d, spline-ai, stable-fast-3d, step1x-3d, trellis, tripo, triposg, triposr, zoo-text-to-cad |
| numeric | 13 | agentcad, cad-coder, cad-recode, cadrille, deepcad, drawing2cad, flexcad, freecad-ai, fusion360-mcp-server, img2cad, sky-001, sw-slacker-llc, text2cad |
| run-only | 7 | adam-cad-copilot, autocad-mcp, build123d-mcp, mcp-cadquery, openscad-mcp-server, sw-andrewbartels1, sw-eduardof0nt |
| none | 4 | cadquery-llm-skill, onshape-ai-advisor, siemens-nx-ai, sw-vespo92 |
| dfm-rules | 2 | earthtojake-text-to-cad, leo-ai |
| solver | 2 | ptc-creo-generative, slvsx-cli |
| export-readback | 1 | amagine3d |
| geometry-gate | 1 | plankassembly |

### 交付（E8）

| 做法 | 项目数 | 谁 |
|---|---|---|
| mesh | 20 | blender-mcp, cadam, cadrille, hunyuan3d-2, img2cad, instantmesh, meshy, openscad-mcp-server, plankassembly, ptc-creo-generative, rodin, slvsx-cli, spar3d, spline-ai, stable-fast-3d, step1x-3d, trellis, tripo, triposg, triposr |
| STEP | 17 | agentcad, amagine3d, build123d-mcp, cad-assistant, cad-coder, cad-recode, earthtojake-text-to-cad, freecad-ai, fusion360-mcp-server, leo-ai, mcp-cadquery, multi-agent-cad, sw-andrewbartels1, sw-eduardof0nt, sw-slacker-llc, sw-vespo92, zoo-text-to-cad |
| none | 9 | adam-cad-copilot, cadquery-llm-skill, drawing2cad, freecad-mcp, fusion-assistant, onshape-ai-advisor, rhinoai, siemens-nx-ai, sky-001 |
| sequence | 3 | deepcad, flexcad, text2cad |
| drawing | 1 | autocad-mcp |

### 中间表示（E2）

| 做法 | 项目数 | 谁 |
|---|---|---|
| code | 15 | agentcad, amagine3d, blender-mcp, build123d-mcp, cad-assistant, cad-coder, cad-recode, cadam, cadquery-llm-skill, cadrille, earthtojake-text-to-cad, mcp-cadquery, multi-agent-cad, rhinoai, zoo-text-to-cad |
| mesh | 13 | hunyuan3d-2, instantmesh, meshy, ptc-creo-generative, rodin, spar3d, spline-ai, stable-fast-3d, step1x-3d, trellis, tripo, triposg, triposr |
| feature-tree | 11 | adam-cad-copilot, freecad-ai, freecad-mcp, fusion-assistant, fusion360-mcp-server, leo-ai, siemens-nx-ai, sw-andrewbartels1, sw-eduardof0nt, sw-slacker-llc, sw-vespo92 |
| sequence | 8 | autocad-mcp, deepcad, drawing2cad, flexcad, img2cad, plankassembly, sky-001, text2cad |
| constraint | 1 | slvsx-cli |
| dsl | 1 | openscad-mcp-server |
| none | 1 | onshape-ai-advisor |

