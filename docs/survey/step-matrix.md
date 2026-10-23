# 步骤做法矩阵（由 `scripts/gen_survey_matrix.py` 生成，勿手改）

分母：`42` 张已带 tag 的卡片（来源：同目录 `architecture-matrix.md`）。

### 编排（E4/E7）

| 做法 | 项目数 | 谁 |
|---|---|---|
| single | 23 | cad-coder, cad-recode, cadrille, deepcad, drawing2cad, flexcad, freecad-mcp, fusion360-mcp-server, hunyuan3d-2, img2cad, instantmesh, meshy, plankassembly, rodin, sky-001, spar3d, stable-fast-3d, step1x-3d, text2cad, trellis, tripo, triposg, triposr |
| loop | 10 | agentcad, amagine3d, blender-mcp, build123d-mcp, cad-assistant, cadam, earthtojake-text-to-cad, leo-ai, mcp-cadquery, zoo-text-to-cad |
| none | 4 | autocad-mcp, cadquery-llm-skill, onshape-ai-advisor, siemens-nx-ai |
| human-approve | 3 | adam-cad-copilot, fusion-assistant, spline-ai |
| multi-agent | 1 | multi-agent-cad |
| template | 1 | ptc-creo-generative |

### 验证（E6）

| 做法 | 项目数 | 谁 |
|---|---|---|
| visual | 19 | blender-mcp, cad-assistant, cadam, freecad-mcp, fusion-assistant, hunyuan3d-2, instantmesh, meshy, multi-agent-cad, rodin, spar3d, spline-ai, stable-fast-3d, step1x-3d, trellis, tripo, triposg, triposr, zoo-text-to-cad |
| numeric | 11 | agentcad, cad-coder, cad-recode, cadrille, deepcad, drawing2cad, flexcad, fusion360-mcp-server, img2cad, sky-001, text2cad |
| run-only | 4 | adam-cad-copilot, autocad-mcp, build123d-mcp, mcp-cadquery |
| none | 3 | cadquery-llm-skill, onshape-ai-advisor, siemens-nx-ai |
| dfm-rules | 2 | earthtojake-text-to-cad, leo-ai |
| export-readback | 1 | amagine3d |
| geometry-gate | 1 | plankassembly |
| solver | 1 | ptc-creo-generative |

### 交付（E8）

| 做法 | 项目数 | 谁 |
|---|---|---|
| mesh | 18 | blender-mcp, cadam, cadrille, hunyuan3d-2, img2cad, instantmesh, meshy, plankassembly, ptc-creo-generative, rodin, spar3d, spline-ai, stable-fast-3d, step1x-3d, trellis, tripo, triposg, triposr |
| STEP | 12 | agentcad, amagine3d, build123d-mcp, cad-assistant, cad-coder, cad-recode, earthtojake-text-to-cad, fusion360-mcp-server, leo-ai, mcp-cadquery, multi-agent-cad, zoo-text-to-cad |
| none | 8 | adam-cad-copilot, cadquery-llm-skill, drawing2cad, freecad-mcp, fusion-assistant, onshape-ai-advisor, siemens-nx-ai, sky-001 |
| sequence | 3 | deepcad, flexcad, text2cad |
| drawing | 1 | autocad-mcp |

### 中间表示（E2）

| 做法 | 项目数 | 谁 |
|---|---|---|
| code | 14 | agentcad, amagine3d, blender-mcp, build123d-mcp, cad-assistant, cad-coder, cad-recode, cadam, cadquery-llm-skill, cadrille, earthtojake-text-to-cad, mcp-cadquery, multi-agent-cad, zoo-text-to-cad |
| mesh | 13 | hunyuan3d-2, instantmesh, meshy, ptc-creo-generative, rodin, spar3d, spline-ai, stable-fast-3d, step1x-3d, trellis, tripo, triposg, triposr |
| sequence | 8 | autocad-mcp, deepcad, drawing2cad, flexcad, img2cad, plankassembly, sky-001, text2cad |
| feature-tree | 6 | adam-cad-copilot, freecad-mcp, fusion-assistant, fusion360-mcp-server, leo-ai, siemens-nx-ai |
| none | 1 | onshape-ai-advisor |

