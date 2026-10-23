# 步骤做法矩阵（由 `scripts/gen_survey_matrix.py` 生成，勿手改）

分母：`13` 张已带 tag 的卡片（来源：同目录 `architecture-matrix.md`）。

### 编排（E4/E7）

| 做法 | 项目数 | 谁 |
|---|---|---|
| loop | 7 | agentcad, amagine3d, blender-mcp, build123d-mcp, cadam, earthtojake-text-to-cad, mcp-cadquery |
| single | 3 | freecad-mcp, fusion360-mcp-server, sky-001 |
| none | 2 | autocad-mcp, cadquery-llm-skill |
| multi-agent | 1 | multi-agent-cad |

### 验证（E6）

| 做法 | 项目数 | 谁 |
|---|---|---|
| visual | 4 | blender-mcp, cadam, freecad-mcp, multi-agent-cad |
| numeric | 3 | agentcad, fusion360-mcp-server, sky-001 |
| run-only | 3 | autocad-mcp, build123d-mcp, mcp-cadquery |
| dfm-rules | 1 | earthtojake-text-to-cad |
| export-readback | 1 | amagine3d |
| none | 1 | cadquery-llm-skill |

### 交付（E8）

| 做法 | 项目数 | 谁 |
|---|---|---|
| STEP | 7 | agentcad, amagine3d, build123d-mcp, earthtojake-text-to-cad, fusion360-mcp-server, mcp-cadquery, multi-agent-cad |
| none | 3 | cadquery-llm-skill, freecad-mcp, sky-001 |
| mesh | 2 | blender-mcp, cadam |
| drawing | 1 | autocad-mcp |

### 中间表示（E2）

| 做法 | 项目数 | 谁 |
|---|---|---|
| code | 9 | agentcad, amagine3d, blender-mcp, build123d-mcp, cadam, cadquery-llm-skill, earthtojake-text-to-cad, mcp-cadquery, multi-agent-cad |
| feature-tree | 2 | freecad-mcp, fusion360-mcp-server |
| sequence | 2 | autocad-mcp, sky-001 |

