## ★★ 规格 211 · B8 收口（21 项逐项结论表）

> ★★★ **这张表由 `tools/gen_spec211_final_table.py` 从两处机器可读来源合成**：
> ★ ① `tools/spec211_manual_verdicts.py`（★ 21 项**人工终判**）· ★ ② `capabilities.yaml`（★ `level` + `evidence`）
> ★★ **不手写** —— ★ 手写会与真源脱节；
> ★★★ **本文件是唯一「给人看的」落点** ✗（★ 早先它在 `output/` 与 `specs/` **各有一份**
> ⇒ ★ **实测漂移过**：★ 一边已改、★ 一边仍旧 ✓）

| 域 | 项 | 台账终判 | 能力 id | 能力 level | 真机证据 |
|---|---|---|---|---|---|
| 其他 | PDM | **不做** | — | — | — |
| 曲面 | 剪裁曲面 | **不做** | — | — | — |
| 曲面 | 扫描曲面 | **可做** | `sweep_surface` | `verified` | ★ 有 |
| 曲面 | 边界曲面 | **不做** | — | — | — |
| 焊件 | 圆角焊缝 | **可做** | `fillet_weld_bead` | `stitched` | ★ 有 |
| 焊件 | 焊接符号 | **可做** | `weld_symbol` | `verified` | ★ 有 |
| 焊件 | 裁剪/延伸焊件 | **可做** | `weldment_trim` | `stitched` | ★ 有 |
| 焊件 | 角撑板（焊件） | **可做** | `weldment_gusset` | `stitched` | ★ 有 |
| 特征 | 曲线驱动阵列 | **不做** | `curve_driven_pattern` | `stitched` | ★ 有 |
| 特征 | 特征识别/Instant3D | **不做** | — | — | — |
| 特征 | 缩放/变形 | **可做** | `scale_feature` | `verified` | ★ 有 |
| 特征 | 边界凸台 | **不做** | — | — | — |
| 装配 | SpeedPak | **可做** | `speedpak` | `verified` | ★ 有 |
| 装配 | 序列 / 说明书（Assembly Visualization） | **不做** | — | — | — |
| 装配 | 爆炸直线 | **可做** | `explode_line_sketch` | `verified` | ★ 有 |
| 装配 | 装配体性能分析 | **不做** | — | — | — |
| 装配 | 零部件阵列 | **不做** | — | — | — |
| 评估 | 截面属性 | **可做** | `section_properties` | `stitched` | ★ 有 |
| 钣金 | 展开/折叠 | **已覆盖** | — | — | — |
| 钣金 | 平板型式/导出 DXF | **不做** | — | — | — |
| 钣金 | 成形工具 | **可做** | `forming_tool` | `verified` | ★ 有 |
