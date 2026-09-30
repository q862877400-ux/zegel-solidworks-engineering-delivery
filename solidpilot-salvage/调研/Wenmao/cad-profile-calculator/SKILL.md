---

name: cad-profile-calculator
description: 型材截面面积提取、米重计算与数据导出。当用户要求计算型材截面面积、从 CAD/DXF 图纸计算每米重量（米重/线密度）、导出型材重量数据，或提到 型材、截面、米重、线密度、DXF、铝型材重量、钢型材重量、截面面积计算 等关键词时应使用本技能。当用户提供 DXF 文件并希望提取工程属性时同样触发。
version: "2.0"
---



# 型材截面面积与米重计算

## Overview

从 CAD DXF 文件中提取型材截面轮廓，计算净截面面积和米重（kg/m），并导出数据报告。

**当前版本（skill v2.0）：**
- `profile_weight.py` **v11.31** — 型材米重主程序（核心计算 + CustomTkinter GUI + Excel/CSV/标注DXF 导出），来自小周工具箱，已补 CLI 入口（`python profile_weight.py <dxf> [--material/--density/--export]`）

> 旧 `profile_calc.py`(v8.5.0) / `gui_profile_calc.py`(v1.5.2) 已归档至 `history/`，其 CLI 核心能力由 `profile_weight.py` 的 CLI 入口继承。

**验证状态：** 68 型材全通过，与 AW 人工数据精确匹配。

版本历史详见 `CHANGELOG.md`，旧版归档于 `history/` 目录。

## Core Capabilities

### 1. 截面面积提取 (Python — profile_weight.py)

读取 DXF 文件，识别所有封闭截面轮廓，计算净面积：
- 单个封闭轮廓 → 面积即为该轮廓面积
- 多个轮廓（外轮廓 + 孔洞）→ 最大为外轮廓，其余为孔洞，**净面积 = 外轮廓面积 - 所有孔洞面积**
- 孔洞判定使用 point-in-polygon 算法（中心点是否在外轮廓内部）

**支持的 DXF 实体类型：**
- `LWPOLYLINE`（闭合多段线，含 bulge 弧段，三种闭合方式）
- `CIRCLE`（圆）
- `ELLIPSE`（完整椭圆）
- `HATCH`（填充边界 — PolylinePath，vertices + bulge 面积计算）
- `SOLID`（三角形）
- `ARC + LINE`（独立弧线+线段组成的截面 — Green 定理面积计算）

**三种闭合方式识别：**

| 类型 | 说明 | 识别条件 |
|------|------|----------|
| closed_lwpoly | 标准 closed=True 多段线 | LWPOLYLINE.closed == True |
| effectively_closed | 首尾重合但 closed=False | start 与 end 坐标差距 < 0.1mm |
| reconstructed | ARC+LINE 组成的闭合环 | 端点 snap + DFS 环检测 + Green 定理 |
| **unclosed (error)** | 未闭合多段线 | closed=False 且 gap >= 0.1mm → 强制闭合计算面积（source=implicit_closed），结果标记为"仅供参考"，错误写入 CSV / 标注 DXF |

**面积计算核心算法：**
- LWPOLYLINE: Shoelace + bulge 弧段修正（与 AutoCAD `vla-get-Area` 等价）
- HATCH PolylinePath: vertices + bulge 面积（注意：`path.edges` 属性不存在，只能用 `path.vertices`）
- ARC+LINE: Green 定理 `cross(A,C)+cross(C,B)+r^2*sweep`
- path_type_flags: bit 0=1 外部边界, bit 0=0 内孔

**Phase 2 碎片处理：**
- 连通分量 + LINE/ARC 端点匹配
- effectively_closed: close_if_needed 面积>0 的开口线作为独立轮廓
- gap ≤ 5mm → 归属附近闭合轮廓/独立闭合
- gap > 5mm → 拆碎入 fragment 池

**Phase 3 分组：**
- 50mm X 轴间距 Union-Find 聚类

**Phase 4 净面积计算：**
- is_hole = not (path_type_flags & 1)
- 外轮廓面积 − Σ孔洞面积
- 共享边/开口多段线 → 错误标记（不扣除，结果仅供参考）

### 2. 米重计算

