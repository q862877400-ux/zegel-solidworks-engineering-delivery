# CHANGELOG — 型材截面面积与米重计算

## 版本归档结构

```
history/
├── profile_calc/           ← Python 核心计算库
└── gui_profile_calc/       ← Python GUI 版本
```

---

## Skill 封装版本

### v2.0 (2026-07-13)
- **封装来源更新**：核心脚本由旧 `profile_calc.py`(v8.5.0)+`gui_profile_calc.py`(v1.5.2) 升级为小周工具箱 `modules/profile_weight.py` **v11.31**（核心算法一致，新增：图纸编号提取、重复轮廓去重、微缺口焊接闭合、Excel 三级状态色导出、标注 DXF 统一配色）
- **单一代码源**：`profile_weight.py` 同时提供 GUI（默认）与 CLI（`argparse` 入口，复用其已有核心函数，算法零改动）；旧两个脚本归档至 `history/`
- **新增 CLI 导出**：`--export xlsx|csv|dxf`，复用 `export_xlsx`/`export_csv`/`generate_annotation_dxf`
- **依赖补充**：新增 `openpyxl`（Excel 导出）；frontmatter 增加 `version: "2.0"`
- **移除 LSP 能力**：GstarCAD AutoLISP 插件（AlumWeight.lsp / MergeSegments.lsp）已从 skill 移除（AI灵匣.cn 不允许 `.lsp` 文件类型；且 skill 定位聚焦 Python 版）。LSP 源码仍保留在小周工具箱真相源，不随 skill 分发。

## profile_calc.py (Python 核心库)

### v8.5.0 (2026-07-01) — 当前版本
- **未闭合轮廓策略变更**: gap >= 0.1mm 的 LWPOLYLINE 不再跳过，改为强制闭合计算面积 + 标记错误
- 轮廓以 `source='implicit_closed'` 加入分组，保证外轮廓未闭合时内部孔洞不会被误识别为独立型材
- 强制闭合时使用 shoelace 纯多边形面积（跳过 arc correction，因为 bulge 值在非闭合几何上无意义）
- **tiny implicit_closed 碎片过滤**: `get_net_area_for_group()` 中顶点数 <= 4 的 implicit_closed 碎片不再作为外轮廓或孔洞候选，避免未闭合小线段被误算成主轮廓
- 错误信息含 `fix` 字段，提示用户在 CAD 中 PEDIT->CLOSE 以获得准确结果
- 结果: 未闭合轮廓仍参与计算，但标记"仅供参考"；用户修图后自动得到正确结果

### v8.4.1 (2026-07-01)
- **未闭合 LWPOLYLINE 检测**: 当 `closed=False` 且 gap >= 0.1mm 时，不再强制计算闭合面积，而是记录错误并跳过
- 修复问题: 未闭合型材（如 新块999.dxf 中 gap=60mm 的轮廓）被错误算成 ~1.12 kg/m，与正常闭合型材几乎相同
- `get_all_contours_from_dxf()` 现在返回 `(all_contours, errors)` 元组
- CLI 输出显示: `[ERROR] LWPOLYLINE handle=XX is not closed (gap=YY.YYmm)`

### v8.4.0 (2026-06-29)
- **Green 定理 ARC 面积**: `cross(A,C)+cross(C,B)+r^2*sweep` 替代 chord+correction
- 修复 v8.3 缩进 bug（`for nb,si in adj[u]` 在 `for i` 循环外，只处理最后一条 ARC）
- 修复 12/23 ARC 的 cycle 遍历方向与 entity 方向相反导致符号错误
- 结果: #1=90.49, #2=90.49 mm^2 (与 CAD HATCH 完全一致)
- **HATCH PolylinePath 支持**: vertices + bulge 面积计算（path.edges 不存在）
- path_type_flags: bit 0=1 外部, bit 0=0 内孔
- 68 型材全通过验证

### v8.3.0
- ARC sweep > 180° 修复: 用 entity sweep 替代 atan2 的 theta
- 结果: #2=89.00→89.77 mm^2 (残余 0.72 来自几何顶点偏移)

### v8.2.0
- ARC+LINE cycle-tracing 重建 (端点链 + DFS + shoelace+bulge)

### v8.1.0
- ARC+LINE 集群重建: 形状签名模板匹配 + Bresenham 光栅化回退

### v8.0.1
- effectively_closed gap 阈值 0.01→0.1mm
- close_if_needed 强制生效