公式：**米重 (kg/m) = 截面面积 (mm2) / 1,000,000 * 材料密度 (kg/m3)**

默认材料：6063铝合金（密度 2700 kg/m3）

可切换材料密度，参考 `references/material_density.md` 中的完整密度表。常用值：
- 6063铝合金 = 2700 kg/m3
- 7075铝合金 = 2810 kg/m3
- 2024铝合金 = 2780 kg/m3
- 碳钢通用 = 7850 kg/m3
- 304不锈钢 = 7930 kg/m3

## Script Usage

### Python 主程序（计算 + GUI + 导出，二合一）

脚本路径：`scripts/profile_weight.py`（来自小周工具箱 v11.31）

**GUI 模式（默认，省略参数）：**
```bash
python scripts/profile_weight.py
# 加载 DXF → 选择材质 → 计算 → 导出 Excel/标注DXF
```

**命令行模式（无界面，便于批量/自动化）：**
```bash
# 计算并打印结果（默认 6063 铝合金）
python scripts/profile_weight.py <dxf_file>

# 指定材料（名称见 references/material_density.md）
python scripts/profile_weight.py <dxf_file> --material "6063 铝合金"

# 自定义密度 kg/m3（优先于 --material）
python scripts/profile_weight.py <dxf_file> --density 7850

# 导出 Excel（.xlsx，三级状态色：绿=正常/黄=小问题/红=错误）
python scripts/profile_weight.py <dxf_file> --export xlsx

# 导出 CSV
python scripts/profile_weight.py <dxf_file> --export csv

# 导出标注 DXF（绿=正常/黄=小问题/红=错误）
python scripts/profile_weight.py <dxf_file> --export dxf
```

功能：
- 加载 DXF 文件，自动计算所有型材（核心算法与旧 profile_calc.py 一致：Shoelace + bulge 修正 + 孔洞扣减 + Green 定理 ARC + 未闭合强制闭合标记）
- 导出 Excel（含错误信息列、三级状态色）、CSV、标注 DXF
- GUI 红色高亮错误行，输出按 x 坐标从左到右排序

## Output Format

计算结果按图纸位置从左到右排列，格式：

```
#1: x=301.4 | 706.10 mm2 = 1.9065 kg/m (1906.46 g/m)
#2: x=663.2 | 571.96 mm2 = 1.5443 kg/m (1544.29 g/m)
...
```

CSV 导出列：No, Position(X), NetArea(mm2), Density(kg/m3), Material, Weight(kg/m), Weight(g/m), OuterArea(mm2), HoleAreas(mm2), Shapes, SourceType

## Prerequisites

- Python 3.10+
- ezdxf 库（读取/标注 DXF）
- openpyxl 库（`pip install openpyxl`，导出 Excel 用）
- customtkinter + tkinter（GUI 模式用；纯命令行模式可免）

## Version History

版本变更详见 `CHANGELOG.md`。旧版本归档于 `history/` 目录：
- `history/profile_calc/` — Python 核心库历史版本
- `history/gui_profile_calc/` — Python GUI 历史版本

## Notes

- v8.4 面积计算使用 Green 定理 ARC 积分，与 CAD HATCH 填充完全一致
- v8.0 弧段修正公式：`correction = copysign(segment_area, bulge)`（不含 shoelace_sign 因子）
- HATCH PolylinePath 只有 `vertices` 属性，没有 `edges`
- 分组使用几何包含检测（point_in_polygon）+ bbox 补充
- 型材排序按 x 坐标从左到右
- 共享边/不闭合多段线 = 图纸错误 → 报错而非自动修复

---

## ⚠️ 运行说明（AI灵匣整理）

本技能为「提示词驱动」型技能：SKILL.md 中引用的部分辅助脚本（scripts/ 下未随包提供的文件）为可选增强，**并非运行必需**。

- 请直接按本技能的流程与规则执行任务，不要因为缺少脚本而中断。
- 若某一步骤需要执行脚本，请由 AI 现场生成等价实现（内联 Python/Node 代码或命令行），或按文档描述直接完成对应功能。
- 如技能涉及外部 API，按其文档指引配置即可；涉及本地软件的部分，按需引导用户安装。

一切以完成用户的真实需求为准。