### v8.0.0
- 精确圆弧面积 (Shoelace + bulge 弧段修正), 与 AutoCAD vla-get-Area 等价
- 弃用 ezdxf make_path 贝塞尔近似 (v7.0 有 ~2mm^2 误差)

---

## gui_profile_calc.py (Python GUI)

### v1.5.2 (2026-07-01) — 当前版本
- **状态栏显示错误型材数量**: 完成提示由 "⚠️ 存在图纸错误" 改为 "⚠️ N 个型材存在图纸错误"，更直观
- 版本号: v1.5.2

### v1.5.1 (2026-07-01)
- **修复 v1.5 回归: 大量型材米重变为 0**: 外轮廓选择改回"面积最大优先"，避免高质量小轮廓被误选为外轮廓、真实大轮廓被扣为孔洞导致净面积为负
- **tiny implicit_closed 碎片不再参与外轮廓/孔洞**: 顶点数 <= 4 的 implicit_closed 碎片从分组候选中完全剔除（之前仅剔除孔洞，仍可误选为外轮廓）
- **孔洞 handle 去重**: 同一 handle 不会同时以 attached_open 和 implicit_closed 被重复扣除
- **负净面积保护**: 若孔洞总面积超过外轮廓面积，标记 geometry_error 并截断为 0，不再输出负米重
- 版本号: v1.5.1

### v1.5 (2026-07-01)
- **错误轮廓仍参与面积扣除**: shared_edge / open_polyline 等图纸错误不再阻止孔洞面积扣除，避免结果严重失真（如 #2 从 17.9918 修正为 1.5443 kg/m）
- **外轮廓选择优先级**: 优先使用 `closed_lwpoly` > `effectively_closed` / `merged_fragments` > `implicit_closed` > `attached_open`，避免 tiny implicit_closed 碎片被误选为外轮廓（如 #58 修正为 0.7128 kg/m）
- **跳过 tiny implicit_closed 碎片**: 顶点数 <= 4 的 implicit_closed 轮廓不再作为孔洞扣除，避免碎片拉低净面积
- **共享边检测例外**: 外轮廓与候选孔洞均为 `implicit_closed` 时，视为同一型材的重复/简化表达，不再判定为 shared_edge 图纸错误
- 版本号: v1.5

### v1.4 (2026-07-01)

### v1.3 (2026-07-01)
- **全局错误注入型材**: 未闭合 LWPOLYLINE 等全局错误自动关联到距离最近的型材
- CSV 导出: 错误数 / 错误详情 列显示未闭合轮廓信息
- 标注 DXF 导出: 含未闭合错误的型材自动标红并显示错误详情
- **同步 v8.4.1**: 未闭合 LWPOLYLINE 检测 (gap >= 0.1mm → 报错，不计算面积)
- GUI 输出显示: `⚠️ 检测到 N 个未闭合轮廓（已跳过）`

### v1.2 (2026-07-01)
- 同步 v8.4.1 未闭合检测逻辑到 GUI

### v1.1 (2026-06-30)
- 修复 #2 shared_edge 误判: 双方 effectively_closed 时跳过 shared_edge 检测
- Phase 2 用连通分量 + LINE/ARC 端点匹配替代固定 5mm 阈值
- 导出标注 DXF: 青色(正常) + 红色(错误), 标注全部型材
- 68 型材全通过验证

### v1.3
- #58 修复: gap>5mm 的 open poly 拆碎入 fragment 池
- #66 修复: 错误轮廓不从净面积扣除
- 11A+11B+LINE 11C → 264.00mm^2 → 0.7128 kg/m

### v1.2
- 修复丢失 3 个型材: effectively_closed 处理恢复
- 66→68 型材, 与旧版一致

### v1.1 / v8.5
- 共享边 = 图纸错误, 报错而非自动修复
- 新增 generate_error_annotation_dxf()
- GUI 红色高亮错误行

---

## 关键经验教训

### 弧面积算法
1. **不要用 Green 定理直接算弧面积** — cross(A,C)+cross(C,B) 对大坐标(~10000)产生巨大值
2. **PEDIT JOIN 是最可靠方案** — 让 CAD 引擎自己算面积
3. **chord+bulge 近似** 对 sweep>180° 弧有 ~1.2% 误差

### ezdxf HATCH 处理
1. PolylinePath 只有 `vertices`, 没有 `edges` 属性
2. `path_type_flags & 1 == 0` → 内孔, `& 1 == 1` → 外边界
